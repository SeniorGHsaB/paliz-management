# setup.py
from setuptools import setup, find_packages

setup(
    name="garment-management",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        'tkcalendar==1.6.1',
    ],
    author="Your Name",
    description="سیستم مدیریت کارگاه بسته‌بندی پوشاک",
)