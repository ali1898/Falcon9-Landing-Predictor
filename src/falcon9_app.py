#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import pickle
import pandas as pd
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                            QLabel, QComboBox, QDoubleSpinBox, QSpinBox, QCheckBox,
                            QPushButton, QGroupBox, QFormLayout, QProgressBar, QMessageBox)
from PySide6.QtCore import Qt, QTimer, QObject, Signal
from PySide6.QtGui import QFont, QIcon, QPixmap


class ResourceManager:
    """مدیریت منابع و یافتن مسیر فایل‌ها"""
    
    @staticmethod
    def get_resource_path(relative_path):
        """تعیین مسیر صحیح فایل‌های منابع در حالت اجرایی و توسعه"""
        try:
            # مسیرهای ممکن برای منابع
            base_paths = [
                # PyInstaller ایجاد یک _MEIPASS مسیر موقت می‌کند
                getattr(sys, '_MEIPASS', None),
                # مسیر کنار فایل اجرایی
                os.path.dirname(sys.executable),
                # مسیر فعلی
                os.getcwd(),
                # مسیر پوشه اصلی پروژه
                os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            ]
            
            # حذف مسیرهای خالی یا None
            base_paths = [p for p in base_paths if p]
            
            # بررسی تمام مسیرهای ممکن
            for base_path in base_paths:
                full_path = os.path.join(base_path, relative_path)
                if os.path.exists(full_path):
                    print(f"فایل پیدا شد: {full_path}")
                    return full_path
                    
            # اگر با مسیر نسبی پیدا نشد، یک بار دیگر با مسیر مطلق بررسی کنیم
            if os.path.exists(relative_path):
                print(f"فایل با مسیر مطلق پیدا شد: {relative_path}")
                return relative_path
                
            # اگر هیچ فایلی پیدا نشد، مسیر پیش‌فرض را برگردانیم
            default_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), relative_path)
            print(f"فایل پیدا نشد، مسیر پیش‌فرض: {default_path}")
            return default_path
            
        except Exception as e:
            print(f"خطا در تعیین مسیر منابع: {e}")
            return os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), relative_path)


class PredictionModel:
    """کلاس مدیریت مدل پیش‌بینی"""
    
    def __init__(self):
        self.model = None
        self.is_loaded = False
        self._load_model()
    
    def _load_model(self):
        """بارگذاری مدل از فایل"""
        model_path = ResourceManager.get_resource_path(os.path.join('models', 'falcon9_landing_model.pkl'))
        print(f"تلاش برای بارگذاری مدل از مسیر: {model_path}")
        
        try:
            if os.path.exists(model_path):
                with open(model_path, 'rb') as f:
                    self.model = pickle.load(f)
                self.is_loaded = True
                print(f"مدل با موفقیت از {model_path} بارگذاری شد.")
            else:
                # تلاش برای یافتن فایل مدل در مسیرهای دیگر
                alternative_paths = [
                    os.path.join(os.getcwd(), 'models', 'falcon9_landing_model.pkl'),
                    os.path.join(os.path.dirname(sys.executable), 'models', 'falcon9_landing_model.pkl'),
                    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'models', 'falcon9_landing_model.pkl')
                ]
                
                for alt_path in alternative_paths:
                    print(f"جستجوی مدل در: {alt_path}")
                    if os.path.exists(alt_path):
                        with open(alt_path, 'rb') as f:
                            self.model = pickle.load(f)
                        self.is_loaded = True
                        print(f"مدل با موفقیت از {alt_path} بارگذاری شد.")
                        break
                
                if not self.is_loaded:
                    print(f"فایل مدل در هیچ مسیری یافت نشد.")
        except Exception as e:
            self.is_loaded = False
            print(f"خطا در بارگذاری مدل: {e}")
    
    def predict(self, input_data):
        """پیش‌بینی با استفاده از مدل"""
        if not self.is_loaded:
            raise ValueError("مدل بارگذاری نشده است")
        
        prediction = self.model.predict(input_data)
        probability = self.model.predict_proba(input_data)
        
        return {
            'prediction': prediction[0],
            'success': prediction[0] == 1,
            'probability': probability[0][1] * 100  # احتمال موفقیت به درصد
        }


