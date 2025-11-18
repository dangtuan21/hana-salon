#!/usr/bin/env python3
"""
Setup script for Hana Salon Booking System
"""

import os
import subprocess
import sys

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    return True

def install_requirements():
    """Install required packages"""
    print("📦 Installing requirements...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Requirements installed successfully")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install requirements")
        return False

def setup_env_file():
    """Setup environment file"""
    env_file = ".env"
    env_example = ".env.example"
    
    if os.path.exists(env_file):
        print("✅ .env file already exists")
        return True
    
    if os.path.exists(env_example):
        print("📝 Creating .env file from template...")
        with open(env_example, 'r') as src, open(env_file, 'w') as dst:
            dst.write(src.read())
        print("✅ .env file created")
        print("⚠️  Please add your OpenAI API key to .env file")
        return True
    else:
        print("❌ .env.example not found")
        return False

def run_setup():
    """Run the complete setup process"""
    print("🚀 HANA SALON BOOKING SYSTEM SETUP")
    print("=" * 40)
    
    steps = [
        ("Checking Python version", check_python_version),
        ("Installing requirements", install_requirements),
        ("Setting up environment", setup_env_file),
    ]
    
    for step_name, step_func in steps:
        print(f"\n🔄 {step_name}...")
        if not step_func():
            print(f"❌ Setup failed at: {step_name}")
            return False
    
    print("\n" + "=" * 40)
    print("✅ Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Add your OpenAI API key to .env file")
    print("2. Run: python booking_app.py")
    print("3. Or run: python test_booking.py --interactive")
    print("4. View workflow: python visualize_workflow.py")
    print("=" * 40)
    
    return True

if __name__ == "__main__":
    run_setup()
