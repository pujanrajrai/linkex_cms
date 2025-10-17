from datetime import datetime, timedelta
from hub.models import VendorLoginCred
from awb.apis.utils import AWBDetailsFetcher
import requests
from awb.models import AWBAPIResponse, AWBDetail, BoxDetails
from datetime import datetime


def dtdc_api(awbno):
    awb_obj = AWBDetail.objects.get(awbno=awbno)

    # --- Pre-checks ---

    if not awb_obj.is_verified:
        return {"success": False, "awbno": awbno, "message": "AWB must be verified first"}
    if awb_obj.is_api_called_success:
        return {"success": True, "awbno": awbno, "message": "Already submitted to PostShipping"}
    if not awb_obj.is_editable:
        return {"success": False, "awbno": awbno, "message": "AWB is not editable"}
    if awb_obj.vendor.code != "DTDC":
        return {"success": False, "awbno": awbno, "message": "AWB is not for DTDC"}

    # --- Credentials ---
    cred = VendorLoginCred.objects.get(vendor__code="DTDC")
    token = cred.password.strip()

    # --- Shipment Details ---
    details = AWBDetailsFetcher(awbno).get_details()
    awb_info = details["details"]
    consignor = details["consignor"]
    consignee = details["consignee"]
    boxes = details["boxes"]
    service_code = awb_info.get("service_code", "")
    if service_code == "DPD111" or service_code == "DPD112" or service_code == "DPDUKEPND":
        third_party_token = "32A4D3D985DA8D47020688462C48BB2C"
    elif service_code == "ERD" or service_code == "ERD111" or service_code == "ERP":
        third_party_token = "B804BCFAFC79DEDF647E1F2FA7BD5523"
    elif service_code == "MDPD112":
        third_party_token = "8C04CCBE70E166A67C8369045ACF5BFF"
    elif service_code == "UKMND" or service_code == "UKMNDM":
        third_party_token = "B381C6199000148430851B87714D8FAE"
    elif service_code == "UKUPS" or service_code == "UPSWEXPD":
        third_party_token = "521B45BC3342EF23140A73A398A6BB9A"

    elif service_code == "DTDCEU" or service_code == "UPSSPLN":
        third_party_token = "84AFBD9845D4B89793D5559C7795EC19"
    else:
        third_party_token = ""

    if service_code == "UPSSPLN":
        pieces = [
            {
                "Weight": float(item.get("unit_weight", 0)),
                "Quantity": int(item.get("quantity", 1)),
                "HarmonisedCode": item.get("hs_code", "")[:30],
                "GoodsDescription": item.get("description", "")[:255],
                "Content": item.get("description", "")[:255],
                "Notes": "",
                "SenderRef1": "",
                "ManufactureCountryCode": consignor.get("country_short_name", ""),
                "OriginCountryCode": consignor.get("country_short_name", ""),
                "CurrencyCode": awb_info.get("currency", "")[:3],
                "CustomsValue": float(item.get("amount", 0)),
                "DeadWeight": float(item.get("unit_weight", 0)),
                "Reference": item.get("reference", f"REF{item.get('id', 0)}")[:30],
                "CPCCode": "",
                "GoodsValue": float(item.get("amount", 0)),
                "GSTValue": 0.0,
                "GSTCurrencyCode": ""
            } for box in boxes for item in box.get("items", [])
        ]
    else:
        pieces = []

    payload = [{
        "ThirdPartyToken": "",
        "SenderDetails": {
            "SenderName": consignor.get("name", "")[:40],
            "SenderCompanyName": consignor.get("company", "")[:100],
            "SenderCountryCode": consignor.get("country_short_name", "")[:2],
            "SenderAdd1": consignor.get("address1", "")[:75],
            "SenderAdd2": consignor.get("address2", "")[:75],
            "SenderAdd3": "",
            "SenderAddCity": consignor.get("city", "")[:50],
            "SenderAddState": consignor.get("state", "")[:50],
            "SenderAddPostcode": consignor.get("postcode", "")[:50],
            "SenderPhone": consignor.get("phone", "")[:20],
            "SenderEmail": consignor.get("email", "")[:200],
            "SenderFax": "",
            "SenderKycType": consignor.get("document_type", "")[:200],
            "SenderKycNumber": consignor.get("document_number", "")[:200],
            "SenderReceivingCountryTaxID": "",
        },
        "ReceiverDetails": {
            "ReceiverName": consignee.get("name", "")[:40],
            "ReceiverCompanyName": consignee.get("company", "")[:100],
            "ReceiverCountryCode": consignee.get("country_short_name", "")[:2],
            "ReceiverAdd1": consignee.get("address1", "")[:75],
            "ReceiverAdd2": consignee.get("address2", "")[:75],
            "ReceiverAdd3": "",
            "ReceiverAddCity": consignee.get("city", "")[:50],
            "ReceiverAddState": consignee.get("state", "")[:50],
            "ReceiverAddPostcode": consignee.get("postcode", "")[:50],
            "ReceiverMobile": consignee.get("phone_2", "")[:20],
            "ReceiverPhone": consignee.get("phone", "")[:20],  # Mandatory
            "ReceiverEmail": consignee.get("email", "")[:200],
            "ReceiverAddResidential": "N",
            "ReceiverFax": "",
            "ReceiverKycType": consignee.get("document_type", "")[:200],
            "ReceiverKycNumber": consignee.get("document_number", "")[:200],
        },
        "PackageDetails": {
            "GoodsDescription": awb_info.get("content", "")[:200],
            "CustomValue": float(awb_info.get("shipment_value", 0)),
            "CustomCurrencyCode": awb_info.get("currency", "")[:3],
            "InsuranceValue": "0.00",
            "InsuranceCurrencyCode": awb_info.get("currency", "")[:3],
            "ShipmentTerm": awb_info.get("shipment_terms", "")[:3],
            "GoodsOriginCountryCode": consignor.get("country_short_name", "")[:2],
            "DeliveryInstructions": ".",
            "Weight": float(awb_info.get("total_charged_weight", 0)),
            "WeightMeasurement": "KG",
            "NoOfItems": int(awb_info.get("box_count", 1)),
            "CubicL": 0,
            "CubicW": 0,
            "CubicH": 0,
            "CubicWeight": float(awb_info.get("total_charged_weight", 0)),
            "ServiceTypeName": f"{awb_info.get('service_code', '')}",
            "BookPickUP": False,
            "AlternateRef": "",
            "SenderRef1": awb_info.get("awbno", "")[:50],
            "SenderRef2": "",
            "SenderRef3": "",
            "DeliveryAgentCode": "",
            "DeliveryRouteCode": "",
            "BusinessType": "B2B",
            "ShipmentResponseItem": [
                {
                    "ItemAlt": "",
                    "ItemNoOfPcs": int(box.get("quantity", 1)),
                    "ItemCubicL": float(box.get("dimensions", {}).get("length", 1)),
                    "ItemCubicW": float(box.get("dimensions", {}).get("breadth", 1)),
                    "ItemCubicH": float(box.get("dimensions", {}).get("height", 1)),
                    "ItemWeight": float(box.get("actual_weight", 0)),
                    "ItemCubicWeight": float(box.get("volumetric_weight", 0)),
                    "ItemDescription": box.get("description", "Misc item")[:255],
                    "ItemCustomValue": float(box.get("custom_value", awb_info.get("shipment_value", 0))),
                    "ItemCustomCurrencyCode": awb_info.get("currency", "")[:3],
                    "Notes": "",
                    "Pieces": pieces
                } for box in boxes
            ],
            "CODAmount": 0.0,
            "CODCurrencyCode": awb_info.get("currency", "")[:3],
            "Bag": 0,
            "Notes": "",
            "OriginLocCode": "",
            "BagNumber": 0,
            "DeadWeight": float(awb_info.get("total_actual_weight", 0)),
            "ReasonExport": awb_info.get("reason_for_export", "")[:200],
            "DestTaxes": 0.0,
            "Security": 0.0,
            "Surcharge": 0.0,
            "ReceiverTaxID": "",
            "OrderNumber": "",
            "Incoterms": awb_info.get("incoterms", "CIF")[:3],
            "ClearanceReference": "",

        },
        "ThirdPartyToken": third_party_token

    }]

    # --- Send Request ---
    try:
        res = requests.post(
            "https://api.postshipping.com/api2/shipments",
            headers={
                "Content-Type": "application/json",
                "Token": token
            },
            json=payload,
            timeout=30
        )
        res.raise_for_status()
        result = res.json()

        api_response = AWBAPIResponse.objects.create(
            awb=awb_obj,
            vendor="DTDC",
            request_url="https://api.postshipping.com/api2/shipments",
            payload=payload,
            response=result,
            is_success=False
        )
        is_success = (
            result[0].get("ErrMessage", "") == ""
        )
        if is_success:
            api_response.is_success = True
            api_response.save(update_fields=["is_success"])
            awb_obj.is_api_called_success = True
            awb_obj.is_editable = False
            awb_obj.label_1 = result[0].get("LabelURL", "")
            awb_obj.reference_number = result[0].get("ShipmentNumber", "")
            awb_obj.forwarding_number = result[0].get("ShipmentNumber", "")
            awb_obj.save(update_fields=[
                         "is_api_called_success", "is_editable", "label_1", "reference_number", "forwarding_number"])
            return {
                "success": True,
                "awbno": awbno,
                "message": "Shipment submitted to PostShipping",
                "data": result
            }
        else:
            return {
                "success": False,
                "awbno": awbno,
                "message": result[0].get("ErrMessage", ""),
                "data": result
            }

    except requests.RequestException as e:
        AWBAPIResponse.objects.create(
            awb=awb_obj,
            vendor="DTDC",
            request_url="https://api.postshipping.com/api2/shipments",
            payload=payload,
            response={"exception": str(e)},
            is_success=False
        )
        return {
            "success": False,
            "awbno": awbno,
            "message": f"Request failed: {e}"
        }
