# models/report_model.py
"""
مدل تولید گزارشات
"""
from typing import List, Dict, Any, Tuple
from datetime import datetime, timedelta
from database.manager import DatabaseManager


class ReportModel:
    """مدل گزارشات"""

    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        self.logger = None

    def set_logger(self, logger):
        """تنظیم لاگر"""
        self.logger = logger

    def generate_daily_report(self, target_date: str = None) -> Dict[str, Any]:
        """
        تولید گزارش روزانه

        Args:
            target_date: تاریخ مورد نظر (اگر None باشد امروز)

        Returns:
            گزارش روزانه
        """
        try:
            if target_date is None:
                target_date = datetime.now().strftime('%Y-%m-%d')

            # آمار روزانه
            query = '''
                    SELECT (SELECT COUNT(*) FROM garment_entries WHERE entry_date = ?)       as entry_count, \
                           (SELECT SUM(quantity) FROM garment_entries WHERE entry_date = ?)  as entry_quantity, \
                           (SELECT COUNT(*) FROM garment_outputs WHERE output_date = ?)      as output_count, \
                           (SELECT SUM(quantity) FROM garment_outputs WHERE output_date = ?) as output_quantity \
                    '''

            results = self.db.execute_query(query, (target_date, target_date, target_date, target_date))

            # جزئیات ورودی‌های امروز
            query_entries = '''
                            SELECT product_code, product_name, color, size, tailor_name, quantity
                            FROM garment_entries
                            WHERE entry_date = ?
                            ORDER BY created_at DESC \
                            '''
            entries_details = self.db.execute_query(query_entries, (target_date,))

            # جزئیات خروجی‌های امروز
            query_outputs = '''
                            SELECT product_code, quality, destination, quantity, package_code
                            FROM garment_outputs
                            WHERE output_date = ?
                            ORDER BY created_at DESC \
                            '''
            outputs_details = self.db.execute_query(query_outputs, (target_date,))

            report = {
                'date': target_date,
                'summary': results[0] if results else {},
                'entries_details': entries_details,
                'outputs_details': outputs_details,
                'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }

            if self.logger:
                self.logger.info(f"گزارش روزانه {target_date} تولید شد")

            return report

        except Exception as e:
            error_msg = f"خطا در تولید گزارش روزانه: {str(e)}"
            if self.logger:
                self.logger.error(error_msg)
            return {'error': error_msg}

    def generate_monthly_report(self, year: int = None, month: int = None) -> Dict[str, Any]:
        """
        تولید گزارش ماهانه

        Args:
            year: سال
            month: ماه

        Returns:
            گزارش ماهانه
        """
        try:
            if year is None:
                year = datetime.now().year
            if month is None:
                month = datetime.now().month

            month_str = f"{year:04d}-{month:02d}"

            # آمار ماهانه
            query = '''
                    SELECT (SELECT COUNT(*) \
                            FROM garment_entries \
                            WHERE strftime('%Y-%m', entry_date) = ?)                                            as entry_count, \
                           (SELECT SUM(quantity) \
                            FROM garment_entries \
                            WHERE strftime('%Y-%m', entry_date) = ?)                                            as entry_quantity, \
                           (SELECT COUNT(*) \
                            FROM garment_outputs \
                            WHERE strftime('%Y-%m', output_date) = ?)                                           as output_count, \
                           (SELECT SUM(quantity) \
                            FROM garment_outputs \
                            WHERE strftime('%Y-%m', output_date) = ?)                                           as output_quantity \
                    '''

            results = self.db.execute_query(query, (month_str, month_str, month_str, month_str))

            # محبوب‌ترین رنگ‌های ماه
            query_colors = '''
                           SELECT color, SUM(quantity) as total
                           FROM garment_entries
                           WHERE strftime('%Y-%m', entry_date) = ?
                           GROUP BY color
                           ORDER BY total DESC LIMIT 10 \
                           '''
            top_colors = self.db.execute_query(query_colors, (month_str,))

            # محبوب‌ترین سایزهای ماه
            query_sizes = '''
                          SELECT size, SUM (quantity) as total
                          FROM garment_entries
                          WHERE strftime('%Y-%m', entry_date) = ?
                          GROUP BY size
                          ORDER BY total DESC
                              LIMIT 10 \
                          '''
            top_sizes = self.db.execute_query(query_sizes, (month_str,))

            # کارمندان فعال ماه
            query_tailors = '''
                            SELECT tailor_name, SUM(quantity) as total
                            FROM garment_entries
                            WHERE strftime('%Y-%m', entry_date) = ?
                            GROUP BY tailor_name
                            ORDER BY total DESC LIMIT 10 \
                            '''
            top_tailors = self.db.execute_query(query_tailors, (month_str,))

            report = {
                'period': month_str,
                'summary': results[0] if results else {},
                'top_colors': top_colors,
                'top_sizes': top_sizes,
                'top_tailors': top_tailors,
                'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }

            if self.logger:
                self.logger.info(f"گزارش ماهانه {month_str} تولید شد")

            return report

        except Exception as e:
            error_msg = f"خطا در تولید گزارش ماهانه: {str(e)}"
            if self.logger:
                self.logger.error(error_msg)
            return {'error': error_msg}

    def generate_inventory_report(self) -> Dict[str, Any]:
        """
        تولید گزارش موجودی

        Returns:
            گزارش موجودی
        """
        try:
            # آمار کلی موجودی
            query_total = 'SELECT SUM(quantity) as total FROM garment_entries'
            total_result = self.db.execute_query(query_total)

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

            # موجودی بر اساس نوع پارچه
            query_fabric = '''
                           SELECT fabric_type, SUM(quantity) as total
                           FROM garment_entries
                           GROUP BY fabric_type
                           ORDER BY total DESC \
                           '''
            fabric_stats = self.db.execute_query(query_fabric)

            # محصولات با موجودی کم (کمتر از 10)
            query_low_stock = '''
                              SELECT product_code, product_name, color, size, quantity
                              FROM garment_entries
                              WHERE quantity < 10
                              ORDER BY quantity
                                  LIMIT 20 \
                              '''
            low_stock = self.db.execute_query(query_low_stock)

            report = {
                'total_inventory': total_result[0]['total'] if total_result and total_result[0]['total'] else 0,
                'color_stats': color_stats,
                'size_stats': size_stats,
                'fabric_stats': fabric_stats,
                'low_stock': low_stock,
                'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }

            if self.logger:
                self.logger.info("گزارش موجودی تولید شد")

            return report

        except Exception as e:
            error_msg = f"خطا در تولید گزارش موجودی: {str(e)}"
            if self.logger:
                self.logger.error(error_msg)
            return {'error': error_msg}

    def generate_quality_report(self) -> Dict[str, Any]:
        """
        تولید گزارش کیفیت

        Returns:
            گزارش کیفیت
        """
        try:
            # آمار کیفیت
            query = '''
                    SELECT quality, COUNT(*) as count, SUM(quantity) as total
                    FROM garment_outputs
                    GROUP BY quality
                    ORDER BY quality \
                    '''
            quality_stats = self.db.execute_query(query)

            # کیفیت بر اساس ماه
            query_monthly = '''
                            SELECT strftime('%Y-%m', output_date) as month,
                    quality,
                    SUM(quantity) as total
                            FROM garment_outputs
                            GROUP BY month, quality
                            ORDER BY month DESC, quality
                                LIMIT 50 \
                            '''
            monthly_stats = self.db.execute_query(query_monthly)

            report = {
                'quality_stats': quality_stats,
                'monthly_stats': monthly_stats,
                'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }

            if self.logger:
                self.logger.info("گزارش کیفیت تولید شد")

            return report

        except Exception as e:
            error_msg = f"خطا در تولید گزارش کیفیت: {str(e)}"
            if self.logger:
                self.logger.error(error_msg)
            return {'error': error_msg}

    def generate_employee_report(self) -> Dict[str, Any]:
        """
        تولید گزارش کارمندان

        Returns:
            گزارش کارمندان
        """
        try:
            # آمار کلی کارمندان
            query_total = '''
                          SELECT COUNT(*)                                            as total, \
                                 SUM(CASE WHEN status = 'فعال' THEN 1 ELSE 0 END)    as active, \
                                 SUM(CASE WHEN status = 'غیرفعال' THEN 1 ELSE 0 END) as inactive
                          FROM employees \
                          '''
            total_stats = self.db.execute_query(query_total)

            # توزیع بر اساس سمت
            query_position = '''
                             SELECT position, COUNT(*) as count
                             FROM employees
                             WHERE position IS NOT NULL AND position != ""
                             GROUP BY position
                             ORDER BY count DESC \
                             '''
            position_stats = self.db.execute_query(query_position)

            # توزیع بر اساس تاریخ استخدام
            query_hire = '''
                         SELECT strftime('%Y', hire_date) as hire_year, \
                                COUNT(*) as count
                         FROM employees
                         WHERE hire_date IS NOT NULL
                         GROUP BY hire_year
                         ORDER BY hire_year DESC \
                         '''
            hire_stats = self.db.execute_query(query_hire)

            # جدیدترین کارمندان
            query_recent = '''
                           SELECT first_name, last_name, position, hire_date, status
                           FROM employees
                           ORDER BY hire_date DESC LIMIT 10 \
                           '''
            recent_employees = self.db.execute_query(query_recent)

            report = {
                'total_stats': total_stats[0] if total_stats else {},
                'position_stats': position_stats,
                'hire_stats': hire_stats,
                'recent_employees': recent_employees,
                'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }

            if self.logger:
                self.logger.info("گزارش کارمندان تولید شد")

            return report

        except Exception as e:
            error_msg = f"خطا در تولید گزارش کارمندان: {str(e)}"
            if self.logger:
                self.logger.error(error_msg)
            return {'error': error_msg}

    def export_report_to_csv(self, report_data: Dict[str, Any], report_type: str) -> Tuple[bool, str]:
        """
        خروجی CSV از گزارش

        Args:
            report_data: داده‌های گزارش
            report_type: نوع گزارش

        Returns:
            (موفقیت, مسیر فایل)
        """
        try:
            import csv
            from datetime import datetime

            # ایجاد پوشه exports در صورت عدم وجود
            import os
            if not os.path.exists('exports'):
                os.makedirs('exports')

            # نام فایل
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"exports/{report_type}_{timestamp}.csv"

            with open(filename, 'w', newline='', encoding='utf-8-sig') as file:
                writer = csv.writer(file)

                # نوشتن هدر
                writer.writerow([f"گزارش {report_type}"])
                writer.writerow([f"تاریخ تولید: {report_data.get('generated_at', '')}"])
                writer.writerow([])

                # نوشتن داده‌ها بر اساس نوع گزارش
                if report_type == 'inventory':
                    writer.writerow(["گزارش موجودی انبار"])
                    writer.writerow([])
                    writer.writerow(["کل موجودی", report_data.get('total_inventory', 0)])
                    writer.writerow([])

                    if 'color_stats' in report_data:
                        writer.writerow(["موجودی بر اساس رنگ"])
                        writer.writerow(["رنگ", "تعداد"])
                        for item in report_data['color_stats']:
                            writer.writerow([item.get('color', ''), item.get('total', 0)])
                        writer.writerow([])

                elif report_type == 'daily':
                    writer.writerow([f"گزارش روزانه {report_data.get('date', '')}"])
                    writer.writerow([])

                    if 'summary' in report_data:
                        summary = report_data['summary']
                        writer.writerow(["آمار روزانه"])
                        writer.writerow(["ورودی‌ها", summary.get('entry_count', 0)])
                        writer.writerow(["تعداد محصولات ورودی", summary.get('entry_quantity', 0)])
                        writer.writerow(["خروجی‌ها", summary.get('output_count', 0)])
                        writer.writerow(["تعداد محصولات خروجی", summary.get('output_quantity', 0)])
                        writer.writerow([])

                # ... (بقیه گزارشات)

            if self.logger:
                self.logger.info(f"گزارش {report_type} به CSV صادر شد: {filename}")

            return True, filename

        except Exception as e:
            error_msg = f"خطا در خروجی CSV: {str(e)}"
            if self.logger:
                self.logger.error(error_msg)
            return False, error_msg