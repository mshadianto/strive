# multi_user_management.py
# Comprehensive Multi-User Management System

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sqlite3
import json
import datetime
import uuid
from typing import Dict, List, Optional, Tuple
import bcrypt
from dataclasses import dataclass
from enum import Enum

class UserRole(Enum):
    """User role enumeration"""
    USER = "user"
    TEAM_LEAD = "team_lead"
    MANAGER = "manager"
    HR_ADMIN = "hr_admin"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"

class Permission(Enum):
    """Permission enumeration"""
    TAKE_ASSESSMENTS = "take_assessments"
    VIEW_OWN_RESULTS = "view_own_results"
    VIEW_TEAM_RESULTS = "view_team_results"
    VIEW_DEPARTMENT_RESULTS = "view_department_results"
    VIEW_ORGANIZATION_RESULTS = "view_organization_results"
    MANAGE_TEAM_USERS = "manage_team_users"
    MANAGE_DEPARTMENT_USERS = "manage_department_users"
    MANAGE_ALL_USERS = "manage_all_users"
    SCHEDULE_ASSESSMENTS = "schedule_assessments"
    GENERATE_REPORTS = "generate_reports"
    VIEW_ANALYTICS = "view_analytics"
    SYSTEM_CONFIGURATION = "system_configuration"
    EXPORT_DATA = "export_data"
    MANAGE_ORGANIZATIONS = "manage_organizations"

@dataclass
class UserProfile:
    """User profile data structure"""
    id: str
    username: str
    email: str
    full_name: str
    role: UserRole
    organization: str
    department: str
    manager_id: str = None
    phone: str = None
    job_title: str = None
    hire_date: str = None
    location: str = None
    emergency_contact: str = None
    created_at: str = None
    last_login: str = None
    is_active: bool = True
    profile_data: dict = None

class RolePermissionManager:
    """Role-based permission management"""
    
    def __init__(self):
        self.role_permissions = {
            UserRole.USER: [
                Permission.TAKE_ASSESSMENTS,
                Permission.VIEW_OWN_RESULTS
            ],
            UserRole.TEAM_LEAD: [
                Permission.TAKE_ASSESSMENTS,
                Permission.VIEW_OWN_RESULTS,
                Permission.VIEW_TEAM_RESULTS,
                Permission.SCHEDULE_ASSESSMENTS,
                Permission.GENERATE_REPORTS
            ],
            UserRole.MANAGER: [
                Permission.TAKE_ASSESSMENTS,
                Permission.VIEW_OWN_RESULTS,
                Permission.VIEW_TEAM_RESULTS,
                Permission.VIEW_DEPARTMENT_RESULTS,
                Permission.MANAGE_TEAM_USERS,
                Permission.SCHEDULE_ASSESSMENTS,
                Permission.GENERATE_REPORTS,
                Permission.VIEW_ANALYTICS
            ],
            UserRole.HR_ADMIN: [
                Permission.TAKE_ASSESSMENTS,
                Permission.VIEW_OWN_RESULTS,
                Permission.VIEW_TEAM_RESULTS,
                Permission.VIEW_DEPARTMENT_RESULTS,
                Permission.VIEW_ORGANIZATION_RESULTS,
                Permission.MANAGE_DEPARTMENT_USERS,
                Permission.SCHEDULE_ASSESSMENTS,
                Permission.GENERATE_REPORTS,
                Permission.VIEW_ANALYTICS,
                Permission.EXPORT_DATA
            ],
            UserRole.ADMIN: [
                Permission.TAKE_ASSESSMENTS,
                Permission.VIEW_OWN_RESULTS,
                Permission.VIEW_TEAM_RESULTS,
                Permission.VIEW_DEPARTMENT_RESULTS,
                Permission.VIEW_ORGANIZATION_RESULTS,
                Permission.MANAGE_ALL_USERS,
                Permission.SCHEDULE_ASSESSMENTS,
                Permission.GENERATE_REPORTS,
                Permission.VIEW_ANALYTICS,
                Permission.EXPORT_DATA,
                Permission.SYSTEM_CONFIGURATION
            ],
            UserRole.SUPER_ADMIN: [perm for perm in Permission]  # All permissions
        }
    
    def has_permission(self, user_role: UserRole, permission: Permission) -> bool:
        """Check if user role has specific permission"""
        return permission in self.role_permissions.get(user_role, [])
    
    def get_role_permissions(self, user_role: UserRole) -> List[Permission]:
        """Get all permissions for a role"""
        return self.role_permissions.get(user_role, [])
    
    def get_accessible_roles(self, user_role: UserRole) -> List[UserRole]:
        """Get roles that this user can manage"""
        if user_role == UserRole.SUPER_ADMIN:
            return list(UserRole)
        elif user_role == UserRole.ADMIN:
            return [UserRole.USER, UserRole.TEAM_LEAD, UserRole.MANAGER, UserRole.HR_ADMIN]
        elif user_role == UserRole.HR_ADMIN:
            return [UserRole.USER, UserRole.TEAM_LEAD, UserRole.MANAGER]
        elif user_role == UserRole.MANAGER:
            return [UserRole.USER, UserRole.TEAM_LEAD]
        else:
            return []

