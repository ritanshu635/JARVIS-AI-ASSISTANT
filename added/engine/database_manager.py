import sqlite3
import json
import os
from datetime import datetime
from typing import List, Dict, Optional, Any
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

class DatabaseManager:
    """Manages both SQLite and MongoDB connections for the unified JARVIS system"""
    
    def __init__(self):
        self.sqlite_conn = None
        self.mongo_client = None
        self.mongo_db = None
        self.initialize_databases()
    
    def initialize_databases(self):
        """Initialize both SQLite and MongoDB connections"""
        try:
            # Initialize SQLite
            self.sqlite_conn = sqlite3.connect("jarvis.db", check_same_thread=False)
            self.create_sqlite_tables()
            print("✅ SQLite database initialized")
            
            # Initialize MongoDB
            mongo_url = os.getenv('MONGO_URL', 'mongodb://localhost:27017/')
            db_name = os.getenv('DB_NAME', 'jarvis_unified')
            
            try:
                self.mongo_client = MongoClient(mongo_url, serverSelectionTimeoutMS=5000)
                # Test connection
                self.mongo_client.server_info()
                self.mongo_db = self.mongo_client[db_name]
                print("✅ MongoDB database initialized")
            except Exception as e:
                print(f"⚠️ MongoDB not available: {e}")
                print("📝 Chat history will be stored in JSON files as fallback")
                self.mongo_client = None
                self.mongo_db = None
                
        except Exception as e:
            print(f"❌ Database initialization error: {e}")
    
    def create_sqlite_tables(self):
        """Create SQLite tables for contacts and system commands"""
        cursor = self.sqlite_conn.cursor()
        
        # Contacts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS contacts (
                id INTEGER PRIMARY KEY,
                name VARCHAR(200),
                mobile_no VARCHAR(255),
                email VARCHAR(255)
            )
        ''')
        
        # System commands table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sys_command (
                id INTEGER PRIMARY KEY,
                name VARCHAR(100),
                path VARCHAR(1000)
            )
        ''')
        
        # Web commands table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS web_command (
                id INTEGER PRIMARY KEY,
                name VARCHAR(100),
                url VARCHAR(1000)
            )
        ''')
        
        # User preferences table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_preferences (
                id INTEGER PRIMARY KEY,
                key VARCHAR(100) UNIQUE,
                value TEXT
            )
        ''')
        
        self.sqlite_conn.commit()
        print("✅ SQLite tables created/verified")
    
    # Contact Management Methods
    def add_contact(self, name: str, mobile_no: str, email: str = None) -> bool:
        """Add a new contact to the database"""
        try:
            cursor = self.sqlite_conn.cursor()
            cursor.execute(
                "INSERT INTO contacts (name, mobile_no, email) VALUES (?, ?, ?)",
                (name, mobile_no, email)
            )
            self.sqlite_conn.commit()
            return True
        except Exception as e:
            print(f"Error adding contact: {e}")
            return False
    
    def get_contact(self, name: str) -> Optional[Dict]:
        """Search for a contact by name (fuzzy matching) - checks CSV file first"""
        try:
            # First check CSV file
            csv_contact = self._get_contact_from_csv(name)
            if csv_contact:
                return csv_contact
            
            # Fallback to database
            cursor = self.sqlite_conn.cursor()
            name = name.strip().lower()
            cursor.execute(
                "SELECT * FROM contacts WHERE LOWER(name) LIKE ? OR LOWER(name) LIKE ?",
                (f'%{name}%', f'{name}%')
            )
            result = cursor.fetchone()
            if result:
                return {
                    'id': result[0],
                    'name': result[1],
                    'mobile_no': result[2],
                    'email': result[3]
                }
            return None
        except Exception as e:
            print(f"Error getting contact: {e}")
            return None
    
    def _get_contact_from_csv(self, name: str) -> Optional[Dict]:
        """Get contact from CSV file"""
        import csv
        import os
        
        csv_files = ['contacts.csv', '../contacts.csv']
        
        for csv_file in csv_files:
            if os.path.exists(csv_file):
                try:
                    with open(csv_file, 'r', encoding='utf-8') as file:
                        reader = csv.DictReader(file)
                        for row in reader:
                            csv_name = (row.get('Name') or row.get('name') or '').strip()
                            csv_phone = (row.get('Phone Number') or row.get('Phone') or row.get('phone') or '').strip()
                            
                            if csv_name and csv_phone:
                                # Check if names match (fuzzy matching)
                                if (name.lower() in csv_name.lower() or 
                                    csv_name.lower() in name.lower() or
                                    name.lower() == csv_name.lower()):
                                    
                                    # Clean phone number
                                    clean_phone = self._clean_phone_number(csv_phone)
                                    
                                    return {
                                        'id': 0,
                                        'name': csv_name,
                                        'mobile_no': clean_phone,
                                        'email': ''
                                    }
                except Exception as e:
                    print(f"Error reading CSV {csv_file}: {e}")
                    continue
        
        return None
    
    def _clean_phone_number(self, phone: str) -> str:
        """Clean and format phone number"""
        import re
        
        # Remove all non-digit characters except +
        phone = re.sub(r'[^\d+]', '', phone)
        
        # Add country code if missing (assuming India +91)
        if phone and not phone.startswith('+'):
            if len(phone) == 10:
                phone = '+91' + phone
            elif len(phone) == 11 and phone.startswith('0'):
                phone = '+91' + phone[1:]
        
        return phone
    
    def get_all_contacts(self) -> List[Dict]:
        """Get all contacts from CSV file and database"""
        contacts = []
        
        # First get contacts from CSV
        csv_contacts = self._get_all_contacts_from_csv()
        contacts.extend(csv_contacts)
        
        # Then get from database (avoid duplicates)
        try:
            cursor = self.sqlite_conn.cursor()
            cursor.execute("SELECT * FROM contacts")
            results = cursor.fetchall()
            
            for result in results:
                db_contact = {
                    'id': result[0],
                    'name': result[1],
                    'mobile_no': result[2],
                    'email': result[3]
                }
                
                # Check if contact already exists from CSV
                duplicate = False
                for csv_contact in csv_contacts:
                    if (csv_contact['name'].lower() == db_contact['name'].lower() or
                        csv_contact['mobile_no'] == db_contact['mobile_no']):
                        duplicate = True
                        break
                
                if not duplicate:
                    contacts.append(db_contact)
                    
        except Exception as e:
            print(f"Error getting database contacts: {e}")
        
        return contacts
    
    def _get_all_contacts_from_csv(self) -> List[Dict]:
        """Get all contacts from CSV file"""
        import csv
        import os
        
        contacts = []
        csv_files = ['contacts.csv', '../contacts.csv']
        
        for csv_file in csv_files:
            if os.path.exists(csv_file):
                try:
                    with open(csv_file, 'r', encoding='utf-8') as file:
                        reader = csv.DictReader(file)
                        for row in reader:
                            csv_name = (row.get('Name') or row.get('name') or '').strip()
                            csv_phone = (row.get('Phone Number') or row.get('Phone') or row.get('phone') or '').strip()
                            
                            if csv_name and csv_phone:
                                clean_phone = self._clean_phone_number(csv_phone)
                                
                                contacts.append({
                                    'id': len(contacts) + 1,
                                    'name': csv_name,
                                    'mobile_no': clean_phone,
                                    'email': ''
                                })
                except Exception as e:
                    print(f"Error reading CSV {csv_file}: {e}")
                    continue
                break  # Only read from first found CSV file
        
        return contacts
    
    # System Commands Management
    def add_system_command(self, name: str, path: str) -> bool:
        """Add a system command/application path"""
        try:
            cursor = self.sqlite_conn.cursor()
            cursor.execute(
                "INSERT OR REPLACE INTO sys_command (name, path) VALUES (?, ?)",
                (name.lower(), path)
            )
            self.sqlite_conn.commit()
            return True
        except Exception as e:
            print(f"Error adding system command: {e}")
            return False
    
    def get_system_command(self, name: str) -> Optional[str]:
        """Get system command path by name"""
        try:
            cursor = self.sqlite_conn.cursor()
            cursor.execute(
                "SELECT path FROM sys_command WHERE name = ?",
                (name.lower(),)
            )
            result = cursor.fetchone()
            return result[0] if result else None
        except Exception as e:
            print(f"Error getting system command: {e}")
            return None
    
    # Web Commands Management
    def add_web_command(self, name: str, url: str) -> bool:
        """Add a web command/URL"""
        try:
            cursor = self.sqlite_conn.cursor()
            cursor.execute(
                "INSERT OR REPLACE INTO web_command (name, url) VALUES (?, ?)",
                (name.lower(), url)
            )
            self.sqlite_conn.commit()
            return True
        except Exception as e:
            print(f"Error adding web command: {e}")
            return False
    
    def get_web_command(self, name: str) -> Optional[str]:
        """Get web command URL by name"""
        try:
            cursor = self.sqlite_conn.cursor()
            cursor.execute(
                "SELECT url FROM web_command WHERE name = ?",
                (name.lower(),)
            )
            result = cursor.fetchone()
            return result[0] if result else None
        except Exception as e:
            print(f"Error getting web command: {e}")
            return None
    
    # Chat History Management
    def save_chat_message(self, user_input: str, response: str, intent: str = None, 
                         processing_time: float = None, ai_model: str = None) -> bool:
        """Save chat message to MongoDB or JSON fallback"""
        chat_data = {
            'timestamp': datetime.utcnow(),
            'user_input': user_input,
            'response': response,
            'intent': intent,
            'processing_time': processing_time,
            'ai_model_used': ai_model
        }
        
        if self.mongo_db is not None:
            try:
                self.mongo_db.chat_history.insert_one(chat_data)
                return True
            except Exception as e:
                print(f"MongoDB save error: {e}")
        
        # Fallback to JSON file
        return self._save_to_json_fallback(chat_data)
    
    def _save_to_json_fallback(self, chat_data: Dict) -> bool:
        """Save chat data to JSON file as fallback"""
        try:
            # Convert datetime to string for JSON serialization
            chat_data['timestamp'] = chat_data['timestamp'].isoformat()
            
            # Load existing data
            chat_file = "ChatLog.json"
            if os.path.exists(chat_file):
                with open(chat_file, 'r') as f:
                    messages = json.load(f)
            else:
                messages = []
            
            # Add new message
            messages.append({
                'role': 'user',
                'content': chat_data['user_input'],
                'timestamp': chat_data['timestamp']
            })
            messages.append({
                'role': 'assistant',
                'content': chat_data['response'],
                'timestamp': chat_data['timestamp'],
                'metadata': {
                    'intent': chat_data['intent'],
                    'processing_time': chat_data['processing_time'],
                    'ai_model': chat_data['ai_model_used']
                }
            })
            
            # Save to file
            with open(chat_file, 'w') as f:
                json.dump(messages, f, indent=4)
            
            return True
        except Exception as e:
            print(f"JSON fallback save error: {e}")
            return False
    
    def get_chat_history(self, limit: int = 50) -> List[Dict]:
        """Get recent chat history"""
        if self.mongo_db is not None:
            try:
                cursor = self.mongo_db.chat_history.find().sort("timestamp", -1).limit(limit)
                return list(cursor)
            except Exception as e:
                print(f"MongoDB read error: {e}")
        
        # Fallback to JSON file
        return self._load_from_json_fallback(limit)
    
    def _load_from_json_fallback(self, limit: int) -> List[Dict]:
        """Load chat history from JSON file"""
        try:
            chat_file = "ChatLog.json"
            if os.path.exists(chat_file):
                with open(chat_file, 'r') as f:
                    messages = json.load(f)
                return messages[-limit:] if len(messages) > limit else messages
            return []
        except Exception as e:
            print(f"JSON fallback load error: {e}")
            return []
    
    # User Preferences Management
    def set_preference(self, key: str, value: Any) -> bool:
        """Set a user preference"""
        try:
            cursor = self.sqlite_conn.cursor()
            cursor.execute(
                "INSERT OR REPLACE INTO user_preferences (key, value) VALUES (?, ?)",
                (key, json.dumps(value))
            )
            self.sqlite_conn.commit()
            return True
        except Exception as e:
            print(f"Error setting preference: {e}")
            return False
    
    def get_preference(self, key: str, default: Any = None) -> Any:
        """Get a user preference"""
        try:
            cursor = self.sqlite_conn.cursor()
            cursor.execute("SELECT value FROM user_preferences WHERE key = ?", (key,))
            result = cursor.fetchone()
            if result:
                return json.loads(result[0])
            return default
        except Exception as e:
            print(f"Error getting preference: {e}")
            return default
    
    # Database Maintenance
    def backup_database(self) -> bool:
        """Create a backup of the SQLite database"""
        try:
            import shutil
            backup_path = f"jarvis_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
            shutil.copy2("jarvis.db", backup_path)
            print(f"✅ Database backed up to {backup_path}")
            return True
        except Exception as e:
            print(f"❌ Backup failed: {e}")
            return False
    
    def close_connections(self):
        """Close all database connections"""
        if self.sqlite_conn:
            self.sqlite_conn.close()
        if self.mongo_client:
            self.mongo_client.close()
        print("🔒 Database connections closed")

