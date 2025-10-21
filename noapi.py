"""
Flask Web Application for RavenCare Medical Triage System - SIMULATION MODE
No API calls - all responses are simulated with realistic delays
Real-time streaming updates with beautiful minimal dashboard UI
"""

import json
import os
import time
import random
from datetime import datetime
from flask import Flask, render_template, request, jsonify, Response, stream_with_context
from rich.console import Console
from rich.panel import Panel
from rich import box
import threading
import queue

app = Flask(__name__)
app.config['SECRET_KEY'] = 'simulation-secret-key-dev-only'

# Global queue for streaming updates
update_queue = queue.Queue()

# Rich console for terminal output
console = Console()

# Store triage system instance and results
processing_status = {
    'is_running': False,
    'current_patient': 0,
    'total_patients': 0,
    'progress': 0,
    'current_step': 'idle',
    'results': []
}

# Simulated data for specialties and urgency levels
SPECIALTIES = [
    'Cardiology', 'Dermatology', 'ENT', 'Gastroenterology', 
    'Hepatology', 'Neurology', 'Ophthalmology', 'Orthopedics',
    'Pediatrics', 'Psychiatry', 'Pulmonology'
]

DOCTORS_BY_SPECIALTY = {
    'Cardiology': ['Dr. Arjun Malhotra', 'Dr. Priya Sharma', 'Dr. Rajesh Kumar'],
    'Dermatology': ['Dr. Meera Patel', 'Dr. Sanjay Verma', 'Dr. Kavita Singh'],
    'ENT': ['Dr. Amit Gupta', 'Dr. Sneha Reddy', 'Dr. Rahul Nair'],
    'Gastroenterology': ['Dr. Vikram Joshi', 'Dr. Anita Desai', 'Dr. Suresh Rao'],
    'Hepatology': ['Dr. Ravi Kumar', 'Dr. Pooja Agarwal', 'Dr. Manoj Singh'],
    'Neurology': ['Dr. Deepak Sharma', 'Dr. Shalini Kapoor', 'Dr. Arun Mehta'],
    'Ophthalmology': ['Dr. Rohan Verma', 'Dr. Neha Gupta', 'Dr. Karan Sethi'],
    'Orthopedics': ['Dr. Vinod Kumar', 'Dr. Sunita Rao', 'Dr. Ajay Patel'],
    'Pediatrics': ['Dr. Ritu Sharma', 'Dr. Mohit Jain', 'Dr. Swati Chopra'],
    'Psychiatry': ['Dr. Manish Gupta', 'Dr. Archana Singh', 'Dr. Tarun Malhotra'],
    'Pulmonology': ['Dr. Ashok Kumar', 'Dr. Lata Verma', 'Dr. Nitin Sharma']
}

RISK_LEVELS = ['Low', 'Moderate', 'High', 'Critical']
TRIAGE_CATEGORIES = ['Routine', 'Urgent', 'Very Urgent', 'Emergency']
CONFIDENCE_LEVELS = ['Low', 'Medium', 'High', 'Very High']
CONSULTATION_PRIORITIES = ['Standard', 'Expedited', 'Immediate', 'Emergency']
MATCH_QUALITIES = ['fair', 'good', 'excellent']

def stream_update(message, type='info', data=None):
    """Push an update to the streaming queue"""
    update = {
        'timestamp': datetime.now().isoformat(),
        'message': message,
        'type': type,
        'data': data
    }
    update_queue.put(json.dumps(update) + '\n')
    
    # Also print to terminal console with rich formatting
    if type == 'success':
        console.print(f"[bold green]{message}[/bold green]")
    elif type == 'error':
        console.print(f"[bold red]{message}[/bold red]")
    elif type == 'warning':
        console.print(f"[bold yellow]{message}[/bold yellow]")
    elif type == 'info':
        console.print(f"[cyan]{message}[/cyan]")
    elif type == 'progress':
        console.print(f"[bold magenta]{message}[/bold magenta]")