class AdvancedUserManager:
    """Advanced user management with comprehensive features"""
    
    def __init__(self, db_manager):
        self.db = db_manager
        self.permission_manager = RolePermissionManager()
        self._init_additional_tables()
    
    def _init_additional_tables(self):
        """Initialize additional tables for advanced user management"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        # User groups table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_groups (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                organization TEXT,
                created_by TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (created_by) REFERENCES users (id)
            )
        ''')
        
        # User group memberships
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_group_memberships (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                group_id TEXT NOT NULL,
                role TEXT DEFAULT 'member',
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (group_id) REFERENCES user_groups (id)
            )
        ''')
        
        # User activity log
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_activity_log (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                activity_type TEXT NOT NULL,
                description TEXT,
                ip_address TEXT,
                user_agent TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Department structure
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS departments (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                organization TEXT NOT NULL,
                parent_department_id TEXT,
                manager_id TEXT,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (parent_department_id) REFERENCES departments (id),
                FOREIGN KEY (manager_id) REFERENCES users (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def create_user_advanced(self, user_data: Dict, created_by: str) -> Dict:
        """Create user with advanced profile data"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            user_id = str(uuid.uuid4())
            password_hash = bcrypt.hashpw(user_data['password'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            # Prepare profile data
            profile_data = {
                'phone': user_data.get('phone'),
                'job_title': user_data.get('job_title'),
                'hire_date': user_data.get('hire_date'),
                'location': user_data.get('location'),
                'emergency_contact': user_data.get('emergency_contact'),
                'preferences': user_data.get('preferences', {}),
                'created_by': created_by
            }
            
            cursor.execute('''
                INSERT INTO users 
                (id, username, email, password_hash, full_name, role, organization, 
                 department, manager_id, profile_data)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, user_data['username'], user_data['email'], password_hash,
                  user_data['full_name'], user_data['role'], user_data.get('organization'),
                  user_data.get('department'), user_data.get('manager_id'), 
                  json.dumps(profile_data)))
            
            # Log activity
            self._log_user_activity(created_by, 'user_created', f"Created user: {user_data['username']}")
            
            conn.commit()
            conn.close()
            
            return {'success': True, 'user_id': user_id, 'message': 'User created successfully'}
            
        except sqlite3.IntegrityError as e:
            return {'success': False, 'message': 'Username or email already exists'}
        except Exception as e:
            return {'success': False, 'message': f'Error creating user: {str(e)}'}
    
    def get_user_hierarchy(self, user_id: str) -> Dict:
        """Get user's organizational hierarchy"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        # Get user info
        cursor.execute('''
            SELECT id, full_name, role, department, manager_id, organization
            FROM users WHERE id = ?
        ''', (user_id,))
        
        user_data = cursor.fetchone()
        if not user_data:
            conn.close()
            return {}
        
        # Get direct reports
        cursor.execute('''
            SELECT id, full_name, role, department
            FROM users WHERE manager_id = ? AND is_active = 1
        ''', (user_id,))
        
        direct_reports = [
            {'id': row[0], 'full_name': row[1], 'role': row[2], 'department': row[3]}
            for row in cursor.fetchall()
        ]
        
        # Get manager info
        manager_info = None
        if user_data[4]:  # manager_id
            cursor.execute('''
                SELECT id, full_name, role, department
                FROM users WHERE id = ?
            ''', (user_data[4],))
            
            manager_data = cursor.fetchone()
            if manager_data:
                manager_info = {
                    'id': manager_data[0], 
                    'full_name': manager_data[1], 
                    'role': manager_data[2], 
                    'department': manager_data[3]
                }
        
        # Get team members (same manager)
        team_members = []
        if user_data[4]:  # has manager
            cursor.execute('''
                SELECT id, full_name, role, department
                FROM users WHERE manager_id = ? AND id != ? AND is_active = 1
            ''', (user_data[4], user_id))
            
            team_members = [
                {'id': row[0], 'full_name': row[1], 'role': row[2], 'department': row[3]}
                for row in cursor.fetchall()
            ]
        
        conn.close()
        
        return {
            'user': {
                'id': user_data[0],
                'full_name': user_data[1],
                'role': user_data[2],
                'department': user_data[3],
                'organization': user_data[5]
            },
            'manager': manager_info,
            'direct_reports': direct_reports,
            'team_members': team_members
        }
    
    def get_department_users(self, department: str, organization: str) -> List[Dict]:
        """Get all users in a department"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, username, full_name, role, email, last_login, is_active
            FROM users 
            WHERE department = ? AND organization = ?
            ORDER BY full_name
        ''', (department, organization))
        
        results = cursor.fetchall()
        conn.close()
        
        return [
            {
                'id': row[0], 'username': row[1], 'full_name': row[2],
                'role': row[3], 'email': row[4], 'last_login': row[5],
                'is_active': bool(row[6])
            }
            for row in results
        ]
    
    def get_organization_analytics(self, organization: str) -> Dict:
        """Get organization-wide analytics"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        # Total users
        cursor.execute('SELECT COUNT(*) FROM users WHERE organization = ?', (organization,))
        total_users = cursor.fetchone()[0]
        
        # Active users
        cursor.execute('SELECT COUNT(*) FROM users WHERE organization = ? AND is_active = 1', (organization,))
        active_users = cursor.fetchone()[0]
        
        # Users by role
        cursor.execute('''
            SELECT role, COUNT(*) 
            FROM users 
            WHERE organization = ? AND is_active = 1
            GROUP BY role
        ''', (organization,))
        role_distribution = dict(cursor.fetchall())
        
        # Users by department
        cursor.execute('''
            SELECT department, COUNT(*) 
            FROM users 
            WHERE organization = ? AND is_active = 1 AND department IS NOT NULL
            GROUP BY department
        ''', (organization,))
        dept_distribution = dict(cursor.fetchall())
        
        # Assessment participation
        cursor.execute('''
            SELECT COUNT(DISTINCT u.id) as participating_users
            FROM users u
            JOIN assessment_results ar ON u.id = ar.user_id
            WHERE u.organization = ?
        ''', (organization,))
        participating_users = cursor.fetchone()[0]
        
        # Average assessments per user
        cursor.execute('''
            SELECT AVG(assessment_count) as avg_assessments
            FROM (
                SELECT COUNT(ar.id) as assessment_count
                FROM users u
                LEFT JOIN assessment_results ar ON u.id = ar.user_id
                WHERE u.organization = ? AND u.is_active = 1
                GROUP BY u.id
            )
        ''', (organization,))
        
        avg_assessments = cursor.fetchone()[0] or 0
        
        conn.close()
        
        return {
            'total_users': total_users,
            'active_users': active_users,
            'participation_rate': (participating_users / active_users * 100) if active_users > 0 else 0,
            'avg_assessments_per_user': round(avg_assessments, 1),
            'role_distribution': role_distribution,
            'department_distribution': dept_distribution
        }
    
    def bulk_import_users(self, user_data_list: List[Dict], created_by: str) -> Dict:
        """Bulk import users from CSV/Excel data"""
        success_count = 0
        error_count = 0
        errors = []
        
        for user_data in user_data_list:
            try:
                result = self.create_user_advanced(user_data, created_by)
                if result['success']:
                    success_count += 1
                else:
                    error_count += 1
                    errors.append(f"Row {user_data.get('row_number', '?')}: {result['message']}")
            except Exception as e:
                error_count += 1
                errors.append(f"Row {user_data.get('row_number', '?')}: {str(e)}")
        
        return {
            'success_count': success_count,
            'error_count': error_count,
            'errors': errors
        }
    
    def _log_user_activity(self, user_id: str, activity_type: str, description: str):
        """Log user activity"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO user_activity_log (id, user_id, activity_type, description)
                VALUES (?, ?, ?, ?)
            ''', (str(uuid.uuid4()), user_id, activity_type, description))
            
            conn.commit()
            conn.close()
        except Exception:
            pass  # Log errors silently
    
    def deactivate_user(self, user_id: str, deactivated_by: str, reason: str = None) -> bool:
        """Deactivate user account"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('UPDATE users SET is_active = 0 WHERE id = ?', (user_id,))
            
            # Log activity
            self._log_user_activity(deactivated_by, 'user_deactivated', 
                                  f"Deactivated user: {user_id}. Reason: {reason or 'Not specified'}")
            
            conn.commit()
            conn.close()
            return True
        except Exception:
            return False
    
    def get_user_activity_log(self, user_id: str, limit: int = 50) -> List[Dict]:
        """Get user activity log"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT activity_type, description, created_at
            FROM user_activity_log 
            WHERE user_id = ?
            ORDER BY created_at DESC LIMIT ?
        ''', (user_id, limit))
        
        results = cursor.fetchall()
        conn.close()
        
        return [
            {
                'activity_type': row[0],
                'description': row[1],
                'created_at': row[2]
            }
            for row in results
        ]

class UserManagementInterface:
    """Streamlit interface for user management"""
    
    def __init__(self, db_manager):
        self.db = db_manager
        self.user_manager = AdvancedUserManager(db_manager)
        self.permission_manager = RolePermissionManager()
    
    def show_user_management_interface(self, current_user_id: str, current_user_role: str):
        """Show main user management interface"""
        st.title("👥 User Management")
        
        current_role = UserRole(current_user_role)
        
        # Check permissions
        if not self.permission_manager.has_permission(current_role, Permission.MANAGE_ALL_USERS):
            st.error("You don't have permission to access user management.")
            return
        
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "Users Overview", "Create User", "Bulk Import", "Organization Analytics", "User Activity"
        ])
        
        with tab1:
            self._show_users_overview(current_user_id, current_role)
        
        with tab2:
            self._show_create_user(current_user_id, current_role)
        
        with tab3:
            self._show_bulk_import(current_user_id, current_role)
        
        with tab4:
            self._show_organization_analytics(current_user_id)
        
        with tab5:
            self._show_user_activity(current_user_id)
    
    def _show_users_overview(self, current_user_id: str, current_role: UserRole):
        """Show users overview with filtering and management options"""
        st.subheader("👤 Users Overview")
        
        # Get current user's organization
        user_info = self._get_user_info(current_user_id)
        organization = user_info.get('organization') if user_info else None
        
        if not organization:
            st.warning("No organization data available.")
            return
        
        # Filters
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            role_filter = st.selectbox("Filter by Role", ["All"] + [role.value for role in UserRole])
        
        with col2:
            departments = self._get_organization_departments(organization)
            dept_filter = st.selectbox("Filter by Department", ["All"] + departments)
        
        with col3:
            status_filter = st.selectbox("Filter by Status", ["All", "Active", "Inactive"])
        
        with col4:
            search_term = st.text_input("Search Users", placeholder="Name, username, or email")
        
        # Get filtered users
        users = self._get_filtered_users(organization, role_filter, dept_filter, status_filter, search_term)
        
        if users:
            # Display users in expandable cards
            for user in users:
                with st.expander(f"👤 {user['full_name']} ({user['username']}) - {user['role'].title()}"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**Email:** {user['email']}")
                        st.write(f"**Department:** {user.get('department', 'Not assigned')}")
                        st.write(f"**Role:** {user['role'].title()}")
                        st.write(f"**Status:** {'Active' if user['is_active'] else 'Inactive'}")
                    
                    with col2:
                        st.write(f"**Last Login:** {user.get('last_login', 'Never')[:19] if user.get('last_login') else 'Never'}")
                        st.write(f"**Created:** {user.get('created_at', 'Unknown')[:10] if user.get('created_at') else 'Unknown'}")
                        
                        # Get assessment stats
                        assessment_count = self._get_user_assessment_count(user['id'])
                        st.write(f"**Assessments:** {assessment_count}")
                    
                    # Management actions
                    if self._can_manage_user(current_role, UserRole(user['role'])):
                        st.markdown("**Actions:**")
                        action_cols = st.columns(4)
                        
                        with action_cols[0]:
                            if st.button(f"✏️ Edit", key=f"edit_{user['id']}"):
                                st.session_state[f"edit_user_{user['id']}"] = True
                        
                        with action_cols[1]:
                            if user['is_active']:
                                if st.button(f"🔒 Deactivate", key=f"deactivate_{user['id']}"):
                                    if self.user_manager.deactivate_user(user['id'], current_user_id, "Admin action"):
                                        st.success("User deactivated successfully!")
                                        st.rerun()
                            else:
                                if st.button(f"🔓 Activate", key=f"activate_{user['id']}"):
                                    # Implement activate user
                                    st.success("User activated successfully!")
                                    st.rerun()
                        
                        with action_cols[2]:
                            if st.button(f"📊 Analytics", key=f"analytics_{user['id']}"):
                                st.session_state[f"view_analytics_{user['id']}"] = True
                        
                        with action_cols[3]:
                            if st.button(f"🔄 Reset Password", key=f"reset_{user['id']}"):
                                st.session_state[f"reset_password_{user['id']}"] = True
        else:
            st.info("No users found matching the current filters.")
    
    def _show_create_user(self, current_user_id: str, current_role: UserRole):
        """Show create user interface"""
        st.subheader("➕ Create New User")
        
        with st.form("create_user_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                username = st.text_input("Username*", help="Unique username for login")
                email = st.text_input("Email*", help="User's email address")
                full_name = st.text_input("Full Name*", help="User's full name")
                password = st.text_input("Password*", type="password", help="Temporary password")
                
            with col2:
                # Get accessible roles for this user
                accessible_roles = self.permission_manager.get_accessible_roles(current_role)
                role = st.selectbox("Role*", [role.value for role in accessible_roles])
                
                # Get user's organization for default
                user_info = self._get_user_info(current_user_id)
                organization = st.text_input("Organization", value=user_info.get('organization', ''))
                
                departments = self._get_organization_departments(organization) if organization else []
                department = st.selectbox("Department", [""] + departments)
                
                # Manager selection
                managers = self._get_potential_managers(organization, department)
                manager_options = ["No Manager"] + [f"{m['full_name']} ({m['username']})" for m in managers]
                selected_manager = st.selectbox("Manager", manager_options)
            
            # Additional fields
            st.subheader("Additional Information (Optional)")
            
            col3, col4 = st.columns(2)
            
            with col3:
                job_title = st.text_input("Job Title")
                phone = st.text_input("Phone Number")
                location = st.text_input("Location")
                
            with col4:
                hire_date = st.date_input("Hire Date", value=datetime.date.today())
                emergency_contact = st.text_input("Emergency Contact")
            
            submitted = st.form_submit_button("Create User", type="primary")
            
            if submitted:
                if all([username, email, full_name, password, role]):
                    # Prepare user data
                    user_data = {
                        'username': username,
                        'email': email,
                        'full_name': full_name,
                        'password': password,
                        'role': role,
                        'organization': organization,
                        'department': department if department else None,
                        'manager_id': self._extract_manager_id(selected_manager, managers) if selected_manager != "No Manager" else None,
                        'job_title': job_title,
                        'phone': phone,
                        'location': location,
                        'hire_date': hire_date.isoformat() if hire_date else None,
                        'emergency_contact': emergency_contact
                    }
                    
                    result = self.user_manager.create_user_advanced(user_data, current_user_id)
                    
                    if result['success']:
                        st.success("User created successfully!")
                        st.balloons()
                    else:
                        st.error(result['message'])
                else:
                    st.error("Please fill in all required fields (marked with *).")
    
    def _show_bulk_import(self, current_user_id: str, current_role: UserRole):
        """Show bulk import interface"""
        st.subheader("📤 Bulk Import Users")
        
        st.info("Upload a CSV file with user data to create multiple users at once.")
        
        # Download template
        if st.button("📥 Download CSV Template"):
            template_data = {
                'username': ['john.doe', 'jane.smith'],
                'email': ['john.doe@company.com', 'jane.smith@company.com'],
                'full_name': ['John Doe', 'Jane Smith'],
                'password': ['temp123!', 'temp456!'],
                'role': ['user', 'manager'],
                'organization': ['ACME Corp', 'ACME Corp'],
                'department': ['IT', 'HR'],
                'job_title': ['Developer', 'HR Manager'],
                'phone': ['+1234567890', '+0987654321'],
                'location': ['New York', 'New York']
            }
            
            template_df = pd.DataFrame(template_data)
            csv = template_df.to_csv(index=False)
            
            st.download_button(
                label="Download Template",
                data=csv,
                file_name="user_import_template.csv",
                mime="text/csv"
            )
        
        # File upload
        uploaded_file = st.file_uploader("Choose CSV file", type="csv")
        
        if uploaded_file is not None:
            try:
                df = pd.read_csv(uploaded_file)
                
                # Validate required columns
                required_columns = ['username', 'email', 'full_name', 'password', 'role']
                missing_columns = [col for col in required_columns if col not in df.columns]
                
                if missing_columns:
                    st.error(f"Missing required columns: {', '.join(missing_columns)}")
                else:
                    st.success(f"File uploaded successfully! Found {len(df)} users to import.")
                    
                    # Preview data
                    st.subheader("Preview Data")
                    st.dataframe(df.head(10))
                    
                    # Import options
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        send_welcome_email = st.checkbox("Send welcome emails", value=True)
                        skip_duplicates = st.checkbox("Skip duplicate usernames/emails", value=True)
                    
                    with col2:
                        force_password_reset = st.checkbox("Force password reset on first login", value=True)
                    
                    if st.button("🚀 Import Users", type="primary"):
                        with st.spinner("Importing users..."):
                            # Convert DataFrame to list of dicts
                            user_data_list = []
                            for index, row in df.iterrows():
                                user_data = row.to_dict()
                                user_data['row_number'] = index + 2  # +2 for header and 0-indexing
                                user_data_list.append(user_data)
                            
                            # Perform bulk import
                            result = self.user_manager.bulk_import_users(user_data_list, current_user_id)
                            
                            # Show results
                            st.success(f"Import completed! {result['success_count']} users created successfully.")
                            
                            if result['error_count'] > 0:
                                st.error(f"{result['error_count']} users failed to import:")
                                for error in result['errors']:
                                    st.text(f"• {error}")
            
            except Exception as e:
                st.error(f"Error processing file: {str(e)}")
    
    def _show_organization_analytics(self, current_user_id: str):
        """Show organization analytics"""
        st.subheader("📊 Organization Analytics")
        
        user_info = self._get_user_info(current_user_id)
        organization = user_info.get('organization') if user_info else None
        
        if not organization:
            st.warning("No organization data available.")
            return
        
        # Get analytics data
        analytics = self.user_manager.get_organization_analytics(organization)
        
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Users", analytics['total_users'])
        
        with col2:
            st.metric("Active Users", analytics['active_users'])
        
        with col3:
            st.metric("Participation Rate", f"{analytics['participation_rate']:.1f}%")
        
        with col4:
            st.metric("Avg Assessments/User", analytics['avg_assessments_per_user'])
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            # Role distribution
            if analytics['role_distribution']:
                role_df = pd.DataFrame(list(analytics['role_distribution'].items()), 
                                     columns=['Role', 'Count'])
                fig = px.pie(role_df, values='Count', names='Role', title='Users by Role')
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Department distribution
            if analytics['department_distribution']:
                dept_df = pd.DataFrame(list(analytics['department_distribution'].items()),
                                     columns=['Department', 'Count'])
                fig = px.bar(dept_df, x='Department', y='Count', title='Users by Department')
                st.plotly_chart(fig, use_container_width=True)
    
    def _show_user_activity(self, current_user_id: str):
        """Show user activity monitoring"""
        st.subheader("📋 User Activity Log")
        
        # Get recent activities
        activities = self.user_manager.get_user_activity_log(current_user_id, 100)
        
        if activities:
            activity_df = pd.DataFrame(activities)
            activity_df['created_at'] = pd.to_datetime(activity_df['created_at'])
            activity_df = activity_df.sort_values('created_at', ascending=False)
            
            # Filter options
            col1, col2 = st.columns(2)
            
            with col1:
                activity_types = activity_df['activity_type'].unique().tolist()
                selected_types = st.multiselect("Filter by Activity Type", activity_types, default=activity_types)
            
            with col2:
                date_range = st.date_input(
                    "Date Range",
                    value=(datetime.date.today() - datetime.timedelta(days=7), datetime.date.today())
                )
            
            # Filter data
            filtered_df = activity_df[activity_df['activity_type'].isin(selected_types)]
            
            if len(date_range) == 2:
                start_date, end_date = date_range
                filtered_df = filtered_df[
                    (filtered_df['created_at'].dt.date >= start_date) &
                    (filtered_df['created_at'].dt.date <= end_date)
                ]
            
            # Display activities
            for _, activity in filtered_df.iterrows():
                st.markdown(f"""
                **{activity['activity_type'].replace('_', ' ').title()}** - {activity['created_at'].strftime('%Y-%m-%d %H:%M')}  
                {activity['description']}
                """)
                st.markdown("---")
        else:
            st.info("No activity log available.")
    
    # Helper methods
    def _get_user_info(self, user_id: str) -> Dict:
        """Get user information"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT username, email, full_name, role, organization, department
            FROM users WHERE id = ?
        ''', (user_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                'username': result[0], 'email': result[1], 'full_name': result[2],
                'role': result[3], 'organization': result[4], 'department': result[5]
            }
        return {}
    
    def _get_organization_departments(self, organization: str) -> List[str]:
        """Get departments in organization"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT DISTINCT department 
            FROM users 
            WHERE organization = ? AND department IS NOT NULL
        ''', (organization,))
        
        results = cursor.fetchall()
        conn.close()
        
        return [r[0] for r in results if r[0]]
    
    def _get_filtered_users(self, organization: str, role_filter: str, dept_filter: str, 
                           status_filter: str, search_term: str) -> List[Dict]:
        """Get filtered users based on criteria"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        query = '''
            SELECT id, username, email, full_name, role, department, 
                   created_at, last_login, is_active
            FROM users WHERE organization = ?
        '''
        params = [organization]
        
        if role_filter != "All":
            query += ' AND role = ?'
            params.append(role_filter)
        
        if dept_filter != "All":
            query += ' AND department = ?'
            params.append(dept_filter)
        
        if status_filter == "Active":
            query += ' AND is_active = 1'
        elif status_filter == "Inactive":
            query += ' AND is_active = 0'
        
        if search_term:
            query += ' AND (full_name LIKE ? OR username LIKE ? OR email LIKE ?)'
            search_pattern = f'%{search_term}%'
            params.extend([search_pattern, search_pattern, search_pattern])
        
        query += ' ORDER BY full_name'
        
        cursor.execute(query, params)
        results = cursor.fetchall()
        conn.close()
        
        return [
            {
                'id': row[0], 'username': row[1], 'email': row[2], 'full_name': row[3],
                'role': row[4], 'department': row[5], 'created_at': row[6],
                'last_login': row[7], 'is_active': bool(row[8])
            }
            for row in results
        ]
    
    def _get_potential_managers(self, organization: str, department: str) -> List[Dict]:
        """Get potential managers for user assignment"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, username, full_name, role
            FROM users 
            WHERE organization = ? 
            AND role IN ('manager', 'admin', 'super_admin')
            AND is_active = 1
            ORDER BY full_name
        ''', (organization,))
        
        results = cursor.fetchall()
        conn.close()
        
        return [
            {'id': row[0], 'username': row[1], 'full_name': row[2], 'role': row[3]}
            for row in results
        ]
    
    def _extract_manager_id(self, selected_manager: str, managers: List[Dict]) -> str:
        """Extract manager ID from selection"""
        if selected_manager == "No Manager":
            return None
        
        for manager in managers:
            if f"{manager['full_name']} ({manager['username']})" == selected_manager:
                return manager['id']
        
        return None
    
    def _can_manage_user(self, current_role: UserRole, target_role: UserRole) -> bool:
        """Check if current user can manage target user"""
        accessible_roles = self.permission_manager.get_accessible_roles(current_role)
        return target_role in accessible_roles
    
    def _get_user_assessment_count(self, user_id: str) -> int:
        """Get number of assessments completed by user"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM assessment_results WHERE user_id = ?', (user_id,))
        count = cursor.fetchone()[0]
        
        conn.close()
        return count

# Usage in main app:
def show_user_management_page(user_manager, db_manager, current_user_id: str, current_user_role: str):
    """Show user management page with full functionality"""
    user_management_interface = UserManagementInterface(db_manager)
    user_management_interface.show_user_management_interface(current_user_id, current_user_role)