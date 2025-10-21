"""
Email Notification Service
Sends professional email notifications with PDF attachments
"""

import os
from datetime import datetime
from typing import Dict, List, Optional
from composio import Composio
from rich.console import Console

from src.config import config


console = Console()


class EmailService:
    """
    Professional email notification service.
    
    Sends HTML-formatted emails to:
    - Admin: Consolidated reports
    - Patients: Individual triage reports
    - Doctors: Clinical assessments
    
    Uploads PDFs to Google Drive and includes download links.
    """
    
    def __init__(self):
        """Initialize Composio clients for Gmail and Drive"""
        if not config.COMPOSIO_API_KEY:
            raise ValueError("COMPOSIO_API_KEY required for Email service")
        
        self.composio = Composio(api_key=config.COMPOSIO_API_KEY)
        self.user_id = config.COMPOSIO_USER_ID
        self.gmail_account_id = config.COMPOSIO_GMAIL_ACCOUNT_ID
        self.drive_account_id = config.COMPOSIO_DRIVE_ACCOUNT_ID
    
    def upload_pdf_to_drive(
        self,
        file_path: str,
        file_name: str
    ) -> Optional[str]:
        """
        Upload PDF to Google Drive and return shareable link.
        
        Args:
            file_path: Full path to PDF file
            file_name: Name for the file (not used currently)
        
        Returns:
            str: Shareable Google Drive link or None if failed
        """
        try:
            if not os.path.exists(file_path):
                console.print(f"[dim red]File not found: {file_path}[/dim red]")
                return None
            
            if not self.drive_account_id:
                return None
            
            # Upload to Google Drive
            upload_params = {
                "file_to_upload": file_path,
                "folder_to_upload_to": "root"
            }
            
            result = self.composio.tools.execute(
                "GOOGLEDRIVE_UPLOAD_FILE",
                user_id=self.user_id,
                arguments=upload_params,
                connected_account_id=self.drive_account_id
            )
            
            if result.get('successful', False):
                file_data = result.get('data', {})
                file_id = file_data.get('id')
                
                if file_id:
                    # Make file shareable
                    share_params = {
                        "file_id": file_id,
                        "role": "reader",
                        "type": "anyone"
                    }
                    
                    self.composio.tools.execute(
                        "GOOGLEDRIVE_ADD_FILE_SHARING_PREFERENCE",
                        user_id=self.user_id,
                        arguments=share_params,
                        connected_account_id=self.drive_account_id
                    )
                    
                    # Return shareable link
                    drive_link = f"https://drive.google.com/file/d/{file_id}/view"
                    return drive_link
            
            return None
            
        except Exception as e:
            console.print(f"[bold red]Drive error: {str(e)}[/bold red]")
            return None
    
    def send_email_with_attachment(
        self,
        recipient_email: str,
        subject: str,
        body: str,
        attachment_path: str,
        attachment_name: str,
        calendar_link: Optional[str] = None
    ) -> Dict:
        """
        Send email with PDF attachment via Google Drive link.
        
        Args:
            recipient_email: Email address of recipient
            subject: Email subject line
            body: Email body (HTML supported)
            attachment_path: Full path to PDF file
            attachment_name: Name for the attachment
            calendar_link: Optional Google Calendar event link
        
        Returns:
            dict: Result of email send operation
        """
        if not self.gmail_account_id:
            return {'successful': False, 'error': 'Gmail not configured'}
        
        if not os.path.exists(attachment_path):
            return {
                'successful': False,
                'error': f'File not found: {attachment_path}'
            }
        
        try:
            # Upload PDF to Google Drive
            drive_link = self.upload_pdf_to_drive(
                attachment_path,
                attachment_name
            )
            
            # Add PDF download link to body if upload succeeded
            if drive_link:
                pdf_section = f'''
<div style="background-color: #fff8e8; padding: 15px; margin: 20px 0; border-left: 4px solid #f39c12;">
    <h3 style="color: #f39c12;">📄 Your PDF Report is Ready!</h3>
    <p>Click the button below to download your comprehensive report:</p>
    <p style="text-align: center; margin: 15px 0;">
        <a href="{drive_link}" 
           style="background-color: #f39c12; color: white; padding: 12px 30px; 
                  text-decoration: none; border-radius: 5px; font-weight: bold; 
                  display: inline-block;">
            📥 Download PDF Report
        </a>
    </p>
    <p style="font-size: 12px; color: #666;">
        File: {attachment_name}<br>
        Stored securely in Google Drive
    </p>
</div>
'''
                body = body.replace('</body>', pdf_section + '</body>')
            
            # Add calendar link to body if provided
            if calendar_link:
                calendar_section = f'''
<div style="background-color: #e8f0f8; padding: 15px; margin: 20px 0; border-left: 4px solid #1a5490;">
    <h3 style="color: #1a5490;">📅 Your Appointment is Scheduled!</h3>
    <p>Click the button below to view your calendar event:</p>
    <p style="text-align: center; margin: 15px 0;">
        <a href="{calendar_link}" 
           style="background-color: #1a5490; color: white; padding: 12px 30px; 
                  text-decoration: none; border-radius: 5px; font-weight: bold; 
                  display: inline-block;">
            📅 View Calendar Appointment
        </a>
    </p>
    <p style="font-size: 12px; color: #666;">
        The event has been automatically added to your Google Calendar with meeting link.
    </p>
</div>
'''
                body = body.replace('</body>', calendar_section + '</body>')
            
            # Send email with HTML body and embedded links
            email_params = {
                "recipient_email": recipient_email,
                "subject": subject,
                "body": body,
                "is_html": True,
                "user_id": "me"
            }
            
            result = self.composio.tools.execute(
                "GMAIL_SEND_EMAIL",
                user_id=self.user_id,
                arguments=email_params,
                connected_account_id=self.gmail_account_id
            )
            
            return result
            
        except Exception as e:
            return {
                'successful': False,
                'error': str(e)
            }
    
    def send_patient_emails(
        self,
        triage_results: List[Dict],
        pdf_dir: str,
        calendar_events: Optional[Dict] = None
    ) -> int:
        """
        Send emails to all patients with their reports.
        
        Args:
            triage_results: List of patient triage data
            pdf_dir: Directory containing patient PDF files
            calendar_events: Map of patient names to calendar data
        
        Returns:
            int: Number of emails successfully sent
        """
        sent_count = 0
        calendar_events = calendar_events or {}
        
        for record in triage_results:
            patient = record.get('patient', {})
            doctor = record.get('matched_doctor', {})
            analyses = record.get('analyses', {})
            
            patient_name = patient.get('name', 'Patient')
            patient_email = patient.get('email')
            
            if not patient_email:
                continue
            
            # Find PDF file
            safe_name = "".join(
                c for c in patient_name
                if c.isalnum() or c in (' ', '_')
            ).rstrip().replace(' ', '_')
            
            pdf_path = f"{pdf_dir}/patients/{safe_name}.pdf"
            
            if not os.path.exists(pdf_path):
                continue
            
            # Get email details
            doctor_name = (
                doctor.get('name', 'Emergency Team')
                if doctor else 'Emergency Team'
            )
            specialty = analyses.get('o4mini', {}).get(
                'final_specialty',
                'General Medicine'
            )
            priority = analyses.get('o4mini', {}).get(
                'consultation_priority',
                'Standard'
            )
            
            # Get calendar link if available
            calendar_link = None
            if patient_name in calendar_events:
                calendar_link = calendar_events[patient_name].get('htmlLink')
            
            subject = "🏥 Your Medical Triage Report - RavenCare"
            body = self._create_patient_email_body(
                patient_name,
                doctor_name,
                priority,
                specialty
            )
            
            # Send email
            result = self.send_email_with_attachment(
                recipient_email=patient_email,
                subject=subject,
                body=body,
                attachment_path=pdf_path,
                attachment_name=f"{safe_name}_Medical_Report.pdf",
                calendar_link=calendar_link
            )
            
            if result.get('successful', False):
                sent_count += 1
        
        return sent_count
    
    def send_doctor_emails(
        self,
        triage_results: List[Dict],
        pdf_dir: str,
        calendar_events: Optional[Dict] = None
    ) -> int:
        """
        Send emails to doctors with clinical reports.
        
        Args:
            triage_results: List of patient triage data
            pdf_dir: Directory containing doctor PDF files
            calendar_events: Map of patient names to calendar data
        
        Returns:
            int: Number of emails successfully sent
        """
        sent_count = 0
        calendar_events = calendar_events or {}
        
        # Group patients by doctor
        doctor_patients = {}
        for record in triage_results:
            doctor = record.get('matched_doctor')
            if not doctor:
                continue
            
            doctor_email = doctor.get('contact_email')
            if not doctor_email:
                continue
            
            doctor_name = doctor.get('name', 'Doctor')
            if doctor_name not in doctor_patients:
                doctor_patients[doctor_name] = {
                    'email': doctor_email,
                    'patients': []
                }
            doctor_patients[doctor_name]['patients'].append(record)
        
        # Send emails for each doctor
        for doctor_name, info in doctor_patients.items():
            doctor_email = info['email']
            patients = info['patients']
            
            # Send email for each patient assigned to this doctor
            for record in patients:
                patient = record.get('patient', {})
                analyses = record.get('analyses', {})
                
                patient_name = patient.get('name', 'Patient')
                
                # Find doctor's version of PDF
                safe_patient = "".join(
                    c for c in patient_name
                    if c.isalnum() or c in (' ', '_')
                ).rstrip().replace(' ', '_')
                safe_doctor = "".join(
                    c for c in doctor_name
                    if c.isalnum() or c in (' ', '_')
                ).rstrip().replace(' ', '_')
                
                pdf_path = (
                    f"{pdf_dir}/doctors/{safe_doctor}/"
                    f"{safe_doctor}_{safe_patient}.pdf"
                )
                
                if not os.path.exists(pdf_path):
                    continue
                
                # Get email details
                priority = analyses.get('o4mini', {}).get(
                    'consultation_priority',
                    'Standard'
                )
                urgency_score = analyses.get('grok', {}).get(
                    'urgency_score',
                    'N/A'
                )
                
                # Get calendar link
                calendar_link = None
                if patient_name in calendar_events:
                    calendar_link = calendar_events[patient_name].get('htmlLink')
                
                subject = (
                    f"🏥 New Patient: {patient_name} [{priority}] - RavenCare"
                )
                body = self._create_doctor_email_body(
                    doctor_name,
                    patient_name,
                    priority,
                    urgency_score
                )
                
                # Send email
                result = self.send_email_with_attachment(
                    recipient_email=doctor_email,
                    subject=subject,
                    body=body,
                    attachment_path=pdf_path,
                    attachment_name=f"Clinical_Report_{safe_patient}.pdf",
                    calendar_link=calendar_link
                )
                
                if result.get('successful', False):
                    sent_count += 1
        
        return sent_count
    
    def send_admin_email(
        self,
        total_patients: int,
        pdf_path: str,
        sheet_url: Optional[str] = None
    ) -> bool:
        """
        Send consolidated report to admin.
        
        Args:
            total_patients: Total number of patients processed
            pdf_path: Path to consolidated PDF report
            sheet_url: Optional Google Sheets URL
        
        Returns:
            bool: True if successful, False otherwise
        """
        if not os.path.exists(pdf_path):
            return False
        
        subject = (
            f"🏥 RavenCare Consolidated Triage Report - "
            f"{total_patients} Patients - "
            f"{datetime.now().strftime('%Y-%m-%d')}"
        )
        
        body = self._create_admin_email_body(total_patients, sheet_url)
        
        result = self.send_email_with_attachment(
            recipient_email=config.ADMIN_EMAIL,
            subject=subject,
            body=body,
            attachment_path=pdf_path,
            attachment_name="RavenCare_Consolidated_Report.pdf"
        )
        
        return result.get('successful', False)
    
    def _create_patient_email_body(
        self,
        patient_name: str,
        doctor_name: str,
        priority: str,
        specialty: str
    ) -> str:
        """Generate HTML email body for patient report"""
        return f"""<html>
<head>
<style>
body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
.header {{ background-color: #1a5490; color: white; padding: 20px; text-align: center; }}
.content {{ padding: 20px; }}
.info-box {{ background-color: #f0f8ff; padding: 15px; border-left: 4px solid #1a5490; margin: 20px 0; }}
.footer {{ background-color: #f5f5f5; padding: 15px; text-align: center; font-size: 12px; color: #666; }}
h1 {{ margin: 0; font-size: 24px; }}
h2 {{ color: #1a5490; font-size: 18px; }}
.important {{ color: #c41e3a; font-weight: bold; }}
</style>
</head>
<body>
<div class="header"><h1>🏥 Your Medical Triage Report</h1></div>
<div class="content">
<h2>Dear {patient_name},</h2>
<p>Thank you for using <strong>RavenCare</strong>. We have completed the AI-powered analysis of your medical information.</p>
<div class="info-box">
<h3>📋 Your Assessment Summary</h3>
<ul>
<li><strong>Assigned Specialty:</strong> {specialty}</li>
<li><strong>Assigned Doctor:</strong> {doctor_name}</li>
<li><strong>Priority Level:</strong> {priority}</li>
<li><strong>Report Date:</strong> {datetime.now().strftime('%Y-%m-%d')}</li>
</ul>
</div>
<p>Wishing you good health,<br><strong>RavenCare Care Team</strong></p>
</div>
<div class="footer">
<p>🤖 Automated message from RavenCare AI Triage System</p>
</div>
</body>
</html>"""
    
    def _create_doctor_email_body(
        self,
        doctor_name: str,
        patient_name: str,
        priority: str,
        urgency_score: str
    ) -> str:
        """Generate HTML email body for doctor report"""
        return f"""<html>
<head>
<style>
body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
.header {{ background-color: #1a5490; color: white; padding: 20px; text-align: center; }}
.content {{ padding: 20px; }}
.clinical-box {{ background-color: #fff0f0; padding: 15px; border-left: 4px solid #c41e3a; margin: 20px 0; }}
.footer {{ background-color: #f5f5f5; padding: 15px; text-align: center; font-size: 12px; color: #666; }}
h1 {{ margin: 0; font-size: 24px; }}
h2 {{ color: #1a5490; font-size: 18px; }}
.urgent {{ color: #c41e3a; font-weight: bold; }}
</style>
</head>
<body>
<div class="header"><h1>👨‍⚕️ New Patient Assignment - Clinical Report</h1></div>
<div class="content">
<h2>Dear {doctor_name},</h2>
<p>You have been assigned a new patient through <strong>RavenCare AI Triage System</strong>.</p>
<div class="clinical-box">
<h3>⚕️ Patient Assignment Details</h3>
<ul>
<li><strong>Patient Name:</strong> {patient_name}</li>
<li><strong>Consultation Priority:</strong> <span class="urgent">{priority}</span></li>
<li><strong>AI Urgency Score:</strong> {urgency_score}/100</li>
<li><strong>Assignment Date:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</li>
</ul>
</div>
<p>Thank you for your dedicated service,<br><strong>RavenCare Clinical Operations</strong></p>
</div>
<div class="footer">
<p>🤖 Automated message from RavenCare Medical Triage System</p>
</div>
</body>
</html>"""
    
    def _create_admin_email_body(
        self,
        total_patients: int,
        sheet_url: Optional[str]
    ) -> str:
        """Generate HTML email body for admin consolidated report"""
        sheet_section = ""
        if sheet_url:
            sheet_section = f'''
<div style="background-color: #f0f8ff; padding: 15px; margin: 20px 0; border-left: 4px solid #1a5490;">
<h3 style="color: #1a5490;">📊 Google Sheets Report</h3>
<p>Access the comprehensive triage data online:</p>
<p><a href="{sheet_url}" style="color: #1a5490; font-weight: bold;">🔗 Open Google Sheet</a></p>
</div>
'''
        
        return f"""<html>
<head>
<style>
body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
.header {{ background-color: #1a5490; color: white; padding: 20px; text-align: center; }}
.content {{ padding: 20px; }}
.summary {{ background-color: #f0f8ff; padding: 15px; border-left: 4px solid #1a5490; margin: 20px 0; }}
.footer {{ background-color: #f5f5f5; padding: 15px; text-align: center; font-size: 12px; color: #666; }}
h1 {{ margin: 0; font-size: 24px; }}
h2 {{ color: #1a5490; font-size: 18px; }}
</style>
</head>
<body>
<div class="header"><h1>🏥 RavenCare Consolidated Triage Report</h1></div>
<div class="content">
<h2>Dear Admin,</h2>
<p>The medical triage system has completed processing <strong>{total_patients} patients</strong>.</p>
<div class="summary">
<h3>📊 Report Summary</h3>
<ul>
<li><strong>Total Patients Processed:</strong> {total_patients}</li>
<li><strong>Report Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</li>
</ul>
</div>
{sheet_section}
<p>Best regards,<br><strong>RavenCare AI Triage System</strong></p>
</div>
<div class="footer">
<p>🤖 This is an automated message from RavenCare Medical Triage System</p>
</div>
</body>
</html>"""
