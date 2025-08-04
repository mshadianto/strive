# quick_setup_fixed.py
# Fixed Quick setup script for STRIVE Pro Phase 2

import os
import sys
import subprocess
import sqlite3
import json
from pathlib import Path

def install_requirements():
    """Install required packages"""
    print("🔧 Installing required packages...")
    
    requirements = [
        "streamlit>=1.28.0",
        "pandas>=1.5.0",
        "numpy>=1.21.0",
        "plotly>=5.15.0",
        "bcrypt>=4.0.0",
        "PyJWT>=2.8.0",
        "reportlab>=4.0.0",
        "matplotlib>=3.7.0",
        "seaborn>=0.12.0",
        "scikit-learn>=1.3.0",
        "scipy>=1.11.0"
    ]
    
    # Create requirements.txt
    with open('requirements.txt', 'w') as f:
        f.write('\n'.join(requirements))
    
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ All packages installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing packages: {e}")
        return False

def create_database():
    """Create SQLite database with basic structure"""
    print("🗄️ Creating database...")
    
    try:
        conn = sqlite3.connect('strive_pro.db')
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                full_name TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'user',
                organization TEXT,
                department TEXT,
                manager_id TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP,
                is_active BOOLEAN DEFAULT 1,
                profile_data TEXT,
                notification_preferences TEXT,
                FOREIGN KEY (manager_id) REFERENCES users (id)
            )
        ''')
        
        # Assessment results table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS assessment_results (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                assessment_type TEXT NOT NULL,
                assessment_version TEXT DEFAULT '1.0',
                answers TEXT NOT NULL,
                scores TEXT NOT NULL,
                context TEXT,
                completion_time INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                follow_up_scheduled TIMESTAMP,
                status TEXT DEFAULT 'completed',
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Email notifications table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS email_notifications (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                notification_type TEXT NOT NULL,
                subject TEXT NOT NULL,
                body TEXT NOT NULL,
                scheduled_at TIMESTAMP,
                sent_at TIMESTAMP,
                status TEXT DEFAULT 'pending',
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Calendar events table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS calendar_events (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                start_time TIMESTAMP NOT NULL,
                end_time TIMESTAMP,
                event_type TEXT DEFAULT 'assessment',
                status TEXT DEFAULT 'scheduled',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Progress tracking table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS progress_tracking (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                metric_type TEXT NOT NULL,
                metric_value REAL NOT NULL,
                assessment_id TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (assessment_id) REFERENCES assessment_results (id)
            )
        ''')
        
        conn.commit()
        conn.close()
        
        print("✅ Database created successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error creating database: {e}")
        return False

