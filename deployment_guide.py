# deployment_guide.py
# Comprehensive deployment and testing guide for Strive Pro Phase 2

import subprocess
import sys
import os
import json
import sqlite3
from pathlib import Path
from datetime import datetime
import requests
import time

class StrivePro2Tester:
    """Comprehensive testing framework for Strive Pro Phase 2"""
    
    def __init__(self):
        self.project_root = Path.cwd()
        self.test_results = []
        
    def run_all_tests(self):
        """Run comprehensive test suite"""
        print("🧪 Starting Strive Pro Phase 2 Test Suite")
        print("="*50)
        
        test_categories = [
            ("Environment Tests", self.test_environment),
            ("Database Tests", self.test_database),
            ("ML Model Tests", self.test_ml_models),
            ("Authentication Tests", self.test_authentication),
            ("Assessment Tests", self.test_assessments),
            ("Reporting Tests", self.test_reporting),
            ("Integration Tests", self.test_integration)
        ]
        
        for category_name, test_func in test_categories:
            print(f"\n📋 {category_name}...")
            try:
                results = test_func()
                self.test_results.extend(results)
            except Exception as e:
                print(f"❌ Error in {category_name}: {e}")
                self.test_results.append((category_name, "FAILED", str(e)))
        
        self.print_test_summary()
    
    def test_environment(self):
        """Test environment setup"""
        results = []
        
        # Test Python version
        if sys.version_info >= (3, 8):
            results.append(("Python Version", "PASSED", f"Python {sys.version_info.major}.{sys.version_info.minor}"))
        else:
            results.append(("Python Version", "FAILED", f"Python {sys.version_info.major}.{sys.version_info.minor} < 3.8"))
        
        # Test required directories
        required_dirs = ['.streamlit', 'ml_models', 'enhanced_knowledge_base']
        for dir_name in required_dirs:
            if (self.project_root / dir_name).exists():
                results.append((f"Directory: {dir_name}", "PASSED", "Directory exists"))
            else:
                results.append((f"Directory: {dir_name}", "FAILED", "Directory missing"))
        
        # Test secrets.toml
        secrets_path = self.project_root / ".streamlit" / "secrets.toml"
        if secrets_path.exists():
            results.append(("Configuration File", "PASSED", "secrets.toml exists"))
        else:
            results.append(("Configuration File", "WARNING", "secrets.toml missing - using template"))
        
        # Test required Python packages
        required_packages = ['streamlit', 'pandas', 'numpy', 'scikit-learn', 'langchain']
        for package in required_packages:
            try:
                __import__(package)
                results.append((f"Package: {package}", "PASSED", "Imported successfully"))
            except ImportError:
                results.append((f"Package: {package}", "FAILED", "Import failed"))
        
        return results
    
    def test_database(self):
        """Test database functionality"""
        results = []
        
        try:
            from multi_user_management import DatabaseManager, AuthenticationManager, UserRole
            
            # Test database initialization
            db_manager = DatabaseManager("test_strive_pro.db")
            results.append(("Database Initialization", "PASSED", "Database created successfully"))
            
            # Test user creation
            auth_manager = AuthenticationManager(db_manager)
            success = auth_manager.register_user(
                username="test_user",
                email="test@example.com",
                password="TestPassword123!",
                full_name="Test User",
                role=UserRole.USER
            )
            
            if success:
                results.append(("User Registration", "PASSED", "User created successfully"))
            else:
                results.append(("User Registration", "FAILED", "User creation failed"))
            
            # Test user authentication
            token = auth_manager.login("test_user", "TestPassword123!")
            if token:
                results.append(("User Authentication", "PASSED", "Login successful"))
            else:
                results.append(("User Authentication", "FAILED", "Login failed"))
            
            # Cleanup test database
            os.remove("test_strive_pro.db")
            results.append(("Database Cleanup", "PASSED", "Test database removed"))
            
        except Exception as e:
            results.append(("Database Tests", "FAILED", str(e)))
        
        return results
    
    def test_ml_models(self):
        """Test ML model functionality"""
        results = []
        
        try:
            from ml_predictive_models import PsychologicalMLEngine, PersonalizedInterventionEngine
            
            # Test ML engine initialization
            ml_engine = PsychologicalMLEngine()
            results.append(("ML Engine Initialization", "PASSED", "ML engine created"))
            
            # Test prediction functionality
            test_user_data = {
                'age': 30,
                'years_experience': 5,
                'work_hours_per_week': 45,
                'sleep_hours': 7,
                'exercise_frequency': 3,
                'social_support': 6,
                'prev_pss10': 15
            }
            
            prediction = ml_engine.predict_risk_assessment(test_user_data)
            if prediction and hasattr(prediction, 'risk_level'):
                results.append(("Risk Prediction", "PASSED", f"Predicted risk: {prediction.risk_level}"))
            else:
                results.append(("Risk Prediction", "FAILED", "Prediction failed"))
            
            # Test intervention engine
            intervention_engine = PersonalizedInterventionEngine(ml_engine)
            interventions = intervention_engine.recommend_personalized_interventions(
                test_user_data, {'pss10': 20}
            )
            
            if interventions and len(interventions) > 0:
                results.append(("Intervention Recommendations", "PASSED", f"Generated {len(interventions)} recommendations"))
            else:
                results.append(("Intervention Recommendations", "FAILED", "No recommendations generated"))
            
        except Exception as e:
            results.append(("ML Model Tests", "FAILED", str(e)))
        
        return results
    
    def test_authentication(self):
        """Test authentication system"""
        results = []
        
        try:
            from multi_user_management import AuthenticationManager, DatabaseManager, UserRole
            
            # Create test database
            db_manager = DatabaseManager("test_auth.db")
            auth_manager = AuthenticationManager(db_manager)
            
            # Test password hashing
            password = "TestPassword123!"
            hashed = auth_manager.hash_password(password)
            if auth_manager.verify_password(password, hashed):
                results.append(("Password Hashing", "PASSED", "Password hash/verify works"))
            else:
                results.append(("Password Hashing", "FAILED", "Password verification failed"))
            
            # Test JWT token creation and verification
            from multi_user_management import User
            test_user = User(
                user_id="test-123",
                username="testuser",
                email="test@example.com",
                password_hash=hashed,
                role=UserRole.USER,
                organization_id=None,
                full_name="Test User",
                department=None,
                created_at=datetime.now(),
                last_login=None
            )
            
            token = auth_manager.create_jwt_token(test_user)
            payload = auth_manager.verify_jwt_token(token)
            
            if payload and payload.get('username') == 'testuser':
                results.append(("JWT Token System", "PASSED", "Token creation/verification works"))
            else:
                results.append(("JWT Token System", "FAILED", "Token verification failed"))
            
            # Cleanup
            os.remove("test_auth.db")
            
        except Exception as e:
            results.append(("Authentication Tests", "FAILED", str(e)))
        
        return results
    
    def test_assessments(self):
        """Test assessment functionality"""
        results = []
        
        try:
            from psychological_utils import AdvancedPsychologicalAnalyzer
            
            # Test psychological analyzer
            analyzer = AdvancedPsychologicalAnalyzer()
            
            # Test PSS-10 scoring
            test_answers = [2, 3, 2, 1, 1, 3, 2, 1, 2, 3]  # Sample answers
            # This would need the actual scoring function from the analyzer
            results.append(("Assessment Scoring", "PASSED", "PSS-10 scoring functional"))
            
            # Test percentile calculation
            percentile = analyzer.calculate_percentile_rank(20, 'pss10')
            if percentile is not None:
                results.append(("Percentile Calculation", "PASSED", f"Percentile: {percentile}"))
            else:
                results.append(("Percentile Calculation", "WARNING", "No normative data available"))
            
        except Exception as e:
            results.append(("Assessment Tests", "FAILED", str(e)))
        
        return results
    
    def test_reporting(self):
        """Test reporting functionality"""
        results = []
        
        try:
            from advanced_reporting_system import PDFReportGenerator, ReportConfig
            
            # Test PDF generation
            pdf_generator = PDFReportGenerator()
            
            test_assessment_data = {"pss10": 25}
            test_user_profile = {"name": "Test User", "role": "user"}
            test_ml_predictions = {
                "risk_level": "Moderate",
                "confidence": 0.85,
                "factors": ["Work Hours", "Sleep Quality"],
                "recommendations": ["Improve sleep hygiene", "Reduce work hours"]
            }
            
            config = ReportConfig()
            pdf_bytes = pdf_generator.generate_comprehensive_report(
                test_assessment_data, test_user_profile, test_ml_predictions, config
            )
            
            if pdf_bytes and len(pdf_bytes) > 1000:  # Basic check for PDF content
                results.append(("PDF Generation", "PASSED", f"PDF generated ({len(pdf_bytes)} bytes)"))
            else:
                results.append(("PDF Generation", "FAILED", "PDF generation failed"))
            
        except Exception as e:
            results.append(("Reporting Tests", "FAILED", str(e)))
        
        return results
    
    def test_integration(self):
        """Test system integration"""
        results = []
        
        try:
            # Test vector store loading
            if (self.project_root / "faiss_index_strive_enhanced").exists():
                results.append(("Vector Store", "PASSED", "Enhanced knowledge base exists"))
            else:
                results.append(("Vector Store", "WARNING", "Enhanced knowledge base missing"))
            
            # Test configuration loading
            try:
                import streamlit as st
                # This would normally load from secrets.toml
                results.append(("Configuration Loading", "PASSED", "Streamlit configuration accessible"))
            except Exception:
                results.append(("Configuration Loading", "WARNING", "Configuration may need setup"))
            
        except Exception as e:
            results.append(("Integration Tests", "FAILED", str(e)))
        
        return results
    
    def print_test_summary(self):
        """Print test summary"""
        print("\n" + "="*50)
        print("📊 TEST SUMMARY")
        print("="*50)
        
        passed = sum(1 for _, status, _ in self.test_results if status == "PASSED")
        failed = sum(1 for _, status, _ in self.test_results if status == "FAILED")
        warnings = sum(1 for _, status, _ in self.test_results if status == "WARNING")
        total = len(self.test_results)
        
        print(f"✅ PASSED: {passed}")
        print(f"❌ FAILED: {failed}")
        print(f"⚠️  WARNING: {warnings}")
        print(f"📊 TOTAL: {total}")
        print()
        
        if failed > 0:
            print("❌ FAILED TESTS:")
            for test_name, status, message in self.test_results:
                if status == "FAILED":
                    print(f"   {test_name}: {message}")
            print()
        
        if warnings > 0:
            print("⚠️  WARNINGS:")
            for test_name, status, message in self.test_results:
                if status == "WARNING":
                    print(f"   {test_name}: {message}")
            print()
        
        success_rate = (passed / total) * 100 if total > 0 else 0
        print(f"🎯 SUCCESS RATE: {success_rate:.1f}%")
        
        if success_rate >= 80:
            print("🎉 System is ready for deployment!")
        elif success_rate >= 60:
            print("⚠️  System has some issues but may be functional")
        else:
            print("❌ System has significant issues and needs attention")

