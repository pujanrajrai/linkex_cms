from hub.models import VendorLoginCred
from hub.models import Hub
from accounts.models import Agency, Company
from hub.models import RunAWB, Run
from awb.models import AWBDetail, BoxDetails, Consignee, Consignor

import requests
from datetime import datetime, timezone as dt_timezone
from django.utils import timezone
from awb.models import AWBDetail, AWBStatus
import pytz

import xml.etree.ElementTree as ET


def track_ubx_api(awb_no, reference_number, timeline, awb_details, local_tz):
    """
    Track AWB using UBX API and return updated timeline and awb_details.
    Returns tuple: (timeline, awb_details, error_message)
    """
    if reference_number == "" or reference_number is None:
        payload = {
            "UserID": "ILC100",
            "Password": "ILC100",
            "AWBNo": awb_no,
            "Type": "A"
        }
    else:
        payload = {
            "UserID": "ILC100",
            "Password": "ILC100",
            "AWBNo": reference_number,
            "Type": "A"
        }

    url = "https://ship.ubx.uk.net/api/v1/Tracking/Tracking"

    try:
        resp = requests.post(url, json=payload, timeout=10)
        resp.raise_for_status()
        data = resp.json().get("Response", {})
    except requests.RequestException as e:
        if awb_details:
            # Return local data if API fails but we have local data
            timeline.sort(
                key=lambda x: x["timestamp"] or datetime.min.replace(
                    tzinfo=local_tz),
                reverse=True
            )
            return timeline, awb_details, None
        return timeline, awb_details, f"API request failed: {e}"

    if data.get("ErrorCode") == "0":
        # Add API events to timeline (parse as UTC, then convert to Asia/Kathmandu)
        for ev in data.get("Events", []):
            try:
                # Parse dd/MM/YYYY + HHMM as naive UTC
                naive = datetime.strptime(
                    ev["EventDate"] + ev["EventTime"], "%d/%m/%Y%H%M")
                ts_utc = naive.replace(tzinfo=dt_timezone.utc)
                ts_local = ts_utc.astimezone(local_tz)
            except Exception:
                ts_local = None

            timeline.append({
                "status": ev.get("Status", ""),
                "location": ev.get("Location", "") or "",
                "timestamp": ts_local,
                "source": "api"
            })

        # If we don't have local AWB details, try to extract from API response
        if not awb_details and data.get("Tracking"):
            tracking_info = data["Tracking"][0]  # first tracking record
            awb_details = {
                'awbno': tracking_info.get("AWBNo"),
                'forwarding_number': tracking_info.get("VendorAWBNo1"),
                'booking_datetime': tracking_info.get("BookingDate1"),
                'origin': {'name': tracking_info.get("Origin")},
                'destination': {'name': tracking_info.get("Destination")},
                'consignee': {'person_name': tracking_info.get("Consignee")},
                'service': tracking_info.get("ServiceName"),
                'vendor': tracking_info.get("VendorName"),
                'weight': tracking_info.get("Weight"),
                'status': tracking_info.get("Status"),
                'delivery_date': tracking_info.get("DeliveryDate1"),
                'delivery_time': tracking_info.get("DeliveryTime1"),
                'receiver_name': tracking_info.get("ReceiverName"),
            }
        elif awb_details and data.get("Tracking"):
            # Update missing fields in local awb_details using API
            tracking_info = data["Tracking"][0]
            if not awb_details.get('service') and tracking_info.get("ServiceName"):
                awb_details['service'] = tracking_info.get("ServiceName")
            if not awb_details.get('vendor') and tracking_info.get("VendorName"):
                awb_details['vendor'] = tracking_info.get("VendorName")
            if not awb_details.get('forwarding_number') and tracking_info.get("VendorAWBNo1"):
                awb_details['forwarding_number'] = tracking_info.get(
                    "VendorAWBNo1")

        return timeline, awb_details, None
    else:
        # API returned an error code
        if awb_details:
            # Return local data only (all timestamps already in local tz)
            timeline.sort(
                key=lambda x: x["timestamp"] or datetime.min.replace(
                    tzinfo=local_tz),
                reverse=True
            )
            return timeline, awb_details, None
        return timeline, awb_details, data.get("ErrorDisc", "AWB not found")


