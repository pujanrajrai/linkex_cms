from xml.etree import ElementTree as ET
from datetime import datetime, timedelta
from hub.models import VendorLoginCred
from awb.apis.utils import AWBDetailsFetcher
import requests
from awb.models import AWBAPIResponse, AWBDetail, BoxDetails
from datetime import datetime

import xml.etree.ElementTree as ET
from xml.dom import minidom
from datetime import datetime


def build_sgau_xml(details, username, password, security_key, auth_code, account_number, service_code):
    awb_info = details["details"]
    consignor = details["consignor"]
    consignee = details["consignee"]
    boxes = details["boxes"]

    root = ET.Element("FFUSACourier", action="Request", version="1.0")

    # --- Requestor ---
    requestor = ET.SubElement(root, "Requestor")
    ET.SubElement(requestor, "Username").text = username
    ET.SubElement(requestor, "Password").text = password
    ET.SubElement(requestor, "SecurityKey").text = security_key
    ET.SubElement(requestor, "AuthorizeCode").text = auth_code
    ET.SubElement(requestor, "AccountNumber").text = account_number

    # --- Shipment ---
    shipments = ET.SubElement(root, "Shipments")
    shipment = ET.SubElement(shipments, "Shipment")

    # Details
    details_tag = ET.SubElement(shipment, "Details")
    ET.SubElement(details_tag, "Date").text = datetime.today().strftime(
        "%Y-%m-%d")
    ET.SubElement(details_tag, "ServiceType").text = awb_info.get(
        "service_code")
    ET.SubElement(details_tag, "ServiceCode").text = service_code
    ET.SubElement(details_tag, "CustomerReference").text = ""
    ET.SubElement(details_tag, "ShipmentReference").text = awb_info.get(
        "awbno", "")
    ET.SubElement(details_tag, "CustomsReference").text = ""

    # Billing
    billing = ET.SubElement(shipment, "Billing")
    ET.SubElement(billing, "ChargesBillToAccountNumber").text = account_number
    ET.SubElement(billing, "ChargesBillToType").text = "S"
    ET.SubElement(billing, "DutiesBillToAccountNumber").text = account_number
    ET.SubElement(billing, "DutiesBillToType").text = "S"

    # Shipper
    shipper = ET.SubElement(shipment, "Shipper")
    ET.SubElement(shipper, "CompanyName").text = consignor.get("company", "")
    ET.SubElement(shipper, "ContactName").text = consignor.get("name", "")
    ET.SubElement(shipper, "Address1").text = consignor.get("address1", "")
    ET.SubElement(shipper, "Address2").text = consignor.get("address2", "")
    ET.SubElement(shipper, "City").text = consignor.get("city", "")
    ET.SubElement(shipper, "StateProvince").text = consignor.get("state", "")
    ET.SubElement(shipper, "ZipPostal").text = consignor.get("postcode", "")
    ET.SubElement(shipper, "Country").text = consignor.get(
        "country_short_name", "")
    ET.SubElement(shipper, "Phone").text = consignor.get("phone", "")
    ET.SubElement(shipper, "Email").text = consignor.get("email", "")
    ET.SubElement(shipper, "Reference").text = ""

    # Receiver
    receiver = ET.SubElement(shipment, "Receiver")
    ET.SubElement(receiver, "CompanyName").text = consignee.get("company", "")
    ET.SubElement(receiver, "ContactName").text = consignee.get("name", "")
    ET.SubElement(receiver, "Address1").text = consignee.get("address1", "")
    ET.SubElement(receiver, "Address2").text = consignee.get("address2", "")
    ET.SubElement(receiver, "City").text = consignee.get("city", "")
    ET.SubElement(receiver, "StateProvince").text = consignee.get("state", "")
    ET.SubElement(receiver, "ZipPostal").text = consignee.get("postcode", "")
    ET.SubElement(receiver, "Country").text = consignee.get(
        "country_short_name", "")
    ET.SubElement(receiver, "Reference").text = ""
    ET.SubElement(receiver, "Phone").text = consignee.get("phone", "")
    ET.SubElement(receiver, "Email").text = consignee.get("email", "")
    ET.SubElement(receiver, "Taxid").text = ""

    # Packages
    packages = ET.SubElement(shipment, "Packages")
    product_type = ""
    if awb_info.get("product_type") == "DOX":
        product_type = "D"
    elif awb_info.get("product_type") == "NON-DOX":
        product_type = "P"

    ET.SubElement(packages, "NumberOfPackages").text = str(len(boxes))
    for idx, box in enumerate(boxes, 1):

        pkg = ET.SubElement(packages, "Package")
        ET.SubElement(pkg, "SequenceNumber").text = str(idx)
        ET.SubElement(pkg, "PackageType").text = product_type
        ET.SubElement(pkg, "Weight").text = str(box.get("actual_weight", 0))
        ET.SubElement(pkg, "WeightType").text = "KG"

        dims = box.get("dimensions", {})
        ET.SubElement(pkg, "Length").text = str(dims.get("length"))
        ET.SubElement(pkg, "Width").text = str(dims.get("breadth"))
        ET.SubElement(pkg, "Height").text = str(dims.get("height"))
        ET.SubElement(pkg, "DimUnit").text = "CM"

        ET.SubElement(pkg, "CustomsValue").text = str(
            awb_info.get("shipment_value", 0))
        ET.SubElement(pkg, "Currency").text = "USD"
        ET.SubElement(pkg, "Content").text = awb_info.get("content", "")

    # Other fields
    ET.SubElement(shipment, "LabelType").text = "Z"
    ET.SubElement(shipment, "CommercialInvoice").text = "False"
    ET.SubElement(shipment, "Sku").text = awb_info.get("sku", "")
    ET.SubElement(shipment, "Hscode").text = awb_info.get("hs_code", "")
    ET.SubElement(shipment, "Vatno").text = awb_info.get("vat_number", "")
    ET.SubElement(shipment, "TempShipDate").text = awb_info.get(
        "is_temp_ship", "No")
    ET.SubElement(shipment, "InboundTracking").text = awb_info.get(
        "inbound_tracking", "")

    # Prettify and return XML string
    rough_string = ET.tostring(root, encoding="utf-8")
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="    ")


