import streamlit as st

st.set_page_config(page_title="LLM Playground")

from PIL import Image
from lib.llm import MessageHistory, display_waiting_indicator, prepare_audio_input_for_llm, prepare_image_input_for_llm, ai_chat_has_audio_input, ai_chat_has_image_input, validate_openai_api_key
from lib.modes import chat, sentiment_classifier

modes = ["Chat", "Structured Output"]

openai_api_key = st.sidebar.text_input("OpenAI API key", type="password")

if not openai_api_key:
    st.error("Please enter your OpenAI API key")
    st.stop()

if not validate_openai_api_key(openai_api_key):
    st.error("Please enter a valid OpenAI API key")
    st.stop()

mode = st.sidebar.selectbox("Select a mode", modes)

def add_temperature_picker():
    st.sidebar.slider("Temperature", key="temperature", min_value=0.0, max_value=5.0, value=0.0, step=0.1)


if 'file_uploader_key' not in st.session_state:
    st.session_state.file_uploader_key = 0

if "audio_recorder_key" not in st.session_state:
    st.session_state.audio_recorder_key = 0

def update_file_uploader_key():
    st.session_state.file_uploader_key += 1

def update_audio_recorder_key():
    st.session_state.audio_recorder_key += 1


def show_chat_mode():
    system_prompt = st.sidebar.text_area("System prompt", value="You are a helpful assistant who is having a conversation with a user. You are given a conversation history and a user message. You are to respond to the user message based on the conversation history. You are to respond in a friendly and helpful manner.", height=300)

    add_temperature_picker()

    def reset_chat_history():
        st.session_state.chat_history = [
            {"role": "assistant", "content": "Hello! How can I help you today?"}
        ]
    
    def reset_ai_chat_history():
        st.session_state.ai_chat_history = MessageHistory()
        st.session_state.ai_chat_history.add_ai_message(st.session_state.chat_history[0]['content'])

    def reset_app_state():
        reset_chat_history()
        reset_ai_chat_history()

    if 'chat_history' not in st.session_state:
        reset_app_state()

    chat_window = st.container(height=425, border=False)

    st.divider()

    def display_user_message(user_message):
        with chat_window.chat_message("user"):
            if isinstance(user_message, dict) and user_message["type"] == "text":
                st.write(user_message["text"])
            elif isinstance(user_message, list) and user_message[0]["type"] == "image":
                st.image(user_message[0]["image"], width=400)
                st.write(user_message[1]["text"])
            elif isinstance(user_message, dict) and user_message["type"] == "audio":
                st.audio(user_message["audio"])

    def display_ai_message(ai_message):
        chat_window.chat_message("assistant").write(ai_message)

    def get_ai_feedback(user_message):
        st.session_state.chat_history.append({"role": "user", "content": user_message})
    
        display_user_message(user_message)

        container = chat_window.chat_message("assistant").empty()

        with container:
            display_waiting_indicator()
        
        if isinstance(user_message, dict) and user_message["type"] == "text":
            user_message_for_ai = user_message["text"]
        elif isinstance(user_message, list) and user_message[0]["type"] == "image":
            user_message_for_ai = [
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/png;base64,{prepare_image_input_for_llm(user_message[0]['image'])}",
                    },
                },
                {"type": "text", "text": user_message[1]["text"]}
            ]
        elif isinstance(user_message, dict) and user_message["type"] == "audio":
            user_message_for_ai = [
                {
                    "type": "input_audio",
                    "input_audio": {
                        "data": prepare_audio_input_for_llm(user_message['audio'].read()),
                    "format": "wav",
                },
            },
        ]
        st.session_state.ai_chat_history.add_user_message(user_message_for_ai)

        with container:
            ai_response = chat(st.session_state.ai_chat_history, system_prompt, openai_api_key, temperature=st.session_state.temperature)
        
        return ai_response

    with chat_window:
        for message in st.session_state.chat_history:
            if message["role"] == "user":
                display_user_message(message["content"])
            else:
                display_ai_message(message["content"])


    cols = st.columns([5, 1])
    with cols[0]:
        input_type = st.radio("Select an input type", ["Text", "Image", "Audio"], horizontal=True)
    with cols[1]:
        if st.button("Clear chat"):
            reset_app_state()
            st.rerun()

    error_container = st.container()

    ai_response = None
    if input_type == "Text":
        if prompt := st.chat_input("Enter your message"):
            user_message = {"type": "text", "text": prompt}

            ai_response = get_ai_feedback(user_message)

    elif input_type == "Image":
        if ai_chat_has_audio_input(st.session_state.ai_chat_history.messages):
            error_container.error("You cannot send an image to a chat that has audio input. Start a new chat to send an image message!")
        else:
            file_obj = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"], accept_multiple_files=False, key=f"file_uploader_{st.session_state.file_uploader_key}")

            if file_obj:
                image = Image.open(file_obj)

                placeholder = st.empty()
                placeholder.image(image, width=400)
            
                if prompt := st.chat_input("What do you want to know about this image?"):        
                    user_message = [{"type": "image", "image": image}, {"type": "text", "text": prompt}]
                    placeholder.empty()
                    update_file_uploader_key()
                    ai_response = get_ai_feedback(user_message)
    elif input_type == "Audio":
        if ai_chat_has_image_input(st.session_state.ai_chat_history.messages):
            error_container.error("You cannot send an audio to a chat that has image input. Start a new chat to send an audio message!")
        else:
            if audio := st.audio_input('Record a voice message', key=f"audio_recorder_{st.session_state.audio_recorder_key}"):
                user_message = {"type": "audio", "audio": audio}
                ai_response = get_ai_feedback(user_message)
                update_audio_recorder_key()

    if ai_response:
        st.session_state.chat_history.append({"role": "assistant", "content": ai_response})
        st.session_state.ai_chat_history.add_ai_message(ai_response)
        st.rerun()


