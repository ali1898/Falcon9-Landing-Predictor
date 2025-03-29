#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
این اسکریپت مدل جنگل تصادفی را برای پیش‌بینی فرود فالکون ۹ آموزش می‌دهد و ذخیره می‌کند.
"""

import pandas as pd
import numpy as np
import os
import pickle
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.ensemble import RandomForestClassifier

def main():
    # مسیر فایل‌ها
    script_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.dirname(script_dir)
    data_path = os.path.join(base_dir, 'data', 'data_falcon9.csv')
    model_dir = os.path.join(base_dir, 'models')
    os.makedirs(model_dir, exist_ok=True)
    
    # بارگذاری داده‌ها
    print("بارگذاری داده‌ها...")
    df = pd.read_csv(data_path)
    
    # ایجاد ستون هدف برای تعیین موفقیت فرود
    print("پردازش داده‌ها...")
    
    def get_landing_outcome(outcome):
        if outcome is np.nan:
            return 0
        elif outcome.startswith('True'):
            return 1
        else:
            return 0
    
    df['Success'] = df['Outcome'].apply(get_landing_outcome)
    
    # تبدیل تاریخ
    df['Date'] = pd.to_datetime(df['Date'])
    df['Year'] = df['Date'].dt.year
    df['Month'] = df['Date'].dt.month
    
    # پر کردن مقادیر گمشده
    df['PayloadMass'].fillna(df['PayloadMass'].median(), inplace=True)
    
    # تبدیل ستون‌های بولین به عددی
    boolean_columns = ['GridFins', 'Reused', 'Legs']
    for col in boolean_columns:
        df[col] = df[col].astype(int)
    
    # انتخاب ویژگی‌ها
    print("آماده‌سازی ویژگی‌ها...")
    features = ['PayloadMass', 'Orbit', 'LaunchSite', 'GridFins', 'Reused', 'Legs', 'Block', 'ReusedCount', 'Year', 'Month']
    X = df[features]
    y = df['Success']
    
    # تقسیم داده‌ها به آموزش و آزمون
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    # تعریف پایپ‌لاین پیش‌پردازش
    print("ایجاد مدل...")
    numerical_features = ['PayloadMass', 'Block', 'ReusedCount', 'Year', 'Month']
    categorical_features = ['Orbit', 'LaunchSite']
    boolean_features = ['GridFins', 'Reused', 'Legs']
    
    numerical_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='median')),
        ('scaler', StandardScaler())
    ])
    
    categorical_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='most_frequent')),
        ('onehot', OneHotEncoder(handle_unknown='ignore'))
    ])
    
    boolean_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='most_frequent'))
    ])
    
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', numerical_transformer, numerical_features),
            ('cat', categorical_transformer, categorical_features),
            ('bool', boolean_transformer, boolean_features)
        ])
    
    # تعریف مدل
    model = Pipeline(steps=[('preprocessor', preprocessor),
                          ('classifier', RandomForestClassifier(n_estimators=100, random_state=42))])
    
    # آموزش مدل
    print("آموزش مدل...")
    model.fit(X_train, y_train)
    
    # ذخیره مدل
    print("ذخیره مدل...")
    model_filename = os.path.join(model_dir, 'falcon9_landing_model.pkl')
    with open(model_filename, 'wb') as file:
        pickle.dump(model, file)
    
    print(f"مدل با موفقیت در مسیر '{model_filename}' ذخیره شد.")
    
    return model_filename

if __name__ == "__main__":
    model_path = main()
    print(f"مسیر فایل مدل: {model_path}")
    print("اکنون می‌توانید اپلیکیشن ویندوزی را با دستور 'python src/falcon9_app.py' اجرا کنید.") 