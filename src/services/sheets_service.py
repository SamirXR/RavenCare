"""
Google Sheets Integration Service
Creates and manages Google Sheets reports for triage data
"""

import json
from typing import Dict, List, Optional
from composio import Composio
from rich.console import Console

from src.config import config


console = Console()


class SheetsService:
    """
    Google Sheets service for creating online triage reports.
    
    Creates formatted Google Sheets with comprehensive triage data
    that can be shared and accessed online.
    """
    
    def __init__(self):
        """Initialize Composio client for Google Sheets integration"""
        if not config.COMPOSIO_API_KEY:
            raise ValueError("COMPOSIO_API_KEY required for Sheets service")
        
        self.composio = Composio(api_key=config.COMPOSIO_API_KEY)
        self.user_id = config.COMPOSIO_USER_ID
        self.account_id = config.COMPOSIO_SHEETS_ACCOUNT_ID
    
    def create_triage_sheet(
        self,
        triage_results: List[Dict],
        title: Optional[str] = None
    ) -> Optional[str]:
        """
        Create Google Sheet from triage results.
        
        Args:
            triage_results: List of patient triage data
            title: Sheet title (auto-generated if not provided)
        
        Returns:
            str: Google Sheets URL if successful, None otherwise
        """
        try:
            if not self.account_id:
                console.print(
                    "[yellow]⚠ Google Sheets not configured, skipping[/yellow]"
                )
                return None
            
            # Convert results to sheet format
            sheet_data = self._convert_to_sheet_format(triage_results)
            
            # Generate title if not provided
            if not title:
                from datetime import datetime
                formatted_date = datetime.now().strftime('%B %d, %Y %I:%M %p')
                title = f"RavenCare Triage Report - {formatted_date}"
            
            # Create the Google Sheet
            result = self.composio.tools.execute(
                "GOOGLESHEETS_SHEET_FROM_JSON",
                user_id=self.user_id,
                arguments={
                    "title": title,
                    "sheet_name": "Patient Triage Data",
                    "sheet_json": sheet_data
                },
                connected_account_id=self.account_id
            )
            
            # Extract spreadsheet URL
            data = result.get("data", {})
            sheet_id = data.get("spreadsheetId")
            
            if sheet_id:
                sheet_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/edit"
                return sheet_url
            else:
                console.print(
                    "[red]❌ Could not retrieve spreadsheet ID[/red]"
                )
                return None
                
        except Exception as e:
            console.print(f"[red]❌ Error creating Google Sheet: {str(e)}[/red]")
            return None
    
    def _convert_to_sheet_format(
        self,
        triage_results: List[Dict]
    ) -> List[Dict]:
        """
        Convert triage results to Google Sheets compatible format.
        
        Args:
            triage_results: List of patient triage data
        
        Returns:
            List[Dict]: Flattened data for sheet rows
        """
        sheet_data = []
        
        for record in triage_results:
            patient = record.get('patient', {})
            analyses = record.get('analyses', {})
            doctor = record.get('matched_doctor', {})
            
            # Extract analysis data
            gemini = analyses.get('gemini', {})
            grok = analyses.get('grok', {})
            o4mini = analyses.get('o4mini', {})
            
            # Create flattened row
            row = {
                # Patient Information
                "Patient Name": patient.get('name', ''),
                "Age": patient.get('age', ''),
                "Gender": patient.get('gender', ''),
                "Contact": patient.get('contact_number', ''),
                "Email": patient.get('email', ''),
                "Language": patient.get('preferred_language', ''),
                "Preferred Slot": patient.get('preferred_slot', ''),
                
                # Medical Information
                "Symptoms": patient.get('symptoms', ''),
                "Pre-existing Conditions": ', '.join(
                    patient.get('pre_existing_conditions', [])
                ),
                
                # Timestamp
                "Timestamp": record.get('timestamp', ''),
                
                # Gemini Analysis
                "Primary Specialty": gemini.get('primary_specialty', ''),
                "Secondary Specialties": ', '.join(
                    gemini.get('secondary_specialties', [])
                ),
                "Key Symptoms": ', '.join(
                    gemini.get('key_symptoms_identified', [])
                ),
                "Potential Conditions": ', '.join(
                    gemini.get('potential_conditions', [])
                ),
                
                # Grok Analysis
                "Urgency Score": grok.get('urgency_score', ''),
                "Risk Level": grok.get('risk_level', ''),
                "Triage Category": grok.get('triage_category', ''),
                "Time to Treatment": grok.get('time_to_treatment', ''),
                "Red Flags": ', '.join(grok.get('red_flags', [])),
                
                # O4Mini Analysis
                "Final Specialty": o4mini.get('final_specialty', ''),
                "Confidence": o4mini.get('confidence_level', ''),
                "Priority": o4mini.get('consultation_priority', ''),
                "Duration": o4mini.get('estimated_consultation_duration', ''),
                "Follow-up Required": str(o4mini.get('follow_up_required', '')),
                
                # Matched Doctor
                "Doctor Name": (
                    doctor.get('name', 'No match') if doctor else 'No match'
                ),
                "Doctor Qualification": (
                    doctor.get('qualification', '') if doctor else ''
                ),
                "Doctor Experience": (
                    f"{doctor.get('experience_years', '')} years"
                    if doctor and doctor.get('experience_years') else ''
                ),
                "Doctor Rating": (
                    doctor.get('patient_rating', '') if doctor else ''
                ),
                "Doctor Contact": (
                    doctor.get('contact_email', '') if doctor else ''
                ),
            }
            
            sheet_data.append(row)
        
        return sheet_data