def simulate_gemini_analysis(patient):
    """Simulate Gemini 2.5 Pro analysis with realistic delay"""
    time.sleep(random.uniform(1.5, 2.5))  # Realistic API delay
    
    specialty = random.choice(SPECIALTIES)
    symptoms = patient.get('symptoms', '').lower()
    
    # Try to intelligently assign specialty based on symptoms keywords
    if 'heart' in symptoms or 'chest' in symptoms or 'cardiac' in symptoms:
        specialty = 'Cardiology'
    elif 'skin' in symptoms or 'rash' in symptoms or 'acne' in symptoms:
        specialty = 'Dermatology'
    elif 'ear' in symptoms or 'nose' in symptoms or 'throat' in symptoms:
        specialty = 'ENT'
    elif 'stomach' in symptoms or 'digestive' in symptoms or 'abdomen' in symptoms:
        specialty = 'Gastroenterology'
    elif 'liver' in symptoms or 'hepatic' in symptoms:
        specialty = 'Hepatology'
    elif 'brain' in symptoms or 'headache' in symptoms or 'neurological' in symptoms:
        specialty = 'Neurology'
    elif 'eye' in symptoms or 'vision' in symptoms or 'sight' in symptoms:
        specialty = 'Ophthalmology'
    elif 'bone' in symptoms or 'joint' in symptoms or 'fracture' in symptoms:
        specialty = 'Orthopedics'
    elif 'child' in symptoms or patient.get('age', 100) < 18:
        specialty = 'Pediatrics'
    elif 'mental' in symptoms or 'anxiety' in symptoms or 'depression' in symptoms:
        specialty = 'Psychiatry'
    elif 'lung' in symptoms or 'breathing' in symptoms or 'respiratory' in symptoms:
        specialty = 'Pulmonology'
    
    return {
        'primary_specialty': specialty,
        'key_symptoms_identified': [
            symptoms.split()[0] if symptoms else 'general malaise',
            symptoms.split()[1] if len(symptoms.split()) > 1 else 'discomfort',
            symptoms.split()[2] if len(symptoms.split()) > 2 else 'pain'
        ],
        'potential_conditions': [
            f"{specialty} condition {i+1}" for i in range(3)
        ],
        'recommended_tests': [
            'Blood test', 'Physical examination', 'Imaging study'
        ]
    }


def simulate_grok_urgency(patient, gemini_result):
    """Simulate Grok 4 urgency assessment with realistic delay"""
    time.sleep(random.uniform(1.5, 2.5))  # Realistic API delay
    
    # Generate urgency based on patient age and symptoms
    age = patient.get('age', 50)
    symptoms = patient.get('symptoms', '').lower()
    
    # Base urgency score
    urgency_score = random.randint(25, 95)
    
    # Adjust based on age
    if age < 5 or age > 70:
        urgency_score += random.randint(5, 15)
    
    # Adjust based on symptom keywords
    critical_keywords = ['severe', 'acute', 'emergency', 'critical', 'intensive']
    if any(keyword in symptoms for keyword in critical_keywords):
        urgency_score += random.randint(10, 20)
    
    # Clamp to 0-100
    urgency_score = min(100, max(0, urgency_score))
    
    # Determine risk level and triage category
    if urgency_score >= 76:
        risk_level = 'Critical'
        triage_category = 'Emergency'
    elif urgency_score >= 51:
        risk_level = 'High'
        triage_category = 'Very Urgent'
    elif urgency_score >= 26:
        risk_level = 'Moderate'
        triage_category = 'Urgent'
    else:
        risk_level = 'Low'
        triage_category = 'Routine'
    
    return {
        'urgency_score': urgency_score,
        'risk_level': risk_level,
        'triage_category': triage_category,
        'reasoning': f"Based on patient age ({age}) and symptom severity, assigned {risk_level} risk."
    }


def simulate_o4mini_evaluation(patient, gemini_result, grok_result):
    """Simulate O4-Mini final evaluation with realistic delay"""
    time.sleep(random.uniform(1.5, 2.5))  # Realistic API delay
    
    urgency = grok_result['urgency_score']
    
    # Determine confidence and priority based on urgency
    if urgency >= 76:
        confidence = 'Very High'
        priority = 'Emergency'
    elif urgency >= 51:
        confidence = 'High'
        priority = 'Immediate'
    elif urgency >= 26:
        confidence = 'Medium'
        priority = 'Expedited'
    else:
        confidence = 'High'
        priority = 'Standard'
    
    return {
        'final_specialty': gemini_result['primary_specialty'],
        'confidence_level': confidence,
        'consultation_priority': priority,
        'summary': f"Patient requires {priority.lower()} attention in {gemini_result['primary_specialty']}.",
        'recommendations': [
            'Schedule consultation as per priority',
            'Review medical history',
            'Prepare necessary documentation'
        ]
    }