def track_postshipping_api(awb_no, reference_number, timeline, awb_details, local_tz):
    """
    Track AWB using PostShipping tracking API.
    Returns: tuple (timeline, awb_details, error_message)
    """
    tracking_number = reference_number

    # --- Get Token ---
    try:
        cred = VendorLoginCred.objects.get(vendor__code="DTDC")
        token = cred.password.strip()
    except VendorLoginCred.DoesNotExist:
        return timeline, awb_details, "Authentication credentials not found."

    url = f"https://api.postshipping.com/api2/tracks?ReferenceNumber={tracking_number}"

    try:
        res = requests.get(
            url,
            headers={
                "Content-Type": "application/json",
                "Token": token
            },
            timeout=15
        )
        res.raise_for_status()
        data = res.json()
    except requests.RequestException as e:
        if awb_details:
            timeline.sort(
                key=lambda x: x["timestamp"] or datetime.min.replace(
                    tzinfo=local_tz),
                reverse=True
            )
            return timeline, awb_details, None
        return timeline, awb_details, f"Tracking request failed: {e}"

    tracking_data = data.get("TrackingDetail", [])
    if tracking_data:
        for event in tracking_data:
            # Parse timestamp
            try:
                utc_dt = datetime.strptime(
                    event["TrackingUTCDate"], "%Y/%m/%d %I:%M:%S %p").replace(tzinfo=dt_timezone.utc)
                ts_local = utc_dt.astimezone(local_tz)
            except Exception:
                ts_local = None

            timeline.append({
                "status": event.get("TrackingEventName", ""),
                "location": event.get("TrackingLocation", ""),
                "timestamp": ts_local,
                "source": "api"
            })

        if not awb_details:
            awb_details = {
                'awbno': tracking_number,
                'forwarding_number': tracking_number,
                'origin': {'name': ''},
                'destination': {'name': ''},
                'consignee': {'person_name': ''},
                'service': '',
                'vendor': 'DTDC',
                'weight': 0,
                'status': tracking_data[-1].get("TrackingEventName", ""),
            }

        timeline.sort(
            key=lambda x: x["timestamp"] or datetime.min.replace(
                tzinfo=local_tz),
            reverse=True
        )
        return timeline, awb_details, None
    else:
        if awb_details:
            timeline.sort(
                key=lambda x: x["timestamp"] or datetime.min.replace(
                    tzinfo=local_tz),
                reverse=True
            )
            return timeline, awb_details, None
        return timeline, awb_details, "No tracking data found for this AWB."


def track_sgus_api(awb_no, reference_number, timeline, awb_details, local_tz):
    """
    Track AWB using SGUS (ShipGlobal US) XML tracking API.
    Returns: tuple (timeline, awb_details, error_message)
    """
    tracking_number = reference_number

    # --- Get Credentials ---
    try:
        cred = VendorLoginCred.objects.get(vendor__code="SGUS")
        username = cred.username.strip()
        password = cred.password.strip()
        security_code = cred.additional_cred1.strip()
        authorize_code = cred.additional_cred2.strip()
        account_number = cred.additional_cred3.strip()
    except VendorLoginCred.DoesNotExist:
        return timeline, awb_details, "Authentication credentials not found."

    # --- Build XML Payload ---
    xml_payload = f"""<?xml version="1.0"?>
<FFUSACourier action="Request" version="1.0">
    <Requestor>
        <Username>{username}</Username>
        <Password>{password}</Password>
        <SecurityKey>{security_code}</SecurityKey>
        <AuthorizeCode>{authorize_code}</AuthorizeCode>
        <AccountNumber>{account_number}</AccountNumber>
    </Requestor>
    <Tracking action="Track" version="1.0">
        <Shipment>
            <TrackingNbr>{tracking_number}</TrackingNbr>
        </Shipment>
    </Tracking>
</FFUSACourier>"""

    url = "https://www.shipglobal.us/api/track"

    try:
        response = requests.post(url, data=xml_payload.encode(
            "utf-8"), headers={"Content-Type": "application/xml"}, timeout=20)
        response.raise_for_status()
        root = ET.fromstring(response.content)
    except requests.RequestException as e:
        return timeline, awb_details, f"Tracking request failed: {e}"
    except ET.ParseError:
        return timeline, awb_details, "Failed to parse tracking response."

    # --- Parse XML Response ---
    shipment = root.find(".//Tracking/Shipment")
    if shipment is None:
        return timeline, awb_details, "No shipment data found."

    # Extract core shipment info
    weight = float(shipment.findtext("TotalWeight", default="0"))
    status_latest = shipment.findtext("Status/Desc", default="Unknown")

    # --- Extract Track History ---
    history = shipment.find("TrackHistory")
    if history is not None:
        for status_node in history.findall("Status"):
            status_text = status_node.findtext("Desc", "").strip()
            date_str = status_node.findtext(
                "Date", "").strip()  # Format: YYYY-MM-DD
            time_str = status_node.findtext(
                "Time", "").strip()  # Format: HH:MM:SS
            location_node = status_node.find("Location")
            city = location_node.findtext(
                "City", "").strip() if location_node is not None else ""
            country = location_node.findtext(
                "Country", "").strip() if location_node is not None else ""

            # Parse datetime
            ts_local = None
            if date_str and time_str:
                try:
                    dt_utc = datetime.strptime(
                        f"{date_str} {time_str}", "%Y-%m-%d %H:%M:%S").replace(tzinfo=dt_timezone.utc)
                    ts_local = dt_utc.astimezone(local_tz)
                except Exception:
                    pass

            timeline.append({
                "status": status_text,
                "location": f"{city}, {country}".strip(", "),
                "timestamp": ts_local,
                "source": "api"
            })

    # Build awb_details if not present
    if not awb_details:
        awb_details = {
            'awbno': tracking_number,
            'forwarding_number': tracking_number,
            'origin': {'name': ''},
            'destination': {'name': ''},
            'consignee': {'person_name': ''},
            'service': shipment.findtext("ServiceType/Desc", "").strip(),
            'vendor': 'SGUS',
            'weight': weight,
            'status': status_latest,
        }

    timeline.sort(
        key=lambda x: x["timestamp"] or datetime.min.replace(tzinfo=local_tz),
        reverse=True
    )

    return timeline, awb_details, None


