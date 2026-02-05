# utils/validators.py
"""
کلاس‌های اعتبارسنجی داده‌های ورودی
"""
import re
from datetime import datetime
from typing import Tuple, Optional


class Validator:
    """اعتبارسنجی عمومی"""

    @staticmethod
    def validate_required(value: str, field_name: str) -> Tuple[bool, str]:
        """اعتبارسنجی فیلد اجباری"""
        if not value or not value.strip():
            return False, f"لطفا {field_name} را وارد کنید"
        return True, ""

    @staticmethod
    def validate_length(value: str, min_length: int, max_length: int,
                        field_name: str) -> Tuple[bool, str]:
        """اعتبارسنجی طول رشته"""
        if not value:
            return False, f"{field_name} نمی‌تواند خالی باشد"

        if len(value.strip()) < min_length:
            return False, f"{field_name} باید حداقل {min_length} کاراکتر باشد"

        if len(value.strip()) > max_length:
            return False, f"{field_name} نباید بیشتر از {max_length} کاراکتر باشد"

        return True, ""

    @staticmethod
    def validate_numeric(value: str, field_name: str) -> Tuple[bool, str]:
        """اعتبارسنجی عددی"""
        try:
            num = float(value)
            if num < 0:
                return False, f"{field_name} نمی‌تواند منفی باشد"
            return True, ""
        except ValueError:
            return False, f"{field_name} باید عدد باشد"

    @staticmethod
    def validate_integer(value: str, field_name: str,
                         min_val: Optional[int] = None,
                         max_val: Optional[int] = None) -> Tuple[bool, str]:
        """اعتبارسنجی عدد صحیح"""
        try:
            num = int(value)

            if min_val is not None and num < min_val:
                return False, f"{field_name} باید حداقل {min_val} باشد"

            if max_val is not None and num > max_val:
                return False, f"{field_name} نباید بیشتر از {max_val} باشد"

            return True, ""
        except ValueError:
            return False, f"{field_name} باید عدد صحیح باشد"


class ProductValidator(Validator):
    """اعتبارسنجی محصولات"""

    @staticmethod
    def validate_product_code(code: str) -> Tuple[bool, str]:
        """اعتبارسنجی کد محصول"""
        # بررسی اجباری بودن
        is_valid, message = Validator.validate_required(code, "کد محصول")
        if not is_valid:
            return False, message

        # بررسی طول
        is_valid, message = Validator.validate_length(code, 2, 50, "کد محصول")
        if not is_valid:
            return False, message

        # بررسی فرمت (اختیاری: فقط حروف و اعداد و خط تیره)
        if not re.match(r'^[a-zA-Z0-9\-_]+$', code):
            return False, "کد محصول فقط می‌تواند شامل حروف، اعداد و خط تیره باشد"

        return True, ""

    @staticmethod
    def validate_product_name(name: str) -> Tuple[bool, str]:
        """اعتبارسنجی نام محصول"""
        return Validator.validate_length(name, 2, 100, "نام محصول")

    @staticmethod
    def validate_quantity(quantity: str) -> Tuple[bool, str]:
        """اعتبارسنجی تعداد"""
        return Validator.validate_integer(quantity, "تعداد", min_val=1, max_val=10000)

    @staticmethod
    def validate_color(color: str) -> Tuple[bool, str]:
        """اعتبارسنجی رنگ"""
        return Validator.validate_length(color, 1, 50, "رنگ")


class DateValidator:
    """اعتبارسنجی تاریخ"""

    @staticmethod
    def validate_date(date_str: str, date_format: str = '%Y-%m-%d') -> Tuple[bool, str]:
        """اعتبارسنجی فرمت تاریخ"""
        try:
            datetime.strptime(date_str, date_format)
            return True, ""
        except ValueError:
            return False, f"فرمت تاریخ نامعتبر است. باید {date_format} باشد"

    @staticmethod
    def validate_date_range(start_date: str, end_date: str,
                            date_format: str = '%Y-%m-%d') -> Tuple[bool, str]:
        """اعتبارسنجی محدوده تاریخ"""
        try:
            start = datetime.strptime(start_date, date_format)
            end = datetime.strptime(end_date, date_format)

            if start > end:
                return False, "تاریخ شروع نمی‌تواند بعد از تاریخ پایان باشد"

            return True, ""
        except ValueError:
            return False, "فرمت تاریخ نامعتبر"


class EmployeeValidator(Validator):
    """اعتبارسنجی کارمندان"""

    @staticmethod
    def validate_name(name: str, field_name: str) -> Tuple[bool, str]:
        """اعتبارسنجی نام و نام خانوادگی"""
        is_valid, message = Validator.validate_length(name, 2, 50, field_name)
        if not is_valid:
            return False, message

        # فقط حروف فارسی و انگلیسی
        if not re.match(r'^[\u0600-\u06FFa-zA-Z\s]+$', name):
            return False, f"{field_name} فقط می‌تواند شامل حروف باشد"

        return True, ""

    @staticmethod
    def validate_phone(phone: str) -> Tuple[bool, str]:
        """اعتبارسنجی شماره تلفن"""
        is_valid, message = Validator.validate_required(phone, "شماره تلفن")
        if not is_valid:
            return False, message

        # فرمت شماره تلفن ایرانی
        if not re.match(r'^09[0-9]{9}$', phone):
            return False, "شماره تلفن باید با 09 شروع شده و 11 رقمی باشد"

        return True, ""

    @staticmethod
    def validate_national_id(national_id: str) -> Tuple[bool, str]:
        """اعتبارسنجی کد ملی"""
        if not national_id:
            return True, ""  # اختیاری

        # بررسی طول
        if len(national_id) != 10:
            return False, "کد ملی باید 10 رقمی باشد"

        # بررسی فقط اعداد
        if not national_id.isdigit():
            return False, "کد ملی فقط باید شامل اعداد باشد"

        # الگوریتم کنترل کد ملی
        control = int(national_id[9])
        sum = 0

        for i in range(9):
            sum += int(national_id[i]) * (10 - i)

        remainder = sum % 11
        if remainder < 2:
            correct_control = remainder
        else:
            correct_control = 11 - remainder

        if correct_control == control:
            return True, ""
        else:
            return False, "کد ملی نامعتبر است"


class ValidationResult:
    """نتیجه اعتبارسنجی"""

    def __init__(self):
        self.is_valid = True
        self.errors = []

    def add_error(self, field: str, message: str):
        """افزودن خطا"""
        self.is_valid = False
        self.errors.append({"field": field, "message": message})

    def get_error_messages(self) -> str:
        """دریافت پیام‌های خطا"""
        if not self.errors:
            return ""

        messages = []
        for error in self.errors:
            messages.append(f"• {error['field']}: {error['message']}")

        return "\n".join(messages)