def sgau_api(awbno):
    # --- Fetch AWB Object ---
    awb_obj = AWBDetail.objects.get(awbno=awbno)

    # --- Pre-checks ---
    if not awb_obj.is_verified:
        return {"success": False, "awbno": awbno, "message": "AWB must be verified first"}
    if awb_obj.is_api_called_success:
        return {"success": True, "awbno": awbno, "message": "Already submitted to SGAU"}
    if not awb_obj.is_editable:
        return {"success": False, "awbno": awbno, "message": "AWB is not editable"}
    if awb_obj.vendor.code != "SGAU":
        return {"success": False, "awbno": awbno, "message": "AWB is not for SGAU"}
    if awb_obj.total_box > 1:
        return {"success": False, "awbno": awbno, "message": "SGAU does not support multiple boxes"}

    # --- Credentials ---
    cred = VendorLoginCred.objects.get(vendor__code="SGAU")
    username = cred.username.strip()
    password = cred.password.strip()
    security_code = cred.additional_cred1.strip()
    authorize_code = cred.additional_cred2.strip()
    account_number = cred.additional_cred3.strip()
    service_code = cred.additional_cred4.strip()

    # --- Shipment Details ---
    details = AWBDetailsFetcher(awbno).get_details()

    # --- Build XML Payload ---
    try:
        xml_payload = build_sgau_xml(
            details,
            username=username,
            password=password,
            security_key=security_code,
            auth_code=authorize_code,
            account_number=account_number,
            service_code=service_code
        )
    except Exception as e:
        return {"success": False, "awbno": awbno, "message": f"XML creation failed: {e}"}
    # --- Send XML to API ---
    try:
        url = "https://www.shipglobal.au/api/shipmentprocess"
        headers = {"Content-Type": "application/xml"}

        response = requests.post(url, headers=headers,
                                 data=xml_payload.encode("utf-8"), timeout=30)
        response.raise_for_status()
        result_text = response.text

        # Save raw API response
        api_response = AWBAPIResponse.objects.create(
            awb=awb_obj,
            vendor="SGAU",
            request_url=url,
            payload=xml_payload,
            response=result_text,
            is_success=False
        )

        # --- XML Parsing ---
        root = ET.fromstring(result_text)
        shipment = root.find("Shipment")
        result_tag = shipment.findtext("Result", default="").strip()

        if result_tag.lower() == "success":
            tracking_number = shipment.findtext(
                "TrackingNumber", default="").strip()
            label = shipment.findtext("Label", default="").strip()
            invoice = shipment.findtext("Invoice", default="").strip()

            awb_obj.is_api_called_success = True
            awb_obj.is_editable = False
            awb_obj.forwarding_number = tracking_number
            awb_obj.label_1 = label
            awb_obj.reference_number = tracking_number
            awb_obj.save(update_fields=[
                "is_api_called_success", "is_editable", "label_1", "reference_number", "forwarding_number"
            ])

            api_response.is_success = True
            api_response.save(update_fields=["is_success"])

            return {
                "success": True,
                "awbno": awbno,
                "message": "Shipment submitted successfully to SGAU",
                "data": {
                    "tracking_number": tracking_number,
                    "label": label,
                    "invoice": invoice,
                    "raw_response": result_text
                }
            }

        else:
            failure_message = shipment.findtext(
                "Message", default="SGAU API responded with failure").strip()
            return {
                "success": False,
                "awbno": awbno,
                "message": failure_message,
                "data": result_text
            }
    except Exception as e:
        AWBAPIResponse.objects.create(
            awb=awb_obj,
            vendor="SGAU",
            request_url=url,
            payload=xml_payload,
            response={"exception": str(e)},
            is_success=False
        )
        return {
            "success": False,
            "awbno": awbno,
            "message": f"Request to SGAU failed: {e}"
        }
