# test_models.py
"""
تست مدل‌های ایجاد شده
"""
import sys
import os

# اضافه کردن مسیر پروژه به sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.manager import DatabaseManager
from models.garment_model import GarmentModel
from models.employee_model import EmployeeModel
from models.report_model import ReportModel
from utils.logger import setup_logger


def test_models():
    """تست عملکرد مدل‌ها"""
    print("🔧 در حال تست مدل‌ها...")

    # راه‌اندازی لاگر
    logger = setup_logger()

    try:
        # راه‌اندازی دیتابیس
        db = DatabaseManager()
        print("✅ دیتابیس راه‌اندازی شد")

        # ایجاد مدل‌ها
        garment_model = GarmentModel(db)
        employee_model = EmployeeModel(db)
        report_model = ReportModel(db)

        # تنظیم لاگر برای مدل‌ها
        garment_model.set_logger(logger)
        employee_model.set_logger(logger)
        report_model.set_logger(logger)

        print("✅ مدل‌ها ایجاد شدند")

        # تست ۱: دریافت لیست‌های ثابت
        print("\n📋 تست ۱: دریافت لیست‌های ثابت")
        constants = garment_model.get_constants()
        print(f"   تعداد رنگ‌ها: {len(constants['fabric_colors'])}")
        print(f"   تعداد سایزها: {len(constants['sizes'])}")

        # تست ۲: آمار موجودی
        print("\n📊 تست ۲: آمار موجودی")
        stats = garment_model.get_inventory_stats()
        print(f"   کل موجودی: {stats['total_inventory']}")

        # تست ۳: آمار روزانه
        print("\n📅 تست ۳: آمار روزانه")
        daily_stats = garment_model.get_daily_stats()
        print(f"   تاریخ: {daily_stats['date']}")
        print(f"   تعداد ورودی‌ها: {daily_stats['entries_count']}")

        # تست ۴: گزارش موجودی
        print("\n📈 تست ۴: گزارش موجودی")
        inventory_report = report_model.generate_inventory_report()
        if 'error' not in inventory_report:
            print(f"   ✅ گزارش موجودی تولید شد")
            print(f"   کل موجودی: {inventory_report.get('total_inventory', 0)}")
        else:
            print(f"   ❌ خطا: {inventory_report.get('error')}")

        print("\n🎉 همه تست‌ها با موفقیت انجام شد!")

        # بستن دیتابیس
        db.close()

    except Exception as e:
        print(f"❌ خطا در تست: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_models()
    input("\nPress Enter to exit...")