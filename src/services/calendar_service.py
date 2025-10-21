"""
Google Calendar Integration Service
Schedules medical appointments via Google Calendar
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional
from composio import Composio
from rich.console import Console

from src.config import config


console = Console()


class CalendarService:
    """
    Google Calendar service for scheduling appointments.
    
    Creates calendar events with meeting links for patient-doctor
    consultations.
    """
    
    def __init__(self):
        """Initialize Composio client for Google Calendar integration"""
        if not config.COMPOSIO_API_KEY:
            raise ValueError("COMPOSIO_API_KEY required for Calendar service")
        
        self.composio = Composio(api_key=config.COMPOSIO_API_KEY)
        self.user_id = config.COMPOSIO_USER_ID
        self.account_id = config.COMPOSIO_CALENDAR_ACCOUNT_ID
    
    def schedule_appointments(
        self,
        triage_results: List[Dict]
    ) -> Dict[str, Dict]:
        """
        Schedule calendar appointments for all patients.
        
        Args:
            triage_results: List of patient triage data
        
        Returns:
            Dict: Map of patient names to calendar event data
        """
        calendar_events = {}
        
        if not self.account_id:
            console.print(
                "[yellow]⚠ Calendar not configured, skipping[/yellow]"
            )
            return calendar_events
        
        try:
            for record in triage_results:
                patient = record.get('patient', {})
                doctor = record.get('matched_doctor')
                analyses = record.get('analyses', {})
                
                patient_name = patient.get('name', 'Patient')
                patient_email = patient.get('email')
                
                # Skip if no doctor or missing emails
                if not doctor or not patient_email:
                    continue
                
                doctor_email = doctor.get('contact_email')
                if not doctor_email:
                    continue
                
                # Schedule appointment
                event_data = self._create_appointment(
                    patient,
                    doctor,
                    analyses
                )
                
                if event_data:
                    calendar_events[patient_name] = event_data
            
        except Exception as e:
            console.print(
                f"[red]❌ Error scheduling appointments: {str(e)}[/red]"
            )
        
        return calendar_events
    
    def _create_appointment(
        self,
        patient: Dict,
        doctor: Dict,
        analyses: Dict
    ) -> Optional[Dict]:
        """Create a single calendar appointment"""
        try:
            # Parse time slot
            preferred_slot = patient.get('preferred_slot', '09:00')
            tomorrow = datetime.now() + timedelta(days=1)
            hour, minute = map(int, preferred_slot.split(':'))
            start_time = tomorrow.replace(
                hour=hour,
                minute=minute,
                second=0,
                microsecond=0
            )
            start_datetime = start_time.strftime("%Y-%m-%dT%H:%M:%S")
            
            # Get duration
            duration_str = analyses.get('o4mini', {}).get(
                'estimated_consultation_duration',
                '30 minutes'
            )
            try:
                duration_minutes = int(''.join(filter(str.isdigit, duration_str)))
            except:
                duration_minutes = 30
            
            # Prepare event parameters
            patient_name = patient.get('name', 'Patient')
            doctor_name = doctor.get('name', 'Doctor')
            specialty = analyses.get('o4mini', {}).get(
                'final_specialty',
                patient.get('mapped_specialty', 'General')
            )
            symptoms = patient.get('symptoms', 'N/A')
            
            event_params = {
                "calendar_id": "primary",
                "summary": f"Medical Consultation: {patient_name} with Dr. {doctor_name}",
                "description": (
                    f"Patient: {patient_name}\n"
                    f"Doctor: Dr. {doctor_name}\n"
                    f"Specialty: {specialty}\n\n"
                    f"Symptoms: {symptoms}\n\n"
                    f"Scheduled via RavenCare AI Triage System"
                ),
                "start_datetime": start_datetime,
                "timezone": "Asia/Kolkata",
                "event_duration_hour": duration_minutes // 60,
                "event_duration_minutes": duration_minutes % 60,
                "attendees": [patient['email'], doctor['contact_email']],
                "location": f"{specialty} Department",
                "send_updates": True,
                "guests_can_modify": False,
                "guestsCanInviteOthers": False,
                "guestsCanSeeOtherGuests": True,
                "create_meeting_room": True,
            }
            
            # Create calendar event
            result = self.composio.tools.execute(
                "GOOGLECALENDAR_CREATE_EVENT",
                user_id=self.user_id,
                arguments=event_params,
                connected_account_id=self.account_id
            )
            
            if result.get('successful', False):
                event_data = result.get('data', {})
                return {
                    'htmlLink': event_data.get('htmlLink', ''),
                    'hangoutLink': event_data.get('hangoutLink', 'N/A'),
                    'event_data': event_data
                }
            
            return None
            
        except Exception as e:
            console.print(
                f"[red]❌ Error creating appointment: {str(e)}[/red]"
            )
            return None
