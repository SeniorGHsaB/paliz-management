from paliz import Paliz
from tkinter import ttk, messagebox
import tkinter as tk
from config import CONFIG

def main():
    root = tk.Tk()
    root.title("paliz")
    root.attributes(fullscreen=True)
    root.configure(bg=CONFIG["bg_color"])

    # تنظیم ردیف‌ها و ستون‌ها برای stretch خودکار
    root.columnconfigure(0, weight=1)
    root.columnconfigure(1, weight=2)
    root.rowconfigure(0, weight=1)
    root.rowconfigure(1, weight=1)
    root.rowconfigure(2, weight=1)

    menubar = tk.Menu(root)

    # ورود اطلاعات
    data_menu = tk.Menu(menubar, tearoff=0)
    data_menu.add_command(label="افزودن جدید", command=None)
    data_menu.add_command(label="ویرایش موجود", command=None)
    menubar.add_cascade(label="ورود اطلاعات", menu=data_menu)

    # پایگاه داده
    db_menu = tk.Menu(menubar, tearoff=0)
    db_menu.add_command(label="اتصال SQL", command=None)
    db_menu.add_command(label="رفرش DB", command=None)
    menubar.add_cascade(label="پایگاه داده", menu=db_menu)

    # گزارش کلی
    report_menu = tk.Menu(menubar, tearoff=0)
    report_menu.add_command(label="نمایش گزارش", command=None)
    menubar.add_cascade(label="گزارش کلی", menu=report_menu)

    # مدیریت کارکنان
    staff_menu = tk.Menu(menubar, tearoff=0)
    staff_menu.add_command(label="افزودن کارمند", command=None)
    staff_menu.add_command(label="ویرایش کارمند", command=None)
    menubar.add_cascade(label="مدیریت کارکنان", menu=staff_menu)

    # تنظیم منوبار
    root.config(menu=menubar)








    root.mainloop()


main()