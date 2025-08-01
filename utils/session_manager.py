"""
Session Manager
===============

Manages POS sessions, cash drawer opening, and daily operations.
"""

import json
import os
from datetime import datetime, date
from typing import Optional, Dict, Any

class SessionManager:
    """Manages POS sessions and cash drawer operations."""
    
    def __init__(self, session_file: str = "pos_session.json"):
        """Initialize session manager."""
        self.session_file = session_file
        self.logout_flag_file = "logout_flag.txt"
        self.current_session = None
        
    def get_today_date(self) -> str:
        """Get today's date as string."""
        return date.today().isoformat()
    
    def load_session_data(self) -> Dict[str, Any]:
        """Load session data from file."""
        if os.path.exists(self.session_file):
            try:
                with open(self.session_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return {}
        return {}
    
    def save_session_data(self, data: Dict[str, Any]):
        """Save session data to file."""
        try:
            with open(self.session_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except IOError as e:
            print(f"Error saving session data: {e}")
    
    def needs_cash_drawer_opening(self) -> bool:
        """Check if cash drawer opening is needed."""
        # Simple approach: check for logout flag file
        if os.path.exists(self.logout_flag_file):
            return True
        
        # Also check if no session exists for today (first time running)
        session_data = self.load_session_data()
        today = self.get_today_date()
        
        if today not in session_data:
            return True
        
        # Load existing session if available
        today_session = session_data[today]
        if not today_session.get('logout_time'):
            self.current_session = today_session
            return False
        
        return True
    
    def start_session(self, cash_amount: float, reason: str = "Ouverture de session") -> Dict[str, Any]:
        """Start a new session with cash drawer opening."""
        # Clear logout flag since we're starting a session
        if os.path.exists(self.logout_flag_file):
            os.remove(self.logout_flag_file)
        
        session_data = self.load_session_data()
        today = self.get_today_date()
        
        # Check if updating existing session or creating new one
        if today in session_data and session_data[today].get('logout_time'):
            # Update existing session after logout
            session_info = session_data[today].copy()
            session_info.update({
                'restart_time': datetime.now().isoformat(),
                'cash_drawer_amount': cash_amount,
                'restart_reason': reason,
                'status': 'open',
                'logout_time': None,  # Clear logout time
            })
        else:
            # Create completely new session
            session_info = {
                'date': today,
                'start_time': datetime.now().isoformat(),
                'cash_drawer_amount': cash_amount,
                'opening_reason': reason,
                'status': 'open',
                'logout_time': None,
                'cashier': 'Admin'  # You can modify this to track actual cashier
            }
        
        session_data[today] = session_info
        self.save_session_data(session_data)
        self.current_session = session_info
        
        return session_info
    
    def end_session(self, reason: str = "Déconnexion"):
        """End current session (logout)."""
        # Set logout flag for next startup
        with open(self.logout_flag_file, 'w') as f:
            f.write("logged_out")
        
        # Update session data
        if not self.current_session:
            # Try to load current session
            session_data = self.load_session_data()
            today = self.get_today_date()
            if today in session_data:
                self.current_session = session_data[today]
            
        if self.current_session:
            session_data = self.load_session_data()
            today = self.get_today_date()
            
            if today in session_data:
                session_data[today].update({
                    'logout_time': datetime.now().isoformat(),
                    'status': 'closed',
                    'closing_reason': reason
                })
                self.save_session_data(session_data)
        
        self.current_session = None
    
    def close_app_without_logout(self):
        """Close app without ending session (keeps session open)."""
        # Session remains open, no changes to session data
        pass
    
    def get_current_session(self) -> Optional[Dict[str, Any]]:
        """Get current session information."""
        if not self.current_session:
            session_data = self.load_session_data()
            today = self.get_today_date()
            if today in session_data and session_data[today].get('status') == 'open':
                self.current_session = session_data[today]
        
        return self.current_session
    
    def get_today_cash_amount(self) -> float:
        """Get today's cash drawer amount."""
        session = self.get_current_session()
        return session.get('cash_drawer_amount', 0.0) if session else 0.0
    
    def update_cash_amount(self, new_amount: float, operation_type: str, reason: str, transaction_amount: float):
        """Update cash amount in current session and log the transaction."""
        if not self.current_session:
            self.get_current_session()  # Try to load current session
            
        if not self.current_session:
            raise ValueError("No active session found")
        
        session_data = self.load_session_data()
        today = self.get_today_date()
        
        if today in session_data:
            # Update cash amount
            session_data[today]['cash_drawer_amount'] = new_amount
            
            # Add transaction to history
            if 'cash_transactions' not in session_data[today]:
                session_data[today]['cash_transactions'] = []
            
            transaction = {
                'timestamp': datetime.now().isoformat(),
                'type': operation_type,
                'amount': transaction_amount,
                'new_balance': new_amount,
                'reason': reason
            }
            
            session_data[today]['cash_transactions'].append(transaction)
            
            # Update current session
            self.current_session['cash_drawer_amount'] = new_amount
            
            # Save changes
            self.save_session_data(session_data)
