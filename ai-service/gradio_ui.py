#!/usr/bin/env python3
"""
Gradio UI for Hana Salon Conversational Booking System
Provides a chat interface to test the pure LLM booking conversations
"""

import gradio as gr
import requests
import json
from typing import List, Tuple, Optional
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class BookingChatInterface:
    """Gradio chat interface for salon booking conversations"""
    
    def __init__(self, api_base_url: str = "http://localhost:8060"):
        self.api_base_url = api_base_url
        self.current_session_id = None
        self.conversation_history = []
    
    def start_new_conversation(self) -> str:
        """Start a new conversation and reset state"""
        self.current_session_id = None
        self.conversation_history = []
        return "🆕 New conversation started! How can I help you book your salon appointment today?"
    
    def send_message(self, message: str, history: List[Tuple[str, str]]) -> Tuple[List[Tuple[str, str]], str]:
        """Send a message to the booking API and update chat history"""
        
        if not message.strip():
            return history, ""
        
        try:
            # Determine if this is a new conversation or continuation
            if self.current_session_id is None:
                # Start new conversation
                response = self._start_conversation(message)
                self.current_session_id = response.get("session_id")
            else:
                # Continue existing conversation
                response = self._continue_conversation(message)
            
            # Extract response data
            assistant_response = response.get("response", "I'm sorry, I couldn't process that request.")
            booking_state = response.get("booking_state", {})
            actions_taken = response.get("actions_taken", [])
            conversation_complete = response.get("conversation_complete", False)
            
            # Format assistant response with booking info
            formatted_response = self._format_response(
                assistant_response, 
                booking_state, 
                actions_taken, 
                conversation_complete
            )
            
            # Update history
            history.append((message, formatted_response))
            
            # Conversation handler now generates completion message naturally
            # No need for hardcoded UI completion message
            
            return history, ""
            
        except requests.exceptions.ConnectionError:
            error_msg = "❌ **Connection Error**: Could not connect to the booking service. Make sure the API server is running on localhost:8060"
            history.append((message, error_msg))
            return history, ""
            
        except Exception as e:
            error_msg = f"❌ **Error**: {str(e)}"
            history.append((message, error_msg))
            return history, ""
    
    def _start_conversation(self, message: str) -> dict:
        """Start a new conversation with the API"""
        url = f"{self.api_base_url}/conversation/start"
        payload = {"message": message}
        
        response = requests.post(url, json=payload, timeout=30)
        response.raise_for_status()
        
        return response.json()
    
    def _continue_conversation(self, message: str) -> dict:
        """Continue existing conversation with the API"""
        url = f"{self.api_base_url}/conversation/continue"
        payload = {
            "session_id": self.current_session_id,
            "message": message
        }
        
        response = requests.post(url, json=payload, timeout=30)
        response.raise_for_status()
        
        return response.json()
    
    def _format_response(self, response: str, booking_state: dict, actions_taken: List[str], complete: bool) -> str:
        """Format the assistant response simply"""
        return response
    
    def get_conversation_status(self) -> str:
        """Get current conversation status"""
        if not self.current_session_id:
            return "No active conversation"
        
        try:
            url = f"{self.api_base_url}/conversation/{self.current_session_id}/status"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            status = response.json()
            
            return f"""
            **Session ID:** {status['session_id']}
            **Created:** {status['created_at']}
            **Messages:** {status['message_count']}
            **Complete:** {status['conversation_complete']}
            """
            
        except Exception as e:
            return f"Error getting status: {str(e)}"
    
    def clear_conversation(self) -> str:
        """Clear current conversation"""
        if not self.current_session_id:
            return "No active conversation to clear"
        
        try:
            url = f"{self.api_base_url}/conversation/{self.current_session_id}"
            response = requests.delete(url, timeout=10)
            response.raise_for_status()
            
            result = response.json()
            self.current_session_id = None
            self.conversation_history = []
            
            return f"✅ {result['message']}"
            
        except Exception as e:
            return f"Error clearing conversation: {str(e)}"
    
    def send_voice_message(self, audio_file: str, history: List[Tuple[str, str]]) -> Tuple[List[Tuple[str, str]], str]:
        """Send a voice message to the booking API and update chat history"""
        
        if not audio_file:
            return history, None
        
        try:
            # Prepare the audio file for upload
            with open(audio_file, 'rb') as f:
                files = {'audio_file': (audio_file, f, 'audio/wav')}
                
                # Determine if this is a new conversation or continuation
                if self.current_session_id is None:
                    # Start new voice conversation
                    url = f"{self.api_base_url}/conversation/voice/start"
                    response = requests.post(url, files=files, timeout=60)
                else:
                    # Continue existing voice conversation
                    url = f"{self.api_base_url}/conversation/{self.current_session_id}/voice/message"
                    response = requests.post(url, files=files, timeout=60)
                
                response.raise_for_status()
                api_response = response.json()
            
            # Update session ID if new conversation
            if self.current_session_id is None:
                self.current_session_id = api_response.get("session_id")
            
            # Extract response data
            assistant_response = api_response.get("response", "I'm sorry, I couldn't process that voice message.")
            booking_state = api_response.get("booking_state", {})
            actions_taken = api_response.get("actions_taken", [])
            
            # Format the response
            formatted_response = self._format_response(
                assistant_response, booking_state, actions_taken, 
                api_response.get("conversation_complete", False)
            )
            
            # Add to conversation history
            history.append(("🎤 [Voice Message]", formatted_response))
            
            return history, None
            
        except requests.exceptions.RequestException as e:
            error_msg = f"Connection error: {str(e)}"
            history.append(("🎤 [Voice Message]", f"❌ {error_msg}"))
            return history, None
        except Exception as e:
            error_msg = f"Error processing voice message: {str(e)}"
            history.append(("🎤 [Voice Message]", f"❌ {error_msg}"))
            return history, None

