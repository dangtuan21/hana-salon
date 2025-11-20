#!/usr/bin/env python3
"""
Restart All Services Script
Convenient script to restart both backend and AI service with one command
"""

import subprocess
import time
import sys
import os
import signal

def run_command(cmd, cwd=None, timeout=10):
    """Run a command and return success status"""
    try:
        result = subprocess.run(cmd, shell=True, cwd=cwd, timeout=timeout, 
                              capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Command timed out"
    except Exception as e:
        return False, "", str(e)

def kill_processes():
    """Kill existing AI service processes"""
    print("🛑 Stopping existing services...")
    
    # Kill AI service processes
    commands = [
        "pkill -f 'start_booking_system.py'",
        "pkill -f 'api_server.py'",
        "pkill -f 'gradio_ui.py'"
    ]
    
    for cmd in commands:
        success, stdout, stderr = run_command(cmd)
        if success:
            print(f"   ✅ {cmd}")
        else:
            print(f"   ⚠️ {cmd} (may not have been running)")
    
    # Wait a moment for processes to terminate
    time.sleep(2)

def check_ports():
    """Check if ports are free"""
    print("🔍 Checking ports...")
    
    ports = [8060, 7860]
    for port in ports:
        success, stdout, stderr = run_command(f"lsof -i :{port}")
        if success and stdout.strip():
            print(f"   ⚠️ Port {port} still in use:")
            print(f"      {stdout.strip()}")
        else:
            print(f"   ✅ Port {port} is free")

def start_ai_service():
    """Start the AI service"""
    print("🚀 Starting AI service...")
    
    # Get the directory of this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    try:
        # Start the booking system with visible output
        print("   📋 Starting with visible logs...")
        print("   " + "="*50)
        
        process = subprocess.Popen(
            [sys.executable, "start_booking_system.py"],
            cwd=script_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,  # Merge stderr into stdout
            text=True,
            bufsize=1,  # Line buffered
            universal_newlines=True
        )
        
        # Show initial startup logs
        startup_lines = []
        start_time = time.time()
        
        while time.time() - start_time < 10:  # Wait up to 10 seconds for startup
            if process.poll() is not None:
                # Process ended
                remaining_output = process.stdout.read()
                if remaining_output:
                    print(remaining_output, end='')
                print("   ❌ AI service process ended unexpectedly")
                return False
            
            # Read available output
            try:
                line = process.stdout.readline()
                if line:
                    print(f"   {line.rstrip()}")
                    startup_lines.append(line)
                    
                    # Check for successful startup indicators
                    if "Application startup complete" in line or "Booking system is running" in line:
                        print("   ✅ AI service started successfully")
                        print(f"   📋 Process ID: {process.pid}")
                        print("   📋 Service is now running in background...")
                        return True
                else:
                    time.sleep(0.1)
            except:
                time.sleep(0.1)
        
        # If we get here, startup took too long
        if process.poll() is None:
            print("   ⚠️ Service started but startup verification timed out")
            print(f"   📋 Process ID: {process.pid}")
            return True
        else:
            print("   ❌ AI service failed to start within timeout")
            return False
            
    except Exception as e:
        print(f"   ❌ Error starting AI service: {e}")
        return False

def verify_services():
    """Verify that services are running"""
    print("🔍 Verifying services...")
    
    # Check AI service API
    success, stdout, stderr = run_command("curl -s http://localhost:8060/health", timeout=5)
    if success and "healthy" in stdout:
        print("   ✅ AI Service API (port 8060) - Healthy")
    else:
        print("   ❌ AI Service API (port 8060) - Not responding")
        return False
    
    # Check Gradio UI
    success, stdout, stderr = run_command("curl -s -o /dev/null -w '%{http_code}' http://localhost:7860", timeout=5)
    if success and "200" in stdout:
        print("   ✅ Gradio UI (port 7860) - Running")
    else:
        print("   ❌ Gradio UI (port 7860) - Not responding")
        return False
    
    return True

def main():
    """Main restart function"""
    print("🔄 RESTARTING ALL SERVICES")
    print("=" * 50)
    
    try:
        # Step 1: Kill existing processes
        kill_processes()
        
        # Step 2: Check ports are free
        check_ports()
        
        # Step 3: Start AI service
        if not start_ai_service():
            print("❌ Failed to start AI service")
            sys.exit(1)
        
        # Step 4: Wait a bit more for full startup
        print("⏳ Waiting for services to fully initialize...")
        time.sleep(8)
        
        # Step 5: Verify services
        if verify_services():
            print("\n🎉 ALL SERVICES RESTARTED SUCCESSFULLY!")
            print("=" * 50)
            print("📋 API Documentation: http://localhost:8060/docs")
            print("💬 Chat Interface: http://localhost:7860")
            print("🔧 API Health Check: http://localhost:8060/health")
            print("=" * 50)
            print("\n🔄 STARTING WITH VISIBLE LOGS...")
            print("💡 Press Ctrl+C to stop the system")
            print("=" * 50)
            
            # Kill the background service and start in foreground with visible logs
            kill_processes()
            time.sleep(2)
            
            # Start booking system in foreground to see logs
            script_dir = os.path.dirname(os.path.abspath(__file__))
            try:
                subprocess.run([sys.executable, "start_booking_system.py"], cwd=script_dir)
            except KeyboardInterrupt:
                print("\n🛑 System stopped by user")
                kill_processes()
        else:
            print("\n❌ SERVICE VERIFICATION FAILED")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️ Restart interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
