# 📚 RavenCare - Technical Information & Component Guide

## Table of Contents
1. [System Architecture](#system-architecture)
2. [AI Analysis Components](#ai-analysis-components)
3. [Composio Integrations](#composio-integrations)
4. [Doctor Matching Engine](#doctor-matching-engine)
5. [Service Components](#service-components)
6. [Configuration Management](#configuration-management)
7. [Data Flow & Pipeline](#data-flow--pipeline)
8. [API Integration Details](#api-integration-details)
9. [Enhancement History](#enhancement-history)

---

## System Architecture

### Overview
RavenCare follows a **modular, service-oriented architecture** with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────────┐
│                   WEB INTERFACE (Flask)                     │
│                      app.py + templates/                    │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│              ORCHESTRATION LAYER                            │
│            src/triage_orchestrator.py                       │
│   (Coordinates all agents, services, and workflow)          │
└─────┬─────────────┬────────────────┬───────────────────────┘
      │             │                │
┌─────▼──────┐ ┌───▼─────────┐ ┌────▼──────────────┐
│  AI AGENTS │ │  SERVICES   │ │  CONFIGURATION    │
│ src/agents/│ │src/services/│ │   src/config/     │
└────────────┘ └─────────────┘ └───────────────────┘
```

### Design Principles
1. **Separation of Concerns**: Each module has a single, well-defined responsibility
2. **Dependency Injection**: Services are injected, making testing easier
3. **Configuration-Driven**: All settings centralized in `src/config/settings.py`
4. **Error Handling**: Graceful degradation when services are unavailable
5. **Type Safety**: Full type hints throughout the codebase

---

## AI Analysis Components

### 1. Gemini Analyzer (`src/agents/gemini_analyzer.py`)

**Purpose**: Initial comprehensive symptom analysis and specialty detection

**Technology**: Google Gemini 2.5 Pro via `google-generativeai` library

**Key Responsibilities**:
- Parse and understand patient symptoms
- Identify medical conditions
- Map to primary and secondary specialties
- Provide initial clinical reasoning

**Output Structure**:
```python
{
    "specialty": "Cardiology",
    "potential_conditions": ["Coronary Artery Disease", "Angina"],
    "reasoning": "Detailed analysis...",
    "red_flags": ["Chest pain radiating to arm"],
    "recommended_tests": ["ECG", "Troponin levels"],
    "secondary_specialties": ["Internal Medicine"]
}
```

**Configuration Required**:
- `GEMINI_API_KEY`: Google AI Studio API key

**Prompting Strategy**:
- System prompt defines medical expert role
- Includes all 11 supported specialties
- Requests structured JSON output
- Emphasizes urgency indicators

---

### 2. Grok Analyzer (`src/agents/grok_analyzer.py`)

**Purpose**: Urgency scoring and risk assessment

**Technology**: xAI Grok 4 Fast Reasoning via custom endpoint

**Key Responsibilities**:
- Calculate urgency score (0-100 scale)
- Identify red flag symptoms
- Estimate time-to-treatment requirement
- Provide risk stratification

**Urgency Scale**:
```
0-25:   Low urgency (routine care, can wait days)
26-50:  Moderate urgency (same-day appointment)
51-75:  High urgency (urgent care within hours)
76-100: Critical urgency (emergency care immediately)
```

**Output Structure**:
```python
{
    "urgency_score": 85,
    "risk_level": "high",
    "time_to_treatment": "immediate",
    "red_flags": ["Severe chest pain", "Shortness of breath"],
    "reasoning": "Detailed risk analysis..."
}
```

**Configuration Required**:
- `GROK_API_KEY`: xAI API key
- `GROK_ENDPOINT`: Custom endpoint URL

**Unique Features**:
- Fast reasoning model optimized for quick decisions
- Calibrated for medical triage scenarios
- Conservative bias (errs on side of caution)

---

### 3. O4-Mini Evaluator (`src/agents/o4mini_evaluator.py`)

**Purpose**: Final evaluation and cross-validation

**Technology**: OpenAI O4-Mini via custom endpoint

**Key Responsibilities**:
- Cross-validate Gemini and Grok analyses
- Final specialty determination
- Consolidated action plan
- Quality check on AI outputs

**Output Structure**:
```python
{
    "final_specialty": "Cardiology",
    "confidence": 0.95,
    "action_plan": "Immediate referral to cardiologist...",
    "additional_recommendations": ["ECG", "Cardiac enzymes"],
    "notes": "Both models agree on cardiovascular origin..."
}
```

**Configuration Required**:
- `OPENAI_API_KEY`: OpenAI API key
- `OPENAI_ENDPOINT`: Custom endpoint URL

**Validation Logic**:
- Compares outputs from Gemini and Grok
- Resolves conflicts using medical knowledge
- Provides confidence scores
- Flags inconsistencies for human review

---

## Composio Integrations

**Composio** is the backbone of all Google Workspace integrations in RavenCare. It provides unified API access to Gmail, Calendar, Sheets, and Drive.

### Why Composio?

✅ **Unified Authentication**: Single API key for all Google services
✅ **Simplified Integration**: No complex OAuth flows to manage
✅ **Account Management**: Connect multiple Google accounts easily
✅ **Reliable API**: Production-grade reliability and error handling
✅ **Fast Setup**: Minutes instead of hours for integration

### Composio Setup

**Required Environment Variables**:
```bash
COMPOSIO_API_KEY=your_composio_key          # Main API key
COMPOSIO_USER_ID=your_user_id               # Your Composio user ID

# Connected Account IDs (one per Google service)
COMPOSIO_SHEETS_ACCOUNT_ID=account_id_1
COMPOSIO_CALENDAR_ACCOUNT_ID=account_id_2
COMPOSIO_GMAIL_ACCOUNT_ID=account_id_3
COMPOSIO_DRIVE_ACCOUNT_ID=account_id_4
```

**Getting Account IDs**:
1. Sign up at https://composio.dev
2. Connect your Google account(s)
3. Note the account IDs for each service
4. Add to `.env` file

---

### 1. Gmail Integration (`src/services/email_service.py`)

**Composio Actions Used**: `GMAIL_SEND_EMAIL`

**Purpose**: Send automated email notifications to stakeholders

**Features Implemented**:
- HTML email templates with professional styling
- Multi-recipient support (admin, patients, doctors)
- Embedded calendar meeting links
- Inline PDF download links (via Google Drive)
- Delivery status tracking

**Email Types**:

1. **Admin Consolidated Report**
```python
{
    "to": config.ADMIN_EMAIL,
    "subject": "RavenCare Triage Report - [Date]",
    "body": """
        <html>
            <body>
                <h2>Patient Triage Summary</h2>
                <ul>
                    <li>Total Patients: X</li>
                    <li>Critical Cases: Y</li>
                    ...
                </ul>
            </body>
        </html>
    """
}
```

2. **Patient Individual Report**
```python
{
    "to": patient_email,
    "subject": "Your Medical Triage Results",
    "body": """
        <html>
            <body>
                <h2>Hello [Name],</h2>
                <p>Your triage assessment is complete.</p>
                <p>Urgency Level: [Level]</p>
                <p>Matched Doctor: Dr. [Name]</p>
                <a href="[drive_link]">Download Report</a>
                <a href="[calendar_link]">View Appointment</a>
            </body>
        </html>
    """
}
```

3. **Doctor Clinical Report**
```python
{
    "to": doctor_email,
    "subject": "New Patient Assignment - [Name]",
    "body": """
        <html>
            <body>
                <h2>Patient Assignment</h2>
                <p>Patient: [Name], Age: [Age]</p>
                <p>Chief Complaint: [Symptoms]</p>
                <p>Urgency: [Score]/100</p>
                <a href="[drive_link]">Clinical Report</a>
            </body>
        </html>
    """
}
```

**Code Example**:
```python
from composio import Composio

composio = Composio(api_key=config.COMPOSIO_API_KEY)

result = composio.tools.execute(
    "GMAIL_SEND_EMAIL",
    user_id=config.COMPOSIO_USER_ID,
    arguments={
        "to": recipient_email,
        "subject": email_subject,
        "body": html_body
    },
    connected_account_id=config.COMPOSIO_GMAIL_ACCOUNT_ID
)
```

**Error Handling**:
- Graceful degradation if Gmail not configured
- Retry logic for temporary failures
- Detailed error logging

---

### 2. Google Sheets Integration (`src/services/sheets_service.py`)

**Composio Actions Used**: `GOOGLESHEETS_SHEET_FROM_JSON`

**Purpose**: Create online, shareable triage dashboards

**Features Implemented**:
- Auto-formatted spreadsheets with headers
- Color-coded urgency levels
- Sortable and filterable columns
- Shareable public links
- Real-time data updates

**Sheet Structure**:

| Column | Data | Format |
|--------|------|--------|
| Patient Name | String | Plain text |
| Age | Number | Plain number |
| Gender | String | Plain text |
| Urgency Score | Number | Conditional formatting |
| Urgency Level | String | Color-coded |
| Specialty | String | Plain text |
| Matched Doctor | String | Plain text |
| Appointment Time | Datetime | Formatted time |
| Status | String | Status badge |

**Data Transformation**:
```python
def _convert_to_sheet_format(self, triage_results: List[Dict]) -> List[Dict]:
    """Convert triage data to Google Sheets JSON format"""
    
    sheet_data = []
    
    # Header row
    sheet_data.append({
        "Patient Name": "name",
        "Age": "age",
        "Urgency Score": "score",
        "Urgency Level": "level",
        ...
    })
    
    # Data rows
    for record in triage_results:
        sheet_data.append({
            "Patient Name": record['patient']['name'],
            "Age": record['patient']['age'],
            "Urgency Score": record['analyses']['urgency_score'],
            ...
        })
    
    return sheet_data
```

**Code Example**:
```python
result = composio.tools.execute(
    "GOOGLESHEETS_SHEET_FROM_JSON",
    user_id=config.COMPOSIO_USER_ID,
    arguments={
        "title": "RavenCare Triage Report - Oct 21, 2025",
        "sheet_name": "Patient Triage Data",
        "sheet_json": formatted_data
    },
    connected_account_id=config.COMPOSIO_SHEETS_ACCOUNT_ID
)

sheet_url = f"https://docs.google.com/spreadsheets/d/{result['data']['spreadsheetId']}/edit"
```

**Benefits**:
- ✅ No manual Excel exports needed
- ✅ Real-time sharing with medical staff
- ✅ Easy data analysis with Google Sheets tools
- ✅ Mobile access for on-the-go viewing

---

### 3. Google Calendar Integration (`src/services/calendar_service.py`)

**Composio Actions Used**: `GOOGLECALENDAR_CREATE_EVENT`

**Purpose**: Automatic appointment scheduling with meeting links

**Features Implemented**:
- Appointment creation for patient-doctor consultations
- Google Meet link generation
- Email invitations to all participants
- Timezone-aware scheduling
- Automatic reminders

**Event Structure**:
```python
{
    "summary": "Medical Consultation: [Patient] with Dr. [Doctor]",
    "description": """
        Patient: [Name]
        Urgency: [Level]
        Specialty: [Specialty]
        
        Please review the clinical report before the appointment.
    """,
    "start": {
        "dateTime": "2025-10-22T10:00:00",
        "timeZone": "Asia/Kolkata"
    },
    "end": {
        "dateTime": "2025-10-22T10:30:00",
        "timeZone": "Asia/Kolkata"
    },
    "attendees": [
        {"email": patient_email},
        {"email": doctor_email},
        {"email": admin_email}
    ],
    "conferenceData": {
        "createRequest": {
            "requestId": "unique_id",
            "conferenceSolutionKey": {"type": "hangoutsMeet"}
        }
    }
}
```

**Code Example**:
```python
# Parse appointment time
tomorrow = datetime.now() + timedelta(days=1)
hour, minute = map(int, preferred_slot.split(':'))
start_time = tomorrow.replace(hour=hour, minute=minute)
end_time = start_time + timedelta(minutes=30)

result = composio.tools.execute(
    "GOOGLECALENDAR_CREATE_EVENT",
    user_id=config.COMPOSIO_USER_ID,
    arguments={
        "summary": f"Medical Consultation: {patient_name} with Dr. {doctor_name}",
        "description": event_description,
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat(),
        "attendees": [patient_email, doctor_email],
        "conference_data": {"create_request": True}
    },
    connected_account_id=config.COMPOSIO_CALENDAR_ACCOUNT_ID
)

meeting_link = result['data']['hangoutLink']
```

**Smart Scheduling**:
- ✅ Matches patient's preferred time slot
- ✅ Defaults to next available day
- ✅ 30-minute appointment duration
- ✅ Sends email invitations automatically
- ✅ Creates Google Meet links for remote consultations

---

### 4. Google Drive Integration (`src/services/email_service.py`)

**Composio Actions Used**: 
- `GOOGLEDRIVE_UPLOAD_FILE`
- `GOOGLEDRIVE_ADD_FILE_SHARING_PREFERENCE`

**Purpose**: Store PDF reports and generate shareable links

**Features Implemented**:
- PDF upload to Google Drive
- Public sharing link generation
- Organized folder structure
- Automatic permissions management

**Workflow**:

1. **Upload PDF to Drive**
```python
result = composio.tools.execute(
    "GOOGLEDRIVE_UPLOAD_FILE",
    user_id=config.COMPOSIO_USER_ID,
    arguments={
        "file_to_upload": "/path/to/report.pdf",
        "folder_to_upload_to": "root"  # or specific folder ID
    },
    connected_account_id=config.COMPOSIO_DRIVE_ACCOUNT_ID
)

file_id = result['data']['id']
```

2. **Make File Shareable**
```python
composio.tools.execute(
    "GOOGLEDRIVE_ADD_FILE_SHARING_PREFERENCE",
    user_id=config.COMPOSIO_USER_ID,
    arguments={
        "file_id": file_id,
        "role": "reader",
        "type": "anyone"  # Public link
    },
    connected_account_id=config.COMPOSIO_DRIVE_ACCOUNT_ID
)
```

3. **Generate Shareable Link**
```python
drive_link = f"https://drive.google.com/file/d/{file_id}/view"
```

**Integration with Email**:
- PDF links embedded in email notifications
- Recipients can download reports directly
- No email attachment size limits
- Reports remain accessible long-term

---

## Doctor Matching Engine

### Overview
The doctor matching system has evolved from a simple 3-factor algorithm to an advanced **8-factor intelligent matching system** with sub-specialization awareness.

### Evolution Timeline

**Version 1.0** (Basic):
- 3 factors: slot, language, rating
- Max score: 100 points
- No sub-specialty matching

**Version 2.0** (Enhanced):
- 8 factors with weighted scoring
- Max score: 170 points
- Sub-specialty matching with 200+ keywords
- Urgency-aware prioritization
- Age-appropriate care matching

---

### 8-Factor Scoring Algorithm

**File**: `src/services/doctor_matcher.py`

#### Factor Breakdown

**1. Slot Availability (40-60 points)**
```python
# Base: 40 points for exact match
# Bonus: +20 points for critical urgency cases
# Partial: 20 points for alternative slots
# None: 0 points

if doctor_slot == preferred_slot:
    score += 40
    if urgency_score >= 90:  # Critical
        score += 20  # Urgency boost
elif doctor_has_any_slots:
    score += 20  # Alternative available
```

**2. Language Match (25 points)**
```python
# Exact match: 25 points
# No match: 0 points

if preferred_language in doctor.languages_spoken:
    score += 25
```

**3. Doctor Rating (20 points)**
```python
# Scale: 0-5 stars → 0-20 points
# Formula: (rating / 5.0) * 20

score += (doctor.rating / 5.0) * 20
```

**4. Experience (15 points)**
```python
# Capped at 30 years for scoring
# Formula: min(years, 30) / 30 * 15

score += min(doctor.experience_years, 30) / 30 * 15
```

**5. Sub-Specialization Match (30 points)** ⭐ **NEW**
```python
# Strong match: 30 points (exact sub-specialty keyword match)
# Partial match: 15 points (related keywords)
# No match: 0 points

from src.services import AdvancedMatchingFeatures

hint = AdvancedMatchingFeatures.suggest_subspecialty(
    symptoms=patient_symptoms,
    specialty=specialty
)

if hint in doctor.sub_specialization.lower():
    score += 30  # Strong match
elif any(keyword in doctor.sub_specialization.lower() 
         for keyword in related_keywords):
    score += 15  # Partial match
```

**6. Awards & Recognition (10 points)**
```python
# Has awards: 10 points
# No awards: 0 points

if doctor.awards and len(doctor.awards) > 0:
    score += 10
```

**7. Age-Appropriate Care (10 points)** ⭐ **NEW**
```python
# Pediatric patients (0-18)
if patient_age < 18:
    if "pediatric" in doctor.sub_specialization.lower():
        score += 10

# Geriatric patients (65+)
elif patient_age >= 65:
    if doctor.experience_years >= 10:
        score += 5
```

**8. Urgency-Experience Alignment (10 points)** ⭐ **NEW**
```python
# High urgency → Experienced doctors
# Critical (90+): 20+ years experience
# High (70-89): 10+ years experience

if urgency_score >= 90 and doctor.experience_years >= 20:
    score += 10
elif urgency_score >= 70 and doctor.experience_years >= 10:
    score += 10
```

---

### Sub-Specialization Intelligence

**File**: `src/services/advanced_matcher.py`

**Purpose**: Map patient symptoms to specific sub-specialties within a specialty

**Keyword Database**: 200+ medical keywords mapped across 11 specialties

#### Example Mappings

**Cardiology**:
```python
CARDIOLOGY_SUBSPECIALTIES = {
    "interventional_cardiology": [
        "blocked arteries", "angioplasty", "stent",
        "coronary artery disease", "heart attack", "MI",
        "chest pain on exertion", "stable angina"
    ],
    "electrophysiology": [
        "arrhythmia", "irregular heartbeat", "palpitations",
        "atrial fibrillation", "AFib", "heart rhythm",
        "fast heart rate", "tachycardia", "bradycardia"
    ],
    "heart_failure": [
        "shortness of breath", "swelling", "edema",
        "fluid retention", "heart failure", "cardiomyopathy",
        "fatigue", "exercise intolerance"
    ],
    "preventive_cardiology": [
        "high cholesterol", "hypertension", "diabetes",
        "risk assessment", "prevention", "family history"
    ]
}
```

**Neurology**:
```python
NEUROLOGY_SUBSPECIALTIES = {
    "stroke": [
        "stroke", "CVA", "paralysis", "weakness",
        "facial drooping", "slurred speech", "TIA",
        "sudden onset", "numbness on one side"
    ],
    "epilepsy": [
        "seizure", "epilepsy", "convulsions", "fits",
        "loss of consciousness", "twitching", "jerking"
    ],
    "movement_disorders": [
        "tremor", "Parkinson's", "shaking", "stiffness",
        "difficulty walking", "balance problems", "rigidity"
    ],
    "headache": [
        "migraine", "severe headache", "chronic headache",
        "visual disturbance", "aura", "tension headache"
    ],
    "dementia": [
        "memory loss", "confusion", "dementia", "Alzheimer's",
        "cognitive decline", "forgetfulness", "disorientation"
    ]
}
```

**Gastroenterology**:
```python
GASTROENTEROLOGY_SUBSPECIALTIES = {
    "hepatology": [
        "jaundice", "liver disease", "hepatitis", "cirrhosis",
        "fatty liver", "elevated liver enzymes", "ascites"
    ],
    "inflammatory_bowel_disease": [
        "Crohn's", "ulcerative colitis", "IBD", "bloody diarrhea",
        "chronic diarrhea", "abdominal pain", "weight loss"
    ],
    "pancreatic": [
        "pancreatitis", "pancreatic", "upper abdominal pain",
        "radiating to back", "nausea", "vomiting"
    ],
    "motility": [
        "GERD", "acid reflux", "heartburn", "dysphagia",
        "difficulty swallowing", "esophageal", "achalasia"
    ]
}
```

#### Matching Algorithm

```python
def suggest_subspecialty(symptoms: str, specialty: str) -> str:
    """
    Analyze symptoms and suggest specific sub-specialty.
    
    Args:
        symptoms: Patient symptom description
        specialty: Primary medical specialty
    
    Returns:
        Sub-specialty hint or empty string
    """
    symptoms_lower = symptoms.lower()
    
    # Get keyword mapping for specialty
    subspecialty_map = SUBSPECIALTY_KEYWORDS.get(specialty, {})
    
    # Score each sub-specialty by keyword matches
    scores = {}
    for subspecialty, keywords in subspecialty_map.items():
        match_count = sum(
            1 for keyword in keywords 
            if keyword in symptoms_lower
        )
        if match_count > 0:
            scores[subspecialty] = match_count
    
    # Return highest scoring sub-specialty
    if scores:
        best_subspecialty = max(scores, key=scores.get)
        return best_subspecialty
    
    return ""
```

---

### Match Quality Determination

```python
def _determine_match_quality(score: float) -> str:
    """Convert numeric score to quality rating"""
    if score >= 100:
        return "excellent"
    elif score >= 70:
        return "good"
    elif score >= 50:
        return "fair"
    else:
        return "low"
```

### Match Explanation Generation

Every match includes a detailed explanation:

```python
def _generate_match_explanation(doctor: Dict, details: Dict) -> str:
    """Generate human-readable match explanation"""
    
    reasons = [f"Dr. {doctor['name']} was matched because:"]
    
    if details['slot_match'] == 'exact':
        reasons.append("appointment slot matches patient preference")
    
    if details['language_match']:
        reasons.append("speaks patient's preferred language")
    
    if details['sub_spec_match'] == 'strong':
        reasons.append("has specific expertise in patient's condition")
    
    if doctor['experience_years'] >= 15:
        reasons.append(f"highly experienced ({doctor['experience_years']} years)")
    
    if doctor['patient_rating'] >= 4.5:
        reasons.append(f"excellent patient rating ({doctor['patient_rating']}/5.0)")
    
    if doctor.get('awards'):
        reasons.append("recognized with professional awards")
    
    return ", ".join(reasons) + "."
```

---

## Service Components

### 1. PDF Generator (`src/services/pdf_generator.py`)

**Technology**: ReportLab library

**Purpose**: Generate professional PDF reports for patients, doctors, and admin

**Report Types**:

1. **Patient Report**
   - Easy-to-understand language
   - Color-coded urgency indicators
   - Doctor contact information
   - Next steps and instructions
   - Appointment details

2. **Doctor Report**
   - Clinical terminology
   - Full AI analysis details
   - Risk factors and red flags
   - Recommended diagnostic tests
   - Patient history and conditions

3. **Consolidated Report**
   - Executive summary
   - Statistics dashboard
   - All patients in one document
   - Priority breakdown
   - Specialty distribution

**Key Features**:
- Custom styling with colors and fonts
- Tables for structured data
- Bullet points for readability
- Headers and footers with branding
- Page numbers and timestamps

---

### 2. Calendar Service (`src/services/calendar_service.py`)

**See [Composio Integrations - Google Calendar](#3-google-calendar-integration)** section above for detailed information.

---

### 3. Email Service (`src/services/email_service.py`)

**See [Composio Integrations - Gmail](#1-gmail-integration)** section above for detailed information.

---

### 4. Sheets Service (`src/services/sheets_service.py`)

**See [Composio Integrations - Google Sheets](#2-google-sheets-integration)** section above for detailed information.

---

## Configuration Management

### Centralized Config (`src/config/settings.py`)

**Design Pattern**: Singleton configuration class with environment variable loading

**Features**:
- ✅ Environment variable validation
- ✅ Default value handling
- ✅ Type conversion and casting
- ✅ Configuration status reporting
- ✅ Feature availability checking

**Structure**:

```python
class Config:
    """Centralized configuration management"""
    
    # AI Model Configuration
    GEMINI_API_KEY: str = os.getenv('GEMINI_API_KEY', '')
    GROK_API_KEY: str = os.getenv('GROK_API_KEY', '')
    GROK_ENDPOINT: str = os.getenv('GROK_ENDPOINT', '')
    OPENAI_API_KEY: str = os.getenv('OPENAI_API_KEY', '')
    OPENAI_ENDPOINT: str = os.getenv('OPENAI_ENDPOINT', '')
    
    # Composio Configuration
    COMPOSIO_API_KEY: str = os.getenv('COMPOSIO_API_KEY', '')
    COMPOSIO_USER_ID: str = os.getenv('COMPOSIO_USER_ID', '')
    COMPOSIO_SHEETS_ACCOUNT_ID: str = os.getenv('COMPOSIO_SHEETS_ACCOUNT_ID', '')
    COMPOSIO_CALENDAR_ACCOUNT_ID: str = os.getenv('COMPOSIO_CALENDAR_ACCOUNT_ID', '')
    COMPOSIO_GMAIL_ACCOUNT_ID: str = os.getenv('COMPOSIO_GMAIL_ACCOUNT_ID', '')
    COMPOSIO_DRIVE_ACCOUNT_ID: str = os.getenv('COMPOSIO_DRIVE_ACCOUNT_ID', '')
    
    # Application Configuration
    ADMIN_EMAIL: str = os.getenv('ADMIN_EMAIL', 'admin@example.com')
    FLASK_SECRET_KEY: str = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key')
    FLASK_DEBUG: bool = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    @classmethod
    def validate_config(cls) -> Dict[str, bool]:
        """Validate all required configuration"""
        return {
            'ai_models': bool(cls.GEMINI_API_KEY and cls.GROK_API_KEY),
            'composio': bool(cls.COMPOSIO_API_KEY and cls.COMPOSIO_USER_ID),
            'google_sheets': bool(cls.COMPOSIO_SHEETS_ACCOUNT_ID),
            'google_calendar': bool(cls.COMPOSIO_CALENDAR_ACCOUNT_ID),
            'gmail': bool(cls.COMPOSIO_GMAIL_ACCOUNT_ID),
            'google_drive': bool(cls.COMPOSIO_DRIVE_ACCOUNT_ID)
        }
    
    @classmethod
    def print_config_status(cls):
        """Print configuration status"""
        status = cls.validate_config()
        
        print("🔧 Configuration Status:")
        print(f"  AI Models: {'✓' if status['ai_models'] else '✗'}")
        print(f"  Composio: {'✓' if status['composio'] else '✗'}")
        print(f"  Google Sheets: {'✓' if status['google_sheets'] else '✗'}")
        print(f"  Google Calendar: {'✓' if status['google_calendar'] else '✗'}")
        print(f"  Gmail: {'✓' if status['gmail'] else '✗'}")
        print(f"  Google Drive: {'✓' if status['google_drive'] else '✗'}")
```

**Usage**:
```python
from src.config import config

# Access configuration
if config.COMPOSIO_API_KEY:
    # Use Composio features
    pass

# Check feature availability
features = config.validate_config()
if features['google_sheets']:
    # Create Google Sheet
    pass
```

---

## Data Flow & Pipeline

### Complete Triage Workflow

```
┌─────────────────────────────────────────────────────────────┐
│ STEP 1: Patient Data Input                                  │
│ • Load from Patient_Details/patients_information.json       │
│ • Validate required fields                                  │
│ • Parse symptoms and medical history                        │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│ STEP 2: Gemini Analysis (AI Agent 1)                        │
│ • Comprehensive symptom analysis                            │
│ • Medical specialty identification                          │
│ • Condition recognition                                     │
│ • Red flag detection                                        │
│ • Recommended tests                                         │
│                                                             │
│ Output: specialty, conditions, reasoning, red_flags         │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│ STEP 3: Grok Urgency Assessment (AI Agent 2)                │
│ • Calculate urgency score (0-100)                           │
│ • Determine risk level                                      │
│ • Identify critical red flags                               │
│ • Estimate time-to-treatment                                │
│                                                             │
│ Output: urgency_score, risk_level, time_to_treatment        │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│ STEP 4: O4-Mini Final Evaluation (AI Agent 3)               │
│ • Cross-validate previous analyses                          │
│ • Resolve specialty conflicts                               │
│ • Generate consolidated action plan                         │
│ • Provide confidence scores                                 │
│                                                             │
│ Output: final_specialty, confidence, action_plan            │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│ STEP 5: Doctor Matching (Enhanced Algorithm)                │
│ • 8-factor scoring calculation                              │
│ • Sub-specialization detection                              │
│ • Urgency-based prioritization                              │
│ • Age-appropriate matching                                  │
│ • Match quality determination                               │
│                                                             │
│ Output: best_doctor, match_score, match_details             │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│ STEP 6: Report Generation                                   │
│ • JSON summary report                                       │
│ • Patient PDF report (simplified language)                  │
│ • Doctor PDF report (clinical details)                      │
│ • Consolidated admin PDF                                    │
│                                                             │
│ Output: Multiple PDF files + JSON data                      │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│ STEP 7: Composio Integrations (Parallel Execution)          │
│                                                             │
│ ┌─────────────────┐ ┌─────────────────┐ ┌────────────────┐ │
│ │ Google Sheets   │ │ Google Calendar │ │ Google Drive   │ │
│ │ • Create sheet  │ │ • Schedule appt │ │ • Upload PDFs  │ │
│ │ • Format data   │ │ • Add attendees │ │ • Share links  │ │
│ │ • Get URL       │ │ • Create Meet   │ │ • Set perms    │ │
│ └─────────────────┘ └─────────────────┘ └────────────────┘ │
│                                                             │
│ Output: sheet_url, calendar_event, drive_links              │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│ STEP 8: Email Notifications (Composio Gmail)                │
│ • Admin email (consolidated report)                         │
│ • Patient emails (individual reports + links)               │
│ • Doctor emails (clinical summaries)                        │
│                                                             │
│ Output: Email delivery confirmations                        │
└─────────────────────────────────────────────────────────────┘
```

### Data Structures

**Patient Input**:
```json
{
  "name": "John Doe",
  "age": 45,
  "gender": "Male",
  "contact_number": "+91-9876543210",
  "email": "john@example.com",
  "symptoms": "Severe chest pain radiating to left arm, shortness of breath, sweating",
  "pre_existing_conditions": ["Hypertension", "Type 2 Diabetes"],
  "preferred_language": "English",
  "preferred_slot": "10:00"
}
```

**Triage Result** (Internal Structure):
```json
{
  "patient": {
    "name": "John Doe",
    "age": 45,
    "gender": "Male",
    "contact_number": "+91-9876543210",
    "email": "john@example.com"
  },
  "analyses": {
    "gemini": {
      "specialty": "Cardiology",
      "potential_conditions": ["Acute Coronary Syndrome", "Myocardial Infarction"],
      "reasoning": "Symptoms suggest cardiac origin...",
      "red_flags": ["Chest pain radiating to arm", "Diaphoresis"],
      "recommended_tests": ["ECG", "Troponin", "CK-MB"]
    },
    "grok": {
      "urgency_score": 95,
      "risk_level": "critical",
      "time_to_treatment": "immediate",
      "red_flags": ["Possible heart attack"],
      "reasoning": "High-risk cardiac event likely..."
    },
    "o4mini": {
      "final_specialty": "Cardiology",
      "confidence": 0.98,
      "action_plan": "Immediate emergency department referral...",
      "additional_recommendations": ["Aspirin 325mg", "Oxygen therapy"]
    }
  },
  "matched_doctor": {
    "name": "Dr. Suresh Iyer",
    "qualification": "MD, DM (Cardiology)",
    "experience_years": 20,
    "sub_specialization": "Interventional Cardiology, Heart Failure",
    "languages_spoken": ["English", "Hindi", "Tamil"],
    "patient_rating": 4.9,
    "slots": ["09:00", "11:00", "14:00"],
    "contact_email": "dr.iyer@hospital.com",
    "awards": ["Excellence in Interventional Cardiology 2022"],
    "match_score": 145.5,
    "match_quality": "excellent",
    "match_details": {
      "slot_match": "alternative",
      "language_match": true,
      "sub_spec_match": "strong",
      "rating_score": 4.9,
      "experience_years": 20,
      "has_awards": true,
      "age_appropriate": "adult",
      "urgency_experience_match": true
    },
    "match_explanation": "Dr. Suresh Iyer was matched because: speaks patient's preferred language, has specific expertise in patient's condition, highly experienced (20 years), excellent patient rating (4.9/5.0), recognized with professional awards."
  },
  "integrations": {
    "google_sheets_url": "https://docs.google.com/spreadsheets/d/abc123/edit",
    "calendar_event_id": "evt_xyz789",
    "meeting_link": "https://meet.google.com/abc-defg-hij",
    "drive_links": {
      "patient_report": "https://drive.google.com/file/d/file1/view",
      "doctor_report": "https://drive.google.com/file/d/file2/view"
    }
  },
  "timestamp": "2025-10-21T14:30:00Z"
}
```

---

## API Integration Details

### Gemini API

**Library**: `google-generativeai`
**Model**: `gemini-2.5-pro`

**Initialization**:
```python
import google.generativeai as genai

genai.configure(api_key=config.GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.5-pro')
```

**Request Structure**:
```python
response = model.generate_content([
    "System: You are a medical expert...",
    f"Patient Symptoms: {symptoms}",
    f"Medical History: {conditions}",
    "Provide analysis in JSON format..."
])
```

**Rate Limits**: Check Google AI Studio documentation

---

### Grok API

**Protocol**: HTTP REST API
**Model**: `grok-4-fast-reasoning`

**Request Structure**:
```python
import requests

headers = {
    "Authorization": f"Bearer {config.GROK_API_KEY}",
    "Content-Type": "application/json"
}

payload = {
    "model": "grok-4-fast-reasoning",
    "messages": [
        {"role": "system", "content": "You are a medical triage specialist..."},
        {"role": "user", "content": patient_data}
    ],
    "temperature": 0.3
}

response = requests.post(
    config.GROK_ENDPOINT,
    headers=headers,
    json=payload
)
```

---

### OpenAI API

**Library**: `openai`
**Model**: `o4-mini`

**Initialization**:
```python
from openai import OpenAI

client = OpenAI(
    api_key=config.OPENAI_API_KEY,
    base_url=config.OPENAI_ENDPOINT
)
```

**Request Structure**:
```python
response = client.chat.completions.create(
    model="o4-mini",
    messages=[
        {"role": "system", "content": "You are a clinical evaluator..."},
        {"role": "user", "content": analyses_to_evaluate}
    ],
    temperature=0.2
)
```

---

### Composio API

**Library**: `composio-core`
**Authentication**: API Key

**Initialization**:
```python
from composio import Composio

composio = Composio(api_key=config.COMPOSIO_API_KEY)
```

**Action Execution Pattern**:
```python
result = composio.tools.execute(
    action="ACTION_NAME",
    user_id=config.COMPOSIO_USER_ID,
    arguments={
        "param1": "value1",
        "param2": "value2"
    },
    connected_account_id=config.COMPOSIO_ACCOUNT_ID
)

# Check result
if result.get('successful'):
    data = result.get('data', {})
    # Process data
else:
    error = result.get('error', 'Unknown error')
    # Handle error
```

---

## Enhancement History

### Version 1.0 - Basic System
- ✅ 3-factor doctor matching
- ✅ Single AI model analysis
- ✅ Basic PDF reports
- ✅ Command-line interface

### Version 1.5 - Multi-Model AI
- ✅ Gemini + Grok + OpenAI pipeline
- ✅ Urgency scoring system
- ✅ Enhanced PDF reports
- ✅ Basic web dashboard

### Version 2.0 - Enhanced Matching
- ✅ 8-factor scoring algorithm
- ✅ Sub-specialization matching (200+ keywords)
- ✅ Age-appropriate care
- ✅ Urgency-based prioritization
- ✅ Match transparency and explanations

### Version 2.1 - Composio Integration
- ✅ Google Sheets dashboards
- ✅ Google Calendar scheduling
- ✅ Gmail notifications
- ✅ Google Drive storage
- ✅ Complete automation

### Future Enhancements (Planned)
- [ ] Machine learning for outcome prediction
- [ ] Patient feedback integration
- [ ] Real-time doctor availability
- [ ] Geographic optimization
- [ ] Multi-language patient support
- [ ] Mobile app
- [ ] EHR integration

---

## Summary

RavenCare is a **production-grade medical triage system** that combines:

1. **Multi-Model AI**: Three AI models working together for accurate analysis
2. **Intelligent Matching**: 8-factor algorithm with sub-specialization awareness
3. **Complete Automation**: Composio-powered Google Workspace integrations
4. **Professional Output**: PDFs, dashboards, emails, and calendar events
5. **Clean Architecture**: Modular, maintainable, and extensible codebase

**Powered by Composio** for seamless Google Workspace integrations.

---

*Last Updated: October 21, 2025*
*RavenCare v2.1 - Technical Documentation*
