# RavenCare - AI-Powered Medical Triage System Built with Composio

## Overview

**RavenCare** is a production-ready, AI-powered medical triage system that revolutionizes patient assessment through hybrid AI consensus methodology, intelligent doctor matching, and seamless healthcare workflow automation. Powered by **Composio** for enterprise-grade Google Workspace integrations.

### What Makes RavenCare Special?

- **Ensemble Intelligence Architecture**: Three AI models (Gemini, Grok, OpenAI) collaborate through consensus-based decision making for enhanced diagnostic accuracy
- **Intelligent Matching Algorithm**: 8-factor scoring system with 200+ medical keywords for precise doctor-patient alignment
- **Complete Automation**: End-to-end workflow automation from triage to appointment scheduling via **Composio**
- **Production-Grade**: Secure, modular architecture ready for real-world deployment

---

## Key Features

### Ensemble Intelligence Architecture
- **Gemini 2.5 Pro**: Comprehensive symptom analysis and medical specialty mapping
- **Grok 4 Fast Reasoning**: Urgency scoring (0-100) and risk assessment with red flags
- **OpenAI O4-Mini**: Final clinical evaluation and cross-validation

### Advanced Doctor Matching (8-Factor Algorithm)
- **Sub-Specialization Matching**: 200+ keyword database for precise expertise alignment
- **Urgency-Based Prioritization**: Critical cases mapped to most experienced doctors
- **Age-Appropriate Care**: Pediatric and geriatric specialization awareness
- **Smart Availability**: Slot matching with urgency multipliers
- **Language Preferences**: Multi-language support
- **Quality Ratings**: Doctor ratings and awards consideration
- **Match Transparency**: Full scoring breakdown and explanations

---

## Supported Medical Specialties

**Cardiology** • **Gastroenterology** • **Hepatology** • **Neurology** • **Orthopedics** • **Pediatrics** • **Dermatology** • **Ophthalmology** • **ENT** • **Psychiatry** • **Pulmonology**

Each specialty includes **sub-specialization detection** for precise matching.

---

## Quick Start

### Prerequisites
```
- Python 3.8+
- Internet connection (for AI APIs)
- Google account (for Composio integrations)
- Composio account (free tier available)
```

### Installation

**1. Install Dependencies**
```powershell
pip install -r requirements.txt
```

**2. Configure Environment Variables**
```powershell
# Copy template
copy .env.example .env

# Edit with your API keys
notepad .env
```

**3. Verify Configuration**
```powershell
python -c "from src.config import config; config.print_config_status()"
```

### Running the System

**Web Dashboard (Recommended)**
```powershell
python app.py
```
Open http://localhost:5000 in your browser

**Command Line**
```powershell
python -m src.triage_orchestrator
```

---

## Configuration

### Required API Keys

```bash
# AI Models
GEMINI_API_KEY=your_gemini_key
GROK_API_KEY=your_grok_key
GROK_ENDPOINT=your_grok_endpoint
OPENAI_API_KEY=your_openai_key
OPENAI_ENDPOINT=your_openai_endpoint

# Composio Platform
COMPOSIO_API_KEY=your_composio_key
COMPOSIO_USER_ID=your_user_id

# Composio Connected Accounts (Optional - Enable features)
COMPOSIO_SHEETS_ACCOUNT_ID=your_sheets_account
COMPOSIO_CALENDAR_ACCOUNT_ID=your_calendar_account
COMPOSIO_GMAIL_ACCOUNT_ID=your_gmail_account
COMPOSIO_DRIVE_ACCOUNT_ID=your_drive_account

# Application
ADMIN_EMAIL=admin@your-domain.com
FLASK_SECRET_KEY=random_secret_key
```



## Composio Integrations

**Composio** powers all Google Workspace integrations for seamless automation.

### Gmail Integration
**File**: `src/services/email_service.py`

**Features**:
- HTML-formatted professional emails
- Multi-recipient support (admin, patients, doctors)
- Embedded calendar links
- Delivery tracking

**Composio Actions Used**:
- `GMAIL_SEND_EMAIL`: Send notifications

### Google Sheets Integration
**File**: `src/services/sheets_service.py`

**Features**:
- Real-time online dashboards
- Formatted triage data tables
- Auto-generated reports
- Shareable links

**Composio Actions Used**:
- `GOOGLESHEETS_SHEET_FROM_JSON`: Create sheets from data

### Google Calendar Integration
**File**: `src/services/calendar_service.py`

**Features**:
- Automatic appointment scheduling
- Meeting link generation
- Multi-participant events
- Timezone handling

**Composio Actions Used**:
- `GOOGLECALENDAR_CREATE_EVENT`: Schedule appointments

### Google Drive Integration
**File**: `src/services/email_service.py`

**Features**:
- PDF report storage
- Shareable link generation
- Public access permissions
- Organized folder structure

**Composio Actions Used**:
- `GOOGLEDRIVE_UPLOAD_FILE`: Upload PDFs
- `GOOGLEDRIVE_ADD_FILE_SHARING_PREFERENCE`: Make files shareable

---



## Web Dashboard

**Real-time Streaming Interface**

**Features**:
- Live progress updates via Server-Sent Events (SSE)
- Visual progress bars


**Access**: Run `python app.py` then navigate to http://localhost:5000

---

## Security & Best Practices

- **Environment Variables**: All secrets in `.env`, never in code
- **Type Hints**: Full type annotations throughout
- **Error Handling**: Graceful exception handling
- **Modular Architecture**: Clean separation of concerns
- **Input Validation**: Patient data sanitization
- **SSL/TLS Support**: HTTPS for web interface

---

## Use Cases

- **Hospital Emergency Departments**: Rapid patient prioritization
- **Telemedicine Platforms**: Remote triage and consultation
- **Healthcare Chatbots**: Automated initial assessment
- **Medical Hotlines**: Operator decision support
- **Walk-in Clinics**: Efficient patient routing
- **Healthcare Education**: Teaching triage principles

---


## Disclaimer

This system is designed for **educational and demonstration purposes**. It should not replace professional medical judgment. Always consult qualified healthcare professionals for medical advice.

---

## Future Roadmap

- Custom Finetuned Model learning for outcome prediction
- Multi-language patient support
- EHR system integration
- Mobile application
- Advanced analytics dashboard
- Prescription management

---


