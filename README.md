# 🏥 RavenCare - AI-Powered Medical Triage System

## 🎯 Overview

**RavenCare** is a production-ready, AI-powered medical triage system that revolutionizes patient assessment through multi-model AI analysis, intelligent doctor matching, and seamless healthcare workflow automation. Powered by **Composio** for enterprise-grade Google Workspace integrations.

### What Makes RavenCare Special?

- 🤖 **Multi-AI Analysis**: Three AI models (Gemini, Grok, OpenAI) work together for accurate diagnosis
- 🎯 **Intelligent Matching**: 8-factor algorithm with 200+ medical keywords for precise doctor-patient matching
- 📊 **Complete Automation**: From triage to appointment scheduling, all automated via **Composio**
- 🔒 **Production-Grade**: Secure, modular architecture ready for real-world deployment

---

## ✨ Key Features

### 🤖 Multi-Model AI Analysis Pipeline
- **Gemini 2.5 Pro**: Comprehensive symptom analysis and medical specialty mapping
- **Grok 4 Fast Reasoning**: Urgency scoring (0-100) and risk assessment with red flags
- **OpenAI O4-Mini**: Final clinical evaluation and cross-validation

### 👨‍⚕️ Advanced Doctor Matching (8-Factor Algorithm)
- ✅ **Sub-Specialization Matching**: 200+ keyword database for precise expertise alignment
- ✅ **Urgency-Based Prioritization**: Critical cases → Most experienced doctors
- ✅ **Age-Appropriate Care**: Pediatric & geriatric specialization awareness
- ✅ **Smart Availability**: Slot matching with urgency multipliers
- ✅ **Language Preferences**: Multi-language support
- ✅ **Quality Ratings**: Doctor ratings and awards consideration
- ✅ **Match Transparency**: Full scoring breakdown and explanations

### 🔗 Composio-Powered Integrations
- 📧 **Gmail**: Automated email notifications with HTML templates
- 📊 **Google Sheets**: Real-time online dashboards with triage data
- 📅 **Google Calendar**: Automatic appointment scheduling with meeting links
- ☁️ **Google Drive**: PDF report storage and shareable links

### 🎨 Professional Interfaces
- **Web Dashboard**: Real-time streaming updates with SSE
- **Rich Terminal UI**: Color-coded, beautiful command-line interface
- **PDF Reports**: Professional patient and doctor-facing documents

---

## 📋 Supported Medical Specialties

✅ **Cardiology** • **Gastroenterology** • **Hepatology** • **Neurology** • **Orthopedics** • **Pediatrics** • **Dermatology** • **Ophthalmology** • **ENT** • **Psychiatry** • **Pulmonology**

Each specialty includes **sub-specialization detection** for precise matching.

---

## 🚀 Quick Start

### Prerequisites
```
✓ Python 3.8+
✓ Internet connection (for AI APIs)
✓ Google account (for Composio integrations)
✓ Composio account (free tier available)
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

**🌐 Web Dashboard (Recommended)**
```powershell
python app.py
```
Open http://localhost:5000 in your browser

**⚡ Command Line**
```powershell
python -m src.triage_orchestrator
```

---

## ⚙️ Configuration

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

### Optional Features
Enable by setting Composio account IDs:
- 📊 Google Sheets: `COMPOSIO_SHEETS_ACCOUNT_ID`
- 📅 Google Calendar: `COMPOSIO_CALENDAR_ACCOUNT_ID`
- 📧 Gmail: `COMPOSIO_GMAIL_ACCOUNT_ID`
- ☁️ Google Drive: `COMPOSIO_DRIVE_ACCOUNT_ID`

---

## 📊 How It Works

### Complete Triage Pipeline

```
📝 Patient Intake
    ↓
🔬 Gemini Analysis (Stage 1)
   ├─ Symptom analysis
   ├─ Specialty mapping
   └─ Condition identification
    ↓
