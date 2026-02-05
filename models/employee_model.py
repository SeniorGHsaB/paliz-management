# models/employee_model.py (نسخه اصلاح‌شده)
"""
مدل مدیریت کارمندان
"""
from typing import List, Dict, Any, Tuple, Optional
from datetime import datetime
from database.manager import DatabaseManager
from utils.validators import EmployeeValidator

# تعریف مستقیم مقادیر (اگر import مشکل داشت)
EMPLOYEE_POSITIONS = ["دوزنده", "برشکار", "بسته‌بند", "انباردار", "مدیر", "کارگر", "ناظر کیفیت"]
EMPLOYEE_STATUSES = ["فعال", "غیرفعال", "مرخصی", "اخراج شده"]


class EmployeeModel:
    """مدل مدیریت کارمندان"""

    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        self.logger = None

    def set_logger(self, logger):
        """تنظیم لاگر"""
        self.logger = logger

    def add_employee(self, data: Dict[str, Any]) -> Tuple[bool, str]:
        """
        افزودن کارمند جدید

        Args:
            data: اطلاعات کارمند

        Returns:
            (موفقیت, پیام)
        """
        try:
            if self.logger:
                self.logger.info(f"در حال ثبت کارمند جدید: {data.get('first_name', '')} {data.get('last_name', '')}")

            # اعتبارسنجی
            validation_result = self._validate_employee_data(data)
            if not validation_result[0]:
                return validation_result

            # بررسی تکراری بودن کد ملی
            national_id = data.get('national_id')
            if national_id and self._is_national_id_duplicate(national_id):
                return False, "کد ملی تکراری است"

            # ذخیره در دیتابیس
            query = '''
                    INSERT INTO employees
                    (first_name, last_name, national_id, birth_date, address, phone,
                     position, hire_date, salary, status, notes)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) \
                    '''

            params = (
                data['first_name'],
                data['last_name'],
                data.get('national_id', ''),
                data.get('birth_date', ''),
                data.get('address', ''),
                data['phone'],
                data.get('position', ''),
                data.get('hire_date', datetime.now().strftime('%Y-%m-%d')),
                float(data.get('salary', 0)) if data.get('salary') else 0.0,
                data.get('status', 'فعال'),
                data.get('notes', '')
            )

            self.db.execute_query(query, params)

            if self.logger:
                self.logger.info(f"کارمند {data['first_name']} {data['last_name']} ثبت شد")

            return True, "کارمند با موفقیت ثبت شد"

        except Exception as e:
            error_msg = f"خطا در ثبت کارمند: {str(e)}"
            if self.logger:
                self.logger.error(error_msg)
            return False, error_msg

    def get_all_employees(self) -> List[Dict[str, Any]]:
        """
        دریافت همه کارمندان

        Returns:
            لیست کارمندان
        """
        try:
            query = '''
                    SELECT id, \
                           first_name, \
                           last_name, \
                           national_id, \
                           position,
                           phone, \
                           hire_date, \
                           status, \
                           salary, \
                           birth_date, \
                           address, \
                           notes
                    FROM employees
                    ORDER BY last_name, first_name \
                    '''

            results = self.db.execute_query(query)
            return results

        except Exception as e:
            if self.logger:
                self.logger.error(f"خطا در دریافت کارمندان: {str(e)}")
            return []

    def get_employee_by_id(self, employee_id: int) -> Optional[Dict[str, Any]]:
        """
        دریافت کارمند بر اساس شناسه

        Args:
            employee_id: شناسه کارمند

        Returns:
            اطلاعات کارمند یا None
        """
        try:
            query = 'SELECT * FROM employees WHERE id = ?'
            results = self.db.execute_query(query, (employee_id,))

            return results[0] if results else None

        except Exception as e:
            if self.logger:
                self.logger.error(f"خطا در دریافت کارمند {employee_id}: {str(e)}")
            return None

    def get_employee_by_national_id(self, national_id: str) -> Optional[Dict[str, Any]]:
        """
        دریافت کارمند بر اساس کد ملی

        Args:
            national_id: کد ملی

        Returns:
            اطلاعات کارمند یا None
        """
        try:
            query = 'SELECT * FROM employees WHERE national_id = ?'
            results = self.db.execute_query(query, (national_id,))

            return results[0] if results else None

        except Exception as e:
            if self.logger:
                self.logger.error(f"خطا در دریافت کارمند با کد ملی {national_id}: {str(e)}")
            return None

    def update_employee(self, employee_id: int, data: Dict[str, Any]) -> Tuple[bool, str]:
        """
        به‌روزرسانی اطلاعات کارمند

        Args:
            employee_id: شناسه کارمند
            data: اطلاعات جدید

        Returns:
            (موفقیت, پیام)
        """
        try:
            # بررسی وجود کارمند
            employee = self.get_employee_by_id(employee_id)
            if not employee:
                return False, "کارمند مورد نظر یافت نشد"

            # اعتبارسنجی
            validation_result = self._validate_employee_data(data, update=True)
            if not validation_result[0]:
                return validation_result

            # به‌روزرسانی
            query = '''
                    UPDATE employees
                    SET first_name  = ?, \
                        last_name   = ?, \
                        national_id = ?, \
                        birth_date  = ?,
                        address     = ?, \
                        phone       = ?, \
                        position    = ?, \
                        hire_date   = ?,
                        salary      = ?, \
                        status      = ?, \
                        notes       = ?
                    WHERE id = ? \
                    '''

            params = (
                data.get('first_name', employee['first_name']),
                data.get('last_name', employee['last_name']),
                data.get('national_id', employee['national_id']),
                data.get('birth_date', employee['birth_date']),
                data.get('address', employee['address']),
                data.get('phone', employee['phone']),
                data.get('position', employee['position']),
                data.get('hire_date', employee['hire_date']),
                float(data.get('salary', employee['salary'])) if data.get('salary') else employee['salary'],
                data.get('status', employee['status']),
                data.get('notes', employee['notes']),
                employee_id
            )

            self.db.execute_query(query, params)

            if self.logger:
                self.logger.info(f"کارمند {employee_id} به‌روزرسانی شد")

            return True, "اطلاعات کارمند با موفقیت به‌روزرسانی شد"

        except Exception as e:
            error_msg = f"خطا در به‌روزرسانی کارمند: {str(e)}"
            if self.logger:
                self.logger.error(error_msg)
            return False, error_msg

    def delete_employee(self, employee_id: int) -> Tuple[bool, str]:
        """
        حذف کارمند

        Args:
            employee_id: شناسه کارمند

        Returns:
            (موفقیت, پیام)
        """
        try:
            # بررسی وجود کارمند
            employee = self.get_employee_by_id(employee_id)
            if not employee:
                return False, "کارمند مورد نظر یافت نشد"

            # حذف
            query = 'DELETE FROM employees WHERE id = ?'
            self.db.execute_query(query, (employee_id,))

            if self.logger:
                self.logger.info(f"کارمند {employee_id} حذف شد")

            return True, "کارمند با موفقیت حذف شد"

        except Exception as e:
            error_msg = f"خطا در حذف کارمند: {str(e)}"
            if self.logger:
                self.logger.error(error_msg)
            return False, error_msg

    def search_employees(self, search_term: str) -> List[Dict[str, Any]]:
        """
        جستجوی کارمندان

        Args:
            search_term: عبارت جستجو

        Returns:
            لیست کارمندان
        """
        try:
            query = '''
                    SELECT id, first_name, last_name, national_id, position, phone, status
                    FROM employees
                    WHERE first_name LIKE ? \
                       OR last_name LIKE ? \
                       OR national_id LIKE ?
                       OR phone LIKE ? \
                       OR position LIKE ?
                    ORDER BY last_name, first_name \
                    '''

            search_pattern = f'%{search_term}%'
            params = (search_pattern, search_pattern, search_pattern,
                      search_pattern, search_pattern)

            return self.db.execute_query(query, params)

        except Exception as e:
            if self.logger:
                self.logger.error(f"خطا در جستجوی کارمندان '{search_term}': {str(e)}")
            return []

    def get_employee_stats(self) -> Dict[str, Any]:
        """
        دریافت آمار کارمندان

        Returns:
            آمار کارمندان
        """
        try:
            # تعداد کل
            query_total = 'SELECT COUNT(*) as total FROM employees'
            total_result = self.db.execute_query(query_total)
            total_employees = total_result[0]['total'] if total_result else 0

            # تعداد فعال
            query_active = 'SELECT COUNT(*) as active FROM employees WHERE status = "فعال"'
            active_result = self.db.execute_query(query_active)
            active_employees = active_result[0]['active'] if active_result else 0

            # تعداد بر اساس سمت
            query_position = '''
                             SELECT position, COUNT(*) as count
                             FROM employees
                             WHERE position IS NOT NULL AND position != ""
                             GROUP BY position
                             ORDER BY count DESC \
                             '''
            position_stats = self.db.execute_query(query_position)

            return {
                'total_employees': total_employees,
                'active_employees': active_employees,
                'inactive_employees': total_employees - active_employees,
                'position_stats': position_stats
            }

        except Exception as e:
            if self.logger:
                self.logger.error(f"خطا در دریافت آمار کارمندان: {str(e)}")
            return {'total_employees': 0, 'active_employees': 0,
                    'inactive_employees': 0, 'position_stats': []}

    def get_constants(self) -> Dict[str, List[str]]:
        """دریافت لیست‌های ثابت"""
        return {
            'positions': EMPLOYEE_POSITIONS,
            'statuses': EMPLOYEE_STATUSES
        }

    # ==================== متدهای خصوصی ====================

    def _validate_employee_data(self, data: Dict[str, Any], update: bool = False) -> Tuple[bool, str]:
        """اعتبارسنجی داده‌های کارمند"""
        required_fields = ['first_name', 'last_name', 'phone']

        for field in required_fields:
            if field not in data or not data[field]:
                return False, f"فیلد {field} الزامی است"

        # اعتبارسنجی نام
        is_valid, message = EmployeeValidator.validate_name(data['first_name'], "نام")
        if not is_valid:
            return False, message

        is_valid, message = EmployeeValidator.validate_name(data['last_name'], "نام خانوادگی")
        if not is_valid:
            return False, message

        # اعتبارسنجی تلفن
        is_valid, message = EmployeeValidator.validate_phone(data['phone'])
        if not is_valid:
            return False, message

        # اعتبارسنجی کد ملی (اگر وجود دارد)
        if 'national_id' in data and data['national_id']:
            is_valid, message = EmployeeValidator.validate_national_id(data['national_id'])
            if not is_valid:
                return False, message

        return True, ""

    def _is_national_id_duplicate(self, national_id: str) -> bool:
        """بررسی تکراری بودن کد ملی"""
        if not national_id:
            return False

        results = self.db.execute_query(
            'SELECT id FROM employees WHERE national_id = ?',
            (national_id,)
        )
        return len(results) > 0