def create_gradio_interface():
    """Create a simple, clean Gradio interface"""
    
    # Initialize chat interface
    chat_interface = BookingChatInterface()
    
    # Simple CSS
    custom_css = """
    .gradio-container {
        max-width: 800px !important;
        margin: 0 auto;
    }
    """
    
    # Create the interface
    with gr.Blocks(
        title="💅 Hana Salon Booking",
        theme=gr.themes.Default(),
        css=custom_css
    ) as interface:
        
        gr.Markdown("# 💅 Hana Salon Booking Assistant")
        gr.Markdown("Chat naturally to book your appointment!")
        
        # Main chat interface
        chatbot = gr.Chatbot(
            label="Conversation",
            height=400,
            show_label=False
        )
        
        # Input options
        with gr.Tab("💬 Text Input"):
            msg_input = gr.Textbox(
                placeholder="Hi, I want to book a manicure...",
                label="Your Message",
                lines=1
            )
            
            with gr.Row():
                send_btn = gr.Button("Send", variant="primary")
                clear_btn = gr.Button("New Chat", variant="secondary")
        
        with gr.Tab("🎤 Voice Input"):
            gr.Markdown("**Record your voice message and we'll transcribe it for you!**")
            
            voice_input = gr.Audio(
                label="Record Voice Message",
                type="filepath",
                format="wav"
            )
            
            with gr.Row():
                voice_send_btn = gr.Button("🎤 Send Voice Message", variant="primary")
                voice_clear_btn = gr.Button("New Chat", variant="secondary")
        
        # Event handlers
        def send_message_handler(message, history):
            return chat_interface.send_message(message, history)
        
        def send_voice_message_handler(audio_file, history):
            return chat_interface.send_voice_message(audio_file, history)
        
        def clear_conversation_handler():
            chat_interface.start_new_conversation()
            return [], ""
        
        # Wire up events
        send_btn.click(
            send_message_handler,
            inputs=[msg_input, chatbot],
            outputs=[chatbot, msg_input]
        )
        
        msg_input.submit(
            send_message_handler,
            inputs=[msg_input, chatbot],
            outputs=[chatbot, msg_input]
        )
        
        clear_btn.click(
            clear_conversation_handler,
            outputs=[chatbot, msg_input]
        )
        
        # Voice input events
        voice_send_btn.click(
            send_voice_message_handler,
            inputs=[voice_input, chatbot],
            outputs=[chatbot, voice_input]
        )
        
        voice_clear_btn.click(
            clear_conversation_handler,
            outputs=[chatbot, voice_input]
        )
    
    return interface

def main():
    """Main function to launch the Gradio interface"""
    
    print("🚀 Starting Hana Salon Booking UI...")
    print("📋 Make sure the API server is running on localhost:8060")
    print("💡 You can start it with: python api_server.py")
    
    # Create and launch interface
    interface = create_gradio_interface()
    
    # Launch with custom settings
    interface.launch(
        server_name="0.0.0.0",  # Allow external access
        server_port=7860,       # Default Gradio port
        share=False,            # Set to True for public sharing
        debug=True,             # Enable debug mode
        show_error=True,        # Show detailed errors
        inbrowser=True          # Auto-open browser
    )

if __name__ == "__main__":
    main()