def track_sgau_api(awb_no, reference_number, timeline, awb_details, local_tz):
    """
    Track AWB using SGUS (ShipGlobal US) XML tracking API.
    Returns: tuple (timeline, awb_details, error_message)
    """
    tracking_number = reference_number

    # --- Get Credentials ---
    try:
        cred = VendorLoginCred.objects.get(vendor__code="SGAU")
        username = cred.username.strip()
        password = cred.password.strip()
        security_code = cred.additional_cred1.strip()
        authorize_code = cred.additional_cred2.strip()
        account_number = cred.additional_cred3.strip()
    except VendorLoginCred.DoesNotExist:
        return timeline, awb_details, "Authentication credentials not found."

    # --- Build XML Payload ---
    xml_payload = f"""<?xml version="1.0"?>
<FFUSACourier action="Request" version="1.0">
    <Requestor>
        <Username>{username}</Username>
        <Password>{password}</Password>
        <SecurityKey>{security_code}</SecurityKey>
        <AuthorizeCode>{authorize_code}</AuthorizeCode>
        <AccountNumber>{account_number}</AccountNumber>
    </Requestor>
    <Tracking action="Track" version="1.0">
        <Shipment>
            <TrackingNbr>{tracking_number}</TrackingNbr>
        </Shipment>
    </Tracking>
</FFUSACourier>"""

    url = "https://www.shipglobal.au/api/track"

    try:
        response = requests.post(url, data=xml_payload.encode(
            "utf-8"), headers={"Content-Type": "application/xml"}, timeout=20)
        response.raise_for_status()
        root = ET.fromstring(response.content)
    except requests.RequestException as e:
        return timeline, awb_details, f"Tracking request failed: {e}"
    except ET.ParseError:
        return timeline, awb_details, "Failed to parse tracking response."

    # --- Parse XML Response ---
    shipment = root.find(".//Tracking/Shipment")
    if shipment is None:
        return timeline, awb_details, "No shipment data found."

    # Extract core shipment info
    weight = float(shipment.findtext("TotalWeight", default="0"))
    status_latest = shipment.findtext("Status/Desc", default="Unknown")

    # --- Extract Track History ---
    history = shipment.find("TrackHistory")
    if history is not None:
        for status_node in history.findall("Status"):
            status_text = status_node.findtext("Desc", "").strip()
            date_str = status_node.findtext(
                "Date", "").strip()  # Format: YYYY-MM-DD
            time_str = status_node.findtext(
                "Time", "").strip()  # Format: HH:MM:SS
            location_node = status_node.find("Location")
            city = location_node.findtext(
                "City", "").strip() if location_node is not None else ""
            country = location_node.findtext(
                "Country", "").strip() if location_node is not None else ""

            # Parse datetime
            ts_local = None
            if date_str and time_str:
                try:
                    dt_utc = datetime.strptime(
                        f"{date_str} {time_str}", "%Y-%m-%d %H:%M:%S").replace(tzinfo=dt_timezone.utc)
                    ts_local = dt_utc.astimezone(local_tz)
                except Exception:
                    pass

            location = f"{city}, {country}".strip(", ")
            if not location:
                location = "Australia"

            timeline.append({
                "status": status_text,
                "location": location,
                "timestamp": ts_local,
                "source": "api"
            })

    # Build awb_details if not present
    if not awb_details:
        awb_details = {
            'awbno': tracking_number,
            'forwarding_number': tracking_number,
            'origin': {'name': ''},
            'destination': {'name': ''},
            'consignee': {'person_name': ''},
            'service': shipment.findtext("ServiceType/Desc", "").strip(),
            'vendor': 'SGUS',
            'weight': weight,
            'status': status_latest,
        }

    timeline.sort(
        key=lambda x: x["timestamp"] or datetime.min.replace(tzinfo=local_tz),
        reverse=True
    )

    return timeline, awb_details, None


