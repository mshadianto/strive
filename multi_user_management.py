# multi_user_management.py

import streamlit as st
import pandas as pd
import sqlite3
import hashlib
import jwt
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import secrets
import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import json
import uuid

class UserRole(Enum):
    """User roles with different access levels"""
    ADMIN = "admin"
    CLINICIAN = "clinician"  
    HR_MANAGER = "hr_manager"
    USER = "user"
    ORGANIZATION_ADMIN = "org_admin"

@dataclass
class User:
    """User data class"""
    user_id: str
    username: str
    email: str
    password_hash: str
    role: UserRole
    organization_id: Optional[str]
    full_name: str
    department: Optional[str]
    created_at: datetime
    last_login: Optional[datetime]
    is_active: bool = True
    profile_data: Optional[Dict] = None

@dataclass
class Organization:
    """Organization data class"""
    org_id: str
    name: str
    industry: str
    size: str  # small, medium, large
    admin_user_id: str
    created_at: datetime
    settings: Dict
    subscription_plan: str = "basic"

@dataclass
class AssessmentRecord:
    """Assessment record for database storage"""
    record_id: str
    user_id: str
    organization_id: Optional[str]
    assessment_type: str
    scores: Dict
    risk_level: str
    recommendations: List[str]
    completed_at: datetime
    follow_up_date: Optional[datetime]
    notes: Optional[str] = None

