"""
Authority Reporter for SafeRoad-Guardian
Generates WhatsApp/Email ready reports for road authorities
"""

import base64
import json
from datetime import datetime
from typing import Dict


def send_to_authority(image_path: str, gps: str, findings: str, severity: str) -> Dict:
    """
    Generate authority-ready report with embedded photo.
    Compatible with: Sri Lanka RDA, Indian PWD, US 311, UK FixMyStreet
    
    Args:
        image_path: Path to hazard image
        gps: GPS coordinates
        findings: Detection results
        severity: HIGH, MEDIUM, or LOW
        
    Returns:
        Report dictionary with all data
    """
    # Encode image to base64 for WhatsApp/Email
    try:
        with open(image_path, "rb") as img_file:
            b64 = base64.b64encode(img_file.read()).decode()
        photo_status = "Attached (base64 ready)"
    except Exception as e:
        b64 = None
        photo_status = f"Error: {e}"

    # Create standardized report
    report = {
        "timestamp": datetime.now().isoformat(),
        "gps": gps,
        "location_link": f"https://maps.google.com/?q={gps}",
        "findings": findings,
        "severity": severity.upper(),
        "photo_base64": b64,
        "source": "SafeRoad-Guardian AI Agent",
        "api_ready": True
    }

    # Print WhatsApp/Email ready format
    print("\n" + "="*70)
    print("📱 WHATSAPP / EMAIL READY REPORT (COPY-PASTE TO AUTHORITY)")
    print("="*70)
    print(f"\n🚨 NEW ROAD HAZARD REPORTED\n")
    print(f"📍 Location    : {gps}")
    print(f"🗺️  Google Maps : https://maps.google.com/?q={gps}")
    print(f"⚠️  Severity    : {severity.upper()}")
    print(f"🔍 Details     : {findings}")
    print(f"🕐 Timestamp   : {report['timestamp']}")
    print(f"📷 Photo       : {photo_status}")
    print(f"🤖 Source      : SafeRoad-Guardian AI System")
    print("\n" + "-"*70)
    print("📨 READY FOR:")
    print("   • Sri Lanka RDA: rda@transport.gov.lk")
    print("   • India PWD: complaints@pwd.gov.in")
    print("   • US 311: Via mobile app or portal")
    print("   • UK FixMyStreet: https://fixmystreet.com")
    print("="*70 + "\n")
    
    # In production, you would add API calls here:
    # Example for WhatsApp Business API:
    # import pywhatkit
    # pywhatkit.sendwhatmsg_instantly("+94771234567", message, 15, True)
    # 
    # Or for Email:
    # import smtplib
    # server.sendmail("guardian@roadai.com", "authority@transport.gov", message)
    
    return report


def generate_authority_email(report: Dict) -> str:
    """
    Generate professional email body for authorities.
    
    Args:
        report: Report dictionary from send_to_authority
        
    Returns:
        Formatted email body
    """
    email_body = f"""
Subject: URGENT: Road Hazard Detected - Action Required

Dear Road Maintenance Authority,

This is an automated report from the SafeRoad-Guardian AI monitoring system.

HAZARD DETAILS:
--------------
Severity: {report['severity']}
Location (GPS): {report['gps']}
Google Maps Link: {report['location_link']}
Detection Details: {report['findings']}
Timestamp: {report['timestamp']}

A high-resolution photo has been attached to this report for your reference.

This hazard has been automatically detected and verified by our computer vision system.
Immediate attention is recommended for public safety.

For inquiries, please contact: SafeRoad-Guardian Operations
System ID: {report['timestamp']}

Best regards,
SafeRoad-Guardian AI System
Automated Road Safety Monitoring
    """
    return email_body.strip()


def check_if_authority_notified(gps: str) -> bool:
    """
    Check if this location was already reported to authority.
    
    Args:
        gps: GPS coordinates
        
    Returns:
        True if already notified, False otherwise
    """
    from memory.memory_bank import was_recently_reported
    
    # Check if reported in last 7 days
    already_reported = was_recently_reported(gps, days=7)
    
    if already_reported:
        print("\n" + "="*70)
        print("✅ AUTHORITY ALREADY NOTIFIED")
        print("="*70)
        print(f"📍 Location {gps} was reported within the last 7 days.")
        print("⏭️  No duplicate notification sent (saving authority time).")
        print("="*70 + "\n")
    
    return already_reported
