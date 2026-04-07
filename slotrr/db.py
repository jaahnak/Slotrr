from supabase import create_client, Client
from .config import SUPABASE_URL, SUPABASE_ANON_KEY
import bcrypt
from datetime import datetime, date, time
from typing import List, Dict, Optional

class Database:
    def __init__(self):
        self._client = None

    def _get_client(self):
        if self._client is None:
            if not SUPABASE_URL or not SUPABASE_ANON_KEY:
                raise ValueError("Supabase credentials not configured. Please set SUPABASE_URL and SUPABASE_ANON_KEY environment variables.")
            self._client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
        return self._client

    # User operations
    def create_user(self, full_name: str, email: str, password: str, role: str) -> Dict:
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        return self._get_client().table('users').insert({
            'full_name': full_name,
            'email': email,
            'password_hash': password_hash,
            'role': role
        }).execute()

    def authenticate_user(self, email: str, password: str) -> Optional[Dict]:
        response = self._get_client().table('users').select('*').eq('email', email).execute()
        if response.data:
            user = response.data[0]
            if bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
                return user
        return None

    def get_users_by_role(self, role: str) -> List[Dict]:
        return self._get_client().table('users').select('*').eq('role', role).execute().data

    def get_all_users(self) -> List[Dict]:
        return self._get_client().table('users').select('*').execute().data

    def update_user(self, user_id: str, updates: Dict) -> Dict:
        return self._get_client().table('users').update(updates).eq('id', user_id).execute()

    def delete_user(self, user_id: str) -> Dict:
        return self._get_client().table('users').delete().eq('id', user_id).execute()

    # Classroom operations
    def get_all_classrooms(self) -> List[Dict]:
        return self._get_client().table('classrooms').select('*').eq('is_active', True).execute().data

    def create_classroom(self, name: str, capacity: int, floor: int, building: str) -> Dict:
        return self._get_client().table('classrooms').insert({
            'name': name,
            'capacity': capacity,
            'floor': floor,
            'building': building,
            'is_active': True
        }).execute()

    def update_classroom(self, room_id: str, updates: Dict) -> Dict:
        return self._get_client().table('classrooms').update(updates).eq('id', room_id).execute()

    def delete_classroom(self, room_id: str) -> Dict:
        return self._get_client().table('classrooms').delete().eq('id', room_id).execute()

    # Booking operations
    def create_booking(self, room_id: str, teacher_id: str, subject_name: str, date: date, start_time: time, end_time: time, note: Optional[str] = None) -> Dict:
        return self._get_client().table('bookings').insert({
            'room_id': room_id,
            'teacher_id': teacher_id,
            'subject_name': subject_name,
            'date': date.isoformat(),
            'start_time': start_time.isoformat(),
            'end_time': end_time.isoformat(),
            'note': note
        }).execute()

    def get_bookings_for_date(self, date: date) -> List[Dict]:
        return self._get_client().table('bookings').select('*, classrooms(name), users(full_name)').eq('date', date.isoformat()).execute().data

    def get_bookings_for_room_date(self, room_id: str, date: date) -> List[Dict]:
        return self._get_client().table('bookings').select('*').eq('room_id', room_id).eq('date', date.isoformat()).execute().data

    def get_user_bookings(self, user_id: str) -> List[Dict]:
        return self._get_client().table('bookings').select('*, classrooms(name)').eq('teacher_id', user_id).execute().data

    def cancel_booking(self, booking_id: str) -> Dict:
        return self._get_client().table('bookings').delete().eq('id', booking_id).execute()

    # Booking students
    def add_students_to_booking(self, booking_id: str, student_ids: List[str]):
        for student_id in student_ids:
            self._get_client().table('booking_students').insert({
                'booking_id': booking_id,
                'student_id': student_id
            }).execute()

    def get_students_for_booking(self, booking_id: str) -> List[Dict]:
        return self._get_client().table('booking_students').select('users(full_name, email)').eq('booking_id', booking_id).execute().data

    # Stats
    def get_stats(self) -> Dict:
        total_rooms = len(self.get_all_classrooms())
        today = date.today().isoformat()
        active_bookings = len(self._get_client().table('bookings').select('*').eq('date', today).execute().data)
        total_teachers = len(self.get_users_by_role('teacher'))
        total_students = len(self.get_users_by_role('student'))
        return {
            'total_rooms': total_rooms,
            'active_bookings_today': active_bookings,
            'total_teachers': total_teachers,
            'total_students': total_students
        }

    @property
    def client(self):
        return self._get_client()

# Global database instance
db = Database()