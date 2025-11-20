#!/usr/bin/env python3
"""
View Live Logs Script
Shows real-time logs from the AI service by restarting it with visible output
"""

import subprocess
import sys
import os
import signal
import time

def main():
    """Start AI service with visible logs"""
    print("📋 VIEWING AI SERVICE LOGS")
    print("=" * 50)
    print("💡 This will restart the AI service with visible logs")
    print("💡 Press Ctrl+C to stop")
    print("=" * 50)
    
    # Get the directory of this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    try:
        # Kill existing processes first
        print("🛑 Stopping existing services...")
        subprocess.run("pkill -f 'start_booking_system.py'", shell=True)
        subprocess.run("pkill -f 'api_server.py'", shell=True)
        time.sleep(2)
        
        print("🚀 Starting AI service with visible logs...")
        print("-" * 50)
        
        # Start the API server directly to see logs
        process = subprocess.Popen(
            [sys.executable, "-u", "api_server.py"],  # -u for unbuffered output
            cwd=script_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=0,  # Unbuffered
            universal_newlines=True
        )
        
        # Stream the output in real-time
        try:
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    print(output.rstrip())
                    
        except KeyboardInterrupt:
            print("\n🛑 Stopping AI service...")
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
            print("✅ AI service stopped")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