class DatabaseManager:
    """Database manager for user and assessment data"""
    
    def __init__(self, db_path: str = "strive_pro.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL,
            organization_id TEXT,
            full_name TEXT NOT NULL,
            department TEXT,
            created_at TEXT NOT NULL,
            last_login TEXT,
            is_active INTEGER DEFAULT 1,
            profile_data TEXT
        )
        ''')
        
        # Organizations table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS organizations (
            org_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            industry TEXT,
            size TEXT,
            admin_user_id TEXT NOT NULL,
            created_at TEXT NOT NULL,
            settings TEXT,
            subscription_plan TEXT DEFAULT 'basic'
        )
        ''')
        
        # Assessment records table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS assessment_records (
            record_id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            organization_id TEXT,
            assessment_type TEXT NOT NULL,
            scores TEXT NOT NULL,
            risk_level TEXT NOT NULL,
            recommendations TEXT,
            completed_at TEXT NOT NULL,
            follow_up_date TEXT,
            notes TEXT,
            FOREIGN KEY (user_id) REFERENCES users (user_id)
        )
        ''')
        
        # Sessions table for authentication
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_sessions (
            session_id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            created_at TEXT NOT NULL,
            expires_at TEXT NOT NULL,
            is_active INTEGER DEFAULT 1,
            FOREIGN KEY (user_id) REFERENCES users (user_id)
        )
        ''')
        
        conn.commit()
        conn.close()
    
    def create_user(self, user: User) -> bool:
        """Create new user"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
            INSERT INTO users (user_id, username, email, password_hash, role, 
                             organization_id, full_name, department, created_at, 
                             last_login, is_active, profile_data)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                user.user_id, user.username, user.email, user.password_hash,
                user.role.value, user.organization_id, user.full_name,
                user.department, user.created_at.isoformat(), 
                user.last_login.isoformat() if user.last_login else None,
                int(user.is_active), json.dumps(user.profile_data) if user.profile_data else None
            ))
            
            conn.commit()
            conn.close()
            return True
            
        except sqlite3.IntegrityError:
            return False
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return User(
                user_id=row[0],
                username=row[1],
                email=row[2],
                password_hash=row[3],
                role=UserRole(row[4]),
                organization_id=row[5],
                full_name=row[6],
                department=row[7],
                created_at=datetime.fromisoformat(row[8]),
                last_login=datetime.fromisoformat(row[9]) if row[9] else None,
                is_active=bool(row[10]),
                profile_data=json.loads(row[11]) if row[11] else None
            )
        return None
    
    def update_last_login(self, user_id: str):
        """Update user's last login time"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            'UPDATE users SET last_login = ? WHERE user_id = ?',
            (datetime.now().isoformat(), user_id)
        )
        
        conn.commit()
        conn.close()
    
    def create_organization(self, org: Organization) -> bool:
        """Create new organization"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
            INSERT INTO organizations (org_id, name, industry, size, admin_user_id,
                                     created_at, settings, subscription_plan)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                org.org_id, org.name, org.industry, org.size,
                org.admin_user_id, org.created_at.isoformat(),
                json.dumps(org.settings), org.subscription_plan
            ))
            
            conn.commit()
            conn.close()
            return True
            
        except sqlite3.IntegrityError:
            return False
    
    def save_assessment_record(self, record: AssessmentRecord) -> bool:
        """Save assessment record"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
            INSERT INTO assessment_records (record_id, user_id, organization_id,
                                          assessment_type, scores, risk_level,
                                          recommendations, completed_at, follow_up_date, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                record.record_id, record.user_id, record.organization_id,
                record.assessment_type, json.dumps(record.scores),
                record.risk_level, json.dumps(record.recommendations),
                record.completed_at.isoformat(),
                record.follow_up_date.isoformat() if record.follow_up_date else None,
                record.notes
            ))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            st.error(f"Error saving assessment: {e}")
            return False
    
    def get_user_assessments(self, user_id: str) -> List[AssessmentRecord]:
        """Get all assessments for a user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            'SELECT * FROM assessment_records WHERE user_id = ? ORDER BY completed_at DESC',
            (user_id,)
        )
        rows = cursor.fetchall()
        conn.close()
        
        assessments = []
        for row in rows:
            assessments.append(AssessmentRecord(
                record_id=row[0],
                user_id=row[1],
                organization_id=row[2],
                assessment_type=row[3],
                scores=json.loads(row[4]),
                risk_level=row[5],
                recommendations=json.loads(row[6]),
                completed_at=datetime.fromisoformat(row[7]),
                follow_up_date=datetime.fromisoformat(row[8]) if row[8] else None,
                notes=row[9]
            ))
        
        return assessments
    
    def get_organization_assessments(self, org_id: str) -> List[AssessmentRecord]:
        """Get all assessments for an organization"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            'SELECT * FROM assessment_records WHERE organization_id = ? ORDER BY completed_at DESC',
            (org_id,)
        )
        rows = cursor.fetchall()
        conn.close()
        
        assessments = []
        for row in rows:
            assessments.append(AssessmentRecord(
                record_id=row[0],
                user_id=row[1],
                organization_id=row[2],
                assessment_type=row[3],
                scores=json.loads(row[4]),
                risk_level=row[5],
                recommendations=json.loads(row[6]),
                completed_at=datetime.fromisoformat(row[7]),
                follow_up_date=datetime.fromisoformat(row[8]) if row[8] else None,
                notes=row[9]
            ))
        
        return assessments

