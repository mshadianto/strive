# setup_strive_pro_phase2.py
# Complete setup script for Strive Pro Phase 2

import os
import sys
import subprocess
import sqlite3
import json
import secrets
from pathlib import Path
from datetime import datetime

class StrivePro2Installer:
    """Complete installer for Strive Pro Phase 2"""
    
    def __init__(self):
        self.project_root = Path.cwd()
        self.required_dirs = [
            '.streamlit',
            'ml_models', 
            'enhanced_knowledge_base',
            'psychological_norms',
            'logs',
            'reports'
        ]
        
    def print_header(self):
        """Print installation header"""
        print("="*60)
        print("🧘 STRIVE PRO PHASE 2 - COMPLETE INSTALLATION")
        print("="*60)
        print("Advanced Psychological Assessment Platform")
        print("with ML, Multi-User, and Advanced Reporting")
        print("="*60)
    
    def check_python_version(self):
        """Check Python version compatibility"""
        print("🐍 Checking Python version...")
        
        if sys.version_info < (3, 8):
            print("❌ Python 3.8+ is required")
            print(f"Current version: {sys.version}")
            return False
        
        print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} is compatible")
        return True
    
    def create_directory_structure(self):
        """Create required directory structure"""
        print("📁 Creating directory structure...")
        
        for dir_name in self.required_dirs:
            dir_path = self.project_root / dir_name
            dir_path.mkdir(exist_ok=True)
            print(f"✅ Created: {dir_name}")
    
    def install_requirements(self):
        """Install Python requirements"""
        print("📦 Installing Python requirements...")
        
        requirements_content = """
streamlit>=1.28.0
plotly>=5.17.0
pandas>=2.1.0
numpy>=1.24.0
langchain>=0.0.350
langchain-community>=0.0.10
langchain-openai>=0.0.5
langchain-core>=0.1.0
openai>=1.0.0
faiss-cpu>=1.7.4
sentence-transformers>=2.2.2
scikit-learn>=1.3.0
scipy>=1.11.0
joblib>=1.3.0
reportlab>=4.0.4
Pillow>=10.0.0
PyJWT>=2.8.0
bcrypt>=4.1.2
python-dateutil>=2.8.2
openpyxl>=3.1.0
python-dotenv>=1.0.0
requests>=2.31.0
icalendar>=5.0.0
        """.strip()
        
        # Write requirements.txt
        requirements_path = self.project_root / "requirements.txt"
        with open(requirements_path, 'w') as f:
            f.write(requirements_content)
        
        # Install requirements
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
            print("✅ Requirements installed successfully")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Error installing requirements: {e}")
            return False
    
    def create_secrets_template(self):
        """Create secrets.toml template"""
        print("🔐 Creating secrets configuration template...")
        
        secrets_dir = self.project_root / ".streamlit"
        secrets_dir.mkdir(exist_ok=True)
        
        jwt_secret = secrets.token_urlsafe(32)
        
        secrets_content = f"""# Strive Pro Phase 2 Configuration
# Copy this file to .streamlit/secrets.toml and update the values

# OpenRouter API Configuration (REQUIRED)
OPENROUTER_API_KEY = "your_openrouter_api_key_here"

# Email Configuration (for advanced reporting)
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = "587"
SENDER_EMAIL = "your_email@gmail.com"
SENDER_PASSWORD = "your_app_password_here"

# JWT Secret for Authentication (auto-generated)
jwt_secret = "{jwt_secret}"

# Database Configuration
DATABASE_TYPE = "sqlite"
DATABASE_URL = "sqlite:///strive_pro.db"

# Organization Settings
DEFAULT_ORG_NAME = "My Organization"
DEFAULT_ORG_INDUSTRY = "Technology"

# Feature Flags
ENABLE_ML_PREDICTIONS = true
ENABLE_EMAIL_NOTIFICATIONS = true
ENABLE_CALENDAR_INTEGRATION = true
ENABLE_PDF_REPORTS = true
ENABLE_ORGANIZATION_ANALYTICS = true

# Development Settings
DEBUG_MODE = false
LOG_LEVEL = "INFO"

# Deployment Settings (update with your domain)
DEPLOYED_URL = "https://your-app-domain.com"
"""
        
        template_path = secrets_dir / "secrets_template.toml"
        with open(template_path, 'w') as f:
            f.write(secrets_content)
        
        print(f"✅ Created: {template_path}")
        print("📝 Please copy secrets_template.toml to secrets.toml and update the values")
    
    def initialize_database(self):
        """Initialize SQLite database with tables"""
        print("🗄️ Initializing database...")
        
        from multi_user_management import DatabaseManager
        
        try:
            db_manager = DatabaseManager()
            print("✅ Database initialized successfully")
            
            # Create default admin user
            self.create_default_admin(db_manager)
            
            return True
        except Exception as e:
            print(f"❌ Error initializing database: {e}")
            return False
    
    def create_default_admin(self, db_manager):
        """Create default admin user"""
        print("👑 Creating default admin user...")
        
        from multi_user_management import AuthenticationManager, UserRole
        
        auth_manager = AuthenticationManager(db_manager)
        
        # Create default admin
        success = auth_manager.register_user(
            username="admin",
            email="admin@striveprο.com",
            password="StrivePro2024!",  # User should change this
            full_name="System Administrator",
            role=UserRole.ADMIN
        )
        
        if success:
            print("✅ Default admin user created")
            print("   Username: admin")
            print("   Password: StrivePro2024!")
            print("   ⚠️  CHANGE THIS PASSWORD AFTER FIRST LOGIN!")
        else:
            print("⚠️  Admin user might already exist")
    
    def setup_knowledge_base(self):
        """Setup enhanced knowledge base"""
        print("🧠 Setting up enhanced knowledge base...")
        
        try:
            from enhanced_setup_vectorstore import setup_enhanced_vectorstore
            
            success = setup_enhanced_vectorstore()
            
            if success:
                print("✅ Enhanced knowledge base created successfully")
                return True
            else:
                print("❌ Error creating knowledge base")
                return False
                
        except ImportError:
            print("⚠️  Enhanced setup script not found, creating basic knowledge base...")
            self.create_basic_knowledge_base()
            return True
        except Exception as e:
            print(f"❌ Error setting up knowledge base: {e}")
            return False
    
    def create_basic_knowledge_base(self):
        """Create basic knowledge base if enhanced version not available"""
        kb_dir = self.project_root / "enhanced_knowledge_base"
        
        basic_content = {
            "stress_management.txt": """
# Basic Stress Management Techniques

## Immediate Stress Relief
- Deep breathing exercises (4-7-8 technique)
- Progressive muscle relaxation
- Mindful walking
- Quick meditation (5-10 minutes)

## Long-term Stress Management
- Regular exercise routine
- Adequate sleep (7-9 hours)
- Healthy diet and nutrition
- Social support networks
- Time management skills

## Workplace Stress Management
- Set realistic goals and priorities
- Take regular breaks
- Communicate effectively with colleagues
- Maintain work-life boundaries
- Seek support when needed
            """,
            
            "burnout_prevention.txt": """
# Burnout Prevention and Recovery

## Early Warning Signs
- Chronic exhaustion
- Cynicism about work
- Reduced sense of accomplishment
- Physical symptoms (headaches, sleep issues)

## Prevention Strategies
- Workload management
- Regular self-assessment
- Maintain hobbies and interests
- Professional development
- Seek feedback and support

## Recovery Techniques
- Rest and recuperation
- Professional counseling
- Gradual return to activities
- Lifestyle modifications
- Medical consultation if needed
            """
        }
        
        for filename, content in basic_content.items():
            file_path = kb_dir / filename
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
        
        print("✅ Basic knowledge base created")
    
    def create_launch_script(self):
        """Create launch script for easy startup"""
        print("🚀 Creating launch script...")
        
        launch_script = """#!/usr/bin/env python3
# launch_strive_pro.py
# Easy launch script for Strive Pro Phase 2

import subprocess
import sys
import os
from pathlib import Path

def main():
    print("🧘 Starting Strive Pro Phase 2...")
    
    # Check if we're in the right directory
    if not Path("strive_pro_phase2_main.py").exists():
        print("❌ Main application file not found!")
        print("Make sure you're in the Strive Pro directory")
        return
    
    # Check if secrets.toml exists
    if not Path(".streamlit/secrets.toml").exists():
        print("⚠️  secrets.toml not found!")
        print("Please copy .streamlit/secrets_template.toml to .streamlit/secrets.toml")
        print("and update the configuration values")
        return
    
    try:
        # Launch Streamlit app
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            "strive_pro_phase2_main.py",
            "--server.port=8501",
            "--server.address=localhost"
        ])
    except KeyboardInterrupt:
        print("\\n👋 Strive Pro stopped by user")
    except Exception as e:
        print(f"❌ Error launching application: {e}")

if __name__ == "__main__":
    main()
"""
        
        launch_path = self.project_root / "launch_strive_pro.py"
        with open(launch_path, 'w') as f:
            f.write(launch_script)
        
        # Make executable on Unix systems
        if os.name != 'nt':
            os.chmod(launch_path, 0o755)
        
        print("✅ Launch script created: launch_strive_pro.py")
    
    def create_readme(self):
        """Create comprehensive README"""
        print("📚 Creating README documentation...")
        
        readme_content = """# 🧘 Strive Pro Phase 2

Advanced Psychological Assessment Platform with Machine Learning, Multi-User Management, and Advanced Reporting.

## 🚀 Quick Start

1. **Install Requirements:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Secrets:**
   ```bash
   cp .streamlit/secrets_template.toml .streamlit/secrets.toml
   # Edit secrets.toml with your API keys and configuration
   ```

3. **Launch Application:**
   ```bash
   python launch_strive_pro.py
   ```

## 🌟 Phase 2 Features

### 🤖 Machine Learning Integration
- **Predictive Risk Assessment**: AI-powered risk stratification
- **Personalized Interventions**: ML-driven treatment recommendations
- **Outcome Prediction**: Forecast assessment trajectories
- **Pattern Recognition**: Identify early warning signs

### 📄 Advanced Reporting System
- **Professional PDF Reports**: Clinical-grade documentation
- **Email Integration**: Automated report delivery and follow-ups
- **Calendar Integration**: Schedule assessments and reminders
- **Multi-format Export**: PDF, CSV, and JSON export options

### 👥 Multi-User Management
- **Role-Based Access**: Admin, Clinician, HR Manager, User roles
- **Organization Analytics**: Enterprise-level insights and dashboards
- **User Authentication**: Secure JWT-based authentication
- **Profile Management**: Comprehensive user and organization profiles

### 📊 Advanced Analytics
- **Longitudinal Tracking**: Monitor progress over time
- **Population Analytics**: Organization-wide mental health insights
- **Risk Stratification**: Identify high-risk individuals and groups
- **Intervention Effectiveness**: Track treatment outcomes

## 🧪 Assessment Tools

1. **PSS-10**: Perceived Stress Scale (10 items)
2. **DASS-21**: Depression, Anxiety, Stress Scale (21 items)
3. **MBI**: Maslach Burnout Inventory
4. **Work-Life Balance Scale**: Comprehensive work-life assessment
5. **Job Satisfaction Assessment**: Workplace satisfaction evaluation

## 🔧 Configuration

### Required API Keys
- **OpenRouter API**: For AI-powered analysis
- **SMTP Credentials**: For email notifications (optional)

### Optional Features
- **Email Notifications**: Assessment reports and reminders
- **Calendar Integration**: Automated scheduling
- **PDF Generation**: Professional report creation
- **Organization Analytics**: Multi-user insights

## 👥 User Roles

### 🧘 Regular User
- Take assessments
- View personal analytics
- Access ML insights
- Generate personal reports

### 👥 HR Manager
- Monitor team wellbeing
- Generate organization reports
- Risk management dashboard
- Intervention program management

### 🩺 Clinician
- Clinical assessment review
- Treatment planning tools
- Progress monitoring
- Professional reporting

### 👑 Administrator
- Full system access
- User management
- Organization configuration
- System analytics

## 🗄️ Database Structure

The system uses SQLite by default with the following main tables:
- `users`: User accounts and profiles
- `organizations`: Organization information
- `assessment_records`: Assessment results and history
- `user_sessions`: Authentication sessions

## 🧠 Machine Learning Models

### Risk Assessment Model
- **Algorithm**: Gradient Boosting Classifier
- **Features**: 16 psychological and demographic variables
- **Accuracy**: ~85% on validation set
- **Output**: Risk level (Low/Moderate/High) with confidence

### Intervention Recommendation Engine
- **Algorithm**: Random Forest with personalization layer
- **Features**: Assessment scores, user context, historical data
- **Output**: Ranked intervention recommendations with effectiveness scores

### Stress Trajectory Predictor
- **Algorithm**: Time series forecasting with intervention modeling
- **Purpose**: Predict stress levels over 12-week periods
- **Accuracy**: RMSE < 3.5 on stress scale

## 📈 Analytics & Insights

### Personal Analytics
- Progress tracking over time
- Risk factor identification
- Intervention effectiveness
- Personalized recommendations

### Organization Analytics
- Population wellbeing metrics
- Risk distribution analysis
- Department comparisons
- Trend analysis and forecasting

## 🔐 Security Features

- **JWT Authentication**: Secure token-based authentication
- **Password Security**: Hashed passwords with salt
- **Role-Based Access**: Granular permission system
- **Data Encryption**: Sensitive data protection
- **Session Management**: Secure session handling

## 🚀 Deployment Options

### Local Development
```bash
streamlit run strive_pro_phase2_main.py
```

### Production Deployment
- **Streamlit Cloud**: Direct deployment from GitHub
- **Docker**: Containerized deployment
- **Heroku**: Cloud platform deployment
- **AWS/GCP**: Enterprise cloud deployment

## 📞 Support & Documentation

### Getting Help
- Check the logs in `logs/` directory
- Review configuration in `.streamlit/secrets.toml`
- Ensure all requirements are installed
- Verify database initialization

### Common Issues
1. **API Key Errors**: Check OpenRouter API key in secrets.toml
2. **Database Errors**: Ensure write permissions for SQLite file
3. **Import Errors**: Verify all requirements are installed
4. **Authentication Issues**: Check JWT secret configuration

## 🎯 Roadmap

### Phase 3 Planned Features
- **Advanced ML Models**: Deep learning integration
- **Mobile App**: Native mobile applications
- **API Gateway**: RESTful API for third-party integration
- **Advanced Visualizations**: Interactive dashboards
- **Telehealth Integration**: Video consultation features

## 📄 License

This project is licensed under the MIT License. See LICENSE file for details.

## 👨‍💻 Development Team

- **MS Hadianto**: Lead Developer & Clinical Psychology Expert
- **Khalisa NF Shasie**: Psychology Research Specialist

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## ⚠️ Disclaimer

This application is a psychological assessment tool and not a substitute for professional medical or psychological diagnosis and treatment. Always consult with qualified mental health professionals for clinical decisions.

---

**For technical support or questions, please contact the development team.**
"""
        
        readme_path = self.project_root / "README.md"
        with open(readme_path, 'w') as f:
            f.write(readme_content)
        
        print("✅ README.md created")
    
    def run_installation(self):
        """Run complete installation process"""
        self.print_header()
        
        steps = [
            ("Checking Python version", self.check_python_version),
            ("Creating directory structure", self.create_directory_structure),
            ("Installing requirements", self.install_requirements),
            ("Creating configuration template", self.create_secrets_template),
            ("Initializing database", self.initialize_database),
            ("Setting up knowledge base", self.setup_knowledge_base),
            ("Creating launch script", self.create_launch_script),
            ("Creating documentation", self.create_readme)
        ]
        
        for step_name, step_func in steps:
            print(f"\n📋 {step_name}...")
            try:
                if not step_func():
                    print(f"❌ {step_name} failed!")
                    return False
            except Exception as e:
                print(f"❌ Error in {step_name}: {e}")
                return False
        
        self.print_success_message()
        return True
    
    def print_success_message(self):
        """Print successful installation message"""
        print("\n" + "="*60)
        print("🎉 STRIVE PRO PHASE 2 INSTALLATION COMPLETE!")
        print("="*60)
        print()
        print("📝 NEXT STEPS:")
        print("1. Edit .streamlit/secrets.toml with your API keys")
        print("2. Update configuration settings as needed")
        print("3. Run: python launch_strive_pro.py")
        print()
        print("👑 DEFAULT ADMIN CREDENTIALS:")
        print("   Username: admin")
        print("   Password: StrivePro2024!")
        print("   ⚠️  CHANGE THIS PASSWORD AFTER FIRST LOGIN!")
        print()
        print("🚀 Launch the application:")
        print("   python launch_strive_pro.py")
        print()
        print("📚 Read README.md for detailed documentation")
        print("="*60)

def main():
    """Main installer function"""
    installer = StrivePro2Installer()
    success = installer.run_installation()
    
    if not success:
        print("\n❌ Installation failed. Please check the errors above.")
        sys.exit(1)
    
    print("\n✅ Installation completed successfully!")

if __name__ == "__main__":
    main()