from hub.models import VendorLoginCred
from awb.apis.utils import AWBDetailsFetcher
from awb.models import AWBAPIResponse, AWBDetail, BoxDetails
import requests


def couriex_api(awbno):
    try:
        awb_obj = AWBDetail.objects.get(awbno=awbno)
    except AWBDetail.DoesNotExist:
        return {"success": False, "awbno": awbno, "message": "AWB does not exist."}

    if not awb_obj.is_editable:
        return {"success": False, "awbno": awbno, "message": "AWB can't be edited because it is verified through API"}
    if awb_obj.is_api_called_success:
        return {"success": True, "awbno": awbno, "message": "AWB is already called"}
    if not awb_obj.is_verified:
        return {"success": False, "awbno": awbno, "message": "AWB must be verified before calling API"}
    if awb_obj.vendor.code.strip().upper() != "COURIERX":
        return {"success": False, "awbno": awbno, "message": "Only vendor with CourierX code can call this API"}

    cred = VendorLoginCred.objects.get(vendor__code="COURIERX")
    details = AWBDetailsFetcher(awbno).get_details()
    awb_info = details.get("details", {})
    consignee = details.get("consignee", {})
    consignor = details.get("consignor", {})
    boxes = details.get("boxes", [])
    couriex_code = awb_info.get("couriex_code", "")
    destination_code = awb_info.get("destination_short_name", "")
    city = consignee.get("city", "").upper()
    if destination_code == "AE":
        if city == "DUBAI":
            couriex_code = "DXB"
        elif city == "ABU DHABI" or city == "ABUDHABI":
            couriex_code = "AUH"
        elif city == "AJMAN":
            couriex_code = "AJM"
        elif city == "ALAIN" or city == "AL AIN":
            couriex_code = "ALN"
        elif city == "FUJAIRAH":
            couriex_code = "FUJ"
        elif city == "RAS AL KHAIMAH":
            couriex_code = "RAK"
        elif city == "UMM AL QAIWAIN":
            couriex_code = "UAQ"
        elif city == "SHARJAH":
            couriex_code = "SHJ"
        else:
            couriex_code = ""

    payload = {
        "Consignee": consignee.get("company", ""),
        "ConsigneeAddress1": consignee.get("address1", ""),
        "ConsigneeAddress2": consignee.get("address2", ""),
        "ConsigneeCPerson": consignee.get("name", ""),
        "ConsigneeState": consignee.get("state_short_name", ""),
        "ConsigneeCity": consignee.get("city", ""),
        "ConsigneeCountry": consignee.get("country", ""),
        "ConsigneeID": "",
        "ConsigneeIDType": "",
        "ConsigneeMob": consignee.get("phone", ""),
        "ConsigneePhone": consignee.get("phone", ""),
        # consignee completed
        "CountryCode": consignee.get("country_short_name", ""),
        "Destination": couriex_code,
        "GoodsDescription": awb_info.get("content", ""),
        "Origin": "KTM",
        "ProductType": awb_info.get("product_type", ""),
        "Quantity": awb_info.get("box_count", ""),
        "RetailZipCode": consignee.get("postcode", ""),

        "ServiceType": "NOR",

        "Shipper": consignor.get("company", ""),
        "ShipperAddress1": consignor.get("address1", ""),
        "ShipperAddress2": consignor.get("address2", ""),
        "ShipperCPErson": consignor.get("name", ""),
        "ShipperCity": consignor.get("city", ""),
        "ShipperCountry": consignor.get("country", ""),
        "ShipperPhone": consignor.get("phone", ""),
        "ShipperEmail": consignor.get("email", ""),
        "ShipperMobile": consignor.get("phone", ""),
        "ShipperRefNo": awb_info.get("awbno", ""),
        "SpecialInstruction": "",
        "ValueCurrency": "USD",
        "ValueOfShipment": awb_info.get("shipment_value", ""),
        "VatNo": "",
        "Weight": awb_info.get("total_actual_weight", ""),
        "UserName": cred.username,
        "Password": cred.password,
        "AccountNo": cred.additional_cred1,
        "PackageRequest": [
            {
                "DimHeight": box.get("dimensions", {}).get("height", ""),
                "DimWidth": box.get("dimensions", {}).get("breadth", ""),
                "DimLength": box.get("dimensions", {}).get("length", ""),
                "DimWeight": box.get("actual_weight", ""),
            } for box in boxes
        ],
        "ExportItemDeclarationRequest": [
            {
                "DimWeight": box.get("actual_weight", ""),
                "NoofPeices": item.get("quantity", ""),
                "ShipmentValue": item.get("amount", ""),
                "ItemDesc": item.get("description", ""),
                "HSCODE": item.get("hs_code", ""),
                "CountryofOrigin": consignee.get("country_short_name", ""),
            }
            for box in boxes for item in box.get("items", [])
        ]
    }

    if awb_info.get("service_code") == "UPS":
        url = "https://ups.couriex.com/Service.svc/CreateAirwayBillUPS"
    elif awb_info.get("service_code") == "COURIERX":
        url = "https://ideal.couriex.com/Service.svc/CreateAirwayBill"
    else:
        return {"success": False, "awbno": awbno, "message": "Invalid service code"}

    try:
        response = requests.post(url, json=payload, timeout=20)
        response.raise_for_status()
        res = response.json()

        is_success = res.get("Code") == 1

        # Save raw API response
        AWBAPIResponse.objects.create(
            awb=awb_obj,
            vendor="COURIERX",
            request_url=url,
            payload=payload,
            response=res,
            pdf=res.get("Invoice", ""),
            is_success=is_success
        )

        if is_success:
            # Save AWB-level reference number
            awb_obj.reference_number = res.get("AirwayBillNumber", "")

            # Split forwarding numbers and labels
            forwarding_nos = res.get(
                "AgentAirwayBillNumber", "").strip(",").split(",")
            label_data = res.get("AgentLabelData", [])

            # Update each box
            box_qs = list(BoxDetails.objects.filter(awb=awb_obj))
            box_qs.sort(key=lambda b: b.get_box_number())
            for idx, box in enumerate(box_qs):
                box.box_awb_no = forwarding_nos[idx] if idx < len(
                    forwarding_nos) else ""
                box.box_label = label_data[idx] if idx < len(
                    label_data) else ""
                box.box_api_response = {
                    "awb": box.box_awb_no,
                    "label": box.box_label
                }
                box.save(update_fields=["box_awb_no",
                         "box_label", "box_api_response"])

            # Save AWB status
            awb_obj.forwarding_number = ", ".join(forwarding_nos)
            awb_obj.label_1 = label_data[0] if label_data else ""
            awb_obj.is_api_called_success = True
            awb_obj.is_editable = False
            awb_obj.save(update_fields=[
                "reference_number", "forwarding_number", "label_1",
                "is_api_called_success", "is_editable"
            ])

            return {
                "success": True,
                "awbno": awbno,
                "message": "AWB submitted to Couriex (UPS) successfully",
                "data": res
            }

        else:
            return {
                "success": False,
                "awbno": awbno,
                "message": res.get("Description", "Couriex API error"),
                "data": res
            }

    except requests.RequestException as e:
        AWBAPIResponse.objects.create(
            awb=awb_obj,
            vendor="UPS",
            request_url=url,
            payload=payload,
            response={"exception": str(e)},
            is_success=False
        )
        return {
            "success": False,
            "awbno": awbno,
            "message": f"Couriex API request error: {e}"
        }