class AuthenticationManager:
    """Handle user authentication and sessions"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.secret_key = self.get_secret_key()
    
    def get_secret_key(self) -> str:
        """Get or create JWT secret key"""
        if 'jwt_secret' not in st.secrets:
            # In production, this should be set in secrets.toml
            return secrets.token_urlsafe(32)
        return st.secrets['jwt_secret']
    
    def hash_password(self, password: str) -> str:
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify password against hash"""
        return hashlib.sha256(password.encode()).hexdigest() == hashed
    
    def create_jwt_token(self, user: User) -> str:
        """Create JWT token for user"""
        payload = {
            'user_id': user.user_id,
            'username': user.username,
            'role': user.role.value,
            'exp': datetime.utcnow() + timedelta(hours=24)
        }
        return jwt.encode(payload, self.secret_key, algorithm='HS256')
    
    def verify_jwt_token(self, token: str) -> Optional[Dict]:
        """Verify JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    def login(self, username: str, password: str) -> Optional[str]:
        """Authenticate user and return JWT token"""
        user = self.db_manager.get_user_by_username(username)
        
        if user and user.is_active and self.verify_password(password, user.password_hash):
            self.db_manager.update_last_login(user.user_id)
            return self.create_jwt_token(user)
        
        return None
    
    def register_user(self, username: str, email: str, password: str, 
                     full_name: str, role: UserRole = UserRole.USER,
                     organization_id: Optional[str] = None,
                     department: Optional[str] = None) -> bool:
        """Register new user"""
        
        # Validate input
        if not self.validate_email(email):
            return False
        
        if not self.validate_password(password):
            return False
        
        # Check if user already exists
        existing_user = self.db_manager.get_user_by_username(username)
        if existing_user:
            return False
        
        # Create new user
        user = User(
            user_id=str(uuid.uuid4()),
            username=username,
            email=email,
            password_hash=self.hash_password(password),
            role=role,
            organization_id=organization_id,
            full_name=full_name,
            department=department,
            created_at=datetime.now(),
            last_login=None
        )
        
        return self.db_manager.create_user(user)
    
    def validate_email(self, email: str) -> bool:
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def validate_password(self, password: str) -> bool:
        """Validate password strength"""
        if len(password) < 8:
            return False
        if not re.search(r'[A-Z]', password):
            return False
        if not re.search(r'[a-z]', password):
            return False
        if not re.search(r'\d', password):
            return False
        return True

class OrganizationAnalytics:
    """Analytics dashboard for organizations"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
    
    def get_organization_overview(self, org_id: str) -> Dict:
        """Get organization overview statistics"""
        assessments = self.db_manager.get_organization_assessments(org_id)
        
        if not assessments:
            return {'total_assessments': 0, 'active_users': 0}
        
        df = pd.DataFrame([asdict(a) for a in assessments])
        
        # Basic statistics
        total_assessments = len(df)
        active_users = df['user_id'].nunique()
        
        # Risk distribution
        risk_distribution = df['risk_level'].value_counts().to_dict()
        
        # Assessment types
        assessment_types = df['assessment_type'].value_counts().to_dict()
        
        # Recent activity (last 30 days)
        recent_date = datetime.now() - timedelta(days=30)
        recent_assessments = df[pd.to_datetime(df['completed_at']) > recent_date]
        recent_count = len(recent_assessments)
        
        # Average risk levels by department (if available)
        # This would require joining with user data
        
        return {
            'total_assessments': total_assessments,
            'active_users': active_users,
            'risk_distribution': risk_distribution,
            'assessment_types': assessment_types,
            'recent_assessments': recent_count,
            'trend_data': self.calculate_trends(df)
        }
    
    def calculate_trends(self, df: pd.DataFrame) -> Dict:
        """Calculate trend data for organization"""
        df['completed_at'] = pd.to_datetime(df['completed_at'])
        df['week'] = df['completed_at'].dt.to_period('W')
        
        # Weekly assessment counts
        weekly_counts = df.groupby('week').size().to_dict()
        
        # Weekly risk levels
        weekly_risk = df.groupby(['week', 'risk_level']).size().unstack(fill_value=0)
        
        return {
            'weekly_counts': {str(k): v for k, v in weekly_counts.items()},
            'weekly_risk_trends': weekly_risk.to_dict()
        }
    
    def create_organization_dashboard(self, org_id: str):
        """Create comprehensive organization dashboard"""
        overview = self.get_organization_overview(org_id)
        
        if overview['total_assessments'] == 0:
            st.info("Belum ada data assessmen untuk organisasi ini.")
            return
        
        # Overview metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Assessmen", overview['total_assessments'])
        
        with col2:
            st.metric("Pengguna Aktif", overview['active_users'])
        
        with col3:
            st.metric("Assessmen Bulan Ini", overview['recent_assessments'])
        
        with col4:
            high_risk_count = overview['risk_distribution'].get('High', 0)
            st.metric("High Risk", high_risk_count, 
                     delta=f"{(high_risk_count/overview['total_assessments']*100):.1f}%" if overview['total_assessments'] > 0 else "0%")
        
        # Risk distribution chart
        st.subheader("📊 Distribusi Tingkat Risiko")
        
        risk_data = overview['risk_distribution']
        if risk_data:
            fig_risk = px.pie(
                values=list(risk_data.values()),
                names=list(risk_data.keys()),
                title="Distribusi Tingkat Risiko Organisasi",
                color_discrete_map={
                    'Low': '#28a745',
                    'Moderate': '#ffc107',
                    'High': '#dc3545'
                }
            )
            st.plotly_chart(fig_risk, use_container_width=True)
        
        # Assessment types distribution
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📋 Jenis Assessmen")
            assessment_data = overview['assessment_types']
            if assessment_data:
                fig_assessments = px.bar(
                    x=list(assessment_data.keys()),
                    y=list(assessment_data.values()),
                    title="Distribusi Jenis Assessmen"
                )
                st.plotly_chart(fig_assessments, use_container_width=True)
        
        with col2:
            st.subheader("📈 Tren Mingguan")
            trend_data = overview['trend_data']['weekly_counts']
            if trend_data:
                weeks = list(trend_data.keys())
                counts = list(trend_data.values())
                
                fig_trend = px.line(
                    x=weeks, y=counts,
                    title="Tren Assessmen Mingguan",
                    labels={'x': 'Minggu', 'y': 'Jumlah Assessmen'}
                )
                st.plotly_chart(fig_trend, use_container_width=True)
        
        # Detailed risk analysis
        st.subheader("🔍 Analisis Risiko Detail")
        
        # This would show more detailed breakdown by department, role, etc.
        self.show_risk_heatmap(org_id)
    
    def show_risk_heatmap(self, org_id: str):
        """Show risk heatmap by department/time"""
        assessments = self.db_manager.get_organization_assessments(org_id)
        
        if not assessments:
            return
        
        df = pd.DataFrame([asdict(a) for a in assessments])
        df['completed_at'] = pd.to_datetime(df['completed_at'])
        df['month'] = df['completed_at'].dt.to_period('M')
        
        # Create risk level mapping
        risk_mapping = {'Low': 1, 'Moderate': 2, 'High': 3}
        df['risk_numeric'] = df['risk_level'].map(risk_mapping)
        
        # Group by month and calculate average risk
        monthly_risk = df.groupby('month')['risk_numeric'].mean().reset_index()
        monthly_risk['month_str'] = monthly_risk['month'].astype(str)
        
        fig = px.bar(
            monthly_risk,
            x='month_str',
            y='risk_numeric',
            title="Tren Tingkat Risiko Rata-rata per Bulan",
            labels={'risk_numeric': 'Tingkat Risiko Rata-rata', 'month_str': 'Bulan'},
            color='risk_numeric',
            color_continuous_scale=['green', 'yellow', 'red']
        )
        
        st.plotly_chart(fig, use_container_width=True)

