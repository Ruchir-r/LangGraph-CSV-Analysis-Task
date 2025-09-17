"""
Database Configuration and Models
Version 1 - SQLite for simplicity
"""
import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List

# Database file location
DB_PATH = Path("data_analysis.db")

def get_connection():
    """Get database connection"""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn

def create_tables():
    """Create database tables"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Files table - stores uploaded file metadata
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            original_filename TEXT NOT NULL,
            file_path TEXT NOT NULL,
            file_size INTEGER NOT NULL,
            columns TEXT NOT NULL,  -- JSON array of column names
            row_count INTEGER NOT NULL,
            numeric_columns TEXT,   -- JSON array of numeric columns
            categorical_columns TEXT, -- JSON array of categorical columns
            date_columns TEXT,      -- JSON array of date columns
            upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'uploaded'
        )
    """)
    
    # Sessions table - stores chat sessions
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            metadata TEXT  -- JSON metadata
        )
    """)
    
    # Messages table - stores chat messages
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            message_type TEXT NOT NULL,  -- 'user' or 'assistant'
            content TEXT NOT NULL,
            analysis_results TEXT,  -- JSON analysis results if applicable
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (session_id) REFERENCES sessions (session_id)
        )
    """)
    
    # Analysis results table - stores computation results
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS analysis_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_id INTEGER NOT NULL,
            operation TEXT NOT NULL,
            column_name TEXT,
            group_by_column TEXT,
            result_data TEXT NOT NULL,  -- JSON result data
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (file_id) REFERENCES files (id)
        )
    """)
    
    # Comprehensive analysis results table - stores LangGraph workflow results
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS comprehensive_analysis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            task_id TEXT UNIQUE NOT NULL,
            query TEXT NOT NULL,
            file_ids TEXT NOT NULL,  -- JSON array of file IDs
            operation_type TEXT,
            analysis_results TEXT NOT NULL,  -- JSON full analysis results
            execution_status TEXT DEFAULT 'completed',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (session_id) REFERENCES sessions (session_id)
        )
    """)
    
    # Comprehensive analysis results table - stores LangGraph workflow results
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS comprehensive_analysis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            task_id TEXT UNIQUE NOT NULL,
            query TEXT NOT NULL,
            file_ids TEXT NOT NULL,  -- JSON array of file IDs
            operation_type TEXT,
            analysis_results TEXT NOT NULL,  -- JSON full analysis results
            execution_status TEXT DEFAULT 'completed',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (session_id) REFERENCES sessions (session_id)
        )
    """)
    
    conn.commit()
    conn.close()
    print("📊 Database tables created successfully")

class FileModel:
    """Model for file operations"""
    
    @staticmethod
    def create(filename: str, original_filename: str, file_path: str, 
               file_size: int, columns: list, row_count: int,
               numeric_columns: list = None, categorical_columns: list = None,
               date_columns: list = None) -> int:
        """Create a new file record"""
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO files (filename, original_filename, file_path, file_size, 
                             columns, row_count, numeric_columns, categorical_columns, date_columns)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            filename, original_filename, file_path, file_size,
            json.dumps(columns), row_count,
            json.dumps(numeric_columns or []),
            json.dumps(categorical_columns or []),
            json.dumps(date_columns or [])
        ))
        
        file_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return file_id
    
    @staticmethod
    def get_by_id(file_id: int) -> Optional[Dict[str, Any]]:
        """Get file by ID"""
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM files WHERE id = ?", (file_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'id': row['id'],
                'filename': row['filename'],
                'original_filename': row['original_filename'],
                'file_path': row['file_path'],
                'file_size': row['file_size'],
                'columns': json.loads(row['columns']),
                'row_count': row['row_count'],
                'numeric_columns': json.loads(row['numeric_columns']),
                'categorical_columns': json.loads(row['categorical_columns']),
                'date_columns': json.loads(row['date_columns']),
                'upload_time': row['upload_time'],
                'status': row['status']
            }
        return None
    
    @staticmethod
    def get_all():
        """Get all files"""
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM files ORDER BY upload_time DESC")
        rows = cursor.fetchall()
        conn.close()
        
        files = []
        for row in rows:
            files.append({
                'id': row['id'],
                'filename': row['filename'],
                'original_filename': row['original_filename'],
                'file_size': row['file_size'],
                'columns': json.loads(row['columns']),
                'row_count': row['row_count'],
                'upload_time': row['upload_time'],
                'status': row['status']
            })
        return files

class SessionModel:
    """Model for session operations"""
    
    @staticmethod
    def create_or_get(session_id: str) -> Dict[str, Any]:
        """Create or get existing session"""
        conn = get_connection()
        cursor = conn.cursor()
        
        # Try to get existing session
        cursor.execute("SELECT * FROM sessions WHERE session_id = ?", (session_id,))
        row = cursor.fetchone()
        
        if row:
            # Update last activity
            cursor.execute(
                "UPDATE sessions SET last_activity = CURRENT_TIMESTAMP WHERE session_id = ?",
                (session_id,)
            )
            conn.commit()
            conn.close()
            return {
                'id': row['id'],
                'session_id': row['session_id'],
                'created_at': row['created_at'],
                'last_activity': datetime.now().isoformat()
            }
        else:
            # Create new session
            cursor.execute(
                "INSERT INTO sessions (session_id, metadata) VALUES (?, ?)",
                (session_id, json.dumps({}))
            )
            conn.commit()
            session_db_id = cursor.lastrowid
            conn.close()
            return {
                'id': session_db_id,
                'session_id': session_id,
                'created_at': datetime.now().isoformat(),
                'last_activity': datetime.now().isoformat()
            }

class MessageModel:
    """Model for message operations"""
    
    @staticmethod
    def create(session_id: str, message_type: str, content: str, 
               analysis_results: Dict[str, Any] = None) -> int:
        """Create a new message"""
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO messages (session_id, message_type, content, analysis_results)
            VALUES (?, ?, ?, ?)
        """, (
            session_id, message_type, content,
            json.dumps(analysis_results) if analysis_results else None
        ))
        
        message_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return message_id
    
    @staticmethod
    def get_session_history(session_id: str, limit: int = 50):
        """Get message history for a session"""
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM messages WHERE session_id = ?
            ORDER BY timestamp DESC LIMIT ?
        """, (session_id, limit))
        
        rows = cursor.fetchall()
        conn.close()
        
        messages = []
        for row in rows:
            messages.append({
                'id': row['id'],
                'message_type': row['message_type'],
                'content': row['content'],
                'analysis_results': json.loads(row['analysis_results']) if row['analysis_results'] else None,
                'timestamp': row['timestamp']
            })
        return list(reversed(messages))  # Return in chronological order

class ComprehensiveAnalysisModel:
    """Model for comprehensive analysis operations"""
    
    @staticmethod
    def create(session_id: str, task_id: str, query: str, file_ids: List[int],
               operation_type: str, analysis_results: Dict[str, Any], 
               execution_status: str = "completed") -> int:
        """Create a new comprehensive analysis record"""
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO comprehensive_analysis 
            (session_id, task_id, query, file_ids, operation_type, analysis_results, execution_status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            session_id, task_id, query, json.dumps(file_ids), 
            operation_type, json.dumps(analysis_results), execution_status
        ))
        
        analysis_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return analysis_id
    
    @staticmethod
    def get_by_session(session_id: str, limit: int = 10):
        """Get comprehensive analysis results for a session"""
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM comprehensive_analysis WHERE session_id = ?
            ORDER BY created_at DESC LIMIT ?
        """, (session_id, limit))
        
        rows = cursor.fetchall()
        conn.close()
        
        analyses = []
        for row in rows:
            analyses.append({
                'id': row['id'],
                'task_id': row['task_id'],
                'query': row['query'],
                'file_ids': json.loads(row['file_ids']),
                'operation_type': row['operation_type'],
                'analysis_results': json.loads(row['analysis_results']),
                'execution_status': row['execution_status'],
                'created_at': row['created_at']
            })
        return list(reversed(analyses))  # Return in chronological order
    
    @staticmethod
    def get_by_task_id(task_id: str) -> Optional[Dict[str, Any]]:
        """Get analysis by task ID"""
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM comprehensive_analysis WHERE task_id = ?", (task_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'id': row['id'],
                'session_id': row['session_id'],
                'task_id': row['task_id'],
                'query': row['query'],
                'file_ids': json.loads(row['file_ids']),
                'operation_type': row['operation_type'],
                'analysis_results': json.loads(row['analysis_results']),
                'execution_status': row['execution_status'],
                'created_at': row['created_at']
            }
        return None
    
    @staticmethod
    def update_status(task_id: str, status: str):
        """Update analysis execution status"""
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "UPDATE comprehensive_analysis SET execution_status = ? WHERE task_id = ?",
            (status, task_id)
        )
        conn.commit()
        conn.close()

if __name__ == "__main__":
    create_tables()