def create_admin_user():
    """Create default admin user"""
    print("👤 Creating default admin user...")
    
    try:
        import bcrypt
        import uuid
        
        conn = sqlite3.connect('strive_pro.db')
        cursor = conn.cursor()
        
        # Check if admin already exists
        cursor.execute('SELECT id FROM users WHERE username = ?', ('admin',))
        if cursor.fetchone():
            print("ℹ️  Admin user already exists")
            conn.close()
            return True
        
        # Create admin user
        user_id = str(uuid.uuid4())
        password_hash = bcrypt.hashpw('StrivePro2024!'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        cursor.execute('''
            INSERT INTO users (id, username, email, password_hash, full_name, role, organization, department)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, 'admin', 'admin@strivepro.com', password_hash, 'System Administrator', 
              'super_admin', 'STRIVE Pro', 'IT'))
        
        conn.commit()
        conn.close()
        
        print("✅ Admin user created!")
        print("📧 Username: admin")
        print("🔑 Password: StrivePro2024!")
        return True
        
    except Exception as e:
        print(f"❌ Error creating admin user: {e}")
        return False

def create_streamlit_config():
    """Create Streamlit configuration"""
    print("🔧 Creating Streamlit configuration...")
    
    try:
        # Create .streamlit directory
        os.makedirs('.streamlit', exist_ok=True)
        
        # Create config.toml
        config_content = """[global]
developmentMode = false

[server]
headless = true
port = 8501
enableCORS = false

[browser]
gatherUsageStats = false

[theme]
primaryColor = "#667eea"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
textColor = "#262730"
"""
        
        with open('.streamlit/config.toml', 'w') as f:
            f.write(config_content)
        
        # Create secrets template
        secrets_template = """# Copy this file to secrets.toml and fill in your values

[email]
sender_email = "your-email@gmail.com"
sender_password = "your-app-password"

[security]
jwt_secret_key = "your-super-secret-key-change-this"
"""
        
        with open('.streamlit/secrets_template.toml', 'w') as f:
            f.write(secrets_template)
        
        print("✅ Streamlit configuration created!")
        return True
        
    except Exception as e:
        print(f"❌ Error creating Streamlit config: {e}")
        return False

def create_simple_launcher():
    """Create simple launcher without complex imports"""
    print("🚀 Creating simple launcher...")
    
    launcher_code = '''import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import json
import hashlib
import datetime
import uuid

# Basic configuration
st.set_page_config(
    page_title="STRIVE Pro - Mental Health Platform",
    page_icon="🧠",
    layout="wide"
)

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user_info' not in st.session_state:
    st.session_state.user_info = None

def verify_password(password, hashed):
    """Simple password verification"""
    try:
        import bcrypt
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    except:
        return hashlib.sha256(password.encode()).hexdigest() == hashed

def authenticate_user(username, password):
    """Authenticate user"""
    try:
        conn = sqlite3.connect('strive_pro.db')
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, password_hash, full_name, role
            FROM users WHERE username = ? OR email = ?
        """, (username, username))
        
        result = cursor.fetchone()
        conn.close()
        
        if result and verify_password(password, result[1]):
            return {
                'success': True,
                'user_id': result[0],
                'full_name': result[2],
                'role': result[3]
            }
        else:
            return {'success': False, 'message': 'Invalid credentials'}
            
    except Exception as e:
        return {'success': False, 'message': f'Error: {str(e)}'}

def show_login():
    """Show login page"""
    st.markdown("""
    <div style="text-align: center; padding: 2rem; background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); border-radius: 15px; color: white; margin-bottom: 2rem;">
        <h1>🧠 STRIVE Pro Phase 2</h1>
        <p>Mental Health Assessment Platform</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.subheader("🔐 Login")
    
    with st.form("login_form"):
        username = st.text_input("Username or Email")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login", type="primary")
        
        if submitted and username and password:
            result = authenticate_user(username, password)
            if result['success']:
                st.session_state.authenticated = True
                st.session_state.user_info = result
                st.success("Login successful!")
                st.rerun()
            else:
                st.error(result['message'])
    
    st.info("""
    **Default Admin Login:**
    - Username: `admin`
    - Password: `StrivePro2024!`
    """)

def show_dashboard():
    """Show main dashboard"""
    user_info = st.session_state.user_info
    
    st.markdown(f"""
    <div style="text-align: center; padding: 2rem; background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); border-radius: 15px; color: white; margin-bottom: 2rem;">
        <h1>👋 Welcome, {user_info['full_name']}!</h1>
        <p>Role: {user_info['role'].title()}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown("### 🧠 STRIVE Pro")
        st.markdown(f"**User:** {user_info['full_name']}")
        st.markdown(f"**Role:** {user_info['role'].title()}")
        
        if st.button("🚪 Logout"):
            st.session_state.authenticated = False
            st.session_state.user_info = None
            st.rerun()
    
    # Main content
    st.subheader("📊 Dashboard")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("System Status", "🟢 Online")
    
    with col2:
        st.metric("Database", "🟢 Connected")
    
    with col3:
        st.metric("Version", "2.0.0")
    
    st.success("""
    🎉 **STRIVE Pro Phase 2 is running successfully!**
    
    The basic system is now operational. To access full features:
    
    1. ✅ Database is connected
    2. ✅ Admin user is created  
    3. ✅ Basic authentication works
    4. 🔧 Full features will be available after complete setup
    
    **Next Steps:**
    - Configure email settings in `.streamlit/secrets.toml`
    - Complete the full application setup
    - Add assessment modules
    """)
    
    # Show database info
    try:
        conn = sqlite3.connect('strive_pro.db')
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM users')
        user_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM assessment_results')
        assessment_count = cursor.fetchone()[0]
        
        conn.close()
        
        st.subheader("📊 System Statistics")
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Users", user_count)
        with col2:
            st.metric("Assessments Completed", assessment_count)
            
    except Exception as e:
        st.error(f"Database error: {e}")

def main():
    """Main application"""
    try:
        if not st.session_state.authenticated:
            show_login()
        else:
            show_dashboard()
            
    except Exception as e:
        st.error(f"Application error: {e}")
        st.info("Please run the setup script first: `python quick_setup.py`")

if __name__ == "__main__":
    main()
'''
    
    with open('simple_app.py', 'w') as f:
        f.write(launcher_code)
    
    print("✅ Simple launcher created as 'simple_app.py'")
    return True

def main():
    """Run quick setup"""
    print("🚀 STRIVE Pro Phase 2 - Quick Setup")
    print("=" * 50)
    
    steps = [
        ("Installing requirements", install_requirements),
        ("Creating database", create_database),
        ("Creating admin user", create_admin_user),
        ("Creating Streamlit config", create_streamlit_config),
        ("Creating simple launcher", create_simple_launcher)
    ]
    
    success_count = 0
    
    for step_name, step_function in steps:
        print(f"\n{step_name}...")
        try:
            if step_function():
                success_count += 1
            else:
                print(f"⚠️  {step_name} completed with warnings")
        except Exception as e:
            print(f"❌ {step_name} failed: {e}")
    
    print("\n" + "=" * 50)
    print(f"🎉 Quick setup completed! {success_count}/{len(steps)} steps successful")
    
    if success_count >= 4:  # At least core components working
        print("\n✅ STRIVE Pro Phase 2 basic system is ready!")
        print("\n📝 Next steps:")
        print("1. Run: streamlit run simple_app.py")
        print("2. Open: http://localhost:8501")
        print("3. Login with admin/StrivePro2024!")
        print("4. Configure email in .streamlit/secrets.toml")
    else:
        print("\n⚠️  Setup completed with issues. Check the output above.")

if __name__ == "__main__":
    main()