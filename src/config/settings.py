"""
RavenCare Configuration Management
Centralized configuration and environment variable management
"""

import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """
    Configuration class for RavenCare application.
    Manages all environment variables with validation and defaults.
    """
    
    # ==================== AI Model Configuration ====================
    
    # Gemini Configuration
    GEMINI_API_KEY: str = os.getenv('GEMINI_API_KEY', '')
    GEMINI_MODEL: str = os.getenv('GEMINI_MODEL', 'gemini-2.5-pro')
    
    # Grok Configuration
    GROK_ENDPOINT: str = os.getenv('GROK_ENDPOINT', '')
    GROK_API_KEY: str = os.getenv('GROK_API_KEY', '')
    GROK_MODEL_NAME: str = os.getenv('GROK_MODEL_NAME', 'grok-4-fast-reasoning')
    
    # OpenAI Configuration
    OPENAI_ENDPOINT: str = os.getenv('OPENAI_ENDPOINT', '')
    OPENAI_API_KEY: str = os.getenv('OPENAI_API_KEY', '')
    OPENAI_MODEL_NAME: str = os.getenv('OPENAI_MODEL_NAME', 'o4-mini')
    OPENAI_API_VERSION: str = os.getenv('OPENAI_API_VERSION', '2024-12-01-preview')
    
    # ==================== Composio Integration ====================
    
    COMPOSIO_API_KEY: str = os.getenv('COMPOSIO_API_KEY', '')
    COMPOSIO_USER_ID: str = os.getenv('COMPOSIO_USER_ID', '')
    
    # Account IDs for different services
    COMPOSIO_SHEETS_ACCOUNT_ID: str = os.getenv('COMPOSIO_SHEETS_ACCOUNT_ID', '')
    COMPOSIO_CALENDAR_ACCOUNT_ID: str = os.getenv('COMPOSIO_CALENDAR_ACCOUNT_ID', '')
    COMPOSIO_GMAIL_ACCOUNT_ID: str = os.getenv('COMPOSIO_GMAIL_ACCOUNT_ID', '')
    COMPOSIO_DRIVE_ACCOUNT_ID: str = os.getenv('COMPOSIO_DRIVE_ACCOUNT_ID', '')
    COMPOSIO_DRIVE_AUTH_CONFIG: str = os.getenv('COMPOSIO_DRIVE_AUTH_CONFIG', '')
    
    # ==================== Application Configuration ====================
    
    # Admin contact
    ADMIN_EMAIL: str = os.getenv('ADMIN_EMAIL', 'admin@ravencare.com')
    
    # Flask configuration
    FLASK_SECRET_KEY: str = os.getenv('FLASK_SECRET_KEY', 'ravencare-secret-key-2024')
    FLASK_DEBUG: bool = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    FLASK_HOST: str = os.getenv('FLASK_HOST', '0.0.0.0')
    FLASK_PORT: int = int(os.getenv('FLASK_PORT', '5000'))
    
    # SSL/TLS Configuration
    SSL_CERT_PATH: Optional[str] = os.getenv('SSL_CERT_PATH')
    SSL_KEY_PATH: Optional[str] = os.getenv('SSL_KEY_PATH')
    
    # ==================== File Paths ====================
    
    # Base directory (RavenCare folder)
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    # Data directories
    PATIENT_DETAILS_DIR: str = os.path.join(BASE_DIR, 'Patient_Details')
    DOCTOR_DETAILS_DIR: str = os.path.join(BASE_DIR, 'Doctor_Details')
    EMERGENCY_DOCTOR_DIR: str = os.path.join(BASE_DIR, 'Emergency_Doctor_Details')
    
    # Output directories
    PDF_REPORTS_DIR: str = os.path.join(BASE_DIR, 'PDF_Reports_Professional')
    
    # Default patient file
    DEFAULT_PATIENT_FILE: str = os.path.join(PATIENT_DETAILS_DIR, 'patients_information.json')
    
    # ==================== Medical Specialties Configuration ====================
    
    SUPPORTED_SPECIALTIES = [
        'cardiology',
        'dermatology',
        'ent',
        'gastroenterology',
        'hepatology',
        'neurology',
        'ophthalmology',
        'orthpedics',
        'pediatrics',
        'psychiatry',
        'pulmonology'
    ]
    
    # ==================== Validation Methods ====================
    
    @classmethod
    def validate_required_config(cls) -> tuple[bool, list[str]]:
        """
        Validate that all required configuration variables are set.
        
        Returns:
            tuple: (is_valid, list of missing variables)
        """
        required_vars = [
            ('GEMINI_API_KEY', cls.GEMINI_API_KEY),
            ('GROK_ENDPOINT', cls.GROK_ENDPOINT),
            ('GROK_API_KEY', cls.GROK_API_KEY),
            ('OPENAI_ENDPOINT', cls.OPENAI_ENDPOINT),
            ('OPENAI_API_KEY', cls.OPENAI_API_KEY),
            ('COMPOSIO_API_KEY', cls.COMPOSIO_API_KEY),
            ('COMPOSIO_USER_ID', cls.COMPOSIO_USER_ID),
        ]
        
        missing = [var_name for var_name, var_value in required_vars if not var_value]
        
        return len(missing) == 0, missing
    
    @classmethod
    def validate_optional_config(cls) -> dict[str, bool]:
        """
        Check status of optional configuration.
        
        Returns:
            dict: Dictionary of optional feature availability
        """
        return {
            'google_sheets': bool(cls.COMPOSIO_SHEETS_ACCOUNT_ID),
            'google_calendar': bool(cls.COMPOSIO_CALENDAR_ACCOUNT_ID),
            'gmail': bool(cls.COMPOSIO_GMAIL_ACCOUNT_ID),
            'google_drive': bool(cls.COMPOSIO_DRIVE_ACCOUNT_ID),
            'ssl_enabled': bool(cls.SSL_CERT_PATH and cls.SSL_KEY_PATH)
        }
    
    @classmethod
    def print_config_status(cls) -> None:
        """Print configuration status to console"""
        from rich.console import Console
        from rich.table import Table
        
        console = Console()
        
        # Check required config
        is_valid, missing = cls.validate_required_config()
        
        # Create configuration status table
        table = Table(title="RavenCare Configuration Status", show_header=True)
        table.add_column("Component", style="cyan", width=30)
        table.add_column("Status", style="bold", width=15)
        table.add_column("Details", style="dim", width=40)
        
        # Required configurations
        table.add_row("", "", "")
        table.add_row("[bold]REQUIRED CONFIGURATION[/bold]", "", "")
        table.add_row("Gemini API", 
                     "[green]✓ Configured[/green]" if cls.GEMINI_API_KEY else "[red]✗ Missing[/red]",
                     cls.GEMINI_MODEL if cls.GEMINI_API_KEY else "Set GEMINI_API_KEY")
        
        table.add_row("Grok API", 
                     "[green]✓ Configured[/green]" if cls.GROK_API_KEY else "[red]✗ Missing[/red]",
                     cls.GROK_MODEL_NAME if cls.GROK_API_KEY else "Set GROK_API_KEY")
        
        table.add_row("OpenAI API", 
                     "[green]✓ Configured[/green]" if cls.OPENAI_API_KEY else "[red]✗ Missing[/red]",
                     cls.OPENAI_MODEL_NAME if cls.OPENAI_API_KEY else "Set OPENAI_API_KEY")
        
        table.add_row("Composio API", 
                     "[green]✓ Configured[/green]" if cls.COMPOSIO_API_KEY else "[red]✗ Missing[/red]",
                     "Integration Services" if cls.COMPOSIO_API_KEY else "Set COMPOSIO_API_KEY")
        
        # Optional configurations
        optional = cls.validate_optional_config()
        table.add_row("", "", "")
        table.add_row("[bold]OPTIONAL FEATURES[/bold]", "", "")
        
        table.add_row("Google Sheets", 
                     "[green]✓ Enabled[/green]" if optional['google_sheets'] else "[yellow]⚠ Disabled[/yellow]",
                     "Reports integration" if optional['google_sheets'] else "Set COMPOSIO_SHEETS_ACCOUNT_ID")
        
        table.add_row("Google Calendar", 
                     "[green]✓ Enabled[/green]" if optional['google_calendar'] else "[yellow]⚠ Disabled[/yellow]",
                     "Appointment scheduling" if optional['google_calendar'] else "Set COMPOSIO_CALENDAR_ACCOUNT_ID")
        
        table.add_row("Gmail", 
                     "[green]✓ Enabled[/green]" if optional['gmail'] else "[yellow]⚠ Disabled[/yellow]",
                     "Email notifications" if optional['gmail'] else "Set COMPOSIO_GMAIL_ACCOUNT_ID")
        
        table.add_row("Google Drive", 
                     "[green]✓ Enabled[/green]" if optional['google_drive'] else "[yellow]⚠ Disabled[/yellow]",
                     "PDF storage" if optional['google_drive'] else "Set COMPOSIO_DRIVE_ACCOUNT_ID")
        
        table.add_row("SSL/TLS", 
                     "[green]✓ Enabled[/green]" if optional['ssl_enabled'] else "[yellow]⚠ Disabled[/yellow]",
                     "HTTPS encryption" if optional['ssl_enabled'] else "Development mode")
        
        console.print(table)
        
        if not is_valid:
            console.print("\n[bold red]⚠ WARNING: Missing required configuration![/bold red]")
            console.print("[red]Missing variables:[/red]")
            for var in missing:
                console.print(f"  • {var}")
            console.print("\n[yellow]Please check your .env file and ensure all required variables are set.[/yellow]")
            return False
        else:
            console.print("\n[bold green]✓ All required configuration is set![/bold green]")
            return True


# Create a singleton instance
config = Config()


# Convenience exports
__all__ = ['Config', 'config']