class MultiUserInterface:
    """Main interface for multi-user system"""
    
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.auth_manager = AuthenticationManager(self.db_manager)
        self.org_analytics = OrganizationAnalytics(self.db_manager)
        
        # Initialize session state
        if 'authenticated' not in st.session_state:
            st.session_state.authenticated = False
        if 'user_data' not in st.session_state:
            st.session_state.user_data = None
        if 'jwt_token' not in st.session_state:
            st.session_state.jwt_token = None
    
    def show_login_page(self):
        """Show login/registration page"""
        st.title("🔐 Strive Pro - Login")
        
        tab1, tab2 = st.tabs(["Login", "Register"])
        
        with tab1:
            self.show_login_form()
        
        with tab2:
            self.show_registration_form()
    
    def show_login_form(self):
        """Show login form"""
        st.subheader("Login ke Akun Anda")
        
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            
            submitted = st.form_submit_button("Login")
            
            if submitted:
                if username and password:
                    token = self.auth_manager.login(username, password)
                    
                    if token:
                        payload = self.auth_manager.verify_jwt_token(token)
                        
                        st.session_state.authenticated = True
                        st.session_state.jwt_token = token
                        st.session_state.user_data = payload
                        
                        st.success("Login berhasil!")
                        st.rerun()
                    else:
                        st.error("Username atau password salah")
                else:
                    st.warning("Silakan isi username dan password")
    
    def show_registration_form(self):
        """Show registration form"""
        st.subheader("Buat Akun Baru")
        
        with st.form("registration_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                username = st.text_input("Username")
                email = st.text_input("Email")
                full_name = st.text_input("Nama Lengkap")
            
            with col2:
                password = st.text_input("Password", type="password")
                confirm_password = st.text_input("Konfirmasi Password", type="password")
                department = st.text_input("Departemen (Opsional)")
            
            role = st.selectbox("Role", [
                ("User", UserRole.USER),
                ("HR Manager", UserRole.HR_MANAGER),
                ("Organization Admin", UserRole.ORGANIZATION_ADMIN)
            ], format_func=lambda x: x[0])
            
            submitted = st.form_submit_button("Register")
            
            if submitted:
                if not all([username, email, password, full_name]):
                    st.error("Silakan isi semua field yang wajib")
                elif password != confirm_password:
                    st.error("Password tidak cocok")
                elif not self.auth_manager.validate_email(email):
                    st.error("Format email tidak valid")
                elif not self.auth_manager.validate_password(password):
                    st.error("Password harus minimal 8 karakter dengan huruf besar, kecil, dan angka")
                else:
                    success = self.auth_manager.register_user(
                        username=username,
                        email=email,
                        password=password,
                        full_name=full_name,
                        role=role[1],
                        department=department if department else None
                    )
                    
                    if success:
                        st.success("Registrasi berhasil! Silakan login.")
                    else:
                        st.error("Username atau email sudah digunakan")
    
    def show_user_dashboard(self):
        """Show dashboard based on user role"""
        user_data = st.session_state.user_data
        role = UserRole(user_data['role'])
        
        # Sidebar navigation
        with st.sidebar:
            st.write(f"**Selamat datang, {user_data['username']}**")
            st.write(f"Role: {role.value.title()}")
            
            if st.button("Logout"):
                self.logout()
        
        # Role-based dashboard
        if role == UserRole.ADMIN:
            self.show_admin_dashboard()
        elif role == UserRole.ORGANIZATION_ADMIN:
            self.show_org_admin_dashboard()
        elif role == UserRole.HR_MANAGER:
            self.show_hr_dashboard()
        elif role == UserRole.CLINICIAN:
            self.show_clinician_dashboard()
        else:
            self.show_regular_user_dashboard()
    
    def show_admin_dashboard(self):
        """Show admin dashboard"""
        st.title("👑 Admin Dashboard")
        
        tab1, tab2, tab3 = st.tabs(["System Overview", "User Management", "Analytics"])
        
        with tab1:
            st.subheader("System Statistics")
            # Show system-wide statistics
            
        with tab2:
            st.subheader("User Management")
            # User management interface
            
        with tab3:
            st.subheader("Global Analytics")
            # System-wide analytics
    
    def show_org_admin_dashboard(self):
        """Show organization admin dashboard"""
        st.title("🏢 Organization Dashboard")
        
        user_data = st.session_state.user_data
        org_id = user_data.get('organization_id')  # This would need to be included in JWT
        
        if org_id:
            self.org_analytics.create_organization_dashboard(org_id)
        else:
            st.warning("No organization associated with this account")
    
    def show_hr_dashboard(self):
        """Show HR manager dashboard"""
        st.title("👥 HR Dashboard")
        
        tab1, tab2, tab3 = st.tabs(["Employee Wellbeing", "Risk Management", "Reports"])
        
        with tab1:
            st.subheader("Employee Wellbeing Overview")
            # Employee wellbeing metrics
            
        with tab2:
            st.subheader("Risk Management")
            # High-risk employee identification and interventions
            
        with tab3:
            st.subheader("Wellbeing Reports")
            # Generate and download wellbeing reports
    
    def show_clinician_dashboard(self):
        """Show clinician dashboard"""
        st.title("🩺 Clinician Dashboard")
        
        tab1, tab2, tab3 = st.tabs(["Client Overview", "Assessment Review", "Treatment Planning"])
        
        with tab1:
            st.subheader("Client Overview")
            # Client list and status
            
        with tab2:
            st.subheader("Assessment Review")
            # Review and interpret assessments
            
        with tab3:
            st.subheader("Treatment Planning")
            # Create treatment plans and track progress
    
    def show_regular_user_dashboard(self):
        """Show regular user dashboard"""
        st.title("🧘 My Wellbeing Dashboard")
        
        user_id = st.session_state.user_data['user_id']
        assessments = self.db_manager.get_user_assessments(user_id)
        
        if assessments:
            # Show user's personal analytics
            self.show_personal_analytics(assessments)
        else:
            st.info("Belum ada data assessmen. Mulai dengan melakukan assessmen pertama Anda!")
            
            if st.button("Mulai Assessmen"):
                st.session_state.current_assessment = "pss10"
                st.rerun()
    
    def show_personal_analytics(self, assessments: List[AssessmentRecord]):
        """Show personal analytics for user"""
        df = pd.DataFrame([asdict(a) for a in assessments])
        
        # Recent assessment summary
        latest = assessments[0]
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Latest Risk Level", latest.risk_level)
        
        with col2:
            st.metric("Total Assessments", len(assessments))
        
        with col3:
            if len(assessments) > 1:
                prev_risk = assessments[1].risk_level
                risk_change = "Improved" if latest.risk_level == "Low" and prev_risk != "Low" else "Stable"
                st.metric("Progress", risk_change)
        
        # Personal trend chart
        st.subheader("📈 Personal Progress")
        
        df['completed_at'] = pd.to_datetime(df['completed_at'])
        
        # Risk level trend
        risk_mapping = {'Low': 1, 'Moderate': 2, 'High': 3}
        df['risk_numeric'] = df['risk_level'].map(risk_mapping)
        
        fig = px.line(
            df.sort_values('completed_at'),
            x='completed_at',
            y='risk_numeric',
            title="Tren Tingkat Risiko Personal",
            labels={'risk_numeric': 'Tingkat Risiko', 'completed_at': 'Tanggal'}
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Recent recommendations
        st.subheader("💡 Rekomendasi Terbaru")
        for rec in latest.recommendations[:5]:
            st.write(f"• {rec}")
    
    def logout(self):
        """Logout user"""
        st.session_state.authenticated = False
        st.session_state.user_data = None
        st.session_state.jwt_token = None
        st.rerun()
    
    def check_authentication(self):
        """Check if user is authenticated"""
        if st.session_state.jwt_token:
            payload = self.auth_manager.verify_jwt_token(st.session_state.jwt_token)
            
            if payload:
                st.session_state.authenticated = True
                st.session_state.user_data = payload
                return True
            else:
                # Token expired
                self.logout()
                return False
        
        return st.session_state.authenticated
    
    def run(self):
        """Main run function"""
        if self.check_authentication():
            self.show_user_dashboard()
        else:
            self.show_login_page()

# Usage example
def main():
    st.set_page_config(
        page_title="Strive Pro - Multi-User",
        page_icon="🧘",
        layout="wide"
    )
    
    interface = MultiUserInterface()
    interface.run()

if __name__ == "__main__":
    main()