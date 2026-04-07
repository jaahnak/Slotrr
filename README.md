# SLOTRR - Classroom Booking System

[![PyPI version](https://badge.fury.io/py/slotrr.svg)](https://pypi.org/project/slotrr/)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tkinter](https://img.shields.io/badge/GUI-Tkinter-orange.svg)](https://docs.python.org/3/library/tkinter.html)

> A comprehensive classroom booking system with a beautiful Tkinter GUI, built for educational institutions to manage classroom reservations efficiently.

![SLOTRR Logo](https://img.shields.io/badge/SLOTRR-Classroom%20Booking-blue?style=for-the-badge&logo=calendar&logoColor=white)

## ✨ Features

### 🎨 Beautiful User Interface
- **Custom Tkinter Design**: Handcrafted UI with rounded corners, shadows, and smooth animations
- **Dark/Light Theme Toggle**: Instant theme switching with persistent preferences
- **Responsive Layout**: Adapts to different window sizes gracefully
- **Modern Navigation**: Horizontal top navigation bar with active indicators

### 🔐 Role-Based Access Control
- **Admin Dashboard**: Full CRUD operations on rooms, users, and bookings
- **Teacher Portal**: Book classrooms and manage personal bookings
- **Student Integration**: Email notifications for scheduled lectures
- **Secure Authentication**: Password hashing with bcrypt

### 📅 Advanced Booking System
- **Real-time Availability**: Check room availability instantly
- **Conflict Detection**: Prevents double-bookings automatically
- **Time Slot Management**: Flexible scheduling with custom time slots
- **Multi-student Selection**: Searchable dropdown for student selection
- **Booking History**: Complete history with filtering options

### 📧 Email Notifications
- **Automated Emails**: Instant notifications to students and admins
- **Custom Templates**: Professional email templates with branding
- **SMTP Integration**: Secure email delivery via Gmail SMTP
- **Booking Confirmations**: Detailed booking summaries

### 🗺️ Campus Visualization
- **Interactive Map**: Visual grid-based campus layout
- **Color Coding**: Green (available), Red (booked), Yellow (partial)
- **Room Details**: Capacity, floor, building information
- **Date Navigation**: View availability for any date

### 📊 Analytics & Reports
- **Booking Statistics**: Most booked rooms, teacher activity
- **Visual Charts**: Canvas-drawn bar and line charts
- **CSV Export**: Download reports for external analysis
- **Real-time Metrics**: Live dashboard with key performance indicators

## 🚀 Quick Start

### Installation

```bash
pip install slotrr
```

### Basic Usage

```bash
# Launch the application
slotrr
```

### Configuration

Create a `.env` file in your working directory:

```env
# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your_supabase_anon_key

# Email Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your_gmail_app_password
```

## 📋 Requirements

- **Python**: 3.8 or higher
- **Dependencies**:
  - `supabase` - Database backend
  - `bcrypt` - Password hashing
  - `Pillow` - Image processing
  - `python-dotenv` - Environment variables

## 🏗️ Architecture

```
slotrr/
├── main.py              # Application entry point
├── config.py            # Configuration management
├── db.py                # Supabase database operations
├── auth.py              # Authentication logic
├── email_service.py     # Email notification service
└── ui/
    ├── components.py    # Reusable UI components
    ├── theme.py         # Theme management
    ├── login_screen.py  # Authentication interface
    ├── admin/           # Admin-specific screens
    └── teacher/         # Teacher-specific screens
```

## 🎯 User Roles & Permissions

### 👑 Administrator
- **User Management**: Add/edit/delete users (teachers, students)
- **Room Management**: CRUD operations on classrooms
- **Booking Oversight**: View, approve, cancel any booking
- **Analytics**: Access to all reports and statistics
- **System Configuration**: Full system access

### 👨‍🏫 Teacher
- **Classroom Booking**: Reserve rooms for lectures
- **Student Management**: Select students for bookings
- **Booking History**: View and manage personal bookings
- **Schedule Planning**: Plan lectures with time slots

### 👨‍🎓 Student
- **Email Notifications**: Receive booking confirmations
- **Lecture Tracking**: Stay informed about scheduled classes
- **No Login Required**: Email-only integration

## 📧 Email Templates

### Student Notification
```
📚 Lecture Scheduled – [Subject Name]

Hello [Student Name],

A new lecture has been scheduled for you:

📖 Subject: [Subject Name]
👨‍🏫 Teacher: [Teacher Name]
🏫 Classroom: [Room Name]
📅 Date: [Date]
⏰ Time: [Start] – [End]

Please arrive on time!

Best regards,
SLOTRR Team
```

### Admin Alert
```
🔔 New Booking Alert – [Room Name]

Hello Admin,

New booking created:

👨‍🏫 Teacher: [Teacher Name]
📖 Subject: [Subject Name]
👥 Students: [Count] enrolled

View details in Admin Dashboard.

— SLOTRR System
```

## 🗄️ Database Schema

### Core Tables
- **`users`**: User accounts with role-based access
- **`classrooms`**: Room information and capacity
- **`bookings`**: Reservation records with time slots
- **`booking_students`**: Many-to-many student assignments

### Sample Data
The package includes SQL scripts for sample data including:
- Pre-configured admin account
- Sample classrooms across multiple buildings
- Test users for each role

## 🔧 Development Setup

```bash
# Clone repository
git clone https://github.com/yourusername/slotrr.git
cd slotrr

# Install in development mode
pip install -e .

# Run application
slotrr
```

## 🧪 Testing

```bash
# Run with test database
export SUPABASE_URL=test_url
export SUPABASE_ANON_KEY=test_key

# Launch app
slotrr
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [Tkinter](https://docs.python.org/3/library/tkinter.html) for the GUI
- Powered by [Supabase](https://supabase.com/) for the backend
- Email service using Python's `smtplib`

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/slotrr/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/slotrr/discussions)
- **Email**: support@slotrr.com

---

**SLOTRR** - Making classroom management simple and beautiful! 🎓✨

## Development

Clone the repo and install dependencies:

```bash
git clone <repo-url>
cd slotrr
pip install -r requirements.txt
python -m slotrr.main
```

## License

MIT License