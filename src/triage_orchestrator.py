"""
Medical Triage Orchestrator
Coordinates all components of the triage system
"""

import json
import os
from datetime import datetime
from typing import Dict, List
from rich.console import Console
from rich.panel import Panel
from rich import box

from src.config import config
from src.agents import GeminiAnalyzer, GrokAnalyzer, O4MiniEvaluator
from src.services import (
    DoctorMatcher,
    PDFGenerator,
    EmailService,
    CalendarService,
    SheetsService
)


console = Console()


class TriageOrchestrator:
    """
    Main orchestrator for the medical triage system.
    
    Coordinates all AI agents and services to provide comprehensive
    patient triage from symptom analysis to doctor assignment and
    notification.
    """
    
    def __init__(self):
        """Initialize all agents and services"""
        console.print("[cyan]Initializing RavenCare Triage System...[/cyan]")
        
        # Initialize AI agents
        self.gemini = GeminiAnalyzer()
        self.grok = GrokAnalyzer()
        self.o4mini = O4MiniEvaluator()
        
        # Initialize services
        self.doctor_matcher = DoctorMatcher()
        self.pdf_generator = PDFGenerator()
        self.email_service = EmailService()
        self.calendar_service = CalendarService()
        self.sheets_service = SheetsService()
        
        # Results storage
        self.results = []
        
        console.print("[green]✓ All components initialized[/green]\n")
    
    def load_patients(self, file_path: str = None) -> List[Dict]:
        """
        Load patient data from JSON file.
        
        Args:
            file_path: Path to patient JSON file
                      Defaults to configured patient file
        
        Returns:
            List[Dict]: List of patient data dictionaries
        """
        if file_path is None:
            file_path = config.DEFAULT_PATIENT_FILE
        
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def process_patient(self, patient_data: Dict) -> Dict:
        """
        Process a single patient through the complete triage pipeline.
        
        Pipeline stages:
        1. Gemini: Symptom analysis and specialty mapping
        2. Grok: Urgency scoring and risk assessment
        3. O4-Mini: Final evaluation and recommendations
        4. Doctor matching based on specialty and availability
        
        Args:
            patient_data: Patient information dictionary
        
        Returns:
            Dict: Complete triage result with all analyses
        """
        patient_name = patient_data.get('name', 'Unknown')
        
        console.print(f"\n[bold cyan]{'='*80}[/bold cyan]")
        console.print(f"[bold yellow]Processing: {patient_name}[/bold yellow]")
        console.print(f"[bold cyan]{'='*80}[/bold cyan]\n")
        
        result = {
            'patient': patient_data,
            'timestamp': datetime.now().isoformat(),
            'analyses': {}
        }
        
        # Stage 1: Gemini Analysis
        console.print("[bold green]🔬 Stage 1: Gemini Analysis[/bold green]")
        try:
            gemini_result = self.gemini.analyze_symptoms(patient_data)
            result['analyses']['gemini'] = gemini_result
            console.print(
                f"[green]✓ Primary Specialty: "
                f"{gemini_result.get('primary_specialty', 'N/A')}[/green]"
            )
        except Exception as e:
            console.print(f"[red]✗ Gemini error: {str(e)}[/red]")
            result['analyses']['gemini'] = {'error': str(e)}
        
        # Stage 2: Grok Urgency Assessment
        console.print("\n[bold blue]⚡ Stage 2: Grok Urgency Assessment[/bold blue]")
        try:
            grok_result = self.grok.calculate_urgency(
                patient_data,
                result['analyses']['gemini']
            )
            result['analyses']['grok'] = grok_result
            urgency = grok_result.get('urgency_score', 'N/A')
            console.print(f"[blue]✓ Urgency Score: {urgency}/100[/blue]")
        except Exception as e:
            console.print(f"[red]✗ Grok error: {str(e)}[/red]")
            result['analyses']['grok'] = {'error': str(e)}
        
        # Stage 3: O4-Mini Final Evaluation
        console.print("\n[bold magenta]🎯 Stage 3: O4-Mini Evaluation[/bold magenta]")
        try:
            o4_result = self.o4mini.final_evaluation(
                patient_data,
                result['analyses']['gemini'],
                result['analyses']['grok']
            )
            result['analyses']['o4mini'] = o4_result
            final_specialty = o4_result.get('final_specialty', 'N/A')
            console.print(
                f"[magenta]✓ Final Specialty: {final_specialty}[/magenta]"
            )
        except Exception as e:
            console.print(f"[red]✗ O4-Mini error: {str(e)}[/red]")
            result['analyses']['o4mini'] = {'error': str(e)}
        
        # Stage 4: Enhanced Doctor Matching
        console.print("\n[bold yellow]👨‍⚕️ Stage 4: Enhanced Doctor Matching[/bold yellow]")
        try:
            specialty = result['analyses']['o4mini'].get(
                'final_specialty',
                result['analyses']['gemini'].get('primary_specialty')
            )
            
            # Extract sub-specialization hints from analyses
            potential_conditions = result['analyses']['gemini'].get(
                'potential_conditions', []
            )
            sub_spec_hint = (
                potential_conditions[0] if potential_conditions else None
            )
            
            # Get urgency score
            urgency_score = result['analyses']['grok'].get(
                'urgency_score', 50
            )
            
            # Enhanced matching with additional parameters
            doctor = self.doctor_matcher.find_best_doctor(
                specialty=specialty,
                preferred_slot=patient_data.get('preferred_slot', '09:00'),
                patient_language=patient_data.get('preferred_language', 'English'),
                urgency_score=urgency_score,
                patient_age=patient_data.get('age'),
                sub_specialization_hint=sub_spec_hint,
                patient_conditions=patient_data.get('pre_existing_conditions', [])
            )
            result['matched_doctor'] = doctor
            
            if doctor:
                doctor_name = doctor.get('name', 'Unknown')
                match_quality = doctor.get('match_quality', 'unknown')
                match_score = doctor.get('match_score', 0)
                console.print(
                    f"[yellow]✓ Matched: Dr. {doctor_name} "
                    f"(Score: {match_score}, Quality: {match_quality})[/yellow]"
                )
            else:
                console.print(
                    "[yellow]⚠ No match - Emergency referral[/yellow]"
                )
        except Exception as e:
            console.print(f"[red]✗ Matching error: {str(e)}[/red]")
            result['matched_doctor'] = None
        
        console.print(f"\n[bold green]✅ Completed: {patient_name}[/bold green]")
        
        return result
    
    def generate_summary_report(self) -> str:
        """
        Generate JSON summary report of all processed patients.
        
        Returns:
            str: Filename of generated report
        """
        if not self.results:
            console.print("[bold red]No patients processed yet.[/bold red]")
            return ""
        
        console.print("\n[bold cyan]📄 Generating JSON Report...[/bold cyan]")
        
        # Save detailed report to JSON
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = f"triage_report_{timestamp}.json"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        
        console.print(f"[green]✓ Report saved: {report_file}[/green]\n")
        
        return report_file
    
    def run(self, patient_file: str = None) -> None:
        """
        Run the complete triage system on all patients.
        
        This is the main entry point that orchestrates the entire
        triage workflow from patient intake to notification.
        
        Args:
            patient_file: Path to patient data JSON file
        """
        # Display banner
        console.print("\n")
        console.print(Panel.fit(
            "[bold white]RavenCare - Advanced Medical Triage System[/bold white]\n"
            "[cyan]AI-Powered Multi-Model Patient Assessment[/cyan]\n"
            "[dim]Gemini 2.5 Pro • Grok 4 • OpenAI O4-Mini[/dim]",
            border_style="bright_blue",
            box=box.DOUBLE
        ))
        console.print("\n")
        
        # Load patients
        console.print("[bold]Loading patient data...[/bold]")
        patients = self.load_patients(patient_file)
        console.print(
            f"[bold green]✓ Loaded {len(patients)} patients[/bold green]\n"
        )
        
        # Process each patient
        for i, patient in enumerate(patients, 1):
            console.print(f"[bold white]Patient {i}/{len(patients)}[/bold white]")
            result = self.process_patient(patient)
            self.results.append(result)
            
            if i < len(patients):
                console.print("[dim]─" * 80 + "[/dim]")
        
        # Generate reports and notifications
        console.print("\n[bold cyan]{'='*80}[/bold cyan]")
        console.print("[bold white]📊 GENERATING REPORTS & NOTIFICATIONS[/bold white]")
        console.print("[bold cyan]{'='*80}[/bold cyan]\n")
        
        # 1. Generate JSON report
        report_file = self.generate_summary_report()
        
        # 2. Create Google Sheet
        console.print("[bold]Creating Google Sheet...[/bold]")
        sheet_url = self.sheets_service.create_triage_sheet(self.results)
        if sheet_url:
            console.print(f"[green]✓ Sheet URL: {sheet_url}[/green]\n")
        else:
            console.print("[yellow]⚠ Google Sheet skipped[/yellow]\n")
        
        # 3. Schedule calendar appointments
        console.print("[bold]Scheduling calendar appointments...[/bold]")
        calendar_events = self.calendar_service.schedule_appointments(
            self.results
        )
        console.print(
            f"[green]✓ Scheduled {len(calendar_events)} appointments[/green]\n"
        )
        
        # 4. Generate PDF reports
        console.print("[bold]Generating PDF reports...[/bold]")
        pdf_count = self._generate_all_pdfs()
        console.print(f"[green]✓ Generated {pdf_count} PDFs[/green]\n")
        
        # 5. Send email notifications
        console.print("[bold]Sending email notifications...[/bold]")
        email_count = self._send_all_emails(sheet_url, calendar_events)
        console.print(f"[green]✓ Sent {email_count} emails[/green]\n")
        
        # Final summary
        console.print("\n[bold cyan]{'='*80}[/bold cyan]")
        console.print(Panel.fit(
            f"[bold green]🎉 TRIAGE COMPLETE![/bold green]\n\n"
            f"[white]✅ Patients Processed: {len(patients)}[/white]\n"
            f"[white]✅ JSON Report: {report_file}[/white]\n"
            f"[white]✅ Google Sheet: {'Created' if sheet_url else 'Skipped'}[/white]\n"
            f"[white]✅ Calendar Events: {len(calendar_events)}[/white]\n"
            f"[white]✅ PDF Reports: {pdf_count}[/white]\n"
            f"[white]✅ Emails Sent: {email_count}[/white]",
            border_style="green",
            box=box.ROUNDED
        ))
        console.print("[bold cyan]{'='*80}[/bold cyan]\n")
    
    def _generate_all_pdfs(self) -> int:
        """Generate all PDF reports (patients, doctors, consolidated)"""
        pdf_count = 0
        output_dir = config.PDF_REPORTS_DIR
        
        # Individual patient and doctor PDFs
        for result in self.results:
            patient_name = result.get('patient', {}).get('name', 'Patient')
            safe_name = "".join(
                c for c in patient_name
                if c.isalnum() or c in (' ', '_')
            ).rstrip().replace(' ', '_')
            
            # Patient PDF
            patient_pdf = f"{output_dir}/patients/{safe_name}.pdf"
            if self.pdf_generator.generate_patient_pdf(result, patient_pdf):
                pdf_count += 1
            
            # Doctor PDF
            doctor = result.get('matched_doctor')
            if doctor:
                doctor_name = doctor.get('name', 'NoDoctor')
                safe_doctor = "".join(
                    c for c in doctor_name
                    if c.isalnum() or c in (' ', '_')
                ).rstrip().replace(' ', '_')
                
                os.makedirs(
                    f"{output_dir}/doctors/{safe_doctor}",
                    exist_ok=True
                )
                doctor_pdf = (
                    f"{output_dir}/doctors/{safe_doctor}/"
                    f"{safe_doctor}_{safe_name}.pdf"
                )
                if self.pdf_generator.generate_doctor_pdf(result, doctor_pdf):
                    pdf_count += 1
        
        # Consolidated report
        consolidated_pdf = f"{output_dir}/doctor_consolidated_report.pdf"
        if self.pdf_generator.generate_consolidated_report(
            self.results,
            consolidated_pdf
        ):
            pdf_count += 1
        
        return pdf_count
    
    def _send_all_emails(
        self,
        sheet_url: str,
        calendar_events: Dict
    ) -> int:
        """Send all email notifications (admin, patients, doctors)"""
        email_count = 0
        output_dir = config.PDF_REPORTS_DIR
        
        # Admin email
        consolidated_pdf = f"{output_dir}/doctor_consolidated_report.pdf"
        if os.path.exists(consolidated_pdf):
            if self.email_service.send_admin_email(
                len(self.results),
                consolidated_pdf,
                sheet_url
            ):
                email_count += 1
        
        # Patient emails
        patient_count = self.email_service.send_patient_emails(
            self.results,
            output_dir,
            calendar_events
        )
        email_count += patient_count
        
        # Doctor emails
        doctor_count = self.email_service.send_doctor_emails(
            self.results,
            output_dir,
            calendar_events
        )
        email_count += doctor_count
        
        return email_count


# Main entry point
if __name__ == "__main__":
    try:
        # Validate configuration
        is_valid = config.print_config_status()
        
        if not is_valid:
            console.print(
                "\n[bold red]❌ Configuration validation failed.[/bold red]"
            )
            console.print(
                "[yellow]Please set required environment variables and try again.[/yellow]\n"
            )
            exit(1)
        
        # Run triage system
        orchestrator = TriageOrchestrator()
        orchestrator.run()
        
    except KeyboardInterrupt:
        console.print(
            "\n[bold yellow]⚠ Triage interrupted by user[/bold yellow]"
        )
    except Exception as e:
        console.print(f"\n[bold red]❌ Error: {str(e)}[/bold red]")
        import traceback
        console.print(f"[dim]{traceback.format_exc()}[/dim]")
