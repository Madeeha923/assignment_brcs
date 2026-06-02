import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict

from config import USE_SUPABASE, SUPABASE_URL, SUPABASE_KEY

logger = logging.getLogger(__name__)

class DatabaseService:
    def __init__(self, db_path: str = "appointments.db"):
        self.use_supabase = USE_SUPABASE

        if self.use_supabase:
            try:
                from supabase import create_client
            except ImportError as exc:
                logger.error("Supabase client is not installed: %s", exc)
                raise

            self.client = create_client(SUPABASE_URL, SUPABASE_KEY)
            self.init_db()
        else:
            import sqlite3
            self.sqlite3 = sqlite3
            self.db_path = db_path
            self.init_db()

    def get_connection(self):
        if self.use_supabase:
            raise RuntimeError("SQLite connection is not available when using Supabase")

        conn = self.sqlite3.connect(self.db_path)
        conn.row_factory = self.sqlite3.Row
        return conn

    def init_db(self):
        if self.use_supabase:
            try:
                self.client.table("appointments").select("id").limit(1).execute()
                self.client.table("message_logs").select("id").limit(1).execute()
            except Exception as exc:
                logger.warning(
                    "Supabase tables are not accessible. Please create 'appointments' and 'message_logs' tables in Supabase. %s",
                    exc,
                )
            return

        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS appointments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_name TEXT NOT NULL,
                phone_number TEXT NOT NULL,
                appointment_time TEXT NOT NULL,
                created_at TEXT NOT NULL,
                reminder_sent BOOLEAN DEFAULT 0,
                confirmation_sent BOOLEAN DEFAULT 0,
                status TEXT DEFAULT 'active'
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS message_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                appointment_id INTEGER NOT NULL,
                message_type TEXT,
                status TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY (appointment_id) REFERENCES appointments(id)
            )
        """)

        conn.commit()
        conn.close()

    def _check_response(self, result):
        if hasattr(result, "error") and result.error is not None:
            raise Exception(result.error)
        return result.data

    def create_appointment(self, customer_name: str, phone_number: str, appointment_time: str) -> Dict:
        created_at = datetime.now().isoformat()

        if self.use_supabase:
            result = self.client.table("appointments").insert({
                "customer_name": customer_name,
                "phone_number": phone_number,
                "appointment_time": appointment_time,
                "created_at": created_at,
                "reminder_sent": False,
                "confirmation_sent": False,
                "status": "active",
            }).execute()

            data = self._check_response(result)
            return data[0] if isinstance(data, list) and data else data

        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO appointments (customer_name, phone_number, appointment_time, created_at)
            VALUES (?, ?, ?, ?)
        """, (customer_name, phone_number, appointment_time, created_at))
        conn.commit()
        appointment_id = cursor.lastrowid
        conn.close()

        return {
            "id": appointment_id,
            "customer_name": customer_name,
            "phone_number": phone_number,
            "appointment_time": appointment_time,
            "created_at": created_at,
            "reminder_sent": False,
            "confirmation_sent": False,
            "status": "active",
        }

    def get_all_appointments(self) -> List[Dict]:
        if self.use_supabase:
            result = self.client.table("appointments").select("*").order("appointment_time", desc=True).execute()
            return self._check_response(result) or []

        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, customer_name, phone_number, appointment_time, 
                   created_at, reminder_sent, confirmation_sent, status
            FROM appointments
            ORDER BY appointment_time DESC
        """)
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def get_appointment(self, appointment_id: int) -> Optional[Dict]:
        if self.use_supabase:
            result = self.client.table("appointments").select("*").eq("id", appointment_id).single().execute()
            return self._check_response(result)

        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, customer_name, phone_number, appointment_time, 
                   created_at, reminder_sent, confirmation_sent, status
            FROM appointments
            WHERE id = ?
        """, (appointment_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    def update_appointment(self, appointment_id: int, **kwargs) -> bool:
        allowed_fields = ["customer_name", "phone_number", "appointment_time", "status"]
        update_fields = {k: v for k, v in kwargs.items() if k in allowed_fields}
        if not update_fields:
            return False

        if self.use_supabase:
            result = self.client.table("appointments").update(update_fields).eq("id", appointment_id).execute()
            self._check_response(result)
            return True

        conn = self.get_connection()
        cursor = conn.cursor()
        set_clause = ", ".join([f"{k} = ?" for k in update_fields.keys()])
        values = list(update_fields.values()) + [appointment_id]
        cursor.execute(f"""
            UPDATE appointments
            SET {set_clause}
            WHERE id = ?
        """, values)
        conn.commit()
        success = cursor.rowcount > 0
        conn.close()
        return success

    def mark_confirmation_sent(self, appointment_id: int) -> bool:
        if self.use_supabase:
            result = self.client.table("appointments").update({"confirmation_sent": True}).eq("id", appointment_id).execute()
            self._check_response(result)
            return True

        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE appointments
            SET confirmation_sent = 1
            WHERE id = ?
        """, (appointment_id,))
        conn.commit()
        success = cursor.rowcount > 0
        conn.close()
        return success

    def mark_reminder_sent(self, appointment_id: int) -> bool:
        if self.use_supabase:
            result = self.client.table("appointments").update({"reminder_sent": True}).eq("id", appointment_id).execute()
            self._check_response(result)
            return True

        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE appointments
            SET reminder_sent = 1
            WHERE id = ?
        """, (appointment_id,))
        conn.commit()
        success = cursor.rowcount > 0
        conn.close()
        return success

    def get_pending_reminders(self, threshold_minutes: int = 60) -> List[Dict]:
        now = datetime.now()
        threshold_time = now + timedelta(minutes=threshold_minutes)

        if self.use_supabase:
            result = (
                self.client.table("appointments")
                .select("*")
                .eq("reminder_sent", False)
                .eq("status", "active")
                .gte("appointment_time", now.isoformat())
                .lte("appointment_time", threshold_time.isoformat())
                .execute()
            )
            return self._check_response(result) or []

        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, customer_name, phone_number, appointment_time, created_at
            FROM appointments
            WHERE reminder_sent = 0
            AND status = 'active'
            AND appointment_time <= ?
            AND appointment_time >= ?
        """, (threshold_time.isoformat(), now.isoformat()))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def log_message(self, appointment_id: int, message_type: str, status: str) -> bool:
        created_at = datetime.now().isoformat()
        if self.use_supabase:
            result = self.client.table("message_logs").insert({
                "appointment_id": appointment_id,
                "message_type": message_type,
                "status": status,
                "created_at": created_at,
            }).execute()
            self._check_response(result)
            return True

        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO message_logs (appointment_id, message_type, status, created_at)
            VALUES (?, ?, ?, ?)
        """, (appointment_id, message_type, status, created_at))
        conn.commit()
        success = cursor.rowcount > 0
        conn.close()
        return success

    def delete_appointment(self, appointment_id: int) -> bool:
        if self.use_supabase:
            result = self.client.table("appointments").delete().eq("id", appointment_id).execute()
            self._check_response(result)
            return True

        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM appointments WHERE id = ?", (appointment_id,))
        conn.commit()
        success = cursor.rowcount > 0
        conn.close()
        return success