class InputForm(QGroupBox):
    """فرم ورودی پارامترها"""
    
    def __init__(self, parent=None):
        super().__init__("مشخصات پرتاب", parent)
        self._init_ui()
    
    def _init_ui(self):
        """تنظیم اجزای فرم ورودی"""
        form_layout = QFormLayout()
        self.setLayout(form_layout)
        
        # وزن محموله
        self.payload_input = QDoubleSpinBox()
        self.payload_input.setRange(300, 16000)
        self.payload_input.setValue(5000)
        self.payload_input.setSuffix(" کیلوگرم")
        self.payload_input.setDecimals(0)
        form_layout.addRow("وزن محموله:", self.payload_input)
        
        # نوع مدار
        self.orbit_input = QComboBox()
        self.orbit_input.addItems(["LEO", "GTO", "ISS", "VLEO", "SSO", "MEO", "HEO", "PO"])
        form_layout.addRow("نوع مدار:", self.orbit_input)
        
        # محل پرتاب
        self.launch_site_input = QComboBox()
        self.launch_site_input.addItems(["CCAFS SLC 40", "VAFB SLC 4E", "KSC LC 39A", "CCAFS LC 40"])
        form_layout.addRow("محل پرتاب:", self.launch_site_input)
        
        # GridFins
        self.grid_fins_input = QCheckBox("دارد")
        self.grid_fins_input.setChecked(True)
        form_layout.addRow("Grid Fins:", self.grid_fins_input)
        
        # استفاده مجدد
        self.reused_input = QCheckBox("بله")
        self.reused_input.setChecked(True)
        form_layout.addRow("استفاده مجدد از بوستر:", self.reused_input)
        
        # پایه‌های فرود
        self.legs_input = QCheckBox("دارد")
        self.legs_input.setChecked(True)
        form_layout.addRow("پایه‌های فرود:", self.legs_input)
        
        # نسخه بلوک
        self.block_input = QComboBox()
        self.block_input.addItems(["1.0", "2.0", "3.0", "4.0", "5.0"])
        self.block_input.setCurrentIndex(4)  # Block 5.0
        form_layout.addRow("نسخه بلوک:", self.block_input)
        
        # تعداد استفاده‌های قبلی
        self.reused_count_input = QSpinBox()
        self.reused_count_input.setRange(0, 15)
        self.reused_count_input.setValue(2)
        form_layout.addRow("تعداد استفاده‌های قبلی:", self.reused_count_input)
        
        # سال پرتاب
        self.year_input = QSpinBox()
        self.year_input.setRange(2010, 2030)
        self.year_input.setValue(2023)
        form_layout.addRow("سال پرتاب:", self.year_input)
        
        # ماه پرتاب
        self.month_input = QSpinBox()
        self.month_input.setRange(1, 12)
        self.month_input.setValue(6)
        form_layout.addRow("ماه پرتاب:", self.month_input)
    
    def get_input_data(self):
        """تهیه دیتافریم از ورودی‌های کاربر"""
        return pd.DataFrame({
            'PayloadMass': [self.payload_input.value()],
            'Orbit': [self.orbit_input.currentText()],
            'LaunchSite': [self.launch_site_input.currentText()],
            'GridFins': [1 if self.grid_fins_input.isChecked() else 0],
            'Reused': [1 if self.reused_input.isChecked() else 0],
            'Legs': [1 if self.legs_input.isChecked() else 0],
            'Block': [float(self.block_input.currentText())],
            'ReusedCount': [self.reused_count_input.value()],
            'Year': [self.year_input.value()],
            'Month': [self.month_input.value()]
        })