def track_courierx_api(awb_no, reference_number, timeline, awb_details, local_tz):
    """
    Track AWB using Courirex tracking API.
    Returns: tuple (timeline, awb_details, error_message)
    """
    tracking_number = reference_number if reference_number else awb_no

    try:
        cred = VendorLoginCred.objects.get(vendor__code="COURIERX")
    except VendorLoginCred.DoesNotExist:
        return timeline, awb_details, "Courirex credentials not found"

    payload = {
        "TrackingAWB": tracking_number,
        "UserName": cred.username,
        "Password": cred.password,
        "AccountNo": cred.additional_cred1,
        "Country": awb_details.get("destination", {}).get("short_name", "").upper() or "us"
    }

    try:
        resp = requests.post("https://ontrack.couriex.com/Service.svc/Tracking",
                             json=payload, timeout=20)
        resp.raise_for_status()
        data = resp.json()
    except requests.RequestException as e:
        if awb_details:
            timeline.sort(key=lambda x: x["timestamp"] or datetime.min.replace(
                tzinfo=local_tz), reverse=True)
            return timeline, awb_details, None
        return timeline, awb_details, f"API request failed: {e}"

    if data.get("Code") != 1:
        error_msg = data.get("Description", "Tracking failed")
        if awb_details:
            timeline.sort(key=lambda x: x["timestamp"] or datetime.min.replace(
                tzinfo=local_tz), reverse=True)
            return timeline, awb_details, None
        return timeline, awb_details, error_msg

    airway_bill_list = data.get("AirwayBillTrackList", [])
    if not airway_bill_list:
        if awb_details:
            timeline.sort(key=lambda x: x["timestamp"] or datetime.min.replace(
                tzinfo=local_tz), reverse=True)
            return timeline, awb_details, None
        return timeline, awb_details, "No tracking data found"

    tracking_info = airway_bill_list[0]
    tracking_logs = tracking_info.get("TrackingLogDetails") or []

    # Process tracking events only if they exist
    for log in tracking_logs:
        try:
            activity_date = log.get("ActivityDate", "")
            activity_time = log.get("ActivityTime", "")

            if activity_date and activity_time:
                date_parts = activity_date.split()
                if len(date_parts) >= 4:
                    day, month, year = date_parts[1], date_parts[2], date_parts[3]
                    month_map = {
                        'January': '01', 'February': '02', 'March': '03', 'April': '04',
                        'May': '05', 'June': '06', 'July': '07', 'August': '08',
                        'September': '09', 'October': '10', 'November': '11', 'December': '12'
                    }
                    month_num = month_map.get(month, '01')
                    date_str = f"{year}-{month_num}-{day.zfill(2)} {activity_time}"
                    ts_naive = datetime.strptime(date_str, "%Y-%m-%d %H:%M")
                    ts_local = ts_naive.replace(
                        tzinfo=dt_timezone.utc).astimezone(local_tz)
                else:
                    ts_local = None
            else:
                ts_local = None
        except Exception:
            ts_local = None

        status_map = {
            "POD": "Proof of Delivery", "PDL": "Package Delivered", "OT": "Out for Delivery",
            "WC": "Loaded on Delivery Vehicle", "AF": "Arrived at Facility", "DF": "Departed from Facility",
            "PS": "Package Information Sent", "INF": "Shipment Information Received"
        }

        timeline.append({
            "status": status_map.get(log.get("Status", ""), log.get("Status", "")),
            "location": log.get("Location", "") or "",
            "timestamp": ts_local,
            "source": "api",
            "remarks": log.get("Remarks", ""),
            "delivered_to": log.get("DeliveredTo", "")
        })

    # Update awb_details with available tracking info
    if not awb_details:
        awb_details = {}

    for field in ["AirWayBillNo", "ForwardingNumber", "Origin", "Destination", "ShipperReference", "Weight", "ShipmentProgress"]:
        value = tracking_info.get(field)
        if value:
            if field == "Origin":
                awb_details['origin'] = {'name': value}
            elif field == "Destination":
                awb_details['destination'] = {'name': value}
            elif field == "ShipmentProgress":
                awb_details['progress'] = value
            else:
                awb_details[field.lower()] = value

    timeline.sort(key=lambda x: x["timestamp"] or datetime.min.replace(
        tzinfo=local_tz), reverse=True)
    return timeline, awb_details, None


