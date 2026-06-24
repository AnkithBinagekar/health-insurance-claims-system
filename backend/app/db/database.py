import sqlite3
import json
from datetime import datetime
from backend.app.schemas.claim import ClaimContext

DB_PATH = "claims_history.db"

def init_db():
    """Initializes the SQLite database schema."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS claims (
            claim_id TEXT PRIMARY KEY,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            member_id TEXT,
            category TEXT,
            decision TEXT,
            approved_amount REAL,
            confidence_score REAL,
            execution_status TEXT,
            halt_reason TEXT,
            full_trace JSON
        )
    ''')
    conn.commit()
    conn.close()

def save_claim_to_db(context: ClaimContext):
    """Extracts required fields from the context and persists them."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Safely extract decision string
        decision_val = context.result.decision.value if context.result.decision else "PENDING"
        execution_status = "HALTED" if context.state.is_halted else "COMPLETED"
        
        cursor.execute('''
            INSERT OR REPLACE INTO claims 
            (claim_id, member_id, category, decision, approved_amount, confidence_score, execution_status, halt_reason, full_trace)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            context.input.claim_id,
            context.input.member_id,
            context.input.claim_category.value,
            decision_val,
            context.result.approved_amount,
            context.trace.current_confidence_score,
            execution_status,
            context.state.halt_reason,
            context.model_dump_json() # Store the entire traceable context
        ))
        conn.commit()
        print(f"💾 Persisted Claim {context.input.claim_id} to SQLite.")
    except Exception as e:
        print(f"Failed to persist claim to DB: {e}")
    finally:
        conn.close()