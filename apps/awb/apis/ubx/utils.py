from hub.models import VendorLoginCred
from awb.apis.utils import AWBDetailsFetcher
import requests
from awb.models import AWBAPIResponse, AWBDetail, BoxDetails


def ubx_api(awbno):
    awb_obj = AWBDetail.objects.get(awbno=awbno)

    # --- pre-checks ---
    if not awb_obj.is_editable:
        return {"success": False, "awbno": awbno,
                "message": "AWB can't be edited because it is verified through API"}
    if awb_obj.is_api_called_success:
        return {"success": True, "awbno": awbno,
                "message": "AWB is already called"}
    if not awb_obj.is_verified:
        return {"success": False, "awbno": awbno,
                "message": "AWB must be verified before calling API"}
    if awb_obj.vendor.code != "UBX":
        return {"success": False, "awbno": awbno,
                "message": "Only vendor with UBX code can call this API"}

    # --- credentials & details ---
    cred = VendorLoginCred.objects.get(vendor__code="UBX")
    username = cred.username
    password = cred.password
    customer_code = cred.additional_cred1

    details = AWBDetailsFetcher(awbno).get_details()
    awb_info = details["details"]
    consignee = details["consignee"]

    url = "https://ship.ubx.uk.net/api/v1/Awbentry/Awbentry"
    # Normalize service keys for consistent comparison
    our_service = {
        'UPS MAIL DDU': 'UPS MAIL DDU',
        'UPS SAVER': 'UPS Saver',
        'UPS STANDARD': 'UPS Standard',
        'UPS EXPEDITED': 'UPS Expedited',
    }

    # Clean and normalize the incoming service string
    raw_service = awb_info.get("service", "").strip().upper()

    # Get formatted service name if it exists in our_service
    awb_service = our_service.get(raw_service, raw_service)

    # Generate performa only if the normalized service is in our predefined list
    if raw_service in our_service:
        performa = [
            {
                "BoxNo":       f"Box-{item['box_number']}",
                "Description": item["description"],
                "HSNCode":     item["hs_code"],
                "Quantity":    item["quantity"],
                "Unit":        item["unit_type"],
                "Rate":        item["unit_rate"],
                "Amount":      item["amount"],
                "Weight":      box["actual_weight"],
            }
            for box in details.get("boxes", [])
            for item in box.get("items", [])
        ]
    else:
        performa = []
    payload = {
        "UserID":          username,
        "Password":        password,
        "CustomerCode":    customer_code,
        "CustomerRefNo":   details["awb_no"],
        "OriginName":      "NP",
        "DestinationName": awb_info["destination_short_name"],
        "ShipperName":     "Ideal Cargo and Courier Pvt ltd",
        "ShipperContact":  "ANISH MANDAL",
        "ShipperAdd1":     "Battisputali Road",
        "ShipperAdd2":     "Near Dwarika Hotel",
        "ShipperCity":     "KTM",
        "ShipperState":    "BAGMATI",
        "ShipperPin":      "44600",
        "ShipperTelno":    "977-01-4478809",
        "ShipperMobile":   "977014478809",
        "ShipperEmail":    "idealcouriernpl@gmail.com",
        "DocumentType":    "",
        "DocumentNumber":  "",
        "ConsigneeName":    consignee.get("company", ""),
        "ConsigneeContact": consignee.get("name", ""),
        "ConsigneeAdd1":    consignee.get("address1", ""),
        "ConsigneeAdd2":    consignee.get("address2", ""),
        "ConsigneeCity":    consignee.get("city", ""),
        "ConsigneeState":   consignee.get("state_short_name", ""),
        "ConsigneePin":     consignee.get("postcode", ""),
        "ConsigneeTelno":   consignee.get("phone", ""),
        "ConsigneeMobile":  consignee.get("phone", ""),
        "ConsigneeEmail":   consignee.get("email", ""),
        "Instruction":      "",
        "VendorName":       awb_info.get("service_code", ""),
        "ServiceName":      awb_info.get("service", ""),
        "ProductCode":      "SPX",
        "Dox_Spx":          "SPX",
        "Pieces":           awb_info.get("box_count", ""),
        "Weight":           awb_info.get("total_actual_weight", ""),
        "Content":          awb_info.get("content", ""),
        "Currency":         awb_info.get("currency", ""),
        "ShipmentValue":    awb_info.get("shipment_value", ""),
        "CODAmount":        "",
        "CSBType":          "",
        "TermofInvoice":    "",
        "InvoiceNo":        awb_info["awb_no"],
        "InvoiceDate":      awb_info["created_at"].strftime("%Y%m%d"),
        "CompanyCode":      "",
        "IsCommercial":     "0",
        "Dimensions": [
            {
                "ActualWeight": box["actual_weight"],
                "Vol_WeightL":  box["dimensions"]["length"],
                "Vol_WeightW":  box["dimensions"]["breadth"],
                "Vol_WeightH":  box["dimensions"]["height"],
            }
            for box in details["boxes"]
        ],
        "Performa": performa
    }
    try:
        resp = requests.post(url, json=payload, timeout=20)
        resp.raise_for_status()
        res = resp.json().get("Response", {})

        is_success = (
            res.get("Status", "").lower() == "success"
            and res.get("APIStatus", "").lower() == "success"
            and res.get("ErrorCode", "") == "0"
        )

        # record raw API response
        AWBAPIResponse.objects.create(
            awb=awb_obj,
            vendor="UBX",
            request_url=url,
            payload=payload,
            response=res,
            pdf=res.get("Pdfdownload", ""),
            is_success=is_success
        )

        if is_success:
            # 1. Save AWB-level PDF

            try:
                refrence_number = res.get("AWBNo", "")
                awb_obj.reference_number = refrence_number
                awb_obj.save(update_fields=["reference_number"])
            except:
                pass
            # 2. Build comma-separated list of all label forwarding numbers
            labels = res.get("Labels", [])
            forwarding_nos = [
                lbl.get("ForwardingNo") or lbl.get("ForwardingNo1")
                for lbl in labels
                if lbl.get("ForwardingNo") or lbl.get("ForwardingNo1")
            ]

            if awb_obj.service.code.strip() == "DPD" or awb_obj.service.code.strip() == "DPDG":
                forwarding_nos = [
                    f"{res.get('ForwardingNo', '')}"
                ]
                awb_obj.forwarding_number = ", ".join(forwarding_nos)
                awb_obj.is_editable = False
                awb_obj.is_api_called_success = True
                awb_obj.label_1 = res.get("Label", "")

                awb_obj.save(update_fields=[
                    "forwarding_number",
                    "is_editable",
                    "is_api_called_success",
                    "label_1"
                ])
                return {
                    "success": True,
                    "awbno": awbno,
                    "message": "AWB submitted successfully",
                    "data": res
                }

            awb_obj.forwarding_number = ", ".join(forwarding_nos)

            # 3. Update each box (sorted by box number)
            box_qs = list(BoxDetails.objects.filter(awb=awb_obj))
            box_qs.sort(key=lambda b: b.get_box_number())
            for idx, box in enumerate(box_qs):
                info = labels[idx] if idx < len(labels) else {}
                box.box_label = info.get("Label", "")
                box.box_api_response = info
                box.box_awb_no = info.get(
                    "ForwardingNo") or info.get("ForwardingNo1")
                box.save(update_fields=[
                    "box_label",
                    "box_api_response",
                    "box_awb_no"
                ])
                print(info.get("Label", ""))

            # 4. Lock and mark success
            awb_obj.is_api_called_success = True
            awb_obj.is_editable = False
            awb_obj.save(update_fields=[
                "forwarding_number",
                "is_api_called_success",
                "is_editable"
            ])

            message = "AWB submitted successfully"
        else:
            message = (
                res.get("APIError")
                or ", ".join(e.get("Description", "") for e in res.get("Error", []))
                or "Unknown API error"
            )

        return {
            "success": is_success,
            "awbno":   awbno,
            "message": message,
            "data":    res,
        }

    except requests.RequestException as e:
        AWBAPIResponse.objects.create(
            awb=awb_obj,
            vendor="UBX",
            request_url=url,
            payload=payload,
            response={"exception": str(e)},
            is_success=False
        )
        return {
            "success": False,
            "awbno":   awbno,
            "message": f"Request error: {e}"
        }
