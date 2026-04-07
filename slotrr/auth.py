from .db import db
from typing import Optional, Dict

class AuthManager:
    def __init__(self):
        self.current_user: Optional[Dict] = None

    def login(self, email: str, password: str, role: str) -> bool:
        user = db.authenticate_user(email, password)
        if user and user['role'] == role:
            self.current_user = user
            return True
        return False

    def logout(self):
        self.current_user = None

    def get_current_user(self) -> Optional[Dict]:
        return self.current_user

    def is_admin(self) -> bool:
        return self.current_user and self.current_user['role'] == 'admin'

    def is_teacher(self) -> bool:
        return self.current_user and self.current_user['role'] == 'teacher'

    def is_student(self) -> bool:
        return self.current_user and self.current_user['role'] == 'student'

# Global auth instance
auth = AuthManager()