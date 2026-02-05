# models/garment_model.py
"""
مدل مدیریت پوشاک - شامل منطق مربوط به ورودی و خروجی پوشاک
"""
from typing import List, Dict, Any, Tuple, Optional
from datetime import datetime, date, timedelta
from database.manager import DatabaseManager
from utils.validators import Validator
from config.constants import FABRIC_COLORS, FABRIC_TYPES, SIZES, QUALITIES


class GarmentModel:
    """مدل مدیریت پوشاک"""

    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        self.logger = None  # بعداً مقداردهی می‌شود

    def set_logger(self, logger):
        """تنظیم لاگر"""
        self.logger = logger

    # ==================== متدهای ورودی پوشاک ====================

    def add_garment_entry(self, data: Dict[str, Any]) -> Tuple[bool, str]:
        """
        افزودن ورودی جدید پوشاک

        Args:
            data: دیکشنری شامل اطلاعات ورودی

        Returns:
            (موفقیت, پیام)
        """
        try:
            if self.logger:
                self.logger.info(f"در حال ثبت ورودی جدید: {data.get('product_code', '')}")

            # اعتبارسنجی داده‌ها
            validation_result = self._validate_garment_entry_data(data)
            if not validation_result[0]:
                return validation_result

            # بررسی تکراری نبودن کد محصول
            if self._is_product_code_duplicate(data['product_code']):
                return False, "کد محصول تکراری است"

            # ذخیره در دیتابیس
            query = '''
                    INSERT INTO garment_entries
                    (product_name, product_code, size, color, custom_color, fabric_type,
                     entry_date, tailor_name, quantity, notes)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?) \
                    '''

            params = (
                data['product_name'],
                data['product_code'],
                data.get('size', 'تک سایز'),
                data.get('color', ''),
                data.get('custom_color', ''),
                data.get('fabric_type', ''),
                data.get('entry_date', datetime.now().strftime('%Y-%m-%d')),
                data.get('tailor_name', ''),
                int(data.get('quantity', 1)),
                data.get('notes', '')
            )

            self.db.execute_query(query, params)

            if self.logger:
                self.logger.info(f"ورودی با کد {data['product_code']} با موفقیت ثبت شد")

            return True, "ورودی پوشاک با موفقیت ثبت شد"

        except Exception as e:
            error_msg = f"خطا در ثبت ورودی: {str(e)}"
            if self.logger:
                self.logger.error(error_msg)
            return False, error_msg

    def get_all_entries(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        دریافت همه ورودی‌ها

        Args:
            limit: تعداد رکوردهای بازگشتی

        Returns:
            لیست ورودی‌ها
        """
        try:
            query = '''
                    SELECT id, \
                           product_code, \
                           product_name, \
                           color, size, fabric_type, entry_date, tailor_name, quantity, notes, created_at
                    FROM garment_entries
                    ORDER BY entry_date DESC, created_at DESC
                        LIMIT ? \
                    '''

            results = self.db.execute_query(query, (limit,))

            if self.logger:
                self.logger.debug(f"تعداد {len(results)} ورودی بازیابی شد")

            return results

        except Exception as e:
            error_msg = f"خطا در دریافت ورودی‌ها: {str(e)}"
            if self.logger:
                self.logger.error(error_msg)
            return []

    def get_entry_by_code(self, product_code: str) -> Optional[Dict[str, Any]]:
        """
        دریافت ورودی بر اساس کد محصول

        Args:
            product_code: کد محصول

        Returns:
            اطلاعات ورودی یا None
        """
        try:
            query = 'SELECT * FROM garment_entries WHERE product_code = ?'
            results = self.db.execute_query(query, (product_code,))

            return results[0] if results else None

        except Exception as e:
            if self.logger:
                self.logger.error(f"خطا در دریافت ورودی {product_code}: {str(e)}")
            return None

    def delete_entry(self, product_code: str) -> Tuple[bool, str]:
        """
        حذف ورودی

        Args:
            product_code: کد محصول

        Returns:
            (موفقیت, پیام)
        """
        try:
            # بررسی وجود ورودی
            entry = self.get_entry_by_code(product_code)
            if not entry:
                return False, "ورودی مورد نظر یافت نشد"

            # حذف
            query = 'DELETE FROM garment_entries WHERE product_code = ?'
            self.db.execute_query(query, (product_code,))

            if self.logger:
                self.logger.info(f"ورودی با کد {product_code} حذف شد")

            return True, "ورودی با موفقیت حذف شد"

        except Exception as e:
            error_msg = f"خطا در حذف ورودی: {str(e)}"
            if self.logger:
                self.logger.error(error_msg)
            return False, error_msg

    def update_entry_quantity(self, product_code: str, new_quantity: int) -> Tuple[bool, str]:
        """
        به‌روزرسانی تعداد موجودی

        Args:
            product_code: کد محصول
            new_quantity: تعداد جدید

        Returns:
            (موفقیت, پیام)
        """
        try:
            query = 'UPDATE garment_entries SET quantity = ? WHERE product_code = ?'
            self.db.execute_query(query, (new_quantity, product_code))

            if self.logger:
                self.logger.info(f"موجودی کد {product_code} به {new_quantity} به‌روز شد")

            return True, "موجودی با موفقیت به‌روز شد"

        except Exception as e:
            error_msg = f"خطا در به‌روزرسانی موجودی: {str(e)}"
            if self.logger:
                self.logger.error(error_msg)
            return False, error_msg

    # ==================== متدهای خروجی پوشاک ====================

    def add_garment_output(self, data: Dict[str, Any]) -> Tuple[bool, str]:
        """
        افزودن خروجی جدید

        Args:
            data: اطلاعات خروجی

        Returns:
            (موفقیت, پیام)
        """
        try:
            if self.logger:
                self.logger.info(f"در حال ثبت خروجی برای کد {data.get('product_code', '')}")

            # اعتبارسنجی
            validation_result = self._validate_garment_output_data(data)
            if not validation_result[0]:
                return validation_result

            # بررسی موجودی
            product_code = data['product_code']
            quantity = int(data['quantity'])

            available = self.get_available_quantity(product_code)
            if available is None:
                return False, "محصول مورد نظر یافت نشد"

            if quantity > available:
                return False, f"موجودی کافی نیست. موجودی: {available}"

            # ذخیره خروجی
            query = '''
                    INSERT INTO garment_outputs
                    (product_code, output_date, quality, destination, quantity, package_code, notes)
                    VALUES (?, ?, ?, ?, ?, ?, ?) \
                    '''

            params = (
                product_code,
                data.get('output_date', datetime.now().strftime('%Y-%m-%d')),
                data.get('quality', ''),
                data.get('destination', ''),
                quantity,
                data.get('package_code', ''),
                data.get('notes', '')
            )

            self.db.execute_query(query, params)

            # کاهش موجودی
            new_quantity = available - quantity
            self.update_entry_quantity(product_code, new_quantity)

            if self.logger:
                self.logger.info(f"خروجی برای کد {product_code} ثبت شد. موجودی جدید: {new_quantity}")

            return True, "خروجی با موفقیت ثبت شد"

        except Exception as e:
            error_msg = f"خطا در ثبت خروجی: {str(e)}"
            if self.logger:
                self.logger.error(error_msg)
            return False, error_msg

    def get_all_outputs(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        دریافت همه خروجی‌ها

        Args:
            limit: تعداد رکوردها

        Returns:
            لیست خروجی‌ها
        """
        try:
            query = '''
                    SELECT id, \
                           product_code, \
                           output_date, \
                           quality, \
                           destination,
                           quantity, \
                           package_code, \
                           notes, \
                           created_at
                    FROM garment_outputs
                    ORDER BY output_date DESC, created_at DESC LIMIT ? \
                    '''

            results = self.db.execute_query(query, (limit,))
            return results

        except Exception as e:
            if self.logger:
                self.logger.error(f"خطا در دریافت خروجی‌ها: {str(e)}")
            return []

    def delete_output(self, output_id: int) -> Tuple[bool, str]:
        """
        حذف خروجی

        Args:
            output_id: شناسه خروجی

        Returns:
            (موفقیت, پیام)
        """
        try:
            # دریافت اطلاعات خروجی
            query = 'SELECT * FROM garment_outputs WHERE id = ?'
            results = self.db.execute_query(query, (output_id,))

            if not results:
                return False, "خروجی مورد نظر یافت نشد"

            output = results[0]
            product_code = output['product_code']
            quantity = output['quantity']

            # بازیابی موجودی
            current = self.get_available_quantity(product_code)
            if current is not None:
                new_quantity = current + quantity
                self.update_entry_quantity(product_code, new_quantity)

            # حذف خروجی
            delete_query = 'DELETE FROM garment_outputs WHERE id = ?'
            self.db.execute_query(delete_query, (output_id,))

            if self.logger:
                self.logger.info(f"خروجی با شناسه {output_id} حذف شد")

            return True, "خروجی با موفقیت حذف شد"

        except Exception as e:
            error_msg = f"خطا در حذف خروجی: {str(e)}"
            if self.logger:
                self.logger.error(error_msg)
            return False, error_msg

    # ==================== متدهای کمکی ====================

    def get_available_quantity(self, product_code: str) -> Optional[int]:
        """
        دریافت موجودی یک محصول

        Args:
            product_code: کد محصول

        Returns:
            تعداد موجودی یا None
        """
        try:
            query = 'SELECT quantity FROM garment_entries WHERE product_code = ?'
            results = self.db.execute_query(query, (product_code,))

            return results[0]['quantity'] if results else None

        except Exception as e:
            if self.logger:
                self.logger.error(f"خطا در دریافت موجودی {product_code}: {str(e)}")
            return None

    def search_products(self, search_term: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        جستجوی محصولات

        Args:
            search_term: عبارت جستجو
            limit: تعداد نتایج

        Returns:
            لیست محصولات
        """
        try:
            query = '''
                    SELECT product_code, product_name, color, size, fabric_type, quantity
                    FROM garment_entries
                    WHERE product_code LIKE ? \
                       OR product_name LIKE ? \
                       OR color LIKE ?
                       OR tailor_name LIKE ? \
                       OR fabric_type LIKE ?
                    ORDER BY product_name
                        LIMIT ? \
                    '''

            search_pattern = f'%{search_term}%'
            params = (search_pattern, search_pattern, search_pattern,
                      search_pattern, search_pattern, limit)

            return self.db.execute_query(query, params)

        except Exception as e:
            if self.logger:
                self.logger.error(f"خطا در جستجوی '{search_term}': {str(e)}")
            return []

    def get_inventory_stats(self) -> Dict[str, Any]:
        """
        دریافت آمار موجودی

        Returns:
            دیکشنری آمار
        """
        try:
            # کل موجودی
            query_total = 'SELECT SUM(quantity) as total FROM garment_entries'
            total_result = self.db.execute_query(query_total)
            total_inventory = total_result[0]['total'] if total_result and total_result[0]['total'] else 0

            # موجودی بر اساس رنگ
            query_color = '''
                          SELECT color, SUM(quantity) as total
                          FROM garment_entries
                          GROUP BY color
                          ORDER BY total DESC \
                          '''
            color_stats = self.db.execute_query(query_color)

            # موجودی بر اساس سایز
            query_size = '''
                         SELECT size, SUM (quantity) as total
                         FROM garment_entries
                         GROUP BY size
                         ORDER BY total DESC \
                         '''
            size_stats = self.db.execute_query(query_size)

            return {
                'total_inventory': total_inventory,
                'color_stats': color_stats,
                'size_stats': size_stats,
                'product_count': len(self.get_all_entries(1000))
            }

        except Exception as e:
            if self.logger:
                self.logger.error(f"خطا در دریافت آمار موجودی: {str(e)}")
            return {'total_inventory': 0, 'color_stats': [], 'size_stats': [], 'product_count': 0}

    def get_daily_stats(self, target_date: Optional[str] = None) -> Dict[str, Any]:
        """
        دریافت آمار روزانه

        Args:
            target_date: تاریخ مورد نظر (اگر None باشد امروز)

        Returns:
            آمار روزانه
        """
        try:
            if target_date is None:
                target_date = datetime.now().strftime('%Y-%m-%d')

            # ورودی‌های امروز
            query_entries = '''
                            SELECT COUNT(*) as count, SUM(quantity) as total
                            FROM garment_entries
                            WHERE entry_date = ? \
                            '''
            entries_result = self.db.execute_query(query_entries, (target_date,))

            # خروجی‌های امروز
            query_outputs = '''
                            SELECT COUNT(*) as count, SUM(quantity) as total
                            FROM garment_outputs
                            WHERE output_date = ? \
                            '''
            outputs_result = self.db.execute_query(query_outputs, (target_date,))

            return {
                'date': target_date,
                'entries_count': entries_result[0]['count'] if entries_result else 0,
                'entries_quantity': entries_result[0]['total'] if entries_result and entries_result[0]['total'] else 0,
                'outputs_count': outputs_result[0]['count'] if outputs_result else 0,
                'outputs_quantity': outputs_result[0]['total'] if outputs_result and outputs_result[0]['total'] else 0
            }

        except Exception as e:
            if self.logger:
                self.logger.error(f"خطا در دریافت آمار روزانه: {str(e)}")
            return {'date': target_date, 'entries_count': 0, 'entries_quantity': 0,
                    'outputs_count': 0, 'outputs_quantity': 0}

    # ==================== متدهای خصوصی ====================

    def _validate_garment_entry_data(self, data: Dict[str, Any]) -> Tuple[bool, str]:
        """اعتبارسنجی داده‌های ورودی"""
        required_fields = ['product_name', 'product_code']

        for field in required_fields:
            if field not in data or not data[field]:
                return False, f"فیلد {field} الزامی است"

        # اعتبارسنجی کد محصول
        is_valid, message = Validator.validate_product_code(data['product_code'])
        if not is_valid:
            return False, message

        # اعتبارسنجی نام محصول
        is_valid, message = Validator.validate_product_name(data['product_name'])
        if not is_valid:
            return False, message

        # اعتبارسنجی تعداد
        if 'quantity' in data:
            is_valid, message = Validator.validate_quantity(str(data['quantity']))
            if not is_valid:
                return False, message

        # اعتبارسنجی تاریخ
        if 'entry_date' in data:
            is_valid, message = Validator.validate_date(data['entry_date'])
            if not is_valid:
                return False, message

        return True, ""

    def _validate_garment_output_data(self, data: Dict[str, Any]) -> Tuple[bool, str]:
        """اعتبارسنجی داده‌های خروجی"""
        required_fields = ['product_code', 'quality']

        for field in required_fields:
            if field not in data or not data[field]:
                return False, f"فیلد {field} الزامی است"

        # اعتبارسنجی تعداد
        if 'quantity' in data:
            is_valid, message = Validator.validate_quantity(str(data['quantity']))
            if not is_valid:
                return False, message

        # اعتبارسنجی تاریخ
        if 'output_date' in data:
            is_valid, message = Validator.validate_date(data['output_date'])
            if not is_valid:
                return False, message

        return True, ""

    def _is_product_code_duplicate(self, product_code: str) -> bool:
        """بررسی تکراری بودن کد محصول"""
        results = self.db.execute_query(
            'SELECT id FROM garment_entries WHERE product_code = ?',
            (product_code,)
        )
        return len(results) > 0

    def get_constants(self) -> Dict[str, List[str]]:
        """دریافت لیست‌های ثابت"""
        return {
            'fabric_colors': FABRIC_COLORS,
            'fabric_types': FABRIC_TYPES,
            'sizes': SIZES,
            'qualities': QUALITIES
        }