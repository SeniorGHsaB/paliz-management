# main.py - نسخه ماژولار
"""
برنامه اصلی مدیریت کارگاه بسته‌بندی پالیز
"""
import tkinter as tk
import ctypes

# تنظیم DPI برای ویندوز
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except:
    pass

# وارد کردن ماژول‌های جدید
from database.manager import DatabaseManager
from utils.logger import AppLogger
from ui.main_window import MainWindow


def main():
    """تابع اصلی برنامه"""
    print("🚀 در حال راه‌اندازی برنامه مدیریت کارگاه بسته‌بندی...")

    # راه‌اندازی لاگر
    logger = AppLogger()
    logger.log_info("برنامه در حال راه‌اندازی است")

    try:
        # ایجاد پنجره اصلی
        root = tk.Tk()
        root.title("مدیریت بسته‌بندی پالیز")

        # تنظیم فول اسکرین
        root.attributes('-fullscreen', True)

        # راه‌اندازی دیتابیس
        db_manager = DatabaseManager()
        logger.log_info("پایگاه داده راه‌اندازی شد")

        # ایجاد پنجره اصلی برنامه
        app = MainWindow(root, db_manager, logger)
        logger.log_info("رابط کاربری ایجاد شد")

        # اجرای برنامه
        logger.log_info("برنامه آماده اجراست")
        root.mainloop()

        # بستن دیتابیس
        db_manager.close()
        logger.log_info("برنامه با موفقیت بسته شد")

    except Exception as e:
        logger.log_error(f"خطا در اجرای برنامه: {str(e)}", exc_info=True)
        print(f"❌ خطا در اجرای برنامه: {e}")
        input("برای خروج Enter بزنید...")


if __name__ == "__main__":
    main()