class ResultsDisplay(QGroupBox):
    """نمایش نتایج پیش‌بینی"""
    
    def __init__(self, parent=None):
        super().__init__("نتیجه پیش‌بینی", parent)
        self._init_ui()
    
    def _init_ui(self):
        """تنظیم اجزای نمایش نتیجه"""
        results_layout = QVBoxLayout()
        self.setLayout(results_layout)
        
        # نتیجه متنی
        self.result_label = QLabel("لطفاً روی دکمه پیش‌بینی کلیک کنید")
        self.result_label.setAlignment(Qt.AlignCenter)
        results_layout.addWidget(self.result_label)
        
        # نوار درصد احتمال
        probability_layout = QHBoxLayout()
        probability_layout.addWidget(QLabel("احتمال موفقیت:"))
        
        self.probability_bar = QProgressBar()
        self.probability_bar.setRange(0, 100)
        self.probability_bar.setValue(0)
        self.probability_bar.setTextVisible(True)
        self.probability_bar.setFormat("%p%")
        probability_layout.addWidget(self.probability_bar)
        
        results_layout.addLayout(probability_layout)
    
    def display_result(self, result):
        """نمایش نتیجه پیش‌بینی"""
        success_text = "موفقیت‌آمیز" if result['success'] else "ناموفق"
        probability = result['probability']
        
        self._animate_result(probability, success_text)
    
    def _animate_result(self, probability, result_text):
        """نمایش انیمیشن برای نتیجه پیش‌بینی"""
        self.probability_bar.setValue(0)
        
        # تنظیم رنگ نوار بر اساس احتمال
        if probability > 80:
            self.probability_bar.setStyleSheet("QProgressBar::chunk { background-color: #4CAF50; }")  # سبز
        elif probability > 50:
            self.probability_bar.setStyleSheet("QProgressBar::chunk { background-color: #FFC107; }")  # زرد
        else:
            self.probability_bar.setStyleSheet("QProgressBar::chunk { background-color: #F44336; }")  # قرمز
        
        # انیمیشن پر شدن نوار پیشرفت
        self.result_label.setText(f"نتیجه پیش‌بینی: فرود <b>{result_text}</b> با احتمال {probability:.1f}%")
        
        # افزایش تدریجی درصد احتمال در نوار پیشرفت
        def update_bar(value):
            if value <= probability:
                self.probability_bar.setValue(value)
                QTimer.singleShot(10, lambda: update_bar(value + 1))
        
        update_bar(0)


class Falcon9PredictorApp(QMainWindow):
    """اپلیکیشن اصلی پیش‌بینی فرود فالکون ۹"""
    
    def __init__(self):
        super().__init__()
        
        # اجزای اصلی برنامه
        self.model = PredictionModel()
        self._init_ui()
        
        # بررسی وضعیت بارگذاری مدل
        if not self.model.is_loaded:
            QMessageBox.warning(self, "خطا در بارگذاری مدل", 
                             "مدل با موفقیت بارگذاری نشد. لطفاً مطمئن شوید که فایل مدل در مسیر صحیح وجود دارد.")
    
    def _init_ui(self):
        """راه‌اندازی و پیکربندی رابط کاربری"""
        # تنظیمات پنجره اصلی
        self.setWindowTitle("پیش‌بینی فرود فالکون ۹")
        self.setMinimumSize(800, 600)
        
        # تنظیم آیکون برنامه (اگر فایل موجود باشد)
        icon_path = ResourceManager.get_resource_path(os.path.join('assets', 'icon.png'))
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        # ویجت مرکزی
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        main_layout.setAlignment(Qt.AlignTop)
        self.setCentralWidget(central_widget)
        
        # عنوان برنامه
        title_label = QLabel("سیستم پیش‌بینی موفقیت فرود فالکون ۹")
        title_font = QFont("Arial", 16, QFont.Weight.Bold)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        # توضیح برنامه
        desc_label = QLabel("با استفاده از این برنامه می‌توانید احتمال موفقیت فرود بوستر فالکون ۹ را پیش‌بینی کنید.")
        desc_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(desc_label)
        
        # فرم ورودی
        self.input_form = InputForm()
        main_layout.addWidget(self.input_form)
        
        # دکمه پیش‌بینی
        self.predict_button = QPushButton("پیش‌بینی موفقیت فرود")
        self.predict_button.setMinimumHeight(40)
        self.predict_button.clicked.connect(self.predict_landing)
        main_layout.addWidget(self.predict_button)
        
        # نمایش نتایج
        self.results_display = ResultsDisplay()
        main_layout.addWidget(self.results_display)
    
    def predict_landing(self):
        """پیش‌بینی موفقیت فرود بر اساس ورودی‌های کاربر"""
        if not self.model.is_loaded:
            QMessageBox.warning(self, "خطا", "مدل بارگذاری نشده است")
            return
        
        try:
            # دریافت داده‌های ورودی
            input_data = self.input_form.get_input_data()
            
            # پیش‌بینی با استفاده از مدل
            result = self.model.predict(input_data)
            
            # نمایش نتایج
            self.results_display.display_result(result)
            
        except Exception as e:
            QMessageBox.critical(self, "خطا در پیش‌بینی", f"خطایی رخ داد: {str(e)}")


def main():
    """تابع اصلی برنامه"""
    app = QApplication(sys.argv)
    window = Falcon9PredictorApp()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main() 