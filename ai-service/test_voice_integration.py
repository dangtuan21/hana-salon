#!/usr/bin/env python3
"""
Test script for voice integration
Tests the voice endpoints and service functionality
"""

import requests
import os
import tempfile
import wave
import numpy as np
from typing import Optional

def create_test_audio_file() -> str:
    """Create a simple test audio file for testing"""
    # Create a simple sine wave audio file
    sample_rate = 44100
    duration = 2  # seconds
    frequency = 440  # A4 note
    
    # Generate sine wave
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    audio_data = np.sin(2 * np.pi * frequency * t)
    
    # Convert to 16-bit integers
    audio_data = (audio_data * 32767).astype(np.int16)
    
    # Create temporary WAV file
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
    
    with wave.open(temp_file.name, 'w') as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 2 bytes per sample
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(audio_data.tobytes())
    
    return temp_file.name

def test_voice_service_import():
    """Test if voice service can be imported"""
    try:
        # Load environment first
        from dotenv import load_dotenv
        load_dotenv()
        
        from services.voice_service import voice_service
        print("✅ Voice service imported successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to import voice service: {e}")
        return False

def test_api_health(base_url: str = "http://localhost:8060"):
    """Test if API server is running"""
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        response.raise_for_status()
        print("✅ API server is running")
        return True
    except Exception as e:
        print(f"❌ API server not accessible: {e}")
        return False

def test_voice_transcription_endpoint(base_url: str = "http://localhost:8060"):
    """Test the voice transcription utility endpoint"""
    try:
        # Create test audio file
        audio_file_path = create_test_audio_file()
        
        # Test transcription endpoint
        with open(audio_file_path, 'rb') as f:
            files = {'audio_file': ('test.wav', f, 'audio/wav')}
            response = requests.post(f"{base_url}/voice/transcribe", files=files, timeout=30)
        
        # Clean up
        os.unlink(audio_file_path)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Voice transcription endpoint working")
            print(f"   Transcribed: {result.get('transcribed_text', 'N/A')}")
            return True
        else:
            print(f"❌ Voice transcription failed: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Voice transcription test failed: {e}")
        return False

def test_voice_conversation_start(base_url: str = "http://localhost:8060"):
    """Test starting a voice conversation"""
    try:
        # Create test audio file
        audio_file_path = create_test_audio_file()
        
        # Test voice conversation start
        with open(audio_file_path, 'rb') as f:
            files = {'audio_file': ('test.wav', f, 'audio/wav')}
            response = requests.post(f"{base_url}/conversation/voice/start", files=files, timeout=30)
        
        # Clean up
        os.unlink(audio_file_path)
        
        if response.status_code == 200:
            result = response.json()
            session_id = result.get('session_id')
            print(f"✅ Voice conversation started successfully")
            print(f"   Session ID: {session_id}")
            print(f"   Response: {result.get('response', 'N/A')[:100]}...")
            return session_id
        else:
            print(f"❌ Voice conversation start failed: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Voice conversation start test failed: {e}")
        return None

def test_voice_conversation_continue(session_id: str, base_url: str = "http://localhost:8060"):
    """Test continuing a voice conversation"""
    if not session_id:
        print("❌ No session ID provided for continuation test")
        return False
        
    try:
        # Create test audio file
        audio_file_path = create_test_audio_file()
        
        # Test voice conversation continuation
        with open(audio_file_path, 'rb') as f:
            files = {'audio_file': ('test.wav', f, 'audio/wav')}
            response = requests.post(f"{base_url}/conversation/{session_id}/voice/message", files=files, timeout=30)
        
        # Clean up
        os.unlink(audio_file_path)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Voice conversation continuation successful")
            print(f"   Response: {result.get('response', 'N/A')[:100]}...")
            return True
        else:
            print(f"❌ Voice conversation continuation failed: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Voice conversation continuation test failed: {e}")
        return False

def main():
    """Run all voice integration tests"""
    print("🎤 Testing Voice Integration for Hana Salon Booking System")
    print("=" * 60)
    
    # Check if required packages are available
    try:
        import numpy as np
        import wave
    except ImportError as e:
        print(f"❌ Missing required packages for testing: {e}")
        print("💡 Install with: pip install numpy")
        return
    
    # Test 1: Voice service import
    print("\n1. Testing voice service import...")
    if not test_voice_service_import():
        print("❌ Voice service import failed. Make sure OpenAI API key is set.")
        return
    
    # Test 2: API server health
    print("\n2. Testing API server health...")
    if not test_api_health():
        print("❌ API server not running. Start with: python api_server.py")
        return
    
    # Test 3: Voice transcription endpoint
    print("\n3. Testing voice transcription endpoint...")
    if not test_voice_transcription_endpoint():
        print("❌ Voice transcription endpoint failed")
        return
    
    # Test 4: Voice conversation start
    print("\n4. Testing voice conversation start...")
    session_id = test_voice_conversation_start()
    if not session_id:
        print("❌ Voice conversation start failed")
        return
    
    # Test 5: Voice conversation continuation
    print("\n5. Testing voice conversation continuation...")
    if not test_voice_conversation_continue(session_id):
        print("❌ Voice conversation continuation failed")
        return
    
    print("\n" + "=" * 60)
    print("🎉 All voice integration tests passed!")
    print("\n📋 Next steps:")
    print("   1. Install dependencies: pip install -r requirements.txt")
    print("   2. Set OPENAI_API_KEY in .env file")
    print("   3. Start API server: python api_server.py")
    print("   4. Start Gradio UI: python gradio_ui.py")
    print("   5. Test voice input in the web interface at http://localhost:7860")

if __name__ == "__main__":
    main()
