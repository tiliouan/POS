"""
User Management Models
======================

This module contains user-related models for authentication and user management.
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional

class UserRole(Enum):
    """User roles in the system."""
    ADMIN = "admin"
    CASHIER = "cashier"
    MANAGER = "manager"

class UserStatus(Enum):
    """User account status."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"

@dataclass
class User:
    """User model representing a system user."""
    id: Optional[int] = None
    username: str = ""
    password_hash: str = ""
    name: str = ""
    role: UserRole = UserRole.CASHIER
    status: UserStatus = UserStatus.ACTIVE
    created_at: Optional[datetime] = None
    last_login: Optional[datetime] = None
    created_by: Optional[int] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()

@dataclass
class UserSession:
    """User session model for tracking login sessions."""
    id: Optional[int] = None
    user_id: int = 0
    login_time: Optional[datetime] = None
    logout_time: Optional[datetime] = None
    session_token: str = ""
    ip_address: str = ""
    
    def __post_init__(self):
        if self.login_time is None:
            self.login_time = datetime.now()

@dataclass
class UserActivity:
    """User activity log for tracking user operations."""
    id: Optional[int] = None
    user_id: int = 0
    activity_type: str = ""
    description: str = ""
    timestamp: Optional[datetime] = None
    sale_id: Optional[int] = None
    amount: Optional[float] = None
    details: str = ""
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
