"""
Flask Web Application for RavenCare Medical Triage System
Real-time streaming updates with beautiful minimal dashboard UI
"""

import json
import os
from datetime import datetime
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify, Response, stream_with_context
from rich.console import Console
from rich.panel import Panel
from rich import box
import threading
import queue

# Import from new modular structure
from src.triage_orchestrator import TriageOrchestrator
from src.config import config

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = config.FLASK_SECRET_KEY

# Global queue for streaming updates
update_queue = queue.Queue()

# Rich console for terminal output
console = Console()

# Store triage system instance and results
triage_instance = None
processing_status = {
    'is_running': False,
    'current_patient': 0,
    'total_patients': 0,
    'progress': 0,
    'current_step': 'idle',
    'results': []
}


def stream_update(message, type='info', data=None):
    """Push an update to the streaming queue (for web only, doesn't affect console)"""
    update = {
        'timestamp': datetime.now().isoformat(),
        'message': message,
        'type': type,  # info, success, warning, error, progress
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


def run_triage_background(patient_file):
    """Run triage system in background with streaming updates"""
    global triage_instance, processing_status
    
    try:
        processing_status['is_running'] = True
        processing_status['current_step'] = 'initializing'
        
        # Print beautiful banner to console
        console.print("\n")
        console.print(Panel.fit(
            "[bold white]RavenCare - Advanced Medical Triage System[/bold white]\n"
            "[cyan]AI-Powered Multi-Model Patient Assessment[/cyan]\n"
            "[dim]Gemini 2.5 Pro • Grok 4 Reasoning • OpenAI O4-Mini[/dim]\n"
            "[yellow]🌐 Web Dashboard Active[/yellow]",
            border_style="bright_blue",
            box=box.DOUBLE
        ))
        console.print("\n")
        
        stream_update('🚀 Initializing RavenCare Triage System...', 'info')
        
        # Initialize system using new orchestrator
        triage_instance = TriageOrchestrator()
        stream_update('✓ System initialized successfully', 'success')
        
        # Load patients
        processing_status['current_step'] = 'loading_patients'
        stream_update('📂 Loading patient data...', 'info')
        patients = triage_instance.load_patients(patient_file)
        processing_status['total_patients'] = len(patients)
        stream_update(f'✓ Loaded {len(patients)} patients for triage', 'success', {
            'total_patients': len(patients)
        })
        
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
            
            # Gemini Analysis
            stream_update(f'  🔬 Running Gemini 2.5 Pro analysis for {patient_name}...', 'info')
            console.print("[bold green]Step 1: Gemini 2.5 Pro Analysis[/bold green]")
            with console.status("[bold green]🔬 Analyzing symptoms...") as status:
                gemini_result = triage_instance.gemini.analyze_symptoms(patient)
            console.print(f"[green]✓[/green] Primary Specialty: [bold]{gemini_result.get('primary_specialty', 'N/A')}[/bold]")
            console.print(f"[green]✓[/green] Key Symptoms: {', '.join(gemini_result.get('key_symptoms_identified', [])[:3])}")
            stream_update(f'  ✓ Gemini analysis complete: {gemini_result.get("primary_specialty", "N/A")}', 'success')
            
            # Grok Analysis
            console.print("\n[bold blue]Step 2: Grok 4 Urgency Assessment[/bold blue]")
            stream_update(f'  ⚡ Running Grok 4 urgency assessment for {patient_name}...', 'info')
            with console.status("[bold blue]⚡ Calculating urgency score...") as status:
                grok_result = triage_instance.grok.calculate_urgency(patient, gemini_result)
            urgency_score = grok_result.get('urgency_score', 0)
            console.print(f"[blue]✓[/blue] Urgency Score: [bold]{urgency_score}/100[/bold]")
            console.print(f"[blue]✓[/blue] Risk Level: [bold]{grok_result.get('risk_level', 'N/A')}[/bold]")
            console.print(f"[blue]✓[/blue] Triage Category: [bold]{grok_result.get('triage_category', 'N/A')}[/bold]")
            stream_update(f'  ✓ Urgency score: {urgency_score}/100 - {grok_result.get("risk_level", "N/A")}', 'success')
            
            # O4-Mini Evaluation
            console.print("\n[bold magenta]Step 3: O4-Mini Final Evaluation[/bold magenta]")
            stream_update(f'  🎯 Running O4-Mini final evaluation for {patient_name}...', 'info')
            with console.status("[bold magenta]🎯 Performing final evaluation...") as status:
                o4_result = triage_instance.o4mini.final_evaluation(patient, gemini_result, grok_result)
            console.print(f"[magenta]✓[/magenta] Final Specialty: [bold]{o4_result.get('final_specialty', 'N/A')}[/bold]")
            console.print(f"[magenta]✓[/magenta] Confidence: [bold]{o4_result.get('confidence_level', 'N/A')}[/bold]")
            console.print(f"[magenta]✓[/magenta] Priority: [bold]{o4_result.get('consultation_priority', 'N/A')}[/bold]")
            stream_update(f'  ✓ Final specialty: {o4_result.get("final_specialty", "N/A")}', 'success')
            
            # Doctor Matching
            console.print("\n[bold yellow]Step 4: Enhanced Doctor Matching[/bold yellow]")
            stream_update(f'  👨‍⚕️ Matching doctor for {patient_name}...', 'info')
            with console.status("[bold yellow]👨‍⚕️ Finding best doctor match...") as status:
                # Extract enhanced matching parameters
                potential_conditions = gemini_result.get('potential_conditions', [])
                sub_spec_hint = potential_conditions[0] if potential_conditions else None
                urgency_score = grok_result.get('urgency_score', 50)
                
                doctor = triage_instance.doctor_matcher.find_best_doctor(
                    specialty=o4_result.get('final_specialty', gemini_result.get('primary_specialty')),
                    preferred_slot=patient.get('preferred_slot', '09:00'),
                    patient_language=patient.get('preferred_language', 'English'),
                    urgency_score=urgency_score,
                    patient_age=patient.get('age'),
                    sub_specialization_hint=sub_spec_hint,
                    patient_conditions=patient.get('pre_existing_conditions', [])
                )
            doctor_name = doctor.get('name', 'No match') if doctor else 'Emergency - No specific doctor'
            match_score = doctor.get('match_score', 0) if doctor else 0
            match_quality = doctor.get('match_quality', 'N/A') if doctor else 'N/A'
            
            if doctor:
                console.print(f"[yellow]✓[/yellow] Matched Doctor: [bold]{doctor_name}[/bold]")
                console.print(f"[yellow]✓[/yellow] Match Score: {match_score} | Quality: {match_quality}")
                console.print(f"[yellow]✓[/yellow] Rating: ⭐ {doctor.get('patient_rating', 'N/A')}/5.0")
            else:
                console.print(f"[red]⚠[/red] No specific doctor match - [bold]Emergency referral[/bold]")
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
            triage_instance.results.append(result)
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
        
        # Generate reports
        console.print("\n[bold cyan]{'='*80}[/bold cyan]")
        console.print("[bold white]📊 GENERATING COMPREHENSIVE REPORTS[/bold white]")
        console.print("[bold cyan]{'='*80}[/bold cyan]\n")
        
        processing_status['current_step'] = 'generating_reports'
        stream_update('📊 Generating comprehensive reports...', 'info')
        
        # JSON Report
        stream_update('  📄 Creating JSON report...', 'info')
        report_file = triage_instance.generate_summary_report()
        stream_update(f'  ✓ JSON report saved: {report_file}', 'success')
        
        # Google Sheet
        stream_update('  ☁️ Creating Google Sheet...', 'info')
        sheet_url = triage_instance.sheets_service.create_triage_sheet(triage_instance.results)
        if sheet_url:
            stream_update(f'  ✓ Google Sheet created: {sheet_url}', 'success', {'sheet_url': sheet_url})
        else:
            stream_update('  ⚠️ Google Sheet creation skipped or failed', 'warning')
        
        # Calendar Appointments
        processing_status['current_step'] = 'scheduling_appointments'
        stream_update('📅 Scheduling calendar appointments...', 'info')
        calendar_events = triage_instance.calendar_service.schedule_appointments(triage_instance.results)
        stream_update(f'  ✓ Scheduled {len(calendar_events)} appointments', 'success')
        
        # PDF Generation
        processing_status['current_step'] = 'generating_pdfs'
        stream_update('📄 Generating professional PDF reports...', 'info')
        pdf_count = triage_instance._generate_all_pdfs()
        stream_update(f'  ✓ Generated {pdf_count} PDF reports', 'success')
        
        # Email Notifications
        processing_status['current_step'] = 'sending_emails'
        stream_update('📧 Sending email notifications...', 'info')
        email_count = triage_instance._send_all_emails(sheet_url, calendar_events)
        stream_update(f'  ✓ Sent {email_count} email notifications', 'success')
        
        # Complete
        processing_status['current_step'] = 'complete'
        processing_status['progress'] = 100
        
        console.print("\n[bold cyan]{'='*80}[/bold cyan]")
        console.print(Panel.fit(
            "[bold green]🎉 TRIAGE PROCESS COMPLETED SUCCESSFULLY![/bold green]\n\n"
            f"[white]✅ Total Patients Processed: {len(patients)}[/white]\n"
            f"[white]✅ JSON Report: {report_file}[/white]\n"
            f"[white]✅ Google Sheet: {'Created' if sheet_url else 'Skipped'}[/white]\n"
            f"[white]✅ Calendar Events: {len(calendar_events)} scheduled[/white]\n"
            f"[white]✅ PDF Reports: {pdf_count} generated[/white]\n"
            f"[white]✅ Emails Sent: {email_count}[/white]\n\n"
            "[cyan]🌐 View results on the web dashboard[/cyan]",
            border_style="green",
            box=box.ROUNDED
        ))
        console.print("[bold cyan]{'='*80}[/bold cyan]\n")
        
        stream_update('🎉 Triage process completed successfully!', 'success', {
            'total_patients': len(patients),
            'report_file': report_file,
            'sheet_url': sheet_url,
            'calendar_events': len(calendar_events),
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
    """Start the triage process"""
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
    
    # Get patient file from request or use default from config
    data = request.get_json() or {}
    patient_file = data.get('patient_file', config.DEFAULT_PATIENT_FILE)
    
    # Start background thread
    thread = threading.Thread(target=run_triage_background, args=(patient_file,))
    thread.daemon = True
    thread.start()
    
    return jsonify({'success': True, 'message': 'Triage process started'})


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
                # Get update from queue with timeout
                update = update_queue.get(timeout=1)
                yield f"data: {update}\n\n"
            except queue.Empty:
                # Send heartbeat to keep connection alive
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
    """Stop the triage process (not fully implemented - would need thread management)"""
    return jsonify({
        'success': False,
        'message': 'Stop functionality not implemented - process will complete'
    })


@app.route('/api/patients')
def get_patients():
    """Get all patient information"""
    try:
        patient_file = config.DEFAULT_PATIENT_FILE
        with open(patient_file, 'r', encoding='utf-8') as f:
            patients = json.load(f)
        
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
    """Get all doctor information from all specialties"""
    try:
        doctors = []
        doctor_dir = 'Doctor_Details'
        
        # Get all JSON files in Doctor_Details directory
        for filename in os.listdir(doctor_dir):
            if filename.endswith('.json'):
                filepath = os.path.join(doctor_dir, filename)
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    # Extract doctors from the specialty file structure
                    if 'departments' in data:
                        for dept in data['departments']:
                            specialty = dept.get('specialty', '')
                            for doctor in dept.get('doctors', []):
                                doctor['specialty'] = specialty
                                hospital = data.get('hospital_name', 'Unknown')
                                doctor['hospital'] = hospital
                                doctor['city'] = data.get('city', 'Unknown')
                                doctor['is_emergency'] = False
                                doctors.append(doctor)
        
        # Load emergency doctors (different structure)
        emergency_file = 'Emergency_Doctor_Details/emergency_doctor.json'
        if os.path.exists(emergency_file):
            with open(emergency_file, 'r', encoding='utf-8') as f:
                emergency_data = json.load(f)
                
                # Emergency doctors are in array format, not departments
                if isinstance(emergency_data, list):
                    for item in emergency_data:
                        # Skip hospital info entry (first item)
                        is_doctor = ('name' in item and
                                     item.get('name', '').startswith('Dr.'))
                        if is_doctor:
                            # Parse experience years
                            exp = item.get('experience', '')
                            if isinstance(exp, str):
                                exp_years = exp.replace(' years', '').strip()
                            else:
                                exp_years = 'N/A'
                            
                            # Get city from first item or Unknown
                            city = 'Unknown'
                            if len(emergency_data) > 0:
                                city = emergency_data[0].get('city', 'Unknown')
                            
                            doctor = {
                                'name': item.get('name', 'Unknown'),
                                'specialty': item.get(
                                    'specialization', 'Emergency'
                                ),
                                'experience_years': exp_years,
                                'languages_spoken': item.get(
                                    'languages_spoken', []
                                ),
                                'contact_email': item.get('email', 'N/A'),
                                'contact_number': item.get(
                                    'contact_number', 'N/A'
                                ),
                                'emergency_contact_number': item.get(
                                    'emergency_contact_number', 'N/A'
                                ),
                                'hospital': item.get(
                                    'hospital_affiliation', 'Emergency'
                                ),
                                'availability': item.get(
                                    'availability', 'On Call'
                                ),
                                'city': city,
                                'is_emergency': True,
                                'patient_rating': 'N/A',
                                'qualification': 'MD',
                                'slots': [item.get('availability', 'On Call')]
                            }
                            doctors.append(doctor)
        
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
        # Get patient count
        patient_file = config.DEFAULT_PATIENT_FILE
        total_patients = 0
        if os.path.exists(patient_file):
            with open(patient_file, 'r', encoding='utf-8') as f:
                patients = json.load(f)
                total_patients = len(patients)
        
        # Get doctor count and specialties
        doctors = []
        specialties = set()
        doctor_dir = 'Doctor_Details'
        
        if os.path.exists(doctor_dir):
            for filename in os.listdir(doctor_dir):
                if filename.endswith('.json'):
                    filepath = os.path.join(doctor_dir, filename)
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        if 'departments' in data:
                            for dept in data['departments']:
                                specialty = dept.get('specialty', '')
                                if specialty:
                                    specialties.add(specialty)
                                doctors.extend(dept.get('doctors', []))
        
        # Create specialty list with doctor counts
        specialty_counts = {}
        doctor_dir = 'Doctor_Details'
        if os.path.exists(doctor_dir):
            for filename in os.listdir(doctor_dir):
                if filename.endswith('.json'):
                    filepath = os.path.join(doctor_dir, filename)
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        if 'departments' in data:
                            for dept in data['departments']:
                                specialty = dept.get('specialty', '')
                                if specialty:
                                    if specialty not in specialty_counts:
                                        specialty_counts[specialty] = 0
                                    doctor_count = len(dept.get('doctors', []))
                                    specialty_counts[specialty] += doctor_count
        
        specialty_list = [
            {'name': spec, 'doctors': count}
            for spec, count in sorted(specialty_counts.items())
        ]
        
        return jsonify({
            'success': True,
            'version': '1.0.0',
            'total_patients': total_patients,
            'total_doctors': len(doctors),
            'specialties': len(specialties),
            'specialty_list': specialty_list
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error loading system info: {str(e)}',
            'version': '1.0.0',
            'total_patients': 0,
            'total_doctors': 0,
            'specialties': 0,
            'specialty_list': []
        })


if __name__ == '__main__':
    print("🏥 RavenCare Triage System - Web Interface")
    print("=" * 60)
    
    # Check for SSL certificates
    ssl_cert = config.SSL_CERT_PATH
    ssl_key = config.SSL_KEY_PATH
    
    ssl_exists = (ssl_cert and ssl_key and
                  os.path.exists(ssl_cert) and os.path.exists(ssl_key))
    
    if ssl_exists:
        # Run with SSL/TLS
        print("🔒 Starting secure HTTPS server...")
        https_url = f"https://localhost:{config.FLASK_PORT}"
        print(f"Dashboard will be available at: {https_url}")
        print("=" * 60)
        
        ssl_context = (ssl_cert, ssl_key)
        app.run(
            debug=config.FLASK_DEBUG,
            host=config.FLASK_HOST,
            port=config.FLASK_PORT,
            threaded=True,
            ssl_context=ssl_context
        )
    else:
        # Run without SSL (development only)
        print("⚠️  WARNING: Running in development mode without SSL/TLS")
        print("   For production, configure SSL_CERT_PATH and SSL_KEY_PATH")
        print("Starting Flask server...")
        http_url = f"http://localhost:{config.FLASK_PORT}"
        print(f"Dashboard will be available at: {http_url}")
        print("=" * 60)
        
        app.run(
            debug=config.FLASK_DEBUG,
            host=config.FLASK_HOST,
            port=config.FLASK_PORT,
            threaded=True
        )