if mode == "Chat":
    show_chat_mode()

def show_structured_output_mode():
    stream_response = st.sidebar.checkbox("Stream response", value=True)

    add_temperature_picker()

    tabs = st.tabs(["Sentiment Classifier"])

    if 'user_message' not in st.session_state:
        st.session_state.input_display_placeholder = st.empty()

    with tabs[0]:
        st.write("Enter any comment to classify its sentiment as either `positive`, `negative`, or `neutral`.")

        cols = st.columns([5, 1])

        response_container = st.empty()

        def reset_display_containers():
            update_file_uploader_key()
            update_audio_recorder_key()
            st.session_state.input_display_placeholder.empty()
            response_container.empty()

        with cols[0]:
            input_type = st.radio("Select an input type", ["Text", "Image", "Audio"], key='input_type', horizontal=True, on_change=reset_display_containers)

            if input_type == "Text":
                if prompt := st.text_input("Enter your message"):
                    st.session_state.user_message = {"type": "text", "text": prompt}

            elif input_type == "Image":
                
                file_obj = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"], accept_multiple_files=False, key=f"file_uploader_{st.session_state.file_uploader_key}")

                if file_obj:
                    image = Image.open(file_obj)

                    st.session_state.input_display_placeholder.image(image, width=400)
                
                    st.session_state.user_message = [{"type": "image", "image": image}]

            elif input_type == "Audio":
                if audio := st.audio_input('Record a voice message', key=f"audio_recorder_{st.session_state.audio_recorder_key}"):
                    st.session_state.user_message = {"type": "audio", "audio": audio}


        cols[1].container(height=10, border=False)
        if cols[1].button("Classify", type="primary"):
            with response_container:
                sentiment_classifier(st.session_state.user_message, stream_response, openai_api_key, temperature=st.session_state.temperature)

if mode == "Structured Output":
    show_structured_output_mode()
