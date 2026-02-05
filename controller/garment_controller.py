# controllers/garment_controller.py
from models.garment_model import GarmentModel
from views.garment_entry_view import GarmentEntryView
from utils.validators import Validator


class GarmentController:
    def __init__(self, model: GarmentModel, view: GarmentEntryView):
        self.model = model
        self.view = view
        self.bind_events()

    def bind_events(self):
        """اتصال رویدادها"""
        # اتصال دکمه‌ها به متدها
        pass

    def on_save_entry(self):
        """رویداد ذخیره ورودی"""
        data = self.view.get_form_data()

        # اعتبارسنجی
        is_valid, message = Validator.validate_product_code(data['product_code'])
        if not is_valid:
            self.show_error(message)
            return

        # ذخیره در مدل
        success, message = self.model.add_entry(data)
        if success:
            self.show_success(message)
            self.view.clear_form()
            self.refresh_table()
        else:
            self.show_error(message)

    def show_error(self, message: str):
        """نمایش خطا"""
        pass

    def show_success(self, message: str):
        """نمایش موفقیت"""
        pass