⚡ Grok Urgency Scoring (Stage 2)
   ├─ Risk calculation (0-100)
   ├─ Red flag detection
   └─ Time-to-treatment recommendation
    ↓
🎯 O4-Mini Final Evaluation (Stage 3)
   ├─ Cross-validation
   ├─ Final specialty determination
   └─ Action plan generation
    ↓
👨‍⚕️ Intelligent Doctor Matching (Stage 4)
   ├─ 8-factor scoring algorithm
   ├─ Sub-specialization matching
   ├─ Urgency + age-appropriate care
   └─ Match score: 0-170 points
    ↓
📋 Report Generation (Stage 5)
   ├─ JSON summary
   ├─ Professional PDFs
   ├─ Google Sheets (via Composio)
   ├─ Calendar appointments (via Composio)
   └─ Email notifications (via Composio)
```

### Urgency Classification

| Level | Score | Action | Timeline |
|-------|-------|--------|----------|
| 🚨 **Critical** | 76-100 | Emergency care | Immediate |
| ⚠️ **High** | 51-75 | Urgent care | Within hours |
| ℹ️ **Moderate** | 26-50 | Same-day appointment | Within 24h |
| ✅ **Low** | 0-25 | Routine care | Within week |

---

## 🏗️ Project Structure

```
RavenCare/
├── src/                              # Modular source code
│   ├── agents/                       # AI Analysis Agents
│   │   ├── gemini_analyzer.py       # Gemini 2.5 Pro integration
│   │   ├── grok_analyzer.py         # Grok 4 integration
│   │   └── o4mini_evaluator.py      # OpenAI O4-Mini integration
│   ├── services/                     # Business Logic Services
│   │   ├── doctor_matcher.py        # 8-factor matching algorithm
│   │   ├── advanced_matcher.py      # Sub-specialization matching
│   │   ├── pdf_generator.py         # Professional PDF reports
│   │   ├── email_service.py         # 📧 Composio Gmail integration
│   │   ├── calendar_service.py      # 📅 Composio Calendar integration
│   │   └── sheets_service.py        # 📊 Composio Sheets integration
│   ├── config/                       # Configuration Management
│   │   └── settings.py              # Centralized config + validation
│   ├── utils/                        # Utility functions
│   └── triage_orchestrator.py       # Main workflow coordinator
├── templates/                        # Web Interface
│   └── index.html                   # Real-time dashboard (SSE)
├── app.py                            # Flask web application
├── Doctor_Details/                   # Doctor database (JSON)
├── Patient_Details/                  # Patient intake data
├── PDF_Reports_Professional/         # Generated reports
├── requirements.txt                  # Python dependencies
├── README.md                         # This file
└── INFORMATION.md                    # Technical documentation
```

---

## 🎯 Doctor Matching Excellence

### 8-Factor Scoring System (170 Points Max)

| Factor | Points | Description |
|--------|--------|-------------|
| 🕐 Slot Availability | 40 (60*) | Exact slot match + urgency boost |
| 🗣️ Language Match | 25 | Patient communication preference |
| ⭐ Doctor Rating | 20 | Based on patient reviews |
| 🎓 Experience | 15 | Years of practice |
| 🔬 Sub-Specialization | 30 | **NEW**: Expertise match (200+ keywords) |
| 🏆 Awards | 10 | Professional recognition |
| 👶👴 Age-Appropriate | 10 | Pediatric/geriatric specialization |
| ⚡ Urgency-Experience | 10 | High urgency → experienced doctors |

**\*Urgency boost**: Critical cases get priority for immediate slots

### Match Quality Ratings
- ✅ **Excellent** (100-170): Perfect match
- ✅ **Good** (70-99): Strong match
- ⚠️ **Fair** (50-69): Acceptable match
- ❌ **Low** (<50): Limited options

---

## 🔗 Composio Integrations

**Composio** powers all Google Workspace integrations for seamless automation.

### 📧 Gmail Integration
**File**: `src/services/email_service.py`

**Features**:
- HTML-formatted professional emails
- Multi-recipient support (admin, patients, doctors)
- Embedded calendar links
- Delivery tracking

**Composio Actions Used**:
- `GMAIL_SEND_EMAIL`: Send notifications

### 📊 Google Sheets Integration
**File**: `src/services/sheets_service.py`

**Features**:
- Real-time online dashboards
- Formatted triage data tables
- Auto-generated reports
- Shareable links

**Composio Actions Used**:
- `GOOGLESHEETS_SHEET_FROM_JSON`: Create sheets from data

### 📅 Google Calendar Integration
**File**: `src/services/calendar_service.py`

**Features**:
- Automatic appointment scheduling
- Meeting link generation
- Multi-participant events
- Timezone handling

**Composio Actions Used**:
- `GOOGLECALENDAR_CREATE_EVENT`: Schedule appointments

### ☁️ Google Drive Integration
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

## 📄 Professional PDF Reports

### Patient Reports
- ✅ Easy-to-understand medical explanations
- ✅ Clear next steps and instructions
- ✅ Doctor contact information
- ✅ Color-coded urgency indicators

### Doctor Reports
- ✅ Detailed clinical reasoning
- ✅ Full AI analysis from all models
- ✅ Risk factors and red flags
- ✅ Recommended diagnostic tests

### Consolidated Admin Reports
- ✅ Executive summary with statistics
- ✅ Priority distribution breakdown
- ✅ Specialty distribution analysis
- ✅ Quick reference for all patients

---

## 🌐 Web Dashboard

**Real-time Streaming Interface**

**Features**:
- ⚡ Live progress updates via Server-Sent Events (SSE)
- 📊 Visual progress bars
- 🎨 Minimal, professional design
- 📱 Mobile-responsive
- ⚠️ Clear error messaging

**Access**: Run `python app.py` → http://localhost:5000

---

## 🔒 Security & Best Practices

✅ **Environment Variables**: All secrets in `.env`, never in code
✅ **Type Hints**: Full type annotations throughout
✅ **Docstrings**: Comprehensive documentation
✅ **Error Handling**: Graceful exception handling
✅ **Modular Architecture**: Clean separation of concerns
✅ **Input Validation**: Patient data sanitization
✅ **SSL/TLS Support**: HTTPS for web interface

---

## 🎓 Use Cases

- 🏥 **Hospital Emergency Departments**: Rapid patient prioritization
- 💻 **Telemedicine Platforms**: Remote triage and consultation
- 🤖 **Healthcare Chatbots**: Automated initial assessment
- 📞 **Medical Hotlines**: Operator decision support
- 🏪 **Walk-in Clinics**: Efficient patient routing
- 📚 **Healthcare Education**: Teaching triage principles

---

## 🏆 Why RavenCare Wins Hackathons

1. ✅ **Production-Ready Code**: Industry-standard architecture
2. ✅ **Complete Workflow**: End-to-end automation
3. ✅ **Real Integrations**: Working Composio + Google services
4. ✅ **Multi-Model AI**: Robust, validated analysis
5. ✅ **Professional UI**: Both web and terminal interfaces
6. ✅ **Comprehensive Docs**: Easy to understand and extend

---

## 📞 Support & Documentation

- 📖 **Technical Details**: See `INFORMATION.md`
- 🔧 **Configuration**: Review `.env.example`
- 💻 **Code Comments**: Inline documentation throughout

---

## ⚠️ Disclaimer

This system is designed for **educational and demonstration purposes**. It should not replace professional medical judgment. Always consult qualified healthcare professionals for medical advice.

---

## 🎉 Future Roadmap

- [ ] Machine learning for outcome prediction
- [ ] Multi-language patient support
- [ ] EHR system integration
- [ ] Mobile application
- [ ] Wearable device integration
- [ ] Advanced analytics dashboard
- [ ] Prescription management

---

**Built with ❤️ for better healthcare delivery**

*Powered by Composio • Version 2.0 • October 2025*
