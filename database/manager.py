# database/manager.py
"""
مدیریت اتصال به پایگاه داده و اجرای کوئری‌ها
"""
import sqlite3
from typing import List, Dict, Any, Optional


class DatabaseManager:
    def __init__(self, db_name: str = 'garment_factory.db'):
        self.db_name = db_name
        self.conn: Optional[sqlite3.Connection] = None
        self.cursor: Optional[sqlite3.Cursor] = None
        self.connect()
        self.create_tables()

    def connect(self):
        """اتصال به پایگاه داده"""
        self.conn = sqlite3.connect(self.db_name, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row  # برای دسترسی به ستون‌ها با نام
        self.cursor = self.conn.cursor()

    def create_tables(self):
        """ایجاد جداول پایگاه داده"""
        try:
            # جدول ورودی پوشاک
            self.cursor.execute('''
                                CREATE TABLE IF NOT EXISTS garment_entries
                                (
                                    id
                                    INTEGER
                                    PRIMARY
                                    KEY
                                    AUTOINCREMENT,
                                    product_name
                                    TEXT
                                    NOT
                                    NULL,
                                    product_code
                                    TEXT
                                    UNIQUE
                                    NOT
                                    NULL,
                                    size
                                    TEXT
                                    NOT
                                    NULL,
                                    color
                                    TEXT
                                    NOT
                                    NULL,
                                    custom_color
                                    TEXT,
                                    fabric_type
                                    TEXT
                                    NOT
                                    NULL,
                                    entry_date
                                    DATE
                                    NOT
                                    NULL,
                                    tailor_name
                                    TEXT
                                    NOT
                                    NULL,
                                    quantity
                                    INTEGER
                                    DEFAULT
                                    1,
                                    notes
                                    TEXT,
                                    created_at
                                    TIMESTAMP
                                    DEFAULT
                                    CURRENT_TIMESTAMP
                                )
                                ''')

            # ایجاد ایندکس‌ها برای بهبود عملکرد
            self.cursor.execute('''
                                CREATE INDEX IF NOT EXISTS idx_entries_product_code
                                    ON garment_entries(product_code)
                                ''')

            self.cursor.execute('''
                                CREATE INDEX IF NOT EXISTS idx_entries_entry_date
                                    ON garment_entries(entry_date)
                                ''')

            self.cursor.execute('''
                                CREATE INDEX IF NOT EXISTS idx_entries_tailor_name
                                    ON garment_entries(tailor_name)
                                ''')

            # جدول خروجی پوشاک
            self.cursor.execute('''
                                CREATE TABLE IF NOT EXISTS garment_outputs
                                (
                                    id
                                    INTEGER
                                    PRIMARY
                                    KEY
                                    AUTOINCREMENT,
                                    product_code
                                    TEXT
                                    NOT
                                    NULL,
                                    output_date
                                    DATE
                                    NOT
                                    NULL,
                                    quality
                                    TEXT
                                    NOT
                                    NULL,
                                    destination
                                    TEXT,
                                    quantity
                                    INTEGER
                                    DEFAULT
                                    1,
                                    package_code
                                    TEXT,
                                    notes
                                    TEXT,
                                    created_at
                                    TIMESTAMP
                                    DEFAULT
                                    CURRENT_TIMESTAMP
                                )
                                ''')

            # ایجاد ایندکس‌ها برای جدول خروجی
            self.cursor.execute('''
                                CREATE INDEX IF NOT EXISTS idx_outputs_product_code
                                    ON garment_outputs(product_code)
                                ''')

            self.cursor.execute('''
                                CREATE INDEX IF NOT EXISTS idx_outputs_output_date
                                    ON garment_outputs(output_date)
                                ''')

            # جدول کارمندان
            self.cursor.execute('''
                                CREATE TABLE IF NOT EXISTS employees
                                (
                                    id
                                    INTEGER
                                    PRIMARY
                                    KEY
                                    AUTOINCREMENT,
                                    first_name
                                    TEXT
                                    NOT
                                    NULL,
                                    last_name
                                    TEXT
                                    NOT
                                    NULL,
                                    national_id
                                    TEXT
                                    UNIQUE,
                                    birth_date
                                    DATE,
                                    address
                                    TEXT,
                                    phone
                                    TEXT
                                    NOT
                                    NULL,
                                    position
                                    TEXT,
                                    hire_date
                                    DATE,
                                    salary
                                    REAL,
                                    status
                                    TEXT
                                    DEFAULT
                                    'فعال',
                                    notes
                                    TEXT,
                                    created_at
                                    TIMESTAMP
                                    DEFAULT
                                    CURRENT_TIMESTAMP
                                )
                                ''')

            self.conn.commit()
            print("✅ جداول پایگاه داده با موفقیت ایجاد شدند")

        except sqlite3.Error as e:
            print(f"❌ خطا در ایجاد جداول: {e}")
            raise

    def execute_query(self, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """
        اجرای کوئری و بازگشت نتایج به صورت دیکشنری

        Args:
            query: کوئری SQL
            params: پارامترهای کوئری

        Returns:
            لیست دیکشنری‌های نتیجه
        """
        try:
            self.cursor.execute(query, params)

            # اگر کوئری SELECT است، نتایج را برگردان
            if query.strip().upper().startswith('SELECT'):
                columns = [col[0] for col in self.cursor.description]
                results = []
                for row in self.cursor.fetchall():
                    results.append(dict(zip(columns, row)))
                return results
            else:
                # برای INSERT, UPDATE, DELETE
                self.conn.commit()
                return []

        except sqlite3.Error as e:
            self.conn.rollback()
            print(f"❌ خطا در اجرای کوئری: {e}")
            print(f"🔍 کوئری: {query}")
            print(f"📊 پارامترها: {params}")
            raise

    def execute_many(self, query: str, params_list: List[tuple]) -> None:
        """اجرای کوئری با چندین مجموعه پارامتر"""
        try:
            self.cursor.executemany(query, params_list)
            self.conn.commit()
        except sqlite3.Error as e:
            self.conn.rollback()
            print(f"❌ خطا در اجرای کوئری چندگانه: {e}")
            raise

    def get_last_row_id(self) -> int:
        """دریافت آخرین id وارد شده"""
        return self.cursor.lastrowid

    def backup_database(self, backup_path: str) -> bool:
        """پشتیبان‌گیری از پایگاه داده"""
        try:
            import shutil
            shutil.copy2(self.db_name, backup_path)
            return True
        except Exception as e:
            print(f"❌ خطا در پشتیبان‌گیری: {e}")
            return False

    def restore_database(self, backup_path: str) -> bool:
        """بازیابی پایگاه داده از فایل پشتیبان"""
        try:
            import shutil
            self.close()  # بستن اتصال فعلی
            shutil.copy2(backup_path, self.db_name)
            self.connect()  # اتصال مجدد
            return True
        except Exception as e:
            print(f"❌ خطا در بازیابی: {e}")
            return False

    def close(self):
        """بستن اتصال پایگاه داده"""
        if self.conn:
            self.conn.close()
            self.conn = None
            self.cursor = None

    def __enter__(self):
        """Context manager enter"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()

    def __del__(self):
        """Destructor"""
        self.close()