# Initialize default data
def initialize_default_data():
    """Initialize database with default system commands and web commands"""
    db = DatabaseManager()
    
    # Default system commands (common Windows applications)
    default_apps = [
        ("notepad", "notepad.exe"),
        ("calculator", "calc.exe"),
        ("paint", "mspaint.exe"),
        ("chrome", "chrome.exe"),
        ("firefox", "firefox.exe"),
        ("edge", "msedge.exe"),
        ("explorer", "explorer.exe"),
        ("cmd", "cmd.exe"),
        ("powershell", "powershell.exe"),
    ]
    
    for name, path in default_apps:
        db.add_system_command(name, path)
    
    # Default web commands
    default_websites = [
        ("youtube", "https://www.youtube.com"),
        ("google", "https://www.google.com"),
        ("facebook", "https://www.facebook.com"),
        ("twitter", "https://www.twitter.com"),
        ("instagram", "https://www.instagram.com"),
        ("linkedin", "https://www.linkedin.com"),
        ("github", "https://www.github.com"),
        ("netflix", "https://www.netflix.com"),
        ("spotify", "https://www.spotify.com"),
        ("amazon", "https://www.amazon.com"),
    ]
    
    for name, url in default_websites:
        db.add_web_command(name, url)
    
    print("✅ Default data initialized")
    return db

if __name__ == "__main__":
    # Test the database manager
    db = initialize_default_data()
    
    # Test contact operations
    db.add_contact("Test User", "+1234567890", "test@example.com")
    contact = db.get_contact("test")
    print(f"Found contact: {contact}")
    
    # Test chat history
    db.save_chat_message("Hello", "Hi there!", "greeting", 0.5, "test")
    history = db.get_chat_history(5)
    print(f"Chat history: {len(history)} messages")
    
    db.close_connections()