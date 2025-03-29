#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
اسکریپت نصب پروژه پیش‌بینی فرود فالکون ۹
"""

from setuptools import setup, find_packages

setup(
    name="falcon9-predictor",
    version="1.0.0",
    description="A tool for predicting Falcon 9 landing success",
    author="Falcon9 Predictor Team",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "pandas>=1.0.0",
        "numpy>=1.18.0",
        "scikit-learn>=0.22.0",
        "PyQt6>=6.4.0",
        "matplotlib>=3.1.0",
        "seaborn>=0.11.0",
    ],
    entry_points={
        "console_scripts": [
            "falcon9-predictor=src.falcon9_app:main",
        ],
    },
    python_requires=">=3.6",
) 