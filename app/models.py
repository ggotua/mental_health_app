from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from . import login_manager
from .db import get_db

class User(UserMixin):
    def __init__(self, id, username, email, password):
        self.id = id
        self.username = username
        self.email = email
        self.password = password

    @staticmethod
    def get_by_id(user_id):
        with get_db() as conn:
            c = conn.cursor()
            c.execute("SELECT * FROM users WHERE id=?", (user_id,))
            user_data = c.fetchone()
        
        if user_data:
            return User(
                id=user_data[0],
                username=user_data[1],
                email=user_data[2],
                password=user_data[3]
            )
        return None

    @staticmethod
    def get_by_username(username):
        with get_db() as conn:
            c = conn.cursor()
            c.execute("SELECT * FROM users WHERE username=?", (username,))
            user_data = c.fetchone()
        
        if user_data:
            return User(
                id=user_data[0],
                username=user_data[1],
                email=user_data[2],
                password=user_data[3]
            )
        return None

    @staticmethod
    def create(username, email, password):
        hashed_password = generate_password_hash(password)
        with get_db() as conn:
            c = conn.cursor()
            c.execute(
                "INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
                (username, email, hashed_password)
            )
            user_id = c.lastrowid
            conn.commit()
        
        return User(
            id=user_id,
            username=username,
            email=email,
            password=hashed_password
        )

    def check_password(self, password):
        return check_password_hash(self.password, password)

class DailyReflection:
    def __init__(self, id, user_id, date, achievement_1, achievement_2, achievement_3, created_at=None, updated_at=None):
        self.id = id
        self.user_id = user_id
        self.date = date
        self.achievement_1 = achievement_1
        self.achievement_2 = achievement_2
        self.achievement_3 = achievement_3
        self.created_at = created_at
        self.updated_at = updated_at

    @staticmethod
    def create(user_id, date, achievement_1, achievement_2, achievement_3):
        with get_db() as conn:
            c = conn.cursor()
            c.execute(
                "INSERT INTO daily_reflections (user_id, date, achievement_1, achievement_2, achievement_3) VALUES (?, ?, ?, ?, ?)",
                (user_id, date, achievement_1, achievement_2, achievement_3)
            )
            reflection_id = c.lastrowid
            conn.commit()
        
        return DailyReflection(
            id=reflection_id,
            user_id=user_id,
            date=date,
            achievement_1=achievement_1,
            achievement_2=achievement_2,
            achievement_3=achievement_3
        )

    @staticmethod
    def get_by_user_and_date(user_id, date):
        with get_db() as conn:
            c = conn.cursor()
            c.execute(
                "SELECT * FROM daily_reflections WHERE user_id=? AND date=?",
                (user_id, date)
            )
            reflection_data = c.fetchone()
        
        if reflection_data:
            return DailyReflection(
                id=reflection_data[0],
                user_id=reflection_data[1],
                date=reflection_data[2],
                achievement_1=reflection_data[3],
                achievement_2=reflection_data[4],
                achievement_3=reflection_data[5],
                created_at=reflection_data[6],
                updated_at=reflection_data[7]
            )
        return None

    @staticmethod
    def get_user_reflections(user_id, limit=7):
        with get_db() as conn:
            c = conn.cursor()
            c.execute(
                "SELECT * FROM daily_reflections WHERE user_id=? ORDER BY date DESC LIMIT ?",
                (user_id, limit)
            )
            reflections = c.fetchall()
        
        return [
            DailyReflection(
                id=r[0],
                user_id=r[1],
                date=r[2],
                achievement_1=r[3],
                achievement_2=r[4],
                achievement_3=r[5],
                created_at=r[6],
                updated_at=r[7]
            )
            for r in reflections
        ]

    def update(self, achievement_1=None, achievement_2=None, achievement_3=None):
        updates = {}
        if achievement_1 is not None:
            updates['achievement_1'] = achievement_1
        if achievement_2 is not None:
            updates['achievement_2'] = achievement_2
        if achievement_3 is not None:
            updates['achievement_3'] = achievement_3
        
        if updates:
            set_clause = ", ".join(f"{k}=?" for k in updates.keys())
            values = list(updates.values()) + [self.id]
            
            with get_db() as conn:
                c = conn.cursor()
                c.execute(
                    f"UPDATE daily_reflections SET {set_clause}, updated_at=CURRENT_TIMESTAMP WHERE id=?",
                    values
                )
                conn.commit()
            
            # Update instance attributes
            for k, v in updates.items():
                setattr(self, k, v)

@login_manager.user_loader
def load_user(user_id):
    return User.get_by_id(int(user_id))
