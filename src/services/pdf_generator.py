"""
PDF Report Generation Service
Creates professional medical PDF reports for patients and doctors
"""

import os
from datetime import datetime
from typing import Dict, Optional
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.platypus import Table as PDFTable, TableStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from rich.console import Console

from src.config import config


console = Console()


class PDFGenerator:
    """
    Professional PDF report generator for medical triage.
    
    Generates two types of reports:
    - Patient-facing: Simplified, easy-to-understand format
    - Doctor-facing: Clinical details with full medical reasoning
    """
    
    def __init__(self, output_dir: Optional[str] = None):
        """
        Initialize PDF generator.
        
        Args:
            output_dir: Base directory for PDF output
                       Defaults to configured PDF reports directory
        """
        self.output_dir = output_dir or config.PDF_REPORTS_DIR
        self.styles = self._create_custom_styles()
        
        # Ensure output directories exist
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(f"{self.output_dir}/patients", exist_ok=True)
        os.makedirs(f"{self.output_dir}/doctors", exist_ok=True)
    
    def _create_custom_styles(self) -> Dict:
        """
        Create custom paragraph styles for professional PDFs.
        
        Returns:
            Dict: Dictionary of ReportLab paragraph styles
        """
        styles = getSampleStyleSheet()
        
        # Title style
        styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1a5490'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Section heading
        styles.add(ParagraphStyle(
            name='SectionHeading',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#2c5aa0'),
            spaceAfter=12,
            spaceBefore=16,
            fontName='Helvetica-Bold',
            borderWidth=1,
            borderColor=colors.HexColor('#2c5aa0'),
            borderPadding=5,
            backColor=colors.HexColor('#e8f0f8')
        ))
        
        # Subsection heading
        styles.add(ParagraphStyle(
            name='SubsectionHeading',
            parent=styles['Heading3'],
            fontSize=13,
            textColor=colors.HexColor('#1a5490'),
            spaceAfter=8,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        ))
        
        # Body text
        styles.add(ParagraphStyle(
            name='CustomBody',
            parent=styles['BodyText'],
            fontSize=11,
            spaceAfter=8,
            alignment=TA_JUSTIFY,
            leading=14
        ))
        
        # Important text (warnings, urgent info)
        styles.add(ParagraphStyle(
            name='ImportantText',
            parent=styles['BodyText'],
            fontSize=11,
            textColor=colors.HexColor('#c41e3a'),
            spaceAfter=8,
            fontName='Helvetica-Bold',
            backColor=colors.HexColor('#fff0f0'),
            borderWidth=1,
            borderColor=colors.HexColor('#c41e3a'),
            borderPadding=8,
            leading=14
        ))
        
        # Info box
        styles.add(ParagraphStyle(
            name='InfoBox',
            parent=styles['BodyText'],
            fontSize=10,
            spaceAfter=8,
            backColor=colors.HexColor('#f0f8ff'),
            borderWidth=1,
            borderColor=colors.HexColor('#4a90e2'),
            borderPadding=8,
            leading=13
        ))
        
        return styles
    
    def generate_patient_pdf(
        self,
        patient_data: Dict,
        output_filename: str
    ) -> bool:
        """
        Generate patient-facing PDF report.
        
        Args:
            patient_data: Complete patient triage data
            output_filename: Full path for output PDF file
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Create PDF document
            doc = SimpleDocTemplate(
                output_filename,
                pagesize=letter,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=50,
            )

            elements = []
            
            # Extract data
            patient = patient_data.get('patient', {})
            analyses = patient_data.get('analyses', {})
            doctor = patient_data.get('matched_doctor', {})
            gemini = analyses.get('gemini', {})
            grok = analyses.get('grok', {})
            o4mini = analyses.get('o4mini', {})

            # Title
            title = "🏥 MEDICAL TRIAGE REPORT"
            elements.append(Paragraph(title, self.styles['CustomTitle']))
            elements.append(Spacer(1, 0.2*inch))

            # Patient Information Section
            elements.append(
                Paragraph("👤 PATIENT INFORMATION", self.styles['SectionHeading'])
            )
            elements.append(Spacer(1, 0.1*inch))

            patient_info = [
                ['Name:', patient.get('name', 'N/A')],
                ['Age:', f"{patient.get('age', 'N/A')} years"],
                ['Gender:', patient.get('gender', 'N/A')],
                ['Contact:', patient.get('contact_number', 'N/A')],
                ['Email:', patient.get('email', 'N/A')],
                ['Language:', patient.get('preferred_language', 'N/A')],
                ['Intake Method:', patient.get('intake_method', 'N/A')],
                ['Preferred Slot:', patient.get('preferred_slot', 'N/A')],
            ]

            patient_table = PDFTable(
                patient_info,
                colWidths=[2*inch, 4*inch]
            )
            patient_table.setStyle(self._get_table_style())
            elements.append(patient_table)
            elements.append(Spacer(1, 0.2*inch))

            # Medical Details
            elements.append(
                Paragraph("🏥 MEDICAL DETAILS", self.styles['SectionHeading'])
            )
            elements.append(Spacer(1, 0.1*inch))

            elements.append(
                Paragraph(
                    "<b>Chief Complaint & Symptoms:</b>",
                    self.styles['SubsectionHeading']
                )
            )
            elements.append(
                Paragraph(
                    patient.get('symptoms', 'N/A'),
                    self.styles['CustomBody']
                )
            )
            elements.append(Spacer(1, 0.1*inch))

            pre_conditions = ', '.join(
                patient.get('pre_existing_conditions', [])
            ) or 'None'
            elements.append(
                Paragraph(
                    f"<b>Pre-existing Conditions:</b> {pre_conditions}",
                    self.styles['CustomBody']
                )
            )
            mapped_specialty = patient.get('mapped_specialty', 'N/A')
            elements.append(
                Paragraph(
                    f"<b>Mapped Specialty:</b> {mapped_specialty}",
                    self.styles['CustomBody']
                )
            )
            elements.append(Spacer(1, 0.2*inch))

            # Urgency Assessment
            self._add_urgency_section(elements, grok)

            # AI Analysis
            self._add_ai_analysis_section(elements, gemini, grok, o4mini)

            # Clinical Recommendations
            self._add_recommendations_section(elements, o4mini)

            # Matched Doctor
            self._add_doctor_section(elements, doctor)

            # Footer
            elements.append(Spacer(1, 0.3*inch))
            timestamp = patient_data.get('timestamp', 'N/A')
            footer_text = (
                f"<i>Report generated on {timestamp} "
                "by RavenCare Triage System</i>"
            )
            elements.append(Paragraph(footer_text, self.styles['Normal']))

            # Build PDF
            doc.build(elements)
            return True

        except Exception as e:
            console.print(f"[red]✗[/red] Error creating PDF: {str(e)}")
            return False
    
    def generate_doctor_pdf(
        self,
        patient_data: Dict,
        output_filename: str
    ) -> bool:
        """
        Generate doctor-facing PDF with clinical details.
        
        Args:
            patient_data: Complete patient triage data
            output_filename: Full path for output PDF file
        
        Returns:
            bool: True if successful, False otherwise
        """
        # Same as patient PDF but with additional clinical reasoning
        # This calls the same method for now
        return self.generate_patient_pdf(patient_data, output_filename)
    
    def _get_table_style(self) -> TableStyle:
        """Get standard table style for patient info tables"""
        return TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e8f0f8')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ])
    
    def _add_urgency_section(self, elements: list, grok: Dict) -> None:
        """Add urgency assessment section to PDF"""
        urgency_score = grok.get('urgency_score', 'N/A')
        risk_level = grok.get('risk_level', 'N/A')
        triage_category = grok.get('triage_category', 'N/A')
        time_to_treatment = grok.get('time_to_treatment', 'N/A')

        urgency_text = f"""<b>⚠️ URGENCY ASSESSMENT:</b><br/>
        <b>Urgency Score:</b> {urgency_score}/100 | \