def simulate_doctor_matching(specialty, patient, urgency_score):
    """Simulate doctor matching with realistic delay"""
    time.sleep(random.uniform(1.0, 2.0))  # Realistic matching delay
    
    # Check if emergency case
    if urgency_score >= 90:
        return {
            'name': 'Emergency - No specific doctor',
            'specialty': 'Emergency',
            'match_score': 0,
            'match_quality': 'emergency',
            'patient_rating': 'N/A',
            'contact_email': 'emergency@hospital.com',
            'is_emergency': True
        }
    
    # Get doctors for specialty
    doctors = DOCTORS_BY_SPECIALTY.get(specialty, ['Dr. General Practitioner'])
    doctor_name = random.choice(doctors)
    
    # Generate match score (higher for lower urgency, as system has more options)
    base_score = random.uniform(100, 150)
    urgency_penalty = (urgency_score / 100) * 20  # Lower score for higher urgency
    match_score = max(50, base_score - urgency_penalty + random.uniform(-10, 10))
    
    # Determine match quality
    if match_score >= 140:
        match_quality = 'excellent'
    elif match_score >= 100:
        match_quality = 'good'
    else:
        match_quality = 'fair'
    
    return {
        'name': doctor_name,
        'specialty': specialty,
        'match_score': round(match_score, 1),
        'match_quality': match_quality,
        'patient_rating': round(random.uniform(4.0, 5.0), 1),
        'experience_years': random.randint(5, 25),
        'qualification': 'MD, ' + random.choice(['MBBS', 'DNB', 'FRCS']),
        'contact_email': f"{doctor_name.lower().replace(' ', '.')}@hospital.com",
        'is_emergency': False
    }


