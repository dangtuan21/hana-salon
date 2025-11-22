#!/usr/bin/env python3
"""
Setup script for voice support in Hana Salon Booking System
Installs dependencies and verifies configuration
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command: str, description: str) -> bool:
    """Run a shell command and return success status"""
    print(f"📦 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python 3.8+ required, found {version.major}.{version.minor}")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible")
    return True

def check_openai_key():
    """Check if OpenAI API key is configured"""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("⚠️  OPENAI_API_KEY not found in environment")
        print("💡 Add it to your .env file: OPENAI_API_KEY=your_key_here")
        return False
    print("✅ OPENAI_API_KEY is configured")
    return True

def install_dependencies():
    """Install required dependencies"""
    commands = [
        ("pip install --upgrade pip", "Upgrading pip"),
        ("pip install -r requirements.txt", "Installing requirements"),
        ("pip install numpy", "Installing numpy for audio processing")
    ]
    
    for command, description in commands:
        if not run_command(command, description):
            return False
    return True

def verify_imports():
    """Verify that all required modules can be imported"""
    modules = [
        ("openai", "OpenAI client"),
        ("fastapi", "FastAPI framework"),
        ("gradio", "Gradio UI"),
        ("numpy", "NumPy for audio processing"),
        ("aiofiles", "Async file handling"),
    ]
    
    print("\n🔍 Verifying module imports...")
    all_good = True
    
    for module, description in modules:
        try:
            __import__(module)
            print(f"✅ {description}")
        except ImportError as e:
            print(f"❌ {description}: {e}")
            all_good = False
    
    return all_good

def create_sample_env():
    """Create a sample .env file if it doesn't exist"""
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if not env_file.exists() and env_example.exists():
        print("📝 Creating .env file from .env.example...")
        with open(env_example, 'r') as src, open(env_file, 'w') as dst:
            dst.write(src.read())
        print("✅ .env file created. Please add your OPENAI_API_KEY")
        return True
    elif not env_file.exists():
        print("📝 Creating basic .env file...")
        with open(env_file, 'w') as f:
            f.write("# Hana AI Voice Support Configuration\n")
            f.write("OPENAI_API_KEY=your_openai_api_key_here\n")
            f.write("MONGODB_URI=your_mongodb_connection_string\n")
            f.write("DATABASE_NAME=hana_salon\n")
            f.write("BACKEND_URL=http://localhost:3060\n")
        print("✅ Basic .env file created. Please add your API keys")
        return True
    else:
        print("✅ .env file already exists")
        return True

def main():
    """Main setup function"""
    print("🎤 Setting up Voice Support for Hana Salon Booking System")
    print("=" * 60)
    
    # Check Python version
    print("\n1. Checking Python version...")
    if not check_python_version():
        return False
    
    # Create .env file if needed
    print("\n2. Setting up environment configuration...")
    create_sample_env()
    
    # Install dependencies
    print("\n3. Installing dependencies...")
    if not install_dependencies():
        print("❌ Dependency installation failed")
        return False
    
    # Verify imports
    print("\n4. Verifying installations...")
    if not verify_imports():
        print("❌ Some modules failed to import")
        return False
    
    # Check OpenAI key
    print("\n5. Checking OpenAI API key...")
    has_key = check_openai_key()
    
    print("\n" + "=" * 60)
    if has_key:
        print("🎉 Voice support setup completed successfully!")
        print("\n📋 Next steps:")
        print("   1. Start the API server: python api_server.py")
        print("   2. Start the Gradio UI: python gradio_ui.py")
        print("   3. Test voice integration: python test_voice_integration.py")
        print("   4. Access the web interface at: http://localhost:7860")
    else:
        print("⚠️  Setup completed with warnings!")
        print("\n📋 Required actions:")
        print("   1. Add your OPENAI_API_KEY to the .env file")
        print("   2. Restart the setup: python setup_voice_support.py")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