def track_sgca_api(awb_no, reference_number, timeline, awb_details, local_tz):
    """
    Track AWB using SGCA (ShipGlobal Canada) XML tracking API.
    Returns: tuple (timeline, awb_details, error_message)
    """
    tracking_number = reference_number

    # --- Get Credentials ---
    try:
        cred = VendorLoginCred.objects.get(vendor__code="SGCA")
        username = cred.username.strip()
        password = cred.password.strip()
        security_code = cred.additional_cred1.strip()
        authorize_code = cred.additional_cred2.strip()
        account_number = cred.additional_cred3.strip()
    except VendorLoginCred.DoesNotExist:
        return timeline, awb_details, "Authentication credentials not found."

    # --- Build XML Payload ---
    xml_payload = f"""<?xml version="1.0"?>
<FFUSACourier action="Request" version="1.0">
    <Requestor>
        <Username>{username}</Username>
        <Password>{password}</Password>
        <SecurityKey>{security_code}</SecurityKey>
        <AuthorizeCode>{authorize_code}</AuthorizeCode>
        <AccountNumber>{account_number}</AccountNumber>
    </Requestor>
    <Tracking action="Track" version="1.0">
        <Shipment>
            <TrackingNbr>{tracking_number}</TrackingNbr>
        </Shipment>
    </Tracking>
</FFUSACourier>"""

    url = "https://www.firstflightcanada.com/api/track"

    try:
        response = requests.post(
            url,
            data=xml_payload.encode("utf-8"),
            headers={"Content-Type": "application/xml"},
            timeout=20
        )
        response.raise_for_status()
        root = ET.fromstring(response.content)
    except requests.RequestException as e:
        return timeline, awb_details, f"Tracking request failed: {e}"
    except ET.ParseError:
        return timeline, awb_details, "Failed to parse tracking response."

    # --- Parse XML Response ---

    shipment = root.find(".//Tracking/Shipment")
    if shipment is None:
        return timeline, awb_details, "No shipment data found."

    weight = float(shipment.findtext("TotalWeight", default="0"))
    status_latest = shipment.findtext("Status/Desc", default="Unknown")
    service = shipment.findtext("ServiceType/Desc", default="").strip()
    carrier_name = shipment.findtext("LastMileCarrierName", default="").strip()
    carrier_tracking = shipment.findtext(
        "LastMileCarrierTrackingNbr", default="").strip()

    # --- Extract Track History ---
    history = shipment.find("TrackHistory")
    if history is not None:
        for status_node in history.findall("Status"):
            status_text = status_node.findtext("Desc", "").strip()
            date_str = status_node.findtext("Date", "").strip()
            time_str = status_node.findtext("Time", "").strip()

            location_node = status_node.find("Location")
            city = location_node.findtext(
                "City", "").strip() if location_node is not None else ""
            country = location_node.findtext(
                "Country", "").strip() if location_node is not None else ""

            # Parse datetime
            ts_local = None
            if date_str and time_str:
                try:
                    dt_utc = datetime.strptime(
                        f"{date_str} {time_str}", "%Y-%m-%d %H:%M:%S").replace(tzinfo=dt_timezone.utc)
                    ts_local = dt_utc.astimezone(local_tz)
                except Exception:
                    pass

            location = f"{city}, {country}".strip(", ")
            if not location:
                location = "Canada"

            timeline.append({
                "status": status_text,
                "location": location,
                "timestamp": ts_local,
                "source": "api"
            })

    # --- Build awb_details if missing ---
    if not awb_details:
        awb_details = {
            'awbno': tracking_number,
            'forwarding_number': tracking_number,
            'origin': {'name': ''},
            'destination': {'name': ''},
            'consignee': {'person_name': ''},
            'service': service,
            'vendor': 'SGCA',
            'weight': weight,
            'status': status_latest,
            'last_mile_carrier': carrier_name,
            'last_mile_tracking': carrier_tracking
        }

    # Sort timeline by timestamp descending
    timeline.sort(
        key=lambda x: x["timestamp"] or datetime.min.replace(tzinfo=local_tz),
        reverse=True
    )

    return timeline, awb_details, None


def _build_tracking_awb_details(awb):
    """
    Helper function to build AWB details structure specifically for tracking.
    """
    awb_details = {
        'created_at': awb.created_at,
        'awbno': awb.awbno,
        'total_box': awb.total_box,
        'forwarding_number': awb.forwarding_number,
        'reference_number': awb.reference_number,
        'booking_datetime': awb.booking_datetime,
        'shipment_value': awb.shipment_value,
        'currency': awb.currency.name if awb.currency else None,
        'content': awb.content,
        'total_actual_weight': awb.total_actual_weight,
        'total_volumetric_weight': awb.total_volumetric_weight,
        'total_charged_weight': awb.total_charged_weight,
        'is_verified': awb.is_verified,
        'is_cancelled': awb.is_cancelled,
        'is_in_run': awb.is_in_run,
        'origin': {
            'name': awb.origin.name if awb.origin else None,
            'short_name': awb.origin.short_name if awb.origin else None,
        },
        'destination': {
            'name': awb.destination.name if awb.destination else None,
            'short_name': awb.destination.short_name if awb.destination else None,
        },
        'consignee': {
            'company': awb.consignee.company if awb.consignee else None,
            'person_name': awb.consignee.person_name if awb.consignee else None,
            'address1': awb.consignee.address1 if awb.consignee else None,
            'city': awb.consignee.city if awb.consignee else None,
            'phone_number': awb.consignee.phone_number if awb.consignee else None,
        } if awb.consignee else None,
        'consignor': {
            'company': awb.consignor.company if awb.consignor else None,
            'person_name': awb.consignor.person_name if awb.consignor else None,
            'address1': awb.consignor.address1 if awb.consignor else None,
            'city': awb.consignor.city if awb.consignor else None,
            'phone_number': awb.consignor.phone_number if awb.consignor else None,
        } if awb.consignor else None,
        'agency': {
            'company_name': awb.agency.company_name if awb.agency else None,
        } if awb.agency else None,
        'service': awb.service.name if awb.service else None,
        'product_type': awb.product_type.name if awb.product_type else None,
        'vendor': awb.vendor.name if awb.vendor else None,
    }

    # Get box details
    boxes = []
    for box in awb.boxdetails.all():
        boxes.append({
            'actual_weight': box.actual_weight,
            'volumetric_weight': box.volumetric_weight,
            'charged_weight': box.charged_weight,
            'dimensions': f"{box.length}x{box.breadth}x{box.height}",
            'box_awb_no': box.box_awb_no,
            'bag_no': box.bag_no,
        })
    awb_details['boxes'] = boxes

    return awb_details


