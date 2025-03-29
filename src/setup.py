#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
اسکریپت برای ساخت فایل اجرایی (exe) از برنامه پیش‌بینی فرود فالکون ۹
با استفاده از PyInstaller به جای cx_Freeze
"""

import sys
import os
import shutil
import subprocess
import time
from pathlib import Path

# مسیر پایه
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def get_project_root():
    """دریافت مسیر ریشه پروژه"""
    return Path(__file__).parent.parent.absolute()

def clean_build_folders():
    """پاک کردن پوشه‌های ساخت قبلی"""
    root_dir = get_project_root()
    build_dir = root_dir / 'build'
    dist_dir = root_dir / 'dist'
    
    print(f"پاک کردن پوشه‌های ساخت قبلی در {build_dir} و {dist_dir}")
    
    if build_dir.exists():
        shutil.rmtree(build_dir)
        print(f"پوشه {build_dir} پاک شد")
    
    if dist_dir.exists():
        shutil.rmtree(dist_dir)
        print(f"پوشه {dist_dir} پاک شد")

def prepare_resources():
    """آماده‌سازی منابع برای بسته‌بندی"""
    root_dir = get_project_root()
    models_dir = root_dir / 'models'
    assets_dir = root_dir / 'assets'
    temp_dir = root_dir / 'temp'
    
    # ایجاد پوشه موقت برای کپی فایل‌ها
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
    
    temp_dir.mkdir()
    temp_models_dir = temp_dir / 'models'
    temp_models_dir.mkdir()
    temp_assets_dir = temp_dir / 'assets'
    temp_assets_dir.mkdir()
    
    # کپی فایل مدل
    model_file = models_dir / 'falcon9_landing_model.pkl'
    if model_file.exists():
        shutil.copy(model_file, temp_models_dir)
        print(f"فایل مدل از {model_file} به {temp_models_dir} کپی شد")
    else:
        print(f"خطا: فایل مدل در {model_file} پیدا نشد")
        sys.exit(1)
    
    # کپی آیکون و فایل‌های گرافیکی
    if assets_dir.exists():
        for file in assets_dir.glob('*'):
            shutil.copy(file, temp_assets_dir)
            print(f"فایل {file} به {temp_assets_dir} کپی شد")
    
    return temp_dir

def create_spec_file(temp_dir):
    """ایجاد فایل spec برای PyInstaller"""
    root_dir = get_project_root()
    app_path = root_dir / 'src' / 'falcon9_app.py'
    spec_path = root_dir / 'Falcon9Predictor.spec'
    
    spec_content = f"""# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['{app_path.as_posix()}'],
    pathex=[],
    binaries=[],
    datas=[
        ('{temp_dir.as_posix()}/models/*', 'models'),
        ('{temp_dir.as_posix()}/assets/*', 'assets'),
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='Falcon9Predictor',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='{temp_dir.as_posix()}/assets/icon.ico' if os.path.exists('{temp_dir.as_posix()}/assets/icon.ico') else None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Falcon9Predictor',
)
"""
    
    with open(spec_path, 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    print(f"فایل spec در {spec_path} ایجاد شد")
    return spec_path

def run_pyinstaller(spec_path):
    """اجرای PyInstaller برای ساخت فایل اجرایی"""
    print("در حال ساخت فایل اجرایی با PyInstaller...")
    
    try:
        subprocess.run(['pyinstaller', spec_path.as_posix()], check=True)
        print("فایل اجرایی با موفقیت ساخته شد!")
        
        # نمایش مسیر فایل اجرایی
        root_dir = get_project_root()
        exe_path = root_dir / 'dist' / 'Falcon9Predictor' / 'Falcon9Predictor.exe'
        
        if exe_path.exists():
            print(f"فایل اجرایی در {exe_path} ساخته شد")
        else:
            print("فایل اجرایی ساخته شد اما در مسیر مورد انتظار پیدا نشد")
            
    except subprocess.CalledProcessError as e:
        print(f"خطا در ساخت فایل اجرایی: {e}")
        sys.exit(1)
    except FileNotFoundError:
        print("خطا: PyInstaller نصب نشده است. لطفاً با دستور 'pip install pyinstaller' آن را نصب کنید")
        sys.exit(1)

def cleanup(temp_dir):
    """پاک‌سازی فایل‌های موقت"""
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
        print(f"پوشه موقت {temp_dir} پاک شد")

def main():
    """تابع اصلی ساخت فایل اجرایی"""
    print("شروع فرآیند ساخت فایل اجرایی برای پیش‌بینی‌کننده فرود فالکون ۹...")
    
    # پاک کردن پوشه‌های ساخت قبلی
    clean_build_folders()
    
    # آماده‌سازی منابع
    temp_dir = prepare_resources()
    
    # ایجاد فایل spec
    spec_path = create_spec_file(temp_dir)
    
    # اجرای PyInstaller
    run_pyinstaller(spec_path)
    
    # پاک‌سازی فایل‌های موقت
    cleanup(temp_dir)
    
    print("فرآیند ساخت فایل اجرایی با موفقیت به پایان رسید!")

if __name__ == "__main__":
    main() 