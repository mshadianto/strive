# multi_user_management.py
# Multi-User Management & Role-Based Access Control

import streamlit as st
import pandas as pd
import sqlite3
import bcrypt
import uuid
from typing import Dict, List
from enum import Enum

class UserRole(Enum):
    USER = "user"
    MANAGER = "manager"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"

class AdvancedUserManager:
    def __init__(self, db_manager):
        self.db = db_manager
    
    def create_user_advanced(self, user_data: Dict, created_by: str) -> Dict:
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            user_id = str(uuid.uuid4())
            password_hash = bcrypt.hashpw(user_data['password'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            query = '''INSERT INTO users 
                      (id, username, email, password_hash, full_name, role, organization, department)
                      VALUES (?, ?, ?, ?, ?, ?, ?, ?)'''
            
            cursor.execute(query, (user_id, user_data['username'], user_data['email'], 
                                 password_hash, user_data['full_name'], user_data['role'], 
                                 user_data.get('organization'), user_data.get('department')))
            
            conn.commit()
            conn.close()
            
            return {'success': True, 'user_id': user_id, 'message': 'User created successfully'}
            
        except sqlite3.IntegrityError:
            return {'success': False, 'message': 'Username or email already exists'}
        except Exception as e:
            return {'success': False, 'message': f'Error creating user: {str(e)}'}

class UserManagementInterface:
    def __init__(self, db_manager):
        self.db = db_manager
        self.user_manager = AdvancedUserManager(db_manager)
    
    def show_user_management_interface(self, current_user_id: str, current_user_role: str):
        st.title("👥 User Management")
        
        tab1, tab2 = st.tabs(["Users Overview", "Create User"])
        
        with tab1:
            self._show_users_overview()
        
        with tab2:
            self._show_create_user(current_user_id)
    
    def _show_users_overview(self):
        st.subheader("👤 Users Overview")
        
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            query = '''SELECT username, full_name, email, role, organization, is_active, created_at
                      FROM users 
                      ORDER BY created_at DESC'''
            
            cursor.execute(query)
            results = cursor.fetchall()
            conn.close()
            
            if results:
                users_data = []
                for result in results:
                    users_data.append({
                        'Username': result[0],
                        'Full Name': result[1],
                        'Email': result[2],
                        'Role': result[3].title(),
                        'Organization': result[4] or 'N/A',
                        'Status': 'Active' if result[5] else 'Inactive',
                        'Created': result[6][:10] if result[6] else 'N/A'
                    })
                
                df = pd.DataFrame(users_data)
                st.dataframe(df, use_container_width=True)
            else:
                st.info("No users found.")
                
        except Exception as e:
            st.error(f"Error loading users: {str(e)}")
    
    def _show_create_user(self, current_user_id: str):
        st.subheader("➕ Create New User")
        
        with st.form("create_user_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                username = st.text_input("Username*")
                email = st.text_input("Email*")
                full_name = st.text_input("Full Name*")
                password = st.text_input("Password*", type="password")
            
            with col2:
                role = st.selectbox("Role*", ["user", "manager", "admin"])
                organization = st.text_input("Organization")
                department = st.text_input("Department")
            
            submitted = st.form_submit_button("Create User", type="primary")
            
            if submitted:
                if all([username, email, full_name, password, role]):
                    user_data = {
                        'username': username,
                        'email': email,
                        'full_name': full_name,
                        'password': password,
                        'role': role,
                        'organization': organization,
                        'department': department
                    }
                    
                    result = self.user_manager.create_user_advanced(user_data, current_user_id)
                    
                    if result['success']:
                        st.success("User created successfully!")
                    else:
                        st.error(result['message'])
                else:
                    st.error("Please fill in all required fields.")

def show_user_management_page(user_manager, db_manager, current_user_id: str, current_user_role: str):
    user_management_interface = UserManagementInterface(db_manager)
    user_management_interface.show_user_management_interface(current_user_id, current_user_role)
