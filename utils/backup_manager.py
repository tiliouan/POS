"""
Backup Manager
==============

This module handles database backup and restoration for the POS system.
"""

import sqlite3
import os
import shutil
import json
import zipfile
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from pathlib import Path
import schedule
import threading
import time

class BackupManager:
    """Manages database backup and restoration operations."""
    
    def __init__(self, db_path: str = "pos_database.db", backup_dir: str = "backups"):
        """Initialize backup manager."""
        self.db_path = db_path
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(exist_ok=True)
        self.settings_file = "config/backup_settings.json"
        self.backup_settings = self.load_backup_settings()
        self.scheduler_running = False
        self.scheduler_thread = None
        
        # Start scheduler if auto-backup is enabled
        if self.backup_settings.get("auto_backup_enabled", False):
            self.start_scheduler()
    
    def load_backup_settings(self) -> Dict:
        """Load backup settings from file."""
        default_settings = {
            "auto_backup_enabled": False,
            "backup_frequency": "daily",  # daily, weekly, monthly
            "backup_time": "02:00",  # HH:MM format
            "max_backups": 30,  # Maximum number of backups to keep
            "compression": True,
            "include_images": False
        }
        
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    # Merge with defaults to ensure all keys exist
                    default_settings.update(settings)
            return default_settings
        except Exception as e:
            print(f"Error loading backup settings: {e}")
            return default_settings
    
    def save_backup_settings(self, settings: Dict):
        """Save backup settings to file."""
        try:
            # Ensure config directory exists
            config_dir = os.path.dirname(self.settings_file)
            if config_dir:
                os.makedirs(config_dir, exist_ok=True)
                
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2, ensure_ascii=False)
            self.backup_settings = settings
            
            # Restart scheduler if needed
            if settings.get("auto_backup_enabled", False):
                self.start_scheduler()
            else:
                self.stop_scheduler()
                
        except Exception as e:
            print(f"Error saving backup settings: {e}")
            raise
    
    def create_backup(self, custom_name: str = None) -> str:
        """Create a backup of the database."""
        try:
            # Generate backup filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            if custom_name:
                backup_name = f"{custom_name}_{timestamp}"
            else:
                backup_name = f"backup_{timestamp}"
            
            if self.backup_settings.get("compression", True):
                backup_filename = f"{backup_name}.zip"
                backup_path = self.backup_dir / backup_filename
                
                # Create compressed backup
                with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    # Add database file
                    if os.path.exists(self.db_path):
                        zipf.write(self.db_path, "database.db")
                    
                    # Add metadata
                    metadata = {
                        "backup_date": datetime.now().isoformat(),
                        "database_size": os.path.getsize(self.db_path) if os.path.exists(self.db_path) else 0,
                        "backup_type": "automatic" if custom_name is None else "manual",
                        "version": "1.0"
                    }
                    zipf.writestr("backup_info.json", json.dumps(metadata, indent=2))
                    
                    # Add images if enabled
                    if self.backup_settings.get("include_images", False):
                        images_dir = Path("images")
                        if images_dir.exists():
                            for image_file in images_dir.rglob("*"):
                                if image_file.is_file():
                                    zipf.write(image_file, f"images/{image_file.relative_to(images_dir)}")
            else:
                # Simple file copy
                backup_filename = f"{backup_name}.db"
                backup_path = self.backup_dir / backup_filename
                shutil.copy2(self.db_path, backup_path)
            
            # Clean old backups
            self.cleanup_old_backups()
            
            return str(backup_path)
            
        except Exception as e:
            print(f"Error creating backup: {e}")
            raise
    
    def restore_backup(self, backup_path: str) -> bool:
        """Restore database from backup."""
        try:
            backup_file = Path(backup_path)
            
            if not backup_file.exists():
                raise FileNotFoundError(f"Backup file not found: {backup_path}")
            
            # Create backup of current database before restore
            current_backup = self.create_backup("pre_restore")
            print(f"Current database backed up to: {current_backup}")
            
            if backup_file.suffix == '.zip':
                # Extract from compressed backup
                with zipfile.ZipFile(backup_file, 'r') as zipf:
                    # Extract database
                    zipf.extract("database.db", path="temp_restore")
                    shutil.move("temp_restore/database.db", self.db_path)
                    
                    # Clean up temp directory
                    shutil.rmtree("temp_restore", ignore_errors=True)
            else:
                # Direct file copy
                shutil.copy2(backup_file, self.db_path)
            
            return True
            
        except Exception as e:
            print(f"Error restoring backup: {e}")
            raise
    
    def get_backup_list(self) -> List[Dict]:
        """Get list of available backups."""
        backups = []
        
        try:
            for backup_file in self.backup_dir.glob("backup_*"):
                if backup_file.is_file():
                    stat = backup_file.stat()
                    backup_info = {
                        "filename": backup_file.name,
                        "path": str(backup_file),
                        "size": stat.st_size,
                        "created": datetime.fromtimestamp(stat.st_mtime),
                        "type": "compressed" if backup_file.suffix == '.zip' else "uncompressed"
                    }
                    
                    # Try to read metadata for compressed backups
                    if backup_file.suffix == '.zip':
                        try:
                            with zipfile.ZipFile(backup_file, 'r') as zipf:
                                if "backup_info.json" in zipf.namelist():
                                    metadata = json.loads(zipf.read("backup_info.json"))
                                    backup_info.update(metadata)
                        except:
                            pass
                    
                    backups.append(backup_info)
            
            # Sort by creation date (newest first)
            backups.sort(key=lambda x: x["created"], reverse=True)
            
        except Exception as e:
            print(f"Error getting backup list: {e}")
        
        return backups
    
    def cleanup_old_backups(self):
        """Remove old backups based on settings."""
        try:
            max_backups = self.backup_settings.get("max_backups", 30)
            backups = self.get_backup_list()
            
            if len(backups) > max_backups:
                # Remove oldest backups
                for backup in backups[max_backups:]:
                    backup_path = Path(backup["path"])
                    if backup_path.exists():
                        backup_path.unlink()
                        print(f"Removed old backup: {backup['filename']}")
                        
        except Exception as e:
            print(f"Error cleaning up old backups: {e}")
    
    def start_scheduler(self):
        """Start the backup scheduler."""
        try:
            # Stop existing scheduler first
            self.stop_scheduler()
            
            # Clear any existing scheduled jobs
            schedule.clear()
            
            frequency = self.backup_settings.get("backup_frequency", "daily")
            backup_time = self.backup_settings.get("backup_time", "02:00")
            
            # Convert time format if needed (handle AM/PM)
            formatted_time = self._format_time_for_scheduler(backup_time)
            
            print(f"Setting up backup scheduler: {frequency} at {formatted_time}")
            
            if frequency == "daily":
                schedule.every().day.at(formatted_time).do(self._scheduled_backup)
            elif frequency == "weekly":
                schedule.every().week.at(formatted_time).do(self._scheduled_backup)
            elif frequency == "monthly":
                schedule.every(30).days.at(formatted_time).do(self._scheduled_backup)
            
            self.scheduler_running = True
            self.scheduler_thread = threading.Thread(target=self._run_scheduler, daemon=True)
            self.scheduler_thread.start()
            
            print(f"Backup scheduler started successfully: {frequency} at {formatted_time}")
            print(f"Next backup scheduled for: {schedule.next_run()}")
            
        except Exception as e:
            print(f"Error starting backup scheduler: {e}")
            self.scheduler_running = False
    
    def stop_scheduler(self):
        """Stop the backup scheduler."""
        try:
            self.scheduler_running = False
            schedule.clear()
            
            if self.scheduler_thread and self.scheduler_thread.is_alive():
                self.scheduler_thread.join(timeout=2)
                
            print("Backup scheduler stopped")
            
        except Exception as e:
            print(f"Error stopping backup scheduler: {e}")
    
    def _format_time_for_scheduler(self, time_str: str) -> str:
        """Format time string for scheduler (convert AM/PM to 24-hour format)."""
        try:
            # Handle AM/PM format
            if 'AM' in time_str.upper() or 'PM' in time_str.upper():
                # Parse 12-hour format and convert to 24-hour
                dt = datetime.strptime(time_str.upper(), "%I:%M %p")
                return dt.strftime("%H:%M")
            else:
                # Already in 24-hour format, validate it
                datetime.strptime(time_str, "%H:%M")
                return time_str
        except ValueError:
            print(f"Invalid time format: {time_str}, using default 02:00")
            return "02:00"
    
    def _run_scheduler(self):
        """Run the scheduler in a separate thread."""
        print("Backup scheduler thread started")
        
        while self.scheduler_running:
            try:
                schedule.run_pending()
                time.sleep(30)  # Check every 30 seconds for better responsiveness
                
                # Log scheduler status periodically (every hour)
                if int(time.time()) % 3600 == 0:
                    next_run = schedule.next_run()
                    if next_run:
                        print(f"Backup scheduler running. Next backup: {next_run}")
                        
            except Exception as e:
                print(f"Error in backup scheduler: {e}")
                time.sleep(60)  # Wait a minute before retrying
        
        print("Backup scheduler thread stopped")
    
    def _scheduled_backup(self):
        """Perform a scheduled backup."""
        try:
            print(f"Starting automatic backup at {datetime.now()}")
            backup_path = self.create_backup("auto")
            print(f"Automatic backup completed successfully: {backup_path}")
            
            # Log backup success to a file
            self._log_backup_event("SUCCESS", f"Automatic backup created: {backup_path}")
            
        except Exception as e:
            error_msg = f"Automatic backup failed: {e}"
            print(error_msg)
            self._log_backup_event("ERROR", error_msg)
    
    def _log_backup_event(self, level: str, message: str):
        """Log backup events to a file."""
        try:
            log_dir = Path("logs")
            log_dir.mkdir(exist_ok=True)
            
            log_file = log_dir / "backup.log"
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(f"[{timestamp}] {level}: {message}\n")
                
        except Exception as e:
            print(f"Error writing to backup log: {e}")
    
    def get_scheduler_status(self) -> dict:
        """Get current scheduler status."""
        try:
            next_run = schedule.next_run() if schedule.jobs else None
            
            return {
                "running": self.scheduler_running,
                "next_run": next_run.isoformat() if next_run else None,
                "jobs_count": len(schedule.jobs),
                "thread_alive": self.scheduler_thread.is_alive() if self.scheduler_thread else False,
                "settings": self.backup_settings
            }
        except Exception as e:
            return {"error": str(e)}
    
    def export_data(self, export_path: str, format: str = "json") -> bool:
        """Export database data to various formats."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                if format.lower() == "json":
                    self._export_to_json(conn, export_path)
                elif format.lower() == "csv":
                    self._export_to_csv(conn, export_path)
                else:
                    raise ValueError(f"Unsupported export format: {format}")
            
            return True
            
        except Exception as e:
            print(f"Error exporting data: {e}")
            raise
    
    def _export_to_json(self, conn: sqlite3.Connection, export_path: str):
        """Export database to JSON format."""
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        export_data = {}
        
        for table_name, in tables:
            cursor.execute(f"SELECT * FROM {table_name}")
            rows = cursor.fetchall()
            
            # Get column names
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = [column[1] for column in cursor.fetchall()]
            
            # Convert rows to dictionaries
            table_data = []
            for row in rows:
                row_dict = dict(zip(columns, row))
                table_data.append(row_dict)
            
            export_data[table_name] = table_data
        
        # Add metadata
        export_data["_metadata"] = {
            "export_date": datetime.now().isoformat(),
            "export_format": "json",
            "total_tables": len(tables)
        }
        
        with open(export_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False, default=str)
    
    def _export_to_csv(self, conn: sqlite3.Connection, export_path: str):
        """Export database to CSV format (multiple files)."""
        import csv
        
        cursor = conn.cursor()
        export_dir = Path(export_path)
        export_dir.mkdir(exist_ok=True)
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        for table_name, in tables:
            cursor.execute(f"SELECT * FROM {table_name}")
            rows = cursor.fetchall()
            
            # Get column names
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = [column[1] for column in cursor.fetchall()]
            
            # Write CSV file
            csv_path = export_dir / f"{table_name}.csv"
            with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(columns)  # Header
                writer.writerows(rows)
