"""
User Management Database Operations
==================================

This module handles database operations for user management, authentication, and activity tracking.
"""

import sqlite3
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import List, Optional, Tuple

from models.user import User, UserRole, UserStatus, UserSession, UserActivity
from database.db_manager import DatabaseManager

class UserManager:
    """Manages user accounts, authentication, and activity tracking."""
    
    def __init__(self, db_path: str = "pos_database.db"):
        """Initialize the user manager."""
        self.db_path = db_path
        self.current_user: Optional[User] = None
        self.current_session: Optional[UserSession] = None
        self._init_tables()
        self._create_default_admin()
    
    def _init_tables(self):
        """Initialize user management tables."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Users table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    name TEXT NOT NULL,
                    role TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'active',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP,
                    created_by INTEGER,
                    FOREIGN KEY (created_by) REFERENCES users (id)
                )
            ''')
            
            # User sessions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    login_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    logout_time TIMESTAMP,
                    session_token TEXT UNIQUE,
                    ip_address TEXT,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            
            # User activities table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_activities (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    activity_type TEXT NOT NULL,
                    description TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    sale_id INTEGER,
                    amount REAL,
                    details TEXT,
                    FOREIGN KEY (user_id) REFERENCES users (id),
                    FOREIGN KEY (sale_id) REFERENCES sales (id)
                )
            ''')
            
            conn.commit()
            
        except Exception as e:
            print(f"Error initializing user tables: {e}")
            conn.rollback()
        finally:
            conn.close()
    
    def _create_default_admin(self):
        """Create default admin user if no users exist."""
        if not self.get_all_users():
            admin_user = User(
                username="admin",
                password_hash=self._hash_password("admin123"),
                name="Administrator",
                role=UserRole.ADMIN,
                status=UserStatus.ACTIVE
            )
            self.create_user(admin_user)
            print("Default admin user created (username: admin, password: admin123)")
    
    def _hash_password(self, password: str) -> str:
        """Hash a password using SHA-256 with salt."""
        salt = secrets.token_hex(16)
        password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
        return f"{salt}:{password_hash}"
    
    def _verify_password(self, password: str, password_hash: str) -> bool:
        """Verify a password against its hash."""
        try:
            salt, hash_value = password_hash.split(':')
            return hashlib.sha256((password + salt).encode()).hexdigest() == hash_value
        except:
            return False
    
    def create_user(self, user: User, created_by_id: int = None) -> bool:
        """Create a new user account."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO users (username, password_hash, name, role, status, created_by)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                user.username,
                user.password_hash,
                user.name,
                user.role.value,
                user.status.value,
                created_by_id
            ))
            
            user.id = cursor.lastrowid
            conn.commit()
            
            # Log user creation activity
            if created_by_id:
                self.log_activity(
                    created_by_id,
                    "USER_CREATED",
                    f"Created user account: {user.username} ({user.name})"
                )
            
            return True
            
        except sqlite3.IntegrityError:
            print(f"Username '{user.username}' already exists")
            return False
        except Exception as e:
            print(f"Error creating user: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()
    
    def authenticate(self, username: str, password: str) -> Optional[User]:
        """Authenticate a user and return user object if successful."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT id, username, password_hash, name, role, status, created_at, last_login
                FROM users
                WHERE username = ? AND status = 'active'
            ''', (username,))
            
            row = cursor.fetchone()
            if not row:
                return None
            
            user_id, username, password_hash, name, role, status, created_at, last_login = row
            
            # Verify password
            if not self._verify_password(password, password_hash):
                return None
            
            # Update last login
            cursor.execute('''
                UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?
            ''', (user_id,))
            conn.commit()
            
            # Create user object
            user = User(
                id=user_id,
                username=username,
                password_hash=password_hash,
                name=name,
                role=UserRole(role),
                status=UserStatus(status),
                created_at=datetime.fromisoformat(created_at) if created_at else None,
                last_login=datetime.now()
            )
            
            return user
            
        except Exception as e:
            print(f"Error during authentication: {e}")
            return None
        finally:
            conn.close()
    
    def login(self, username: str, password: str) -> bool:
        """Login a user and create a session."""
        user = self.authenticate(username, password)
        if not user:
            return False
        
        # Create session
        session_token = secrets.token_urlsafe(32)
        session = UserSession(
            user_id=user.id,
            session_token=session_token,
            ip_address="127.0.0.1"  # Local for desktop app
        )
        
        if self._create_session(session):
            self.current_user = user
            self.current_session = session
            
            # Log login activity
            self.log_activity(
                user.id,
                "LOGIN",
                f"User logged in: {user.name}"
            )
            
            return True
        
        return False
    
    def logout(self) -> bool:
        """Logout current user and end session."""
        if not self.current_user or not self.current_session:
            return False
        
        # Log logout activity
        self.log_activity(
            self.current_user.id,
            "LOGOUT",
            f"User logged out: {self.current_user.name}"
        )
        
        # End session
        self._end_session(self.current_session.id)
        
        self.current_user = None
        self.current_session = None
        
        return True
    
    def _create_session(self, session: UserSession) -> bool:
        """Create a new user session."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO user_sessions (user_id, session_token, ip_address)
                VALUES (?, ?, ?)
            ''', (session.user_id, session.session_token, session.ip_address))
            
            session.id = cursor.lastrowid
            conn.commit()
            return True
            
        except Exception as e:
            print(f"Error creating session: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()
    
    def _end_session(self, session_id: int) -> bool:
        """End a user session."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                UPDATE user_sessions 
                SET logout_time = CURRENT_TIMESTAMP 
                WHERE id = ?
            ''', (session_id,))
            
            conn.commit()
            return True
            
        except Exception as e:
            print(f"Error ending session: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()
    
    def log_activity(self, user_id: int, activity_type: str, description: str, 
                     sale_id: int = None, amount: float = None, details: str = "") -> bool:
        """Log user activity."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO user_activities (user_id, activity_type, description, sale_id, amount, details)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (user_id, activity_type, description, sale_id, amount, details))
            
            conn.commit()
            return True
            
        except Exception as e:
            print(f"Error logging activity: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()
    
    def get_all_users(self) -> List[User]:
        """Get all users in the system."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT id, username, password_hash, name, role, status, created_at, last_login
                FROM users
                ORDER BY created_at DESC
            ''')
            
            users = []
            for row in cursor.fetchall():
                user_id, username, password_hash, name, role, status, created_at, last_login = row
                
                user = User(
                    id=user_id,
                    username=username,
                    password_hash=password_hash,
                    name=name,
                    role=UserRole(role),
                    status=UserStatus(status),
                    created_at=datetime.fromisoformat(created_at) if created_at else None,
                    last_login=datetime.fromisoformat(last_login) if last_login else None
                )
                users.append(user)
            
            return users
            
        except Exception as e:
            print(f"Error getting users: {e}")
            return []
        finally:
            conn.close()
    
    def get_user_activities(self, user_id: int = None, start_date: datetime = None, 
                           end_date: datetime = None) -> List[UserActivity]:
        """Get user activities with optional filtering."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            query = '''
                SELECT ua.id, ua.user_id, ua.activity_type, ua.description, 
                       ua.timestamp, ua.sale_id, ua.amount, ua.details,
                       u.name, u.username
                FROM user_activities ua
                JOIN users u ON ua.user_id = u.id
                WHERE 1=1
            '''
            params = []
            
            if user_id:
                query += " AND ua.user_id = ?"
                params.append(user_id)
            
            if start_date:
                query += " AND ua.timestamp >= ?"
                params.append(start_date.isoformat())
            
            if end_date:
                query += " AND ua.timestamp <= ?"
                params.append(end_date.isoformat())
            
            query += " ORDER BY ua.timestamp DESC"
            
            cursor.execute(query, params)
            
            activities = []
            for row in cursor.fetchall():
                activity_id, user_id, activity_type, description, timestamp, sale_id, amount, details, name, username = row
                
                activity = UserActivity(
                    id=activity_id,
                    user_id=user_id,
                    activity_type=activity_type,
                    description=description,
                    timestamp=datetime.fromisoformat(timestamp) if timestamp else None,
                    sale_id=sale_id,
                    amount=amount,
                    details=details
                )
                
                # Add user info to details for display
                activity.details = f"{activity.details}\nUser: {name} ({username})" if activity.details else f"User: {name} ({username})"
                
                activities.append(activity)
            
            return activities
            
        except Exception as e:
            print(f"Error getting user activities: {e}")
            return []
        finally:
            conn.close()
    
    def get_user_sales_summary(self, user_id: int = None, start_date: datetime = None, 
                              end_date: datetime = None) -> dict:
        """Get sales summary by user."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            query = '''
                SELECT u.id, u.name, u.username,
                       COUNT(s.id) as total_sales,
                       COALESCE(SUM(s.total), 0) as total_amount,
                       COALESCE(AVG(s.total), 0) as avg_sale
                FROM users u
                LEFT JOIN sales s ON u.id = s.cashier_id
                WHERE u.status = 'active'
            '''
            params = []
            
            if user_id:
                query += " AND u.id = ?"
                params.append(user_id)
            
            if start_date:
                query += " AND s.timestamp >= ?"
                params.append(start_date.isoformat())
            
            if end_date:
                query += " AND s.timestamp <= ?"
                params.append(end_date.isoformat())
            
            query += " GROUP BY u.id, u.name, u.username ORDER BY total_amount DESC"
            
            cursor.execute(query, params)
            
            summary = {}
            for row in cursor.fetchall():
                user_id, name, username, total_sales, total_amount, avg_sale = row
                summary[user_id] = {
                    'name': name,
                    'username': username,
                    'total_sales': total_sales,
                    'total_amount': total_amount,
                    'average_sale': avg_sale
                }
            
            return summary
            
        except Exception as e:
            print(f"Error getting user sales summary: {e}")
            return {}
        finally:
            conn.close()
    
    def update_user(self, user: User) -> bool:
        """Update user information."""
        if not self.current_user or self.current_user.role != UserRole.ADMIN:
            return False
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                UPDATE users 
                SET name = ?, role = ?, status = ?
                WHERE id = ?
            ''', (user.name, user.role.value, user.status.value, user.id))
            
            conn.commit()
            
            # Log activity
            self.log_activity(
                self.current_user.id,
                "USER_UPDATED",
                f"Updated user: {user.username} ({user.name})"
            )
            
            return True
            
        except Exception as e:
            print(f"Error updating user: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()
    
    def change_password(self, user_id: int, new_password: str) -> bool:
        """Change user password."""
        if not self.current_user:
            return False
        
        # Only admin or the user themselves can change password
        if self.current_user.role != UserRole.ADMIN and self.current_user.id != user_id:
            return False
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            password_hash = self._hash_password(new_password)
            cursor.execute('''
                UPDATE users 
                SET password_hash = ?
                WHERE id = ?
            ''', (password_hash, user_id))
            
            conn.commit()
            
            # Log activity
            self.log_activity(
                self.current_user.id,
                "PASSWORD_CHANGED",
                f"Password changed for user ID: {user_id}"
            )
            
            return True
            
        except Exception as e:
            print(f"Error changing password: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()
    
    def remove_user(self, user_id: int) -> bool:
        """Remove a user account."""
        if not self.current_user or self.current_user.role != UserRole.ADMIN:
            return False
        
        # Prevent removing the current user
        if self.current_user.id == user_id:
            return False
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Get user info for logging
            cursor.execute('SELECT username, name FROM users WHERE id = ?', (user_id,))
            user_info = cursor.fetchone()
            if not user_info:
                return False
            
            username, name = user_info
            
            # Remove user activities first (to maintain referential integrity)
            cursor.execute('DELETE FROM user_activities WHERE user_id = ?', (user_id,))
            
            # Remove user sessions
            cursor.execute('DELETE FROM user_sessions WHERE user_id = ?', (user_id,))
            
            # Remove the user
            cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
            
            conn.commit()
            
            # Log activity
            self.log_activity(
                self.current_user.id,
                "USER_REMOVED",
                f"Removed user account: {username} ({name})"
            )
            
            return True
            
        except Exception as e:
            print(f"Error removing user: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()
    
    def is_admin(self) -> bool:
        """Check if current user is admin."""
        return self.current_user and self.current_user.role == UserRole.ADMIN
    
    def get_current_user(self) -> Optional[User]:
        """Get currently logged in user."""
        return self.current_user
    
    def is_logged_in(self) -> bool:
        """Check if a user is currently logged in."""
        return self.current_user is not None

# Global user manager instance
user_manager = UserManager()
