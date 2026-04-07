import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from .config import SMTP_SERVER, SMTP_PORT, SMTP_USERNAME, SMTP_PASSWORD
from typing import List, Dict

class EmailService:
    def __init__(self):
        self.server = SMTP_SERVER
        self.port = SMTP_PORT
        self.username = SMTP_USERNAME
        self.password = SMTP_PASSWORD

    def send_email(self, to: str, subject: str, body: str):
        msg = MIMEMultipart()
        msg['From'] = self.username
        msg['To'] = to
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP(self.server, self.port)
        server.starttls()
        server.login(self.username, self.password)
        text = msg.as_string()
        server.sendmail(self.username, to, text)
        server.quit()

    def send_lecture_notification(self, student_email: str, student_name: str, teacher_name: str, subject: str, room: str, date: str, start_time: str, end_time: str):
        subject_line = f"📚 Lecture Scheduled – {subject}"
        body = f"""Hello {student_name},

A new lecture has been scheduled for you. Here are the details:

📖 Subject     : {subject}
👨‍🏫 Teacher     : {teacher_name}
🏫 Classroom   : {room}
📅 Date        : {date}
⏰ Time        : {start_time} – {end_time}

Please make sure to arrive on time. The classroom will be locked 10 minutes after the lecture starts.

If you have any questions, contact your teacher or the admin.

Best regards,
SLOTRR Classroom Management System
"""
        self.send_email(student_email, subject_line, body)

    def send_admin_booking_alert(self, admin_email: str, teacher_name: str, subject: str, room: str, date: str, start_time: str, end_time: str, students: List[str]):
        subject_line = f"🔔 New Booking Alert – {room} by {teacher_name}"
        student_list = ', '.join(students)
        body = f"""Hello Admin,

A new classroom booking has been made. Here's a summary:

👨‍🏫 Teacher     : {teacher_name}
📖 Subject     : {subject}
🏫 Classroom   : {room}
📅 Date        : {date}
⏰ Time        : {start_time} – {end_time}
👥 Students    : {student_list}

You can review or cancel this booking from the Admin Dashboard.

— SLOTRR System
"""
        self.send_email(admin_email, subject_line, body)

# Global email service instance
email_service = EmailService()