def run_triage_background(patient_file):
    """Run simulated triage system in background with streaming updates"""
    global processing_status
    
    try:
        processing_status['is_running'] = True
        processing_status['current_step'] = 'initializing'
        
        # Print beautiful banner to console
        console.print("\n")
        console.print(Panel.fit(
            "[bold white]RavenCare - Advanced Medical Triage System[/bold white]\n"
            "[cyan]🔄 SIMULATION MODE - No API Calls[/cyan]\n"
            "[dim]Simulated: Gemini 2.5 Pro • Grok 4 Reasoning • OpenAI O4-Mini[/dim]\n"
            "[yellow]🌐 Web Dashboard Active[/yellow]",
            border_style="bright_blue",
            box=box.DOUBLE
        ))
        console.print("\n")
        
        stream_update('🚀 Initializing RavenCare Triage System (Simulation Mode)...', 'info')
        time.sleep(1)
        
        stream_update('✓ System initialized successfully', 'success')
        
        # Load patients
        processing_status['current_step'] = 'loading_patients'
        stream_update('📂 Loading patient data...', 'info')
        time.sleep(0.5)
        
        try:
            with open(patient_file, 'r', encoding='utf-8') as f:
                patients = json.load(f)
        except Exception as e:
            stream_update(f'⚠️ Could not load patient file, using mock data', 'warning')
            # Generate mock patients
            patients = [
                {
                    'name': f'Patient {i+1}',
                    'age': random.randint(20, 80),
                    'gender': random.choice(['Male', 'Female']),
                    'symptoms': f'Symptom description {i+1}',
                    'contact_number': f'555-{random.randint(1000, 9999)}',
                    'email': f'patient{i+1}@email.com',
                    'preferred_language': random.choice(['English', 'Hindi', 'Telugu']),
                    'preferred_slot': random.choice(['09:00', '10:00', '11:00', '14:00', '15:00']),
                    'mapped_specialty': random.choice(SPECIALTIES),
                    'pre_existing_conditions': []
                }
                for i in range(5)
            ]
        
        processing_status['total_patients'] = len(patients)
        stream_update(f'✓ Loaded {len(patients)} patients for triage', 'success', {
            'total_patients': len(patients)
        })
        
        all_results = []
        
        # Process each patient
        for i, patient in enumerate(patients, 1):
            processing_status['current_patient'] = i
            processing_status['current_step'] = 'processing_patient'
            processing_status['progress'] = int((i / len(patients)) * 100)
            
            patient_name = patient.get('name', f'Patient {i}')
            
            # Console separator
            console.print(f"\n[bold cyan]{'='*80}[/bold cyan]")
            console.print(f"[bold yellow]Processing Patient {i}/{len(patients)}: {patient_name}[/bold yellow]")
            console.print(f"[bold cyan]{'='*80}[/bold cyan]\n")
            
            stream_update(f'👤 Processing patient {i}/{len(patients)}: {patient_name}', 'info', {
                'patient_number': i,
                'patient_name': patient_name,
                'total': len(patients),
                'progress': processing_status['progress']
            })
            
            # Gemini Analysis (Simulated)
            stream_update(f'  🔬 Running Gemini 2.5 Pro analysis for {patient_name}...', 'info')
            console.print("[bold green]Step 1: Gemini 2.5 Pro Analysis (Simulated)[/bold green]")
            with console.status("[bold green]🔬 Analyzing symptoms...") as status:
                gemini_result = simulate_gemini_analysis(patient)
            
            console.print(f"[green]✓[/green] Primary Specialty: [bold]{gemini_result.get('primary_specialty', 'N/A')}[/bold]")
            console.print(f"[green]✓[/green] Key Symptoms: {', '.join(gemini_result.get('key_symptoms_identified', [])[:3])}")
            stream_update(f'  ✓ Gemini analysis complete: {gemini_result.get("primary_specialty", "N/A")}', 'success')
            
            # Grok Analysis (Simulated)
            console.print("\n[bold blue]Step 2: Grok 4 Urgency Assessment (Simulated)[/bold blue]")
            stream_update(f'  ⚡ Running Grok 4 urgency assessment for {patient_name}...', 'info')
            with console.status("[bold blue]⚡ Calculating urgency score...") as status:
                grok_result = simulate_grok_urgency(patient, gemini_result)
            
            urgency_score = grok_result.get('urgency_score', 0)
            console.print(f"[blue]✓[/blue] Urgency Score: [bold]{urgency_score}/100[/bold]")
            console.print(f"[blue]✓[/blue] Risk Level: [bold]{grok_result.get('risk_level', 'N/A')}[/bold]")
            console.print(f"[blue]✓[/blue] Triage Category: [bold]{grok_result.get('triage_category', 'N/A')}[/bold]")
            stream_update(f'  ✓ Urgency score: {urgency_score}/100 - {grok_result.get("risk_level", "N/A")}', 'success')
            
            # O4-Mini Evaluation (Simulated)
            console.print("\n[bold magenta]Step 3: O4-Mini Final Evaluation (Simulated)[/bold magenta]")
            stream_update(f'  🎯 Running O4-Mini final evaluation for {patient_name}...', 'info')
            with console.status("[bold magenta]🎯 Performing final evaluation...") as status:
                o4_result = simulate_o4mini_evaluation(patient, gemini_result, grok_result)
            
            console.print(f"[magenta]✓[/magenta] Final Specialty: [bold]{o4_result.get('final_specialty', 'N/A')}[/bold]")
            console.print(f"[magenta]✓[/magenta] Confidence: [bold]{o4_result.get('confidence_level', 'N/A')}[/bold]")
            console.print(f"[magenta]✓[/magenta] Priority: [bold]{o4_result.get('consultation_priority', 'N/A')}[/bold]")
            stream_update(f'  ✓ Final specialty: {o4_result.get("final_specialty", "N/A")}', 'success')
            
            # Doctor Matching (Simulated)
            console.print("\n[bold yellow]Step 4: Enhanced Doctor Matching (Simulated)[/bold yellow]")
            stream_update(f'  👨‍⚕️ Matching doctor for {patient_name}...', 'info')
            with console.status("[bold yellow]👨‍⚕️ Finding best doctor match...") as status:
                doctor = simulate_doctor_matching(
                    o4_result.get('final_specialty'),
                    patient,
                    urgency_score
                )
            
            doctor_name = doctor.get('name', 'No match')
            match_score = doctor.get('match_score', 0)
            match_quality = doctor.get('match_quality', 'N/A')
            is_emergency = doctor.get('is_emergency', False)
            
            if is_emergency:
                console.print(f"[red]⚠[/red] EMERGENCY CASE - [bold]No specific doctor assigned[/bold]")
                console.print(f"[red]🚨[/red] Immediate emergency protocol activated")
            else:
                console.print(f"[yellow]✓[/yellow] Matched Doctor: [bold]{doctor_name}[/bold]")
                console.print(f"[yellow]✓[/yellow] Match Score: {match_score} | Quality: {match_quality}")
                console.print(f"[yellow]✓[/yellow] Rating: ⭐ {doctor.get('patient_rating', 'N/A')}/5.0")
            
            stream_update(f'  ✓ Matched with: {doctor_name} (Score: {match_score})', 'success')
            
            # Store result
            result = {
                'patient': patient,
                'timestamp': datetime.now().isoformat(),
                'analyses': {
                    'gemini': gemini_result,
                    'grok': grok_result,
                    'o4mini': o4_result
                },
                'matched_doctor': doctor
            }
            all_results.append(result)
            processing_status['results'].append(result)
            
            console.print(f"\n[bold green]✅ Completed triage for {patient_name}[/bold green]\n")
            
            stream_update(f'✅ Completed triage for {patient_name}', 'success', {
                'patient_name': patient_name,
                'specialty': o4_result.get('final_specialty'),
                'urgency': urgency_score,
                'doctor': doctor_name,
                'match_score': match_score,
                'match_quality': match_quality,
                'progress': processing_status['progress']
            })
        
        # Generate reports (Simulated)
        console.print("\n[bold cyan]{'='*80}[/bold cyan]")
        console.print("[bold white]📊 GENERATING COMPREHENSIVE REPORTS (Simulated)[/bold white]")
        console.print("[bold cyan]{'='*80}[/bold cyan]\n")
        
        processing_status['current_step'] = 'generating_reports'
        stream_update('📊 Generating comprehensive reports...', 'info')
        
        # JSON Report
        stream_update('  📄 Creating JSON report...', 'info')
        time.sleep(1)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = f'triage_report_simulated_{timestamp}.json'
        
        try:
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'simulation_mode': True,
                    'timestamp': datetime.now().isoformat(),
                    'total_patients': len(patients),
                    'results': all_results
                }, f, indent=2)
            stream_update(f'  ✓ JSON report saved: {report_file}', 'success')
        except Exception as e:
            stream_update(f'  ⚠️ JSON report save failed: {str(e)}', 'warning')
            report_file = 'report_not_saved'
        
        # Google Sheet (Simulated)
        stream_update('  ☁️ Creating Google Sheet (Simulated)...', 'info')
        time.sleep(1.5)
        sheet_url = f'https://docs.google.com/spreadsheets/d/simulated_{timestamp}'
        stream_update(f'  ✓ Google Sheet created (simulated): {sheet_url}', 'success', {'sheet_url': sheet_url})
        
        # Calendar Appointments (Simulated)
        processing_status['current_step'] = 'scheduling_appointments'
        stream_update('📅 Scheduling calendar appointments (Simulated)...', 'info')
        time.sleep(1)
        calendar_events = len(patients)
        stream_update(f'  ✓ Scheduled {calendar_events} appointments (simulated)', 'success')
        
        # PDF Generation (Simulated)
        processing_status['current_step'] = 'generating_pdfs'
        stream_update('📄 Generating professional PDF reports (Simulated)...', 'info')
        time.sleep(1.5)
        pdf_count = len(patients) * 2  # Patient + Doctor PDFs
        stream_update(f'  ✓ Generated {pdf_count} PDF reports (simulated)', 'success')
        
        # Email Notifications (Simulated)
        processing_status['current_step'] = 'sending_emails'
        stream_update('📧 Sending email notifications (Simulated)...', 'info')
        time.sleep(1)
        email_count = len(patients) * 2
        stream_update(f'  ✓ Sent {email_count} email notifications (simulated)', 'success')
        
        # Complete
        processing_status['current_step'] = 'complete'
        processing_status['progress'] = 100
        
        console.print("\n[bold cyan]{'='*80}[/bold cyan]")
        console.print(Panel.fit(
            "[bold green]🎉 TRIAGE PROCESS COMPLETED SUCCESSFULLY! (Simulation)[/bold green]\n\n"
            f"[white]✅ Total Patients Processed: {len(patients)}[/white]\n"
            f"[white]✅ JSON Report: {report_file}[/white]\n"
            f"[white]✅ Google Sheet: Created (simulated)[/white]\n"
            f"[white]✅ Calendar Events: {calendar_events} scheduled (simulated)[/white]\n"
            f"[white]✅ PDF Reports: {pdf_count} generated (simulated)[/white]\n"
            f"[white]✅ Emails Sent: {email_count} (simulated)[/white]\n\n"
            "[cyan]🌐 View results on the web dashboard[/cyan]\n"
            "[yellow]⚠️ All API calls were simulated - no real services used[/yellow]",
            border_style="green",
            box=box.ROUNDED
        ))
        console.print("[bold cyan]{'='*80}[/bold cyan]\n")
        
        stream_update('🎉 Triage process completed successfully! (Simulation)', 'success', {
            'total_patients': len(patients),
            'report_file': report_file,
            'sheet_url': sheet_url,
            'calendar_events': calendar_events,
            'pdf_count': pdf_count,
            'email_count': email_count
        })
        
    except Exception as e:
        processing_status['current_step'] = 'error'
        stream_update(f'❌ Error: {str(e)}', 'error', {'error': str(e)})
        import traceback
        stream_update(traceback.format_exc(), 'error')
    
    finally:
        processing_status['is_running'] = False


