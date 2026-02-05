# utils/helpers.py
"""
توابع کمکی و ابزارهای عمومی
"""
import os
import shutil
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import tkinter.messagebox as messagebox


def create_backup_dir():
    """ایجاد پوشه پشتیبان‌گیری در صورت عدم وجود"""
    if not os.path.exists('backups'):
        os.makedirs('backups')


def get_today_date() -> str:
    """دریافت تاریخ امروز به فرمت YYYY-MM-DD"""
    return datetime.now().strftime('%Y-%m-%d')


def get_current_time() -> str:
    """دریافت زمان فعلی"""
    return datetime.now().strftime('%H:%M:%S')


def format_date_persian(date_str: str) -> str:
    """تبدیل تاریخ میلادی به شمسی ساده"""
    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        return date_obj.strftime('%Y/%m/%d')
    except:
        return date_str


def format_number(number: int) -> str:
    """قالب‌بندی اعداد با جداکننده هزارگان"""
    return f"{number:,}"


def calculate_age(birth_date: str) -> Optional[int]:
    """محاسبه سن از روی تاریخ تولد"""
    try:
        birth = datetime.strptime(birth_date, '%Y-%m-%d')
        today = datetime.now()
        age = today.year - birth.year

        # بررسی اینکه آیا امسال هنوز تولدش نرسیده
        if (today.month, today.day) < (birth.month, birth.day):
            age -= 1

        return age
    except:
        return None


def calculate_work_duration(hire_date: str) -> Optional[str]:
    """محاسبه مدت کار"""
    try:
        hire = datetime.strptime(hire_date, '%Y-%m-%d')
        today = datetime.now()

        # تفاوت سال و ماه
        years = today.year - hire.year
        months = today.month - hire.month

        if months < 0:
            years -= 1
            months += 12

        if years > 0:
            if months > 0:
                return f"{years} سال و {months} ماه"
            else:
                return f"{years} سال"
        else:
            return f"{months} ماه"
    except:
        return None


def backup_file(file_path: str) -> bool:
    """پشتیبان‌گیری از فایل"""
    try:
        if not os.path.exists(file_path):
            return False

        backup_name = f"{file_path}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        shutil.copy2(file_path, backup_name)
        return True
    except Exception as e:
        print(f"خطا در پشتیبان‌گیری: {e}")
        return False


def restore_file(backup_path: str, original_path: str) -> bool:
    """بازیابی فایل از پشتیبان"""
    try:
        if not os.path.exists(backup_path):
            return False

        shutil.copy2(backup_path, original_path)
        return True
    except Exception as e:
        print(f"خطا در بازیابی: {e}")
        return False


def show_info_message(title: str, message: str):
    """نمایش پیام اطلاعات"""
    messagebox.showinfo(title, message)


def show_warning_message(title: str, message: str):
    """نمایش پیام هشدار"""
    messagebox.showwarning(title, message)


def show_error_message(title: str, message: str):
    """نمایش پیام خطا"""
    messagebox.showerror(title, message)


def ask_yes_no_question(title: str, question: str) -> bool:
    """پرسش بله/خیر"""
    return messagebox.askyesno(title, question)


def filter_list(items: List[Dict[str, Any]],
                search_term: str,
                search_fields: List[str]) -> List[Dict[str, Any]]:
    """
    فیلتر کردن لیست بر اساس عبارت جستجو

    Args:
        items: لیست آیتم‌ها
        search_term: عبارت جستجو
        search_fields: فیلدهایی که باید جستجو شوند

    Returns:
        لیست فیلتر شده
    """
    if not search_term:
        return items

    search_term = search_term.lower()
    filtered_items = []

    for item in items:
        for field in search_fields:
            if field in item and search_term in str(item[field]).lower():
                filtered_items.append(item)
                break

    return filtered_items


def sort_list(items: List[Dict[str, Any]],
              sort_field: str,
              descending: bool = True) -> List[Dict[str, Any]]:
    """
    مرتب‌سازی لیست

    Args:
        items: لیست آیتم‌ها
        sort_field: فیلد مرتب‌سازی
        descending: نزولی/صعودی
    """
    try:
        return sorted(items,
                      key=lambda x: x.get(sort_field, ''),
                      reverse=descending)
    except:
        return items


def validate_file_path(file_path: str, extensions: List[str]) -> bool:
    """اعتبارسنجی مسیر فایل و پسوند"""
    if not file_path:
        return False

    if not os.path.exists(os.path.dirname(file_path)):
        return False

    file_ext = os.path.splitext(file_path)[1].lower()
    return file_ext in extensions


def generate_report_filename(report_type: str) -> str:
    """تولید نام فایل گزارش"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    return f"{report_type}_{timestamp}.csv"


def get_file_size_mb(file_path: str) -> float:
    """دریافت حجم فایل به مگابایت"""
    if os.path.exists(file_path):
        return os.path.getsize(file_path) / (1024 * 1024)
    return 0