def track_awb(awb_no):
    """
    Returns a combined, chronologically sorted timeline (newest first) of:
      - local AWBStatus entries (converted to Asia/Kathmandu time)
      - external API Events (EventDate+EventTime → parsed as UTC → converted to Asia/Kathmandu time)
    Also returns comprehensive AWB details including total boxes, forwarding number, etc.
    If the shipment is already delivered locally, only DB statuses (in local tz) are returned.
    On API failure or "not found," returns {"error": "..."}.
    """
    timeline = []
    awb_details = None

    # Define local timezone
    local_tz = pytz.timezone("Asia/Kathmandu")
    reference_number = ""
    awb = None

    # 1) Load AWB details and statuses from your DB using AWBDetailsFetcher
    try:
        fetcher = AWBDetailsFetcher(awb_no)
        fetcher.fetch_awb()
        awb = fetcher.awb

        # Build tracking-specific AWB details
        awb_details = _build_tracking_awb_details(awb)

        # Get local statuses (convert created_at → Asia/Kathmandu)
        qs = AWBStatus.objects.filter(awb=awb)
        for s in qs:
            # created_at may be aware or naive; convert robustly and avoid defaulting to "now" when missing

            if s.created_at:
                if timezone.is_aware(s.created_at):
                    local_ts = s.created_at.astimezone(local_tz)
                else:
                    # Assume naive is stored in UTC; attach UTC then convert to local
                    local_ts = s.created_at.replace(
                        tzinfo=dt_timezone.utc).astimezone(local_tz)
            else:
                local_ts = None

            timeline.append({
                "status": s.status,
                "location": s.location or "",
                "timestamp": local_ts,
                "source": "local"
            })

        # If already delivered, skip API and just sort DB statuses (all in local tz)
        if qs.filter(status="SHIPMENT DELIVERED").exists():
            timeline.sort(
                key=lambda x: x["timestamp"] or datetime.min.replace(
                    tzinfo=local_tz),
                reverse=True
            )
            # Push special initial statuses to the end while preserving current (desc) order
            special_statuses = {"LABEL CREATED",
                                "VERIFIED", "FORWARDING NO ASSIGNED"}
            awb_created_at = getattr(awb, "created_at", None)
            if awb_created_at:
                if timezone.is_aware(awb_created_at):
                    awb_created_at = awb_created_at.astimezone(local_tz)
                else:
                    awb_created_at = awb_created_at.replace(
                        tzinfo=dt_timezone.utc).astimezone(local_tz)
            for item in timeline:
                if item.get("status") in special_statuses and not item.get("timestamp"):
                    item["timestamp"] = awb_created_at
            # Place specials as the last three in exact order
            normals = [x for x in timeline if x.get(
                "status") not in special_statuses]
            specials = [x for x in timeline if x.get(
                "status") in special_statuses]
            desired_order = [
                "FORWARDING NO ASSIGNED",
                "VERIFIED",
                "LABEL CREATED",
            ]
            order_index = {s: i for i, s in enumerate(desired_order)}
            specials.sort(key=lambda x: order_index.get(x.get("status"), 999))
            timeline = normals + specials
            return {"timeline": timeline, "awb": awb_details}
        reference_number = awb.reference_number
    except (AWBDetail.DoesNotExist, ValueError):
        # Not in DB → fall through to API only
        pass

    # 2) Fetch API events based on vendor
    # api logic here
    if awb and awb.vendor and awb.vendor.code != None:
        if awb.vendor.code.lower() == "dtdc":
            timeline, awb_details, error = track_postshipping_api(
                awb_no, reference_number, timeline, awb_details, local_tz
            )
            if error:
                return {"error": error}
        elif awb.vendor.code.lower() == "ubx":
            timeline, awb_details, error = track_ubx_api(
                awb_no, reference_number, timeline, awb_details, local_tz
            )
            if error:
                return {"error": error}
        elif awb.vendor.code.lower() == "sgus":
            timeline, awb_details, error = track_sgus_api(
                awb_no, reference_number, timeline, awb_details, local_tz
            )
            if error:
                return {"error": error}
        elif awb.vendor.code.lower() == "sgau":
            timeline, awb_details, error = track_sgau_api(
                awb_no, reference_number, timeline, awb_details, local_tz
            )
            if error:
                return {"error": error}
        elif awb.vendor.code.lower() == "sgca":
            timeline, awb_details, error = track_sgca_api(
                awb_no, reference_number, timeline, awb_details, local_tz
            )
            print(timeline, awb_details, error)
            if error:
                return {"error": error}
        elif awb.vendor.code.lower() == "courierx":

            timeline, awb_details, error = track_courierx_api(
                awb_no, reference_number, timeline, awb_details, local_tz
            )
            if error:
                return {"error": error}
    # 1) Sort everything by timestamp (newest first)
    timeline.sort(
        key=lambda x: x["timestamp"] or datetime.min.replace(tzinfo=local_tz),
        reverse=True
    )

    # 2) Move special initial statuses to the end while keeping latest-first ordering for others
    special_statuses = {"FORWARDING NO ASSIGNED", "VERIFIED", "LABEL CREATED"}
    awb_created_at = awb_details.get("created_at") if awb_details else None
    if awb_created_at:
        if timezone.is_aware(awb_created_at):
            awb_created_at = awb_created_at.astimezone(local_tz)
        else:
            awb_created_at = awb_created_at.replace(
                tzinfo=dt_timezone.utc).astimezone(local_tz)
    for item in timeline:
        if item.get("status") in special_statuses and not item.get("timestamp"):
            item["timestamp"] = awb_created_at
    # Place specials as the last three in exact order
    normals = [x for x in timeline if x.get("status") not in special_statuses]
    specials = [x for x in timeline if x.get("status") in special_statuses]
    desired_order = [
        "FORWARDING NO ASSIGNED",
        "VERIFIED",
        "LABEL CREATED",
    ]
    order_index = {s: i for i, s in enumerate(desired_order)}
    specials.sort(key=lambda x: order_index.get(x.get("status"), 999))
    timeline = normals + specials
    print(timeline)

    return {"timeline": timeline, "awb": awb_details}


