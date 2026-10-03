import sqlite3

DB_PATH = "metrics_vault.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS audit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            document_type TEXT,
            extracted_json TEXT,
            compliance_score REAL,
            status TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def save_audit(filename, doc_type, extracted_json, score, status):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO audit_logs (filename, document_type, extracted_json, compliance_score, status)
        VALUES (?, ?, ?, ?, ?)
    """, (filename, doc_type, extracted_json, score, status))
    conn.commit()
    conn.close()

def fetch_history():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT filename, document_type, compliance_score, status, timestamp, extracted_json FROM audit_logs ORDER BY timestamp DESC")
    rows = cursor.fetchall()
    conn.close()
    return rows
