import streamlit as st
import base64
from PIL import Image
from io import BytesIO
from openai import OpenAI

class MessageHistory:
    def __init__(self):
        self._messages = []

    def add_user_message(self, message):
        self._messages.append({"role": "user", "content": message})

    def add_ai_message(self, message):
        self._messages.append({"role": "assistant", "content": message})

    def add_messages(self, messages):
        self._messages.extend(messages)

    @property
    def messages(self):
        return self._messages

    def clear(self):
        self._messages = []



def display_waiting_indicator():
    st.markdown(
        """
        <style>
        .typing-indicator {
            display: flex;
            align-items: center;
            height: 20px;
        }
        .typing-indicator span {
            display: inline-block;
            width: 5px;
            height: 5px;
            margin: 0 2px;
            background: #999;
            border-radius: 50%;
            animation: bounce 1s infinite alternate;
        }
        .typing-indicator span:nth-child(2) {
            animation-delay: 0.2s;
        }
        .typing-indicator span:nth-child(3) {
            animation-delay: 0.4s;
        }
        @keyframes bounce {
            from { transform: translateY(0); }
            to { transform: translateY(-15px); }
        }
        </style>
        <div class="typing-indicator">
            <span></span><span></span><span></span>
        </div>
    """,
        unsafe_allow_html=True,
    )


def prepare_audio_input_for_llm(audio_data: bytes):
    return base64.b64encode(audio_data).decode("utf-8")


def prepare_image_input_for_llm(image: Image) -> str:
    """base64 encode the given image"""
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode("utf-8")


def ai_chat_has_audio_input(messages: list[dict]):
    return any(message["content"][0]["type"] == "input_audio" for message in messages if isinstance(message["content"], list))


def ai_chat_has_image_input(messages: list[dict]):
    return any(message["content"][0]["type"] == "image_url" for message in messages if isinstance(message["content"], list))

@st.cache_data(show_spinner="Validating OpenAI API key...")
def validate_openai_api_key(openai_api_key: str):
    client = OpenAI(
        api_key=openai_api_key
    )
    try:
        client.models.list()
        return True
    except Exception:
        return False
