#!/usr/bin/env python3
"""
Voice Service for Hana Salon Booking System
Handles speech-to-text conversion using OpenAI Whisper API
"""

import os
import tempfile
import aiofiles
from typing import Optional
from openai import AsyncOpenAI
from fastapi import UploadFile, HTTPException
import logging

logger = logging.getLogger(__name__)

class VoiceService:
    """Service for handling voice input processing"""
    
    def __init__(self):
        """Initialize the voice service with OpenAI client"""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        
        self.client = AsyncOpenAI(api_key=api_key)
        self.supported_formats = {
            'audio/mpeg', 'audio/mp3', 'audio/wav', 'audio/m4a', 
            'audio/mp4', 'audio/webm', 'audio/ogg'
        }
        self.max_file_size = 25 * 1024 * 1024  # 25MB limit for Whisper API
    
    async def transcribe_audio(self, audio_file: UploadFile) -> str:
        """
        Transcribe audio file to text using OpenAI Whisper API
        
        Args:
            audio_file: Uploaded audio file
            
        Returns:
            Transcribed text string
            
        Raises:
            HTTPException: If file validation fails or transcription errors
        """
        try:
            # Validate file
            self._validate_audio_file(audio_file)
            
            # Create temporary file for processing
            with tempfile.NamedTemporaryFile(delete=False, suffix=self._get_file_extension(audio_file.filename)) as temp_file:
                temp_path = temp_file.name
                
                # Write uploaded file to temporary location
                async with aiofiles.open(temp_path, 'wb') as f:
                    content = await audio_file.read()
                    await f.write(content)
                
                # Transcribe using OpenAI Whisper
                with open(temp_path, 'rb') as audio:
                    transcript = await self.client.audio.transcriptions.create(
                        model="whisper-1",
                        file=audio,
                        language="en"  # Specify English for salon booking context
                    )
                
                # Clean up temporary file
                os.unlink(temp_path)
                
                transcribed_text = transcript.text.strip()
                logger.info(f"Successfully transcribed audio: {transcribed_text[:100]}...")
                
                return transcribed_text
                
        except Exception as e:
            logger.error(f"Error transcribing audio: {str(e)}")
            # Clean up temp file if it exists
            if 'temp_path' in locals() and os.path.exists(temp_path):
                os.unlink(temp_path)
            raise HTTPException(status_code=500, detail=f"Audio transcription failed: {str(e)}")
    
    def _validate_audio_file(self, audio_file: UploadFile) -> None:
        """Validate uploaded audio file"""
        
        # Check file size
        if hasattr(audio_file, 'size') and audio_file.size > self.max_file_size:
            raise HTTPException(
                status_code=413, 
                detail=f"File too large. Maximum size is {self.max_file_size // (1024*1024)}MB"
            )
        
        # Check content type
        if audio_file.content_type and audio_file.content_type not in self.supported_formats:
            raise HTTPException(
                status_code=415,
                detail=f"Unsupported audio format. Supported formats: {', '.join(self.supported_formats)}"
            )
        
        # Check filename extension
        if audio_file.filename:
            ext = self._get_file_extension(audio_file.filename).lower()
            supported_extensions = {'.mp3', '.wav', '.m4a', '.mp4', '.webm', '.ogg'}
            if ext not in supported_extensions:
                raise HTTPException(
                    status_code=415,
                    detail=f"Unsupported file extension. Supported: {', '.join(supported_extensions)}"
                )
    
    def _get_file_extension(self, filename: Optional[str]) -> str:
        """Extract file extension from filename"""
        if not filename:
            return '.wav'  # Default extension
        
        if '.' in filename:
            return '.' + filename.split('.')[-1].lower()
        return '.wav'
    
    async def process_voice_message(self, audio_file: UploadFile, session_id: Optional[str] = None) -> dict:
        """
        Process voice message and return structured response
        
        Args:
            audio_file: Uploaded audio file
            session_id: Optional session ID for conversation context
            
        Returns:
            Dictionary with transcribed text and metadata
        """
        try:
            # Transcribe the audio
            transcribed_text = await self.transcribe_audio(audio_file)
            
            # Return structured response
            return {
                "transcribed_text": transcribed_text,
                "session_id": session_id,
                "audio_duration": getattr(audio_file, 'size', 0),  # Approximate
                "success": True
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error processing voice message: {str(e)}")
            raise HTTPException(status_code=500, detail="Voice processing failed")

# Global voice service instance
voice_service = VoiceService()
