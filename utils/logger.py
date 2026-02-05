# utils/logger.py
"""
سیستم لاگ‌گیری برنامه
"""
import logging
import os
from datetime import datetime


def setup_logger(log_name: str = 'garment_manager',
                 log_level: int = logging.DEBUG) -> logging.Logger:
    """
    راه‌اندازی لاگر

    Args:
        log_name: نام لاگر
        log_level: سطح لاگ

    Returns:
        شیء لاگر
    """
    # ایجاد پوشه لاگ در صورت عدم وجود
    if not os.path.exists('logs'):
        os.makedirs('logs')

    # تنظیم فرمت لاگ
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    date_format = '%Y-%m-%d %H:%M:%S'

    # تنظیم لاگر
    logger = logging.getLogger(log_name)
    logger.setLevel(log_level)

    # جلوگیری از اضافه شدن هندلرهای تکراری
    if logger.handlers:
        return logger

    # هندلر فایل
    log_file = f'logs/{log_name}_{datetime.now().strftime("%Y%m%d")}.log'
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(log_level)
    file_formatter = logging.Formatter(log_format, date_format)
    file_handler.setFormatter(file_formatter)

    # هندلر کنسول
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.ERROR)  # فقط خطاها در کنسول
    console_formatter = logging.Formatter('%(levelname)s: %(message)s')
    console_handler.setFormatter(console_formatter)

    # اضافه کردن هندلرها
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


class AppLogger:
    """لاگر اصلی برنامه"""

    def __init__(self):
        self.logger = setup_logger('garment_manager')

    def log_info(self, message: str):
        """لاگ اطلاعات"""
        self.logger.info(message)

    def log_warning(self, message: str):
        """لاگ هشدار"""
        self.logger.warning(message)

    def log_error(self, message: str, exc_info: bool = False):
        """لاگ خطا"""
        self.logger.error(message, exc_info=exc_info)

    def log_debug(self, message: str):
        """لاگ دیباگ"""
        self.logger.debug(message)

    def log_critical(self, message: str):
        """لاگ بحرانی"""
        self.logger.critical(message)