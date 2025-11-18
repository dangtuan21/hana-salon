#!/usr/bin/env python3
"""
Launcher script for Hana Salon Booking System
Starts both the API server and Gradio UI
"""

import subprocess
import time
import sys
import os
import signal
import threading
from pathlib import Path

class BookingSystemLauncher:
    """Manages launching and stopping the booking system components"""
    
    def __init__(self):
        self.api_process = None
        self.ui_process = None
        self.running = False
    
    def start_api_server(self):
        """Start the FastAPI server in background"""
        print("🚀 Starting API server...")
        
        try:
            self.api_process = subprocess.Popen(
                [sys.executable, "api_server.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Give it a moment to start
            time.sleep(3)
            
            if self.api_process.poll() is None:
                print("✅ API server started successfully on http://localhost:8060")
                return True
            else:
                stdout, stderr = self.api_process.communicate()
                print(f"❌ API server failed to start:")
                print(f"STDOUT: {stdout}")
                print(f"STDERR: {stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Error starting API server: {e}")
            return False
    
    def start_gradio_ui(self):
        """Start the Gradio UI"""
        print("🎨 Starting Gradio UI...")
        
        try:
            self.ui_process = subprocess.Popen(
                [sys.executable, "gradio_ui.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Give it a moment to start
            time.sleep(2)
            
            if self.ui_process.poll() is None:
                print("✅ Gradio UI started successfully on http://localhost:7860")
                return True
            else:
                stdout, stderr = self.ui_process.communicate()
                print(f"❌ Gradio UI failed to start:")
                print(f"STDOUT: {stdout}")
                print(f"STDERR: {stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Error starting Gradio UI: {e}")
            return False
    
    def check_dependencies(self):
        """Check if required dependencies are installed"""
        print("🔍 Checking dependencies...")
        
        required_packages = [
            "fastapi",
            "uvicorn", 
            "gradio",
            "requests",
            "langchain",
            "langchain_openai"
        ]
        
        missing_packages = []
        
        for package in required_packages:
            try:
                __import__(package)
            except ImportError:
                missing_packages.append(package)
        
        if missing_packages:
            print(f"❌ Missing packages: {', '.join(missing_packages)}")
            print("💡 Install them with: pip install -r requirements.txt")
            return False
        
        print("✅ All dependencies are installed")
        return True
    
    def check_environment(self):
        """Check if environment variables are set"""
        print("🔍 Checking environment...")
        
        required_env_vars = ["OPENAI_API_KEY"]
        missing_vars = []
        
        for var in required_env_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
            print("💡 Set them in your .env file or environment")
            return False
        
        print("✅ Environment variables are set")
        return True
    
    def stop_processes(self):
        """Stop all running processes"""
        print("\n🛑 Stopping booking system...")
        
        if self.api_process and self.api_process.poll() is None:
            print("🔄 Stopping API server...")
            self.api_process.terminate()
            try:
                self.api_process.wait(timeout=5)
                print("✅ API server stopped")
            except subprocess.TimeoutExpired:
                print("⚠️  Force killing API server...")
                self.api_process.kill()
        
        if self.ui_process and self.ui_process.poll() is None:
            print("🔄 Stopping Gradio UI...")
            self.ui_process.terminate()
            try:
                self.ui_process.wait(timeout=5)
                print("✅ Gradio UI stopped")
            except subprocess.TimeoutExpired:
                print("⚠️  Force killing Gradio UI...")
                self.ui_process.kill()
        
        self.running = False
        print("✅ Booking system stopped")
    
    def signal_handler(self, signum, frame):
        """Handle Ctrl+C gracefully"""
        self.stop_processes()
        sys.exit(0)
    
    def start_system(self):
        """Start the complete booking system"""
        print("💅 Hana Salon Booking System Launcher")
        print("=" * 50)
        
        # Check prerequisites
        if not self.check_dependencies():
            return False
        
        if not self.check_environment():
            return False
        
        # Set up signal handler for graceful shutdown
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        # Start API server
        if not self.start_api_server():
            return False
        
        # Start Gradio UI
        if not self.start_gradio_ui():
            self.stop_processes()
            return False
        
        self.running = True
        
        print("\n🎉 Booking system is running!")
        print("=" * 50)
        print("📋 API Documentation: http://localhost:8060/docs")
        print("💬 Chat Interface: http://localhost:7860")
        print("🔧 API Health Check: http://localhost:8060/health")
        print("\n💡 Press Ctrl+C to stop the system")
        
        # Keep the main process alive
        try:
            while self.running:
                time.sleep(1)
                
                # Check if processes are still running
                if self.api_process and self.api_process.poll() is not None:
                    print("❌ API server stopped unexpectedly")
                    break
                
                if self.ui_process and self.ui_process.poll() is not None:
                    print("❌ Gradio UI stopped unexpectedly")
                    break
                    
        except KeyboardInterrupt:
            pass
        
        self.stop_processes()
        return True

def main():
    """Main function"""
    launcher = BookingSystemLauncher()
    
    try:
        success = launcher.start_system()
        if not success:
            print("\n❌ Failed to start booking system")
            sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        launcher.stop_processes()
        sys.exit(1)

if __name__ == "__main__":
    main()