@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html')


@app.route('/start_triage', methods=['POST'])
def start_triage():
    """Start the simulated triage process"""
    global processing_status
    
    if processing_status['is_running']:
        return jsonify({'success': False, 'message': 'Triage already running'})
    
    # Reset status
    processing_status = {
        'is_running': True,
        'current_patient': 0,
        'total_patients': 0,
        'progress': 0,
        'current_step': 'starting',
        'results': []
    }
    
    # Clear queue
    while not update_queue.empty():
        try:
            update_queue.get_nowait()
        except:
            break
    
    # Get patient file from request or use default
    data = request.get_json() or {}
    patient_file = data.get('patient_file', 'Patient_Details/patients_information.json')
    
    # Start background thread
    thread = threading.Thread(target=run_triage_background, args=(patient_file,))
    thread.daemon = True
    thread.start()
    
    return jsonify({'success': True, 'message': 'Triage process started (Simulation Mode)'})


@app.route('/status')
def get_status():
    """Get current processing status"""
    return jsonify(processing_status)


@app.route('/stream')
def stream():
    """Server-Sent Events stream for real-time updates"""
    def event_stream():
        while True:
            try:
                update = update_queue.get(timeout=1)
                yield f"data: {update}\n\n"
            except queue.Empty:
                yield f"data: {json.dumps({'type': 'heartbeat'})}\n\n"
            except Exception as e:
                yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
                break
    
    return Response(stream_with_context(event_stream()), mimetype='text/event-stream')


