# RavenCare: Multi-Agent Health Coordination System Built with Composio

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
- Gemini API (Google AI Studio)
- Grok-4-Fast-Reasioning API (Azure)
- OpenAI O4-Mini (Azure)
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

RavenCare requires several API keys for full functionality. Below is a detailed guide on obtaining each key:

#### 1. **Gemini API Key** (Google AI Studio)
```bash
GEMINI_API_KEY=your_gemini_key
```

**How to obtain:**
1. Visit [Google AI Studio](https://aistudio.google.com/apikey)
2. Sign in with your Google account
3. Click **"Get API Key"** or **"Create API Key"**
4. Copy the generated key and paste it in your `.env` file

**Free Tier:** Available with generous quota for testing

---

#### 2. **Grok API** (Azure AI Services)
```bash
GROK_API_KEY=your_grok_key
GROK_ENDPOINT=https://your-endpoint.services.ai.azure.com/openai/v1/
```

**How to obtain:**
1. Create an account at [Azure Portal](https://portal.azure.com)
2. Navigate to **Azure AI Services** or **Azure OpenAI**
3. Click **"Create"** to set up a new resource
4. Once created, go to **"Keys and Endpoint"** in the left sidebar
5. Copy **KEY 1** or **KEY 2** → Use as `GROK_API_KEY`
6. Copy the **Endpoint URL** → Use as `GROK_ENDPOINT`
7. Go to **"Model deployments"** and deploy the Grok model
8. Note the deployment name for `GROK_MODEL_NAME`

**Note:** Requires Azure subscription (free trial available)

---

#### 3. **OpenAI API** (Azure OpenAI Service)
```bash
OPENAI_API_KEY=your_openai_key
OPENAI_ENDPOINT=https://your-endpoint.cognitiveservices.azure.com/
```

**How to obtain:**
1. Go to [Azure Portal](https://portal.azure.com)
2. Search for **"Azure OpenAI"** service
3. Create a new Azure OpenAI resource (may require access approval)
4. Once approved and created, navigate to **"Keys and Endpoint"**
5. Copy **KEY 1** or **KEY 2** → Use as `OPENAI_API_KEY`
6. Copy the **Endpoint URL** → Use as `OPENAI_ENDPOINT`
7. Deploy the **o4-mini** model in **"Model deployments"**

**Important:** Azure OpenAI access may require application approval. Apply at [Azure OpenAI Access Form](https://aka.ms/oai/access)

---

#### 4. **Composio Platform Keys**
```bash
COMPOSIO_API_KEY=your_composio_key
COMPOSIO_USER_ID=your_user_id
```

**How to obtain:**
1. Sign up at [Composio Dashboard](https://app.composio.dev)
2. Navigate to **Settings → API Keys**
3. Copy your **API Key** → Use as `COMPOSIO_API_KEY`
4. Find your **User ID** in the dashboard or profile → Use as `COMPOSIO_USER_ID`

**Free Tier:** Available with sufficient quota for development

---

#### 5. **Composio Connected Accounts** (Optional - Enables Automation)
```bash
COMPOSIO_SHEETS_ACCOUNT_ID=your_sheets_account
COMPOSIO_CALENDAR_ACCOUNT_ID=your_calendar_account
COMPOSIO_GMAIL_ACCOUNT_ID=your_gmail_account
COMPOSIO_DRIVE_ACCOUNT_ID=your_drive_account
```

**How to obtain:**
1. Go to [Composio Apps](https://app.composio.dev/apps)
2. Connect each Google Workspace app:
   - **Google Sheets** (for data dashboards)
   - **Google Calendar** (for appointment scheduling)
   - **Gmail** (for email notifications)
   - **Google Drive** (for PDF report storage)
3. Authorize each app with your Google account
4. After connection, go to **"Connected Accounts"**
5. Copy each **Account ID** and add to `.env`

**Note:** These are optional but highly recommended for full automation features

---

#### 6. **Application Settings**
```bash
ADMIN_EMAIL=admin@your-domain.com
FLASK_SECRET_KEY=random_secret_key
```

- **ADMIN_EMAIL**: Your email to receive system notifications
- **FLASK_SECRET_KEY**: Generate securely with:
  ```powershell
  python -c "import secrets; print(secrets.token_hex(32))"
  ```

---


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

## Security

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



## Future Roadmap

- Custom Finetuned Model learning for outcome prediction
- Multi-language patient support
- EHR system integration
- Mobile application
- Advanced analytics dashboard
- Prescription management

---

## Disclaimer

This system is designed for **educational and demonstration purposes**. It should not replace professional medical judgment. Always consult qualified healthcare professionals for medical advice.