class AWBDetailsFetcher:
    def __init__(self, awb_no):
        self.awb_no = awb_no
        self.awb = None

    def fetch_awb(self):
        try:
            self.awb = AWBDetail.objects.select_related(
                'origin', 'destination', 'consignee', 'consignor', 'agency',
                'company', 'service', 'product_type', 'vendor', 'currency'
            ).prefetch_related('boxdetails').get(awbno=self.awb_no)
        except AWBDetail.DoesNotExist:
            raise ValueError(f"AWB with ID {self.awb_no} does not exist.")

    def get_details(self):
        self.fetch_awb()

        return {
            "awb_no": str(self.awb.awbno).upper(),

            "details": {

                "shipment_value": str(self.awb.shipment_value).upper() if self.awb.shipment_value else 0.00,
                "currency": str(self.awb.currency.name).upper() if self.awb.currency else "",
                "origin": str(self.awb.origin.name).upper() if self.awb.origin else "",
                "destination": str(self.awb.destination.name).upper() if self.awb.destination else "",
                "destination_short_name": str(self.awb.destination.short_name).upper() if self.awb.destination else "",
                "booking_datetime": self.awb.booking_datetime,
                "total_charged_weight": str(self.awb.total_charged_weight).upper() if self.awb.total_charged_weight else "",
                "total_actual_weight": str(self.awb.total_actual_weight).upper() if self.awb.total_actual_weight else "",
                "total_volumetric_weight": str(self.awb.total_volumetric_weight).upper() if self.awb.total_volumetric_weight else "",
                "total_box_items_amount": str(self.awb.total_box_items_amount).upper() if self.awb.total_box_items_amount else "",
                "all_box_awb": str(self.awb.all_box_awb).upper() if self.awb.all_box_awb else "",
                "box_count": str(self.awb.total_box).upper() if self.awb.total_box else "",
                "service": str(self.awb.service.name).upper() if self.awb.service else "",
                "service_code": str(self.awb.service.code).upper() if self.awb.service else "",
                "service_product_code": str(self.awb.service.product_code).upper() if self.awb.service else "",
                "vendor": str(self.awb.vendor).upper() if self.awb.vendor else "",
                "forwarding_number": str(self.awb.forwarding_number).upper() if self.awb.forwarding_number else "",
                "reference_number": str(self.awb.reference_number).upper() if self.awb.reference_number else "",
                "content": str(self.awb.content).upper() if self.awb.content else "",
                "awb_no": str(self.awb.awbno).upper(),
                "awbno": str(self.awb.awbno).upper(),
                "is_cash_user": self.awb.is_cash_user,
                "created_at": self.awb.created_at,
                "reason_for_export": str(self.awb.reason_for_export).upper() if self.awb.reason_for_export else "",
                "shipment_terms": str(self.awb.shipment_terms).upper() if self.awb.shipment_terms else "",
                "product_type": str(self.awb.product_type.name).upper() if self.awb.product_type else "",
                "couriex_code": str(self.awb.destination.couriex_code).upper() if self.awb.destination else "",

            },

            "consignee": {
                "name": str(self.awb.consignee.person_name or "").upper(),
                "company": str(self.awb.consignee.company or "").upper(),
                "address1": str(self.awb.consignee.address1 or "").upper(),
                "address2": str(self.awb.consignee.address2 or "").upper(),
                "country": str(self.awb.destination.name or "").upper(),
                "country_short_name": str(self.awb.destination.short_name or "").upper(),
                "city": str(self.awb.consignee.city or "").upper(),
                "state_short_name": str(self.awb.consignee.state_abbreviation or "").upper(),
                "state": str(self.awb.consignee.state_county or "").upper(),
                "postcode": str(self.awb.consignee.post_zip_code or "").upper(),
                "phone": str(self.awb.consignee.phone_number or "").upper(),
                "phone_2": str(self.awb.consignee.phone_number_2 or "").upper(),
                "email": str(self.awb.consignee.email_address or "").upper(),
                "first_name": " ".join(self.awb.consignee.person_name.split(" ")[:-1]).upper() if self.awb.consignee.person_name else "",
                "last_name": self.awb.consignee.person_name.split(" ")[-1].upper() if self.awb.consignee.person_name else "",
            } if hasattr(self.awb, 'consignee') else "",

            "consignor": {
                "name": str(self.awb.consignor.person_name or "").upper(),
                "company": str(self.awb.consignor.company or "").upper(),
                "address1": str(self.awb.consignor.address1 or "").upper(),
                "address2": str(self.awb.consignor.address2 or "").upper(),
                "city": str(self.awb.consignor.city or "").upper(),
                "state": str(self.awb.consignor.state_county or "").upper(),
                "postcode": str(self.awb.consignor.post_zip_code or "").upper(),
                "phone": str(self.awb.consignor.phone_number or "").upper(),
                "email": str(self.awb.consignor.email_address or "").upper(),
                "first_name": " ".join(self.awb.consignor.person_name.split(" ")[:-1]).upper() if self.awb.consignor.person_name else "",
                "last_name": self.awb.consignor.person_name.split(" ")[-1].upper() if self.awb.consignor.person_name else "",
                "country_short_name": str(self.awb.destination.short_name).upper() if self.awb.destination else "",
                "country": str(self.awb.destination.name).upper() if self.awb.destination else "",
            } if hasattr(self.awb, 'consignor') else "",


            "company": {
                "name": str(self.awb.company.name).upper(),
                "address": f"{str(self.awb.company.address1).upper()}, {str(self.awb.company.city).upper()}, {str(self.awb.company.country).upper()}",
                "address1": str(self.awb.company.address1).upper() if self.awb.company.address1 else "",
                "city": str(self.awb.company.city).upper() if self.awb.company.city else "",
                "state": str(self.awb.company.state_county).upper() if self.awb.company.state_county else "",
                "postcode": str(self.awb.company.post_zip_code).upper() if self.awb.company.post_zip_code else "",
                "country_short_name": str(self.awb.company.country.short_name).upper() if self.awb.company.country.short_name else "",
                "country": str(self.awb.company.country.name).upper() if self.awb.company.country.name else "",
            },
            "hub": {
                "name": str(self.awb.hub.name).upper() if self.awb.hub else "",
                "currency": str(self.awb.hub.currency.name).upper() if self.awb.hub and self.awb.hub.currency else "",
            } if self.awb.hub else "",
            "agency": {
                "name": str(self.awb.agency.company_name).upper() if self.awb.agency else "",
                "owner_name": str(self.awb.agency.owner_name).upper() if self.awb.agency and self.awb.agency.owner_name else "",
                "address1": str(self.awb.agency.address1).upper() if self.awb.agency and self.awb.agency.address1 else "",
                "zip_code": str(self.awb.agency.zip_code).upper() if self.awb.agency and self.awb.agency.zip_code else "",
                "address2": str(self.awb.agency.address2).upper() if self.awb.agency and self.awb.agency.address2 else "",
                "office_phone": str(self.awb.agency.contact_no_1).upper() if self.awb.agency and self.awb.agency.contact_no_1 else "",
                "email": str(self.awb.agency.email).upper() if self.awb.agency and self.awb.agency.email else "",
                "country": str(self.awb.agency.country.name).upper() if self.awb.agency and self.awb.agency.country else ""
            } if self.awb.agency else "",
            "boxes": [{
                "box_awb_no": box.box_awb_no,
                "actual_weight": box.actual_weight,
                "volumetric_weight": box.volumetric_weight,
                "charged_weight": box.charged_weight,
                "bag_no": box.bag_no,
                "dimensions": {
                    "length": str(box.length).upper(),
                    "breadth": str(box.breadth).upper(),
                    "height": str(box.height).upper()
                },
                "items": [{
                    "box_number": str(box.get_box_number()).upper(),
                    "description": str(item.description).upper(),
                    "hs_code": str(item.hs_code).upper().ljust(8, '0')[:8],
                    "quantity": str(item.quantity).upper(),
                    "unit_weight": str(item.unit_weight).upper(),
                    "unit_type": str(item.unit_type.name).upper(),
                    "unit_rate": str(item.unit_rate).upper(),
                    "amount": str(item.amount).upper(),
                } for item in box.items.all()]
            } for box in self.awb.boxdetails.all()],
        }