@app.route('/results')
def get_results():
    """Get all triage results"""
    return jsonify({
        'success': True,
        'results': processing_status['results'],
        'total': len(processing_status['results'])
    })


@app.route('/stop_triage', methods=['POST'])
def stop_triage():
    """Stop the triage process"""
    return jsonify({
        'success': False,
        'message': 'Stop functionality not implemented - process will complete'
    })


@app.route('/api/patients')
def get_patients():
    """Get all patient information"""
    try:
        patient_file = 'Patient_Details/patients_information.json'
        
        if os.path.exists(patient_file):
            with open(patient_file, 'r', encoding='utf-8') as f:
                patients = json.load(f)
        else:
            # Return mock patients if file doesn't exist
            patients = [
                {
                    'name': f'Patient {i+1}',
                    'age': random.randint(20, 80),
                    'gender': random.choice(['Male', 'Female']),
                    'symptoms': f'Sample symptoms for patient {i+1}',
                    'contact_number': f'555-{random.randint(1000, 9999)}',
                    'email': f'patient{i+1}@email.com',
                    'preferred_language': random.choice(['English', 'Hindi', 'Telugu']),
                    'preferred_slot': random.choice(['09:00', '10:00', '11:00', '14:00', '15:00']),
                    'mapped_specialty': random.choice(SPECIALTIES),
                    'pre_existing_conditions': []
                }
                for i in range(5)
            ]
        
        return jsonify({
            'success': True,
            'patients': patients,
            'total': len(patients)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error loading patients: {str(e)}',
            'patients': []
        })


