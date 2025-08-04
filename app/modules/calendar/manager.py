# calendar_integration_system.py
# Calendar Integration & Email Notifications

import streamlit as st
import pandas as pd
import datetime
import json
import uuid
from typing import Dict, List, Optional, Tuple
import smtplib
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
from email.mime.base import MimeBase
from email import encoders
import sqlite3
import calendar as cal
import plotly.express as px
import plotly.graph_objects as go
from dataclasses import dataclass
import threading
import time
import schedule

@dataclass
class CalendarEvent:
    """Calendar event data structure"""
    id: str
    user_id: str
    title: str
    description: str
    start_time: datetime.datetime
    end_time: datetime.datetime
    event_type: str
    status: str
    reminder_minutes: int = 60
    created_at: datetime.datetime = None

@dataclass
class EmailNotification:
    """Email notification data structure"""
    id: str
    user_id: str
    notification_type: str
    subject: str
    body: str
    scheduled_at: datetime.datetime
    sent_at: datetime.datetime = None
    status: str = 'pending'

class EmailManager:
    """Email notification management system"""
    
    def __init__(self, db_manager, smtp_server: str = "smtp.gmail.com", 
                 smtp_port: int = 587, sender_email: str = None, sender_password: str = None):
        self.db = db_manager
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.sender_email = sender_email or st.secrets.get("email", {}).get("sender_email")
        self.sender_password = sender_password or st.secrets.get("email", {}).get("sender_password")
        
        # Email templates
        self.templates = {
            'assessment_reminder': {
                'subject': '🧠 STRIVE Pro - Assessment Reminder',
                'template': '''
                Dear {full_name},
                
                This is a friendly reminder to complete your {assessment_type} assessment.
                
                Regular assessments help you track your wellness journey and identify areas for improvement.
                
                📊 Assessment: {assessment_type}
                ⏰ Due: {due_date}
                🔗 Complete now: {assessment_link}
                
                Benefits of regular assessments:
                • Track your progress over time
                • Identify trends and patterns
                • Get personalized recommendations
                • Maintain your wellness goals
                
                If you have any questions, please don't hesitate to reach out.
                
                Best regards,
                STRIVE Pro Team
                '''
            },
            'assessment_completed': {
                'subject': '✅ Assessment Completed - Results Available',
                'template': '''
                Dear {full_name},
                
                Thank you for completing your {assessment_type} assessment!
                
                Your results are now available in your STRIVE Pro dashboard.
                
                📊 Assessment: {assessment_type}
                📅 Completed: {completion_date}
                🎯 Score: {score_summary}
                
                Key insights from your assessment:
                {key_insights}
                
                📄 View detailed results: {results_link}
                📈 Track your progress: {progress_link}
                
                Remember, consistent self-monitoring is key to maintaining good mental health.
                
                Best regards,
                STRIVE Pro Team
                '''
            },
            'weekly_summary': {
                'subject': '📈 Your Weekly Wellness Summary',
                'template': '''
                Dear {full_name},
                
                Here's your wellness summary for the week of {week_start} - {week_end}:
                
                📊 Assessments Completed: {assessments_count}
                📈 Progress Trend: {trend_summary}
                🎯 Current Status: {current_status}
                
                This Week's Highlights:
                {weekly_highlights}
                
                Recommended Actions:
                {recommendations}
                
                📱 View full dashboard: {dashboard_link}
                📄 Download report: {report_link}
                
                Keep up the great work on your wellness journey!
                
                Best regards,
                STRIVE Pro Team
                '''
            },
            'follow_up': {
                'subject': '💙 How are you doing? - Wellness Check-in',
                'template': '''
                Dear {full_name},
                
                We wanted to check in and see how you're doing since your last assessment.
                
                📅 Last Assessment: {last_assessment_date}
                📊 Assessment Type: {assessment_type}
                🎯 Results: {last_results}
                
                It's been {days_since} days since your last check-in. Regular monitoring helps maintain your wellness goals.
                
                Consider taking a quick assessment to:
                • Track your current state
                • Monitor any changes
                • Get updated recommendations
                • Maintain your wellness routine
                
                🔗 Take a quick assessment: {assessment_link}
                💬 Need support? Contact us: {support_link}
                
                Your wellness matters to us.
                
                Best regards,
                STRIVE Pro Team
                '''
            }
        }
    
    def send_email(self, to_email: str, subject: str, body: str, html_body: str = None) -> bool:
        """Send email notification"""
        try:
            if not self.sender_email or not self.sender_password:
                st.error("Email configuration not found. Please configure email settings.")
                return False
            
            msg = MimeMultipart('alternative')
            msg['From'] = self.sender_email
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Add text body
            msg.attach(MimeText(body, 'plain'))
            
            # Add HTML body if provided
            if html_body:
                msg.attach(MimeText(html_body, 'html'))
            
            # Send email
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.sender_email, self.sender_password)
            server.sendmail(self.sender_email, to_email, msg.as_string())
            server.quit()
            
            return True
            
        except Exception as e:
            st.error(f"Failed to send email: {str(e)}")
            return False
    
    def schedule_notification(self, user_id: str, notification_type: str, 
                            scheduled_at: datetime.datetime, **template_vars) -> str:
        """Schedule email notification"""
        try:
            # Get email template
            template_info = self.templates.get(notification_type)
            if not template_info:
                raise ValueError(f"Unknown notification type: {notification_type}")
            
            # Format email content
            subject = template_info['subject'].format(**template_vars)
            body = template_info['template'].format(**template_vars)
            
            # Save to database
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            notification_id = str(uuid.uuid4())
            cursor.execute('''
                INSERT INTO email_notifications 
                (id, user_id, notification_type, subject, body, scheduled_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (notification_id, user_id, notification_type, subject, body, scheduled_at.isoformat()))
            
            conn.commit()
            conn.close()
            
            return notification_id
            
        except Exception as e:
            st.error(f"Failed to schedule notification: {str(e)}")
            return None
    
    def send_scheduled_notifications(self):
        """Send pending scheduled notifications"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            # Get pending notifications that are due
            cursor.execute('''
                SELECT en.id, en.user_id, en.subject, en.body, u.email, u.full_name
                FROM email_notifications en
                JOIN users u ON en.user_id = u.id
                WHERE en.status = 'pending' 
                AND en.scheduled_at <= ?
            ''', (datetime.datetime.now().isoformat(),))
            
            notifications = cursor.fetchall()
            
            for notification in notifications:
                notification_id, user_id, subject, body, email, full_name = notification
                
                # Send email
                success = self.send_email(email, subject, body)
                
                # Update status
                if success:
                    cursor.execute('''
                        UPDATE email_notifications 
                        SET status = 'sent', sent_at = ?
                        WHERE id = ?
                    ''', (datetime.datetime.now().isoformat(), notification_id))
                else:
                    cursor.execute('''
                        UPDATE email_notifications 
                        SET status = 'failed'
                        WHERE id = ?
                    ''', (notification_id,))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            st.error(f"Error sending scheduled notifications: {str(e)}")

class CalendarManager:
    """Calendar and scheduling management system"""
    
    def __init__(self, db_manager, email_manager):
        self.db = db_manager
        self.email_manager = email_manager
    
    def create_event(self, user_id: str, title: str, description: str,
                    start_time: datetime.datetime, end_time: datetime.datetime = None,
                    event_type: str = 'assessment', reminder_minutes: int = 60) -> str:
        """Create calendar event"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            event_id = str(uuid.uuid4())
            
            # Set end time if not provided
            if end_time is None:
                end_time = start_time + datetime.timedelta(minutes=30)
            
            cursor.execute('''
                INSERT INTO calendar_events 
                (id, user_id, title, description, start_time, end_time, event_type, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (event_id, user_id, title, description, start_time.isoformat(), 
                  end_time.isoformat(), event_type, 'scheduled'))
            
            conn.commit()
            conn.close()
            
            # Schedule reminder notification
            if reminder_minutes > 0:
                reminder_time = start_time - datetime.timedelta(minutes=reminder_minutes)
                self._schedule_reminder(user_id, event_id, title, reminder_time)
            
            return event_id
            
        except Exception as e:
            st.error(f"Failed to create event: {str(e)}")
            return None
    
    def get_user_events(self, user_id: str, start_date: datetime.date = None, 
                       end_date: datetime.date = None) -> List[Dict]:
        """Get user's calendar events"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        query = '''
            SELECT id, title, description, start_time, end_time, event_type, status
            FROM calendar_events 
            WHERE user_id = ?
        '''
        params = [user_id]
        
        if start_date:
            query += ' AND DATE(start_time) >= ?'
            params.append(start_date.isoformat())
        
        if end_date:
            query += ' AND DATE(start_time) <= ?'
            params.append(end_date.isoformat())
        
        query += ' ORDER BY start_time'
        
        cursor.execute(query, params)
        results = cursor.fetchall()
        conn.close()
        
        events = []
        for result in results:
            events.append({
                'id': result[0],
                'title': result[1],
                'description': result[2],
                'start_time': datetime.datetime.fromisoformat(result[3]),
                'end_time': datetime.datetime.fromisoformat(result[4]),
                'event_type': result[5],
                'status': result[6]
            })
        
        return events
    
    def schedule_recurring_assessments(self, user_id: str, assessment_type: str,
                                     frequency: str, start_date: datetime.date,
                                     preferred_time: datetime.time, count: int = 12) -> List[str]:
        """Schedule recurring assessment reminders"""
        event_ids = []
        
        for i in range(count):
            # Calculate next date based on frequency
            if frequency == 'weekly':
                next_date = start_date + datetime.timedelta(weeks=i)
            elif frequency == 'biweekly':
                next_date = start_date + datetime.timedelta(weeks=i*2)
            elif frequency == 'monthly':
                # Approximate monthly scheduling
                next_date = start_date + datetime.timedelta(days=i*30)
            elif frequency == 'quarterly':
                next_date = start_date + datetime.timedelta(days=i*90)
            else:
                continue
            
            # Create datetime
            event_datetime = datetime.datetime.combine(next_date, preferred_time)
            
            # Create event
            title = f"{assessment_type.upper()} Assessment Due"
            description = f"Time to complete your {assessment_type} assessment. Regular monitoring helps track your wellness progress."
            
            event_id = self.create_event(
                user_id, title, description, event_datetime,
                event_type='assessment_reminder'
            )
            
            if event_id:
                event_ids.append(event_id)
        
        return event_ids
    
    def _schedule_reminder(self, user_id: str, event_id: str, title: str, 
                          reminder_time: datetime.datetime):
        """Schedule reminder notification for event"""
        # Get user info
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT full_name FROM users WHERE id = ?', (user_id,))
        result = cursor.fetchone()
        conn.close()
        
        if result:
            full_name = result[0]
            
            # Schedule reminder email
            self.email_manager.schedule_notification(
                user_id,
                'assessment_reminder',
                reminder_time,
                full_name=full_name,
                assessment_type=title.replace(' Assessment Due', ''),
                due_date=reminder_time.strftime('%B %d, %Y at %I:%M %p'),
                assessment_link="https://your-app-url.com/assessments"
            )

class CalendarInterface:
    """Streamlit interface for calendar functionality"""
    
    def __init__(self, db_manager, user_manager, email_manager):
        self.db = db_manager
        self.user_manager = user_manager
        self.email_manager = email_manager
        self.calendar_manager = CalendarManager(db_manager, email_manager)
    
    def show_calendar_interface(self, user_id: str, user_role: str):
        """Show main calendar interface"""
        st.title("📅 Assessment Calendar & Scheduling")
        
        tab1, tab2, tab3, tab4 = st.tabs(["Calendar View", "Schedule Assessments", "Notifications", "Settings"])
        
        with tab1:
            self._show_calendar_view(user_id)
        
        with tab2:
            self._show_assessment_scheduling(user_id)
        
        with tab3:
            self._show_notifications_management(user_id)
        
        with tab4:
            self._show_calendar_settings(user_id)
    
    def _show_calendar_view(self, user_id: str):
        """Show calendar view with events"""
        st.subheader("📆 Your Assessment Calendar")
        
        # Date range selector
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Start Date", datetime.date.today())
        with col2:
            end_date = st.date_input("End Date", datetime.date.today() + datetime.timedelta(days=30))
        
        # Get events
        events = self.calendar_manager.get_user_events(user_id, start_date, end_date)
        
        if events:
            # Create calendar visualization
            self._create_calendar_chart(events)
            
            # Events list
            st.subheader("📋 Upcoming Events")
            
            for event in events:
                with st.expander(f"{event['title']} - {event['start_time'].strftime('%B %d, %Y at %I:%M %p')}"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**Type:** {event['event_type'].replace('_', ' ').title()}")
                        st.write(f"**Status:** {event['status'].title()}")
                        st.write(f"**Duration:** {event['start_time'].strftime('%I:%M %p')} - {event['end_time'].strftime('%I:%M %p')}")
                    
                    with col2:
                        st.write(f"**Description:**")
                        st.write(event['description'])
                    
                    # Action buttons
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        if st.button(f"✅ Complete", key=f"complete_{event['id']}"):
                            self._mark_event_completed(event['id'])
                            st.rerun()
                    
                    with col2:
                        if st.button(f"⏰ Reschedule", key=f"reschedule_{event['id']}"):
                            st.session_state[f"reschedule_{event['id']}"] = True
                    
                    with col3:
                        if st.button(f"❌ Cancel", key=f"cancel_{event['id']}"):
                            self._cancel_event(event['id'])
                            st.rerun()
        else:
            st.info("No events scheduled in the selected date range.")
            st.markdown("**💡 Tip:** Use the 'Schedule Assessments' tab to set up recurring assessment reminders.")
    
    def _show_assessment_scheduling(self, user_id: str):
        """Show assessment scheduling interface"""
        st.subheader("📝 Schedule Regular Assessments")
        
        col1, col2 = st.columns(2)
        
        with col1:
            assessment_types = ['PSS-10 (Stress)', 'DASS-21 (Mental Health)', 'Burnout Assessment', 
                              'Work-Life Balance', 'Job Satisfaction']
            selected_assessment = st.selectbox("Assessment Type", assessment_types)
            
            frequency_options = ['weekly', 'biweekly', 'monthly', 'quarterly']
            frequency = st.selectbox("Frequency", frequency_options)
            
            start_date = st.date_input("Start Date", datetime.date.today() + datetime.timedelta(days=1))
        
        with col2:
            preferred_time = st.time_input("Preferred Time", datetime.time(9, 0))
            
            reminder_options = [15, 30, 60, 120, 1440]  # minutes
            reminder_labels = ['15 minutes', '30 minutes', '1 hour', '2 hours', '1 day']
            reminder_minutes = st.selectbox("Reminder Time", 
                                          options=reminder_options,
                                          format_func=lambda x: reminder_labels[reminder_options.index(x)])
            
            count = st.number_input("Number of Reminders", min_value=1, max_value=52, value=12)
        
        if st.button("📅 Schedule Assessments", type="primary"):
            assessment_type = selected_assessment.split(' (')[0].lower().replace('-', '').replace(' ', '')
            
            event_ids = self.calendar_manager.schedule_recurring_assessments(
                user_id, assessment_type, frequency, start_date, preferred_time, count
            )
            
            if event_ids:
                st.success(f"Successfully scheduled {len(event_ids)} assessment reminders!")
                st.info(f"You will receive email reminders {reminder_labels[reminder_options.index(reminder_minutes)]} before each assessment.")
            else:
                st.error("Failed to schedule assessments. Please try again.")
        
        # Show existing scheduled assessments
        st.subheader("📊 Current Assessment Schedule")
        
        upcoming_events = self.calendar_manager.get_user_events(
            user_id, 
            datetime.date.today(),
            datetime.date.today() + datetime.timedelta(days=90)
        )
        
        assessment_events = [e for e in upcoming_events if e['event_type'] in ['assessment', 'assessment_reminder']]
        
        if assessment_events:
            schedule_df = pd.DataFrame([
                {
                    'Assessment': e['title'].replace(' Assessment Due', ''),
                    'Date': e['start_time'].strftime('%B %d, %Y'),
                    'Time': e['start_time'].strftime('%I:%M %p'),
                    'Status': e['status'].title()
                }
                for e in assessment_events
            ])
            
            st.dataframe(schedule_df, use_container_width=True)
        else:
            st.info("No assessment reminders scheduled.")
    
    def _show_notifications_management(self, user_id: str):
        """Show notifications management interface"""
        st.subheader("📧 Email Notifications")
        
        # Notification preferences
        st.subheader("🔔 Notification Preferences")
        
        col1, col2 = st.columns(2)
        
        with col1:
            assessment_reminders = st.checkbox("Assessment Reminders", value=True)
            completion_confirmations = st.checkbox("Completion Confirmations", value=True)
            weekly_summaries = st.checkbox("Weekly Progress Summaries", value=False)
            
        with col2:
            follow_up_reminders = st.checkbox("Follow-up Reminders", value=True)
            wellness_tips = st.checkbox("Wellness Tips & Insights", value=False)
            emergency_alerts = st.checkbox("Emergency Support Alerts", value=True)
        
        if st.button("💾 Save Preferences"):
            preferences = {
                'assessment_reminders': assessment_reminders,
                'completion_confirmations': completion_confirmations,
                'weekly_summaries': weekly_summaries,
                'follow_up_reminders': follow_up_reminders,
                'wellness_tips': wellness_tips,
                'emergency_alerts': emergency_alerts
            }
            
            self._save_notification_preferences(user_id, preferences)
            st.success("Notification preferences saved!")
        
        # Recent notifications
        st.subheader("📬 Recent Notifications")
        recent_notifications = self._get_recent_notifications(user_id)
        
        if recent_notifications:
            for notif in recent_notifications:
                status_color = "🟢" if notif['status'] == 'sent' else "🟡" if notif['status'] == 'pending' else "🔴"
                
                with st.expander(f"{status_color} {notif['subject']} - {notif['scheduled_at'][:10]}"):
                    st.write(f"**Type:** {notif['notification_type'].replace('_', ' ').title()}")
                    st.write(f"**Status:** {notif['status'].title()}")
                    st.write(f"**Scheduled:** {notif['scheduled_at']}")
                    if notif['sent_at']:
                        st.write(f"**Sent:** {notif['sent_at']}")
        else:
            st.info("No recent notifications.")
    
    def _show_calendar_settings(self, user_id: str):
        """Show calendar settings interface"""
        st.subheader("⚙️ Calendar Settings")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🕐 Time Preferences")
            timezone = st.selectbox("Timezone", ['UTC', 'PST', 'EST', 'CST', 'MST'])
            work_start = st.time_input("Work Day Start", datetime.time(9, 0))
            work_end = st.time_input("Work Day End", datetime.time(17, 0))
            
        with col2:
            st.subheader("📅 Calendar Integration")
            calendar_provider = st.selectbox("Calendar Provider", ['None', 'Google Calendar', 'Outlook', 'Apple Calendar'])
            sync_enabled = st.checkbox("Enable Calendar Sync", value=False)
            
            if calendar_provider != 'None' and sync_enabled:
                st.info(f"Calendar sync with {calendar_provider} would be configured here.")
        
        st.subheader("🎯 Default Assessment Schedule")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            default_stress_freq = st.selectbox("Stress Assessment", ['weekly', 'biweekly', 'monthly'], index=2)
        
        with col2:
            default_mental_health_freq = st.selectbox("Mental Health Assessment", ['monthly', 'quarterly', 'biannually'], index=1)
        
        with col3:
            default_burnout_freq = st.selectbox("Burnout Assessment", ['monthly', 'quarterly', 'biannually'], index=1)
        
        if st.button("💾 Save Settings"):
            settings = {
                'timezone': timezone,
                'work_start': work_start.isoformat(),
                'work_end': work_end.isoformat(),
                'calendar_provider': calendar_provider,
                'sync_enabled': sync_enabled,
                'default_frequencies': {
                    'stress': default_stress_freq,
                    'mental_health': default_mental_health_freq,
                    'burnout': default_burnout_freq
                }
            }
            
            self._save_calendar_settings(user_id, settings)
            st.success("Calendar settings saved!")
    
    def _create_calendar_chart(self, events: List[Dict]):
        """Create calendar visualization"""
        if not events:
            return
        
        # Create event data for chart
        event_data = []
        for event in events:
            event_data.append({
                'Date': event['start_time'].date(),
                'Time': event['start_time'].time(),
                'Event': event['title'],
                'Type': event['event_type'].replace('_', ' ').title(),
                'Status': event['status'].title()
            })
        
        df = pd.DataFrame(event_data)
        
        # Create timeline chart
        fig = px.timeline(df, x_start="Date", x_end="Date", y="Event", color="Status",
                         title="Assessment Calendar Timeline")
        
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    def _mark_event_completed(self, event_id: str):
        """Mark event as completed"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE calendar_events 
            SET status = 'completed'
            WHERE id = ?
        ''', (event_id,))
        
        conn.commit()
        conn.close()
    
    def _cancel_event(self, event_id: str):
        """Cancel event"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE calendar_events 
            SET status = 'cancelled'
            WHERE id = ?
        ''', (event_id,))
        
        conn.commit()
        conn.close()
    
    def _save_notification_preferences(self, user_id: str, preferences: Dict):
        """Save user notification preferences"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE users 
            SET notification_preferences = ?
            WHERE id = ?
        ''', (json.dumps(preferences), user_id))
        
        conn.commit()
        conn.close()
    
    def _save_calendar_settings(self, user_id: str, settings: Dict):
        """Save user calendar settings"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        # Get current profile data
        cursor.execute('SELECT profile_data FROM users WHERE id = ?', (user_id,))
        result = cursor.fetchone()
        
        profile_data = json.loads(result[0]) if result and result[0] else {}
        profile_data['calendar_settings'] = settings
        
        cursor.execute('''
            UPDATE users 
            SET profile_data = ?
            WHERE id = ?
        ''', (json.dumps(profile_data), user_id))
        
        conn.commit()
        conn.close()
    
    def _get_recent_notifications(self, user_id: str) -> List[Dict]:
        """Get recent notifications for user"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT notification_type, subject, scheduled_at, sent_at, status
            FROM email_notifications 
            WHERE user_id = ?
            ORDER BY scheduled_at DESC LIMIT 10
        ''', (user_id,))
        
        results = cursor.fetchall()
        conn.close()
        
        return [
            {
                'notification_type': r[0],
                'subject': r[1],
                'scheduled_at': r[2],
                'sent_at': r[3],
                'status': r[4]
            }
            for r in results
        ]

# Background notification service
class NotificationService:
    """Background service for sending scheduled notifications"""
    
    def __init__(self, email_manager):
        self.email_manager = email_manager
        self.running = False
    
    def start_service(self):
        """Start the notification service"""
        self.running = True
        
        # Schedule the notification check every minute
        schedule.every(1).minutes.do(self.check_and_send_notifications)
        
        # Run in background thread
        def run_scheduler():
            while self.running:
                schedule.run_pending()
                time.sleep(60)
        
        thread = threading.Thread(target=run_scheduler, daemon=True)
        thread.start()
    
    def stop_service(self):
        """Stop the notification service"""
        self.running = False
    
    def check_and_send_notifications(self):
        """Check and send due notifications"""
        self.email_manager.send_scheduled_notifications()

# Usage in main app:
def show_calendar_page(db_manager, user_id, user_manager):
    """Show calendar page with full functionality"""
    email_manager = EmailManager(db_manager)
    calendar_interface = CalendarInterface(db_manager, user_manager, email_manager)
    calendar_interface.show_calendar_interface(user_id, st.session_state.user_info['role'])