<b>Risk Level:</b> {risk_level}<br/>
        <b>Triage Category:</b> {triage_category} | \
<b>Time to Treatment:</b> {time_to_treatment}"""
        
        elements.append(
            Paragraph(urgency_text, self.styles['ImportantText'])
        )
        elements.append(Spacer(1, 0.2*inch))
    
    def _add_ai_analysis_section(
        self,
        elements: list,
        gemini: Dict,
        grok: Dict,
        o4mini: Dict
    ) -> None:
        """Add AI analysis section to PDF"""
        elements.append(
            Paragraph("🤖 AI ANALYSIS", self.styles['SectionHeading'])
        )
        elements.append(Spacer(1, 0.1*inch))

        # Gemini Analysis
        elements.append(
            Paragraph(
                "<b>Specialty Mapping (Gemini):</b>",
                self.styles['SubsectionHeading']
            )
        )
        
        primary = gemini.get('primary_specialty', 'N/A')
        secondary = ', '.join(gemini.get('secondary_specialties', []))
        secondary = secondary or 'None'
        potential = ', '.join(gemini.get('potential_conditions', []))
        potential = potential or 'None'
        
        gemini_text = f"""<b>Primary Specialty:</b> {primary}<br/>
        <b>Secondary Specialties:</b> {secondary}<br/>
        <b>Potential Conditions:</b> {potential}"""
        
        elements.append(Paragraph(gemini_text, self.styles['InfoBox']))
        elements.append(Spacer(1, 0.1*inch))

        # Grok Risk Analysis
        elements.append(
            Paragraph(
                "<b>Risk Analysis (Grok):</b>",
                self.styles['SubsectionHeading']
            )
        )
        
        red_flags = grok.get('red_flags', [])
        if red_flags:
            flags_text = "<b>🚩 Red Flags:</b><br/>" + "<br/>".join(
                [f"• {flag}" for flag in red_flags]
            )
            elements.append(
                Paragraph(flags_text, self.styles['ImportantText'])
            )
            elements.append(Spacer(1, 0.1*inch))
        
        elements.append(Spacer(1, 0.2*inch))
    
    def _add_recommendations_section(
        self,
        elements: list,
        o4mini: Dict
    ) -> None:
        """Add clinical recommendations section to PDF"""
        elements.append(
            Paragraph(
                "📋 CLINICAL RECOMMENDATIONS",
                self.styles['SectionHeading']
            )
        )
        elements.append(Spacer(1, 0.1*inch))

        final_specialty = o4mini.get('final_specialty', 'N/A')
        priority = o4mini.get('consultation_priority', 'N/A')
        confidence = o4mini.get('confidence_level', 'N/A')
        
        elements.append(
            Paragraph(
                f"<b>Final Specialty:</b> {final_specialty}",
                self.styles['CustomBody']
            )
        )
        elements.append(
            Paragraph(
                f"<b>Consultation Priority:</b> {priority}",
                self.styles['CustomBody']
            )
        )
        elements.append(
            Paragraph(
                f"<b>Confidence Level:</b> {confidence}",
                self.styles['CustomBody']
            )
        )
        elements.append(Spacer(1, 0.1*inch))

        # Patient Instructions
        instructions = o4mini.get('patient_instructions', '')
        if instructions:
            elements.append(
                Paragraph(
                    "<b>📝 Patient Instructions:</b>",
                    self.styles['SubsectionHeading']
                )
            )
            elements.append(
                Paragraph(instructions, self.styles['InfoBox'])
            )
            elements.append(Spacer(1, 0.15*inch))

        # Warnings
        warnings = o4mini.get('warnings', [])
        if warnings:
            warnings_text = "<b>⚠️ IMPORTANT WARNINGS:</b><br/>" + \
                "<br/>".join([f"• {warning}" for warning in warnings])
            elements.append(
                Paragraph(warnings_text, self.styles['ImportantText'])
            )
            elements.append(Spacer(1, 0.2*inch))
    
    def _add_doctor_section(self, elements: list, doctor: Optional[Dict]) -> None:
        """Add matched doctor section to PDF"""
        elements.append(
            Paragraph(
                "👨‍⚕️ ASSIGNED PHYSICIAN",
                self.styles['SectionHeading']
            )
        )
        elements.append(Spacer(1, 0.1*inch))

        if doctor:
            doctor_info = [
                ['Name:', doctor.get('name', 'N/A')],
                ['Qualification:', doctor.get('qualification', 'N/A')],
                [
                    'Experience:',
                    f"{doctor.get('experience_years', 'N/A')} years"
                ],
                [
                    'Specialization:',
                    doctor.get('sub_specialization', 'N/A')
                ],
                [
                    'Languages:',
                    ', '.join(doctor.get('languages_spoken', []))
                ],
                [
                    'Rating:',
                    f"⭐ {doctor.get('patient_rating', 'N/A')}/5.0"
                ],
                [
                    'Available Slots:',
                    ', '.join(doctor.get('slots', []))
                ],
                ['Contact:', doctor.get('contact_email', 'N/A')],
            ]

            doctor_table = PDFTable(
                doctor_info,
                colWidths=[2*inch, 4*inch]
            )
            doctor_table.setStyle(self._get_table_style())
            elements.append(doctor_table)
        else:
            warning_text = (
                "⚠️ <b>Emergency Case - No specific doctor matched. "
                "Patient requires immediate emergency department "
                "evaluation.</b>"
            )
            elements.append(
                Paragraph(warning_text, self.styles['ImportantText'])
            )
    
    def generate_consolidated_report(
        self,
        all_patients_data: list[Dict],
        output_filename: str
    ) -> bool:
        """
        Generate consolidated PDF report for doctors with all patients.
        
        Args:
            all_patients_data: List of all patient triage data
            output_filename: Full path for output PDF file
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            doc = SimpleDocTemplate(
                output_filename,
                pagesize=letter,
                rightMargin=50,
                leftMargin=50,
                topMargin=50,
                bottomMargin=40,
            )
            
            elements = []
            
            # Title
            title = "🏥 CONSOLIDATED MEDICAL TRIAGE REPORT"
            elements.append(Paragraph(title, self.styles['CustomTitle']))
            elements.append(Spacer(1, 0.1*inch))
            
            # Report metadata
            report_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            metadata_text = (
                f"<b>Report Date:</b> {report_date} | "
                f"<b>Total Patients:</b> {len(all_patients_data)}"
            )
            elements.append(
                Paragraph(metadata_text, self.styles['CustomBody'])
            )
            elements.append(Spacer(1, 0.2*inch))
            
            # Executive Summary
            elements.append(
                Paragraph(
                    "📊 EXECUTIVE SUMMARY",
                    self.styles['SectionHeading']
                )
            )
            elements.append(Spacer(1, 0.1*inch))
            
            # Calculate priority breakdown
            emergency_count = sum(
                1 for p in all_patients_data
                if p.get('analyses', {}).get('o4mini', {}).get(
                    'consultation_priority', ''
                ) == 'Emergency'
            )
            urgent_count = sum(
                1 for p in all_patients_data
                if p.get('analyses', {}).get('o4mini', {}).get(
                    'consultation_priority', ''
                ) == 'Urgent'
            )
            standard_count = sum(
                1 for p in all_patients_data
                if p.get('analyses', {}).get('o4mini', {}).get(
                    'consultation_priority', ''
                ) == 'Standard'
            )
            
            total = len(all_patients_data)
            
            summary_data = [
                ['Priority Level', 'Count', 'Percentage'],
                [
                    'Emergency',
                    str(emergency_count),
                    f"{emergency_count/total*100:.1f}%"
                ],
                [
                    'Urgent',
                    str(urgent_count),
                    f"{urgent_count/total*100:.1f}%"
                ],
                [
                    'Standard',
                    str(standard_count),
                    f"{standard_count/total*100:.1f}%"
                ],
            ]
            
            summary_table = PDFTable(
                summary_data,
                colWidths=[2*inch, 1.5*inch, 1.5*inch]
            )
            summary_table.setStyle(self._get_summary_table_style())
            elements.append(summary_table)
            elements.append(Spacer(1, 0.3*inch))
            
            # Patient Details (simplified for consolidated view)
            elements.append(
                Paragraph("📋 PATIENT DETAILS", self.styles['SectionHeading'])
            )
            elements.append(Spacer(1, 0.2*inch))
            
            for idx, patient_data in enumerate(all_patients_data, 1):
                patient = patient_data.get('patient', {})
                analyses = patient_data.get('analyses', {})
                doctor = patient_data.get('matched_doctor', {})
                
                grok = analyses.get('grok', {})
                o4mini = analyses.get('o4mini', {})
                
                # Patient header
                patient_name = patient.get('name', 'N/A')
                age = patient.get('age', 'N/A')
                gender = patient.get('gender', 'N/A')
                
                header_text = f"<b>{idx}. {patient_name}</b> ({age}y, {gender})"
                elements.append(
                    Paragraph(header_text, self.styles['SubsectionHeading'])
                )
                
                # Quick info
                urgency = grok.get('urgency_score', 'N/A')
                specialty = o4mini.get('final_specialty', 'N/A')
                priority = o4mini.get('consultation_priority', 'N/A')
                doctor_name = (
                    doctor.get('name', 'Emergency - No match')
                    if doctor else 'Emergency'
                )
                
                quick_info_text = (
                    f"<b>Urgency:</b> {urgency}/100 | "
                    f"<b>Specialty:</b> {specialty} | "
                    f"<b>Priority:</b> {priority}<br/>"
                    f"<b>Doctor:</b> {doctor_name}"
                )
                elements.append(
                    Paragraph(quick_info_text, self.styles['CustomBody'])
                )
                
                elements.append(Spacer(1, 0.2*inch))
                
                # Page break after every 2 patients
                if idx % 2 == 0 and idx < len(all_patients_data):
                    elements.append(PageBreak())
            
            # Footer
            elements.append(Spacer(1, 0.2*inch))
            footer_text = (
                f"<i>Consolidated report generated on {report_date} "
                "by RavenCare Triage System</i>"
            )
            elements.append(Paragraph(footer_text, self.styles['Normal']))
            
            # Build PDF
            doc.build(elements)
            return True
            
        except Exception as e:
            console.print(
                f"[red]✗[/red] Error creating consolidated PDF: {str(e)}"
            )
            return False
    
    def _get_summary_table_style(self) -> TableStyle:
        """Get style for summary tables in consolidated reports"""
        return TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c5aa0')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f0f8ff')),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('TOPPADDING', (0, 1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
        ])