@app.route('/api/doctors')
def get_doctors():
    """Get all doctor information (simulated)"""
    try:
        doctors = []
        
        # Generate simulated doctors for each specialty
        for specialty, doc_names in DOCTORS_BY_SPECIALTY.items():
            for doc_name in doc_names:
                doctor = {
                    'name': doc_name,
                    'specialty': specialty,
                    'qualification': 'MD, ' + random.choice(['MBBS', 'DNB', 'FRCS', 'DM']),
                    'experience_years': random.randint(5, 25),
                    'languages_spoken': random.sample(['English', 'Hindi', 'Telugu', 'Tamil', 'Bengali'], k=random.randint(2, 4)),
                    'patient_rating': round(random.uniform(4.0, 5.0), 1),
                    'contact_email': f"{doc_name.lower().replace(' ', '.')}@hospital.com",
                    'contact_number': f'555-{random.randint(1000, 9999)}',
                    'hospital': random.choice(['Apollo Hospital', 'Fortis Healthcare', 'Max Hospital', 'AIIMS']),
                    'city': random.choice(['Mumbai', 'Delhi', 'Bangalore', 'Chennai', 'Hyderabad']),
                    'is_emergency': False,
                    'slots': random.sample(['09:00', '10:00', '11:00', '12:00', '14:00', '15:00', '16:00', '17:00'], k=4),
                    'sub_specialization': f"{specialty} specialist",
                    'awards': random.sample([
                        'Best Doctor Award 2023',
                        'Excellence in Patient Care',
                        'Medical Innovation Award',
                        'Outstanding Service Award'
                    ], k=random.randint(0, 2))
                }
                doctors.append(doctor)
        
        # Add emergency doctors
        emergency_doctors = [
            {
                'name': 'Dr. Emergency Smith',
                'specialty': 'Emergency Medicine',
                'qualification': 'MD, Emergency Medicine',
                'experience_years': '15',
                'languages_spoken': ['English', 'Hindi', 'Telugu'],
                'patient_rating': 'N/A',
                'contact_email': 'emergency@hospital.com',
                'contact_number': '555-9999',
                'emergency_contact_number': '911',
                'hospital': 'Emergency Medical Center',
                'city': 'All Cities',
                'availability': '24/7 Available',
                'is_emergency': True,
                'slots': ['On Call']
            }
        ]
        doctors.extend(emergency_doctors)
        
        return jsonify({
            'success': True,
            'doctors': doctors,
            'total': len(doctors)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error loading doctors: {str(e)}',
            'doctors': []
        })


@app.route('/api/system-info')
def get_system_info():
    """Get system information and statistics"""
    try:
        # Count simulated data
        total_patients = 0
        patient_file = 'Patient_Details/patients_information.json'
        
        if os.path.exists(patient_file):
            with open(patient_file, 'r', encoding='utf-8') as f:
                patients = json.load(f)
                total_patients = len(patients)
        else:
            total_patients = 5  # Mock data count
        
        # Count simulated doctors
        total_doctors = sum(len(docs) for docs in DOCTORS_BY_SPECIALTY.values()) + 1  # +1 for emergency
        
        # Create specialty list with doctor counts
        specialty_list = [
            {'name': spec, 'doctors': len(docs)}
            for spec, docs in sorted(DOCTORS_BY_SPECIALTY.items())
        ]
        
        return jsonify({
            'success': True,
            'version': '1.0.0-SIMULATION',
            'total_patients': total_patients,
            'total_doctors': total_doctors,
            'specialties': len(SPECIALTIES),
            'specialty_list': specialty_list,
            'simulation_mode': True
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error loading system info: {str(e)}',
            'version': '1.0.0-SIMULATION',
            'total_patients': 0,
            'total_doctors': 0,
            'specialties': 0,
            'specialty_list': [],
            'simulation_mode': True
        })


if __name__ == '__main__':
    print("🏥 RavenCare Triage System - SIMULATION MODE")
    print("=" * 60)
    print("⚠️  NO API CALLS - All responses are simulated")
    print("=" * 60)
    print("Starting Flask server...")
    
    http_url = "http://localhost:5000"
    print(f"Dashboard will be available at: {http_url}")
    print("=" * 60)
    print("\n✨ Features:")
    print("  • Realistic delays (1-2 seconds per analysis)")
    print("  • Simulated Gemini, Grok, and O4-Mini responses")
    print("  • Intelligent specialty matching based on symptoms")
    print("  • Full frontend integration")
    print("  • No external API dependencies\n")
    
    app.run(
        debug=True,
        host='0.0.0.0',
        port=5000,
        threaded=True
    )
