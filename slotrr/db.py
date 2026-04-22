import sqlite3
import bcrypt
import uuid
import os
from datetime import datetime, date, time
from typing import List, Dict, Optional

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'slotrr_local.db')


class Database:
    def __init__(self):
        self._conn = None
        self._ensure_tables()
        self._seed_data()

    def _get_conn(self):
        if self._conn is None:
            self._conn = sqlite3.connect(DB_PATH)
            self._conn.row_factory = sqlite3.Row
            self._conn.execute("PRAGMA foreign_keys = ON")
        return self._conn

    def _ensure_tables(self):
        conn = self._get_conn()
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                full_name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL,
                created_at TEXT DEFAULT (datetime('now'))
            );
            CREATE TABLE IF NOT EXISTS classrooms (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                capacity INTEGER NOT NULL,
                floor INTEGER NOT NULL,
                building TEXT NOT NULL,
                is_active INTEGER DEFAULT 1,
                created_at TEXT DEFAULT (datetime('now'))
            );
            CREATE TABLE IF NOT EXISTS bookings (
                id TEXT PRIMARY KEY,
                room_id TEXT NOT NULL,
                teacher_id TEXT NOT NULL,
                subject_name TEXT NOT NULL,
                date TEXT NOT NULL,
                start_time TEXT NOT NULL,
                end_time TEXT NOT NULL,
                note TEXT,
                created_at TEXT DEFAULT (datetime('now')),
                FOREIGN KEY (room_id) REFERENCES classrooms(id),
                FOREIGN KEY (teacher_id) REFERENCES users(id)
            );
            CREATE TABLE IF NOT EXISTS booking_students (
                id TEXT PRIMARY KEY,
                booking_id TEXT NOT NULL,
                student_id TEXT NOT NULL,
                FOREIGN KEY (booking_id) REFERENCES bookings(id),
                FOREIGN KEY (student_id) REFERENCES users(id)
            );
        """)
        conn.commit()

    def _seed_data(self):
        conn = self._get_conn()
        # Only seed if no users exist
        row = conn.execute("SELECT COUNT(*) as cnt FROM users").fetchone()
        if row['cnt'] > 0:
            return

        # Create default admin
        admin_hash = bcrypt.hashpw("admin123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        conn.execute("INSERT INTO users (id, full_name, email, password_hash, role) VALUES (?, ?, ?, ?, ?)",
                     (str(uuid.uuid4()), "Admin User", "admin@slotrr.com", admin_hash, "admin"))

        # Create a teacher
        teacher_hash = bcrypt.hashpw("teacher123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        teacher_id = str(uuid.uuid4())
        conn.execute("INSERT INTO users (id, full_name, email, password_hash, role) VALUES (?, ?, ?, ?, ?)",
                     (teacher_id, "Dr. Sharma", "sharma@slotrr.com", teacher_hash, "teacher"))

        # Create students
        student_hash = bcrypt.hashpw("student123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        student_names = [
            ("Aarav Patel", "aarav@student.com"),
            ("Priya Singh", "priya@student.com"),
            ("Rohan Gupta", "rohan@student.com"),
            ("Ananya Desai", "ananya@student.com"),
            ("Vikram Mehta", "vikram@student.com"),
        ]
        for name, email in student_names:
            conn.execute("INSERT INTO users (id, full_name, email, password_hash, role) VALUES (?, ?, ?, ?, ?)",
                         (str(uuid.uuid4()), name, email, student_hash, "student"))

        # Create classrooms
        classrooms = [
            ("Room 101", 40, 1, "Main Block"),
            ("Room 102", 35, 1, "Main Block"),
            ("Room 201", 50, 2, "Main Block"),
            ("Room 202", 30, 2, "Main Block"),
            ("Lab A", 25, 1, "Science Block"),
            ("Lab B", 25, 1, "Science Block"),
            ("Seminar Hall", 100, 3, "Main Block"),
            ("Room 301", 45, 3, "Main Block"),
            ("Room 103", 40, 1, "Arts Block"),
            ("Room 203", 35, 2, "Arts Block"),
        ]
        for name, cap, floor, building in classrooms:
            conn.execute("INSERT INTO classrooms (id, name, capacity, floor, building, is_active) VALUES (?, ?, ?, ?, ?, 1)",
                         (str(uuid.uuid4()), name, cap, floor, building))

        # Create a couple of sample bookings
        rooms = conn.execute("SELECT id FROM classrooms LIMIT 2").fetchall()
        if rooms:
            today = date.today().isoformat()
            b_id1 = str(uuid.uuid4())
            conn.execute("INSERT INTO bookings (id, room_id, teacher_id, subject_name, date, start_time, end_time, note) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                         (b_id1, rooms[0]['id'], teacher_id, "Mathematics", today, "09:00:00", "10:00:00", "Chapter 5 - Calculus"))
            b_id2 = str(uuid.uuid4())
            conn.execute("INSERT INTO bookings (id, room_id, teacher_id, subject_name, date, start_time, end_time, note) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                         (b_id2, rooms[1]['id'], teacher_id, "Physics", today, "11:00:00", "12:00:00", "Lab experiment"))

            # Add students to bookings
            students = conn.execute("SELECT id FROM users WHERE role='student' LIMIT 3").fetchall()
            for s in students:
                conn.execute("INSERT INTO booking_students (id, booking_id, student_id) VALUES (?, ?, ?)",
                             (str(uuid.uuid4()), b_id1, s['id']))

        conn.commit()

    def _row_to_dict(self, row):
        if row is None:
            return None
        return dict(row)

    def _rows_to_list(self, rows):
        return [dict(r) for r in rows]

    # ── User operations ──────────────────────────────────────────

    def create_user(self, full_name: str, email: str, password: str, role: str) -> Dict:
        conn = self._get_conn()
        user_id = str(uuid.uuid4())
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        conn.execute("INSERT INTO users (id, full_name, email, password_hash, role) VALUES (?, ?, ?, ?, ?)",
                     (user_id, full_name, email, password_hash, role))
        conn.commit()
        return self._row_to_dict(conn.execute("SELECT * FROM users WHERE id=?", (user_id,)).fetchone())

    def authenticate_user(self, email: str, password: str) -> Optional[Dict]:
        conn = self._get_conn()
        row = conn.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
        if row:
            user = dict(row)
            if bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
                return user
        return None

    def get_users_by_role(self, role: str) -> List[Dict]:
        conn = self._get_conn()
        return self._rows_to_list(conn.execute("SELECT * FROM users WHERE role=?", (role,)).fetchall())

    def get_all_users(self) -> List[Dict]:
        conn = self._get_conn()
        return self._rows_to_list(conn.execute("SELECT * FROM users").fetchall())

    def update_user(self, user_id: str, updates: Dict) -> Dict:
        conn = self._get_conn()
        set_clause = ", ".join(f"{k}=?" for k in updates)
        values = list(updates.values()) + [user_id]
        conn.execute(f"UPDATE users SET {set_clause} WHERE id=?", values)
        conn.commit()
        return self._row_to_dict(conn.execute("SELECT * FROM users WHERE id=?", (user_id,)).fetchone())

    def delete_user(self, user_id: str) -> None:
        conn = self._get_conn()
        conn.execute("DELETE FROM users WHERE id=?", (user_id,))
        conn.commit()

    # ── Classroom operations ─────────────────────────────────────

    def get_all_classrooms(self) -> List[Dict]:
        conn = self._get_conn()
        return self._rows_to_list(conn.execute("SELECT * FROM classrooms WHERE is_active=1").fetchall())

    def get_all_classrooms_including_inactive(self) -> List[Dict]:
        conn = self._get_conn()
        return self._rows_to_list(conn.execute("SELECT * FROM classrooms").fetchall())

    def get_classroom_by_id(self, room_id: str) -> Optional[Dict]:
        conn = self._get_conn()
        return self._row_to_dict(conn.execute("SELECT * FROM classrooms WHERE id=?", (room_id,)).fetchone())

    def create_classroom(self, name: str, capacity: int, floor: int, building: str) -> Dict:
        conn = self._get_conn()
        room_id = str(uuid.uuid4())
        conn.execute("INSERT INTO classrooms (id, name, capacity, floor, building, is_active) VALUES (?, ?, ?, ?, ?, 1)",
                     (room_id, name, capacity, floor, building))
        conn.commit()
        return self._row_to_dict(conn.execute("SELECT * FROM classrooms WHERE id=?", (room_id,)).fetchone())

    def update_classroom(self, room_id: str, updates: Dict) -> Dict:
        conn = self._get_conn()
        set_clause = ", ".join(f"{k}=?" for k in updates)
        values = list(updates.values()) + [room_id]
        conn.execute(f"UPDATE classrooms SET {set_clause} WHERE id=?", values)
        conn.commit()
        return self._row_to_dict(conn.execute("SELECT * FROM classrooms WHERE id=?", (room_id,)).fetchone())

    def delete_classroom(self, room_id: str) -> None:
        conn = self._get_conn()
        conn.execute("DELETE FROM classrooms WHERE id=?", (room_id,))
        conn.commit()

    # ── Booking operations ───────────────────────────────────────

    def create_booking(self, room_id: str, teacher_id: str, subject_name: str,
                       booking_date: date, start_time: time, end_time: time,
                       note: Optional[str] = None) -> Dict:
        conn = self._get_conn()
        booking_id = str(uuid.uuid4())
        conn.execute(
            "INSERT INTO bookings (id, room_id, teacher_id, subject_name, date, start_time, end_time, note) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (booking_id, room_id, teacher_id, subject_name,
             booking_date.isoformat() if isinstance(booking_date, date) else booking_date,
             start_time.isoformat() if isinstance(start_time, time) else start_time,
             end_time.isoformat() if isinstance(end_time, time) else end_time,
             note))
        conn.commit()
        booking = self._row_to_dict(conn.execute("SELECT * FROM bookings WHERE id=?", (booking_id,)).fetchone())
        # Wrap in a result-like object for compatibility  (booking.data[0]['id'])
        class Result:
            def __init__(self, data):
                self.data = data
        return Result([booking])

    def get_bookings_for_date(self, d: date) -> List[Dict]:
        conn = self._get_conn()
        date_str = d.isoformat() if isinstance(d, date) else d
        rows = conn.execute("""
            SELECT b.*, c.name as classroom_name, u.full_name as teacher_name
            FROM bookings b
            JOIN classrooms c ON b.room_id = c.id
            JOIN users u ON b.teacher_id = u.id
            WHERE b.date = ?
        """, (date_str,)).fetchall()
        result = []
        for r in rows:
            d_dict = dict(r)
            d_dict['classrooms'] = {'name': d_dict.pop('classroom_name')}
            d_dict['users'] = {'full_name': d_dict.pop('teacher_name')}
            result.append(d_dict)
        return result

    def get_bookings_for_room_date(self, room_id: str, d: date) -> List[Dict]:
        conn = self._get_conn()
        date_str = d.isoformat() if isinstance(d, date) else d
        return self._rows_to_list(
            conn.execute("SELECT * FROM bookings WHERE room_id=? AND date=?", (room_id, date_str)).fetchall())

    def get_user_bookings(self, user_id: str) -> List[Dict]:
        conn = self._get_conn()
        rows = conn.execute("""
            SELECT b.*, c.name as classroom_name
            FROM bookings b
            JOIN classrooms c ON b.room_id = c.id
            WHERE b.teacher_id = ?
            ORDER BY b.date DESC
        """, (user_id,)).fetchall()
        result = []
        for r in rows:
            d_dict = dict(r)
            d_dict['classrooms'] = {'name': d_dict.pop('classroom_name')}
            result.append(d_dict)
        return result

    def cancel_booking(self, booking_id: str) -> None:
        conn = self._get_conn()
        conn.execute("DELETE FROM booking_students WHERE booking_id=?", (booking_id,))
        conn.execute("DELETE FROM bookings WHERE id=?", (booking_id,))
        conn.commit()

    # ── Booking students ─────────────────────────────────────────

    def add_students_to_booking(self, booking_id: str, student_ids: List[str]):
        conn = self._get_conn()
        for student_id in student_ids:
            conn.execute("INSERT INTO booking_students (id, booking_id, student_id) VALUES (?, ?, ?)",
                         (str(uuid.uuid4()), booking_id, student_id))
        conn.commit()

    def get_students_for_booking(self, booking_id: str) -> List[Dict]:
        conn = self._get_conn()
        rows = conn.execute("""
            SELECT u.full_name, u.email
            FROM booking_students bs
            JOIN users u ON bs.student_id = u.id
            WHERE bs.booking_id = ?
        """, (booking_id,)).fetchall()
        return [{'users': {'full_name': r['full_name'], 'email': r['email']}} for r in rows]

    # ── Stats ────────────────────────────────────────────────────

    def get_stats(self) -> Dict:
        conn = self._get_conn()
        total_rooms = conn.execute("SELECT COUNT(*) as cnt FROM classrooms WHERE is_active=1").fetchone()['cnt']
        today = date.today().isoformat()
        active_bookings = conn.execute("SELECT COUNT(*) as cnt FROM bookings WHERE date=?", (today,)).fetchone()['cnt']
        total_teachers = conn.execute("SELECT COUNT(*) as cnt FROM users WHERE role='teacher'").fetchone()['cnt']
        total_students = conn.execute("SELECT COUNT(*) as cnt FROM users WHERE role='student'").fetchone()['cnt']
        return {
            'total_rooms': total_rooms,
            'active_bookings_today': active_bookings,
            'total_teachers': total_teachers,
            'total_students': total_students
        }

    # ── Methods used directly by UI code (replaces db.client.table(...)) ──

    def get_recent_bookings(self, limit: int = 10) -> List[Dict]:
        conn = self._get_conn()
        rows = conn.execute("""
            SELECT b.*, c.name as classroom_name, u.full_name as teacher_name
            FROM bookings b
            JOIN classrooms c ON b.room_id = c.id
            JOIN users u ON b.teacher_id = u.id
            ORDER BY b.created_at DESC
            LIMIT ?
        """, (limit,)).fetchall()
        result = []
        for r in rows:
            d_dict = dict(r)
            d_dict['classrooms'] = {'name': d_dict.pop('classroom_name')}
            d_dict['users'] = {'full_name': d_dict.pop('teacher_name')}
            result.append(d_dict)
        return result

    def get_all_bookings(self, date_filter: Optional[str] = None) -> List[Dict]:
        conn = self._get_conn()
        query = """
            SELECT b.*, c.name as classroom_name, u.full_name as teacher_name
            FROM bookings b
            JOIN classrooms c ON b.room_id = c.id
            JOIN users u ON b.teacher_id = u.id
        """
        params = ()
        if date_filter:
            query += " WHERE b.date = ?"
            params = (date_filter,)
        query += " ORDER BY b.date DESC, b.start_time"
        rows = conn.execute(query, params).fetchall()
        result = []
        for r in rows:
            d_dict = dict(r)
            d_dict['classrooms'] = {'name': d_dict.pop('classroom_name')}
            d_dict['users'] = {'full_name': d_dict.pop('teacher_name')}
            result.append(d_dict)
        return result

    def get_all_bookings_with_room(self) -> List[Dict]:
        """For reports - returns bookings with room info."""
        conn = self._get_conn()
        rows = conn.execute("""
            SELECT b.room_id, c.name as classroom_name
            FROM bookings b
            JOIN classrooms c ON b.room_id = c.id
        """).fetchall()
        return [{'room_id': r['room_id'], 'classrooms': {'name': r['classroom_name']}} for r in rows]

    def get_all_bookings_with_teacher(self) -> List[Dict]:
        """For reports - returns bookings with teacher info."""
        conn = self._get_conn()
        rows = conn.execute("""
            SELECT b.teacher_id, u.full_name as teacher_name
            FROM bookings b
            JOIN users u ON b.teacher_id = u.id
        """).fetchall()
        return [{'teacher_id': r['teacher_id'], 'users': {'full_name': r['teacher_name']}} for r in rows]

    def get_user_by_id(self, user_id: str) -> Optional[Dict]:
        conn = self._get_conn()
        return self._row_to_dict(conn.execute("SELECT * FROM users WHERE id=?", (user_id,)).fetchone())

    def get_classroom_name(self, room_id: str) -> str:
        room = self.get_classroom_by_id(room_id)
        return room['name'] if room else 'Unknown'


# Global database instance
db = Database()