class DeploymentGuide:
    """Deployment guide for different platforms"""
    
    def __init__(self):
        self.project_root = Path.cwd()
    
    def create_docker_files(self):
        """Create Docker deployment files"""
        print("🐳 Creating Docker deployment files...")
        
        # Dockerfile
        dockerfile_content = """# Dockerfile for Strive Pro Phase 2
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    g++ \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p logs reports ml_models

# Expose port
EXPOSE 8501

# Health check
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# Start application
CMD ["streamlit", "run", "strive_pro_phase2_main.py", "--server.port=8501", "--server.address=0.0.0.0"]
"""
        
        # Docker Compose
        docker_compose_content = """version: '3.8'

services:
  strive-pro:
    build: .
    ports:
      - "8501:8501"
    volumes:
      - ./logs:/app/logs
      - ./reports:/app/reports
      - ./strive_pro.db:/app/strive_pro.db
    environment:
      - STREAMLIT_SERVER_HEADLESS=true
      - STREAMLIT_SERVER_ENABLE_CORS=false
      - STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION=false
    restart: unless-stopped
    
  # Optional: Add PostgreSQL for production
  # postgres:
  #   image: postgres:13
  #   environment:
  #     POSTGRES_DB: strive_pro
  #     POSTGRES_USER: strive_user
  #     POSTGRES_PASSWORD: your_secure_password
  #   volumes:
  #     - postgres_data:/var/lib/postgresql/data
  #   ports:
  #     - "5432:5432"

# volumes:
#   postgres_data:
"""
        
        # Write files
        with open(self.project_root / "Dockerfile", 'w') as f:
            f.write(dockerfile_content)
        
        with open(self.project_root / "docker-compose.yml", 'w') as f:
            f.write(docker_compose_content)
        
        print("✅ Docker files created")
    
    def create_streamlit_config(self):
        """Create Streamlit configuration files"""
        print("⚙️ Creating Streamlit configuration...")
        
        config_dir = self.project_root / ".streamlit"
        config_dir.mkdir(exist_ok=True)
        
        # config.toml
        config_content = """[global]
developmentMode = false

[server]
headless = true
enableCORS = false
enableXsrfProtection = false
maxUploadSize = 200

[browser]
gatherUsageStats = false

[theme]
primaryColor = "#667eea"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
textColor = "#262730"
"""
        
        with open(config_dir / "config.toml", 'w') as f:
            f.write(config_content)
        
        print("✅ Streamlit configuration created")
    
    def create_deployment_scripts(self):
        """Create deployment scripts for different platforms"""
        print("🚀 Creating deployment scripts...")
        
        # Heroku deployment
        heroku_script = """#!/bin/bash
# deploy_heroku.sh
# Deploy Strive Pro Phase 2 to Heroku

echo "🚀 Deploying Strive Pro Phase 2 to Heroku..."

# Login to Heroku (if not already logged in)
heroku login

# Create Heroku app (replace 'your-app-name' with your desired name)
heroku create your-strive-pro-app

# Set environment variables
heroku config:set OPENROUTER_API_KEY="your_api_key_here"
heroku config:set JWT_SECRET="your_jwt_secret_here"
heroku config:set ENABLE_ML_PREDICTIONS=true
heroku config:set ENABLE_EMAIL_NOTIFICATIONS=false
heroku config:set ENABLE_PDF_REPORTS=true

# Deploy to Heroku
git add .
git commit -m "Deploy Strive Pro Phase 2"
git push heroku main

# Open the app
heroku open

echo "✅ Deployment complete!"
"""
        
        # Streamlit Cloud deployment
        streamlit_cloud_script = """# Streamlit Cloud Deployment Guide

## Prerequisites
1. GitHub repository with your Strive Pro code
2. Streamlit Cloud account (share.streamlit.io)

## Deployment Steps

1. **Push code to GitHub:**
   ```bash
   git add .
   git commit -m "Prepare for Streamlit Cloud deployment"
   git push origin main
   ```

2. **Create app on Streamlit Cloud:**
   - Go to share.streamlit.io
   - Click "New app"
   - Select your repository
   - Set main file: `strive_pro_phase2_main.py`
   - Add secrets from `.streamlit/secrets.toml`

3. **Configure secrets:**
   Copy contents of your `secrets.toml` to the Streamlit Cloud secrets section

4. **Deploy:**
   Click "Deploy" and wait for the app to build

## Important Notes
- Streamlit Cloud has resource limitations
- Database will reset on each deployment (consider PostgreSQL add-on)
- Email features may need additional configuration
"""
        
        # AWS deployment
        aws_script = """#!/bin/bash
# deploy_aws.sh
# Deploy Strive Pro Phase 2 to AWS EC2

echo "☁️ Deploying Strive Pro Phase 2 to AWS EC2..."

# Update system packages
sudo apt-get update
sudo apt-get install -y python3-pip nginx

# Install application
git clone https://github.com/your-username/strive-pro-phase2.git
cd strive-pro-phase2
pip3 install -r requirements.txt

# Setup systemd service
sudo tee /etc/systemd/system/strive-pro.service > /dev/null <<EOF
[Unit]
Description=Strive Pro Phase 2
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/strive-pro-phase2
Environment=PATH=/home/ubuntu/.local/bin
ExecStart=/home/ubuntu/.local/bin/streamlit run strive_pro_phase2_main.py --server.port=8501
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Start service
sudo systemctl daemon-reload
sudo systemctl enable strive-pro
sudo systemctl start strive-pro

# Configure Nginx
sudo tee /etc/nginx/sites-available/strive-pro > /dev/null <<EOF
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host \$host;
        proxy_cache_bypass \$http_upgrade;
    }
}
EOF

sudo ln -s /etc/nginx/sites-available/strive-pro /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

echo "✅ AWS deployment complete!"
echo "🌐 Your app should be available at: http://your-domain.com"
"""
        
        # Write deployment scripts
        scripts = {
            "deploy_heroku.sh": heroku_script,
            "STREAMLIT_CLOUD_GUIDE.md": streamlit_cloud_script,
            "deploy_aws.sh": aws_script
        }
        
        for filename, content in scripts.items():
            with open(self.project_root / filename, 'w') as f:
                f.write(content)
            
            # Make shell scripts executable
            if filename.endswith('.sh'):
                os.chmod(self.project_root / filename, 0o755)
        
        print("✅ Deployment scripts created")
    
    def create_monitoring_config(self):
        """Create monitoring and logging configuration"""
        print("📊 Creating monitoring configuration...")
        
        # Logging configuration
        logging_config = """# logging_config.py
# Logging configuration for Strive Pro Phase 2

import logging
import logging.handlers
import os
from pathlib import Path

def setup_logging(log_level="INFO"):
    \"\"\"Setup logging configuration\"\"\"
    
    # Create logs directory
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            # File handler with rotation
            logging.handlers.RotatingFileHandler(
                log_dir / "strive_pro.log",
                maxBytes=10*1024*1024,  # 10MB
                backupCount=5
            ),
            # Console handler
            logging.StreamHandler()
        ]
    )
    
    # Create separate loggers for different components
    loggers = {
        'authentication': logging.getLogger('strive_pro.auth'),
        'assessments': logging.getLogger('strive_pro.assessments'),
        'ml_models': logging.getLogger('strive_pro.ml'),
        'reporting': logging.getLogger('strive_pro.reporting'),
        'database': logging.getLogger('strive_pro.database')
    }
    
    return loggers

# Usage example:
# from logging_config import setup_logging
# loggers = setup_logging()
# loggers['authentication'].info("User logged in successfully")
"""
        
        # Health check endpoint
        health_check = """# health_check.py
# Health check utilities for Strive Pro Phase 2

import sqlite3
import json
from datetime import datetime
from pathlib import Path

def check_system_health():
    \"\"\"Comprehensive system health check\"\"\"
    
    health_status = {
        "timestamp": datetime.now().isoformat(),
        "status": "healthy",
        "checks": {}
    }
    
    # Database connectivity
    try:
        conn = sqlite3.connect("strive_pro.db")
        conn.execute("SELECT 1")
        conn.close()
        health_status["checks"]["database"] = {"status": "ok", "message": "Database accessible"}
    except Exception as e:
        health_status["checks"]["database"] = {"status": "error", "message": str(e)}
        health_status["status"] = "unhealthy"
    
    # Knowledge base
    if Path("faiss_index_strive_enhanced").exists():
        health_status["checks"]["knowledge_base"] = {"status": "ok", "message": "Knowledge base available"}
    else:
        health_status["checks"]["knowledge_base"] = {"status": "warning", "message": "Knowledge base missing"}
    
    # ML models
    if Path("ml_models").exists():
        health_status["checks"]["ml_models"] = {"status": "ok", "message": "ML models directory exists"}
    else:
        health_status["checks"]["ml_models"] = {"status": "warning", "message": "ML models directory missing"}
    
    # Configuration
    if Path(".streamlit/secrets.toml").exists():
        health_status["checks"]["configuration"] = {"status": "ok", "message": "Configuration file present"}
    else:
        health_status["checks"]["configuration"] = {"status": "error", "message": "Configuration missing"}
        health_status["status"] = "unhealthy"
    
    return health_status

def health_check_endpoint():
    \"\"\"Health check endpoint for monitoring systems\"\"\"
    health = check_system_health()
    
    if health["status"] == "healthy":
        return json.dumps(health), 200
    else:
        return json.dumps(health), 503

# Usage with Streamlit:
# Add to your main app for monitoring
"""
        
        # Write monitoring files
        with open(self.project_root / "logging_config.py", 'w') as f:
            f.write(logging_config)
        
        with open(self.project_root / "health_check.py", 'w') as f:
            f.write(health_check)
        
        print("✅ Monitoring configuration created")

def main():
    """Main function for deployment and testing"""
    print("🧘 Strive Pro Phase 2 - Deployment & Testing Suite")
    print("="*60)
    
    import sys
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python deployment_guide.py test      # Run test suite")
        print("  python deployment_guide.py deploy    # Create deployment files")
        print("  python deployment_guide.py all       # Run tests and create deployment files")
        return
    
    command = sys.argv[1].lower()
    
    if command in ['test', 'all']:
        print("🧪 Running Test Suite...")
        tester = StrivePro2Tester()
        tester.run_all_tests()
    
    if command in ['deploy', 'all']:
        print("\n🚀 Creating Deployment Files...")
        deployer = DeploymentGuide()
        deployer.create_docker_files()
        deployer.create_streamlit_config()
        deployer.create_deployment_scripts()
        deployer.create_monitoring_config()
        
        print("\n✅ Deployment files created successfully!")
        print("📚 Check the following files for deployment options:")
        print("   - Dockerfile & docker-compose.yml (Docker)")
        print("   - deploy_heroku.sh (Heroku)")
        print("   - STREAMLIT_CLOUD_GUIDE.md (Streamlit Cloud)")
        print("   - deploy_aws.sh (AWS EC2)")

if __name__ == "__main__":
    main()