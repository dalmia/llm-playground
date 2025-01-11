# LLM Playground

This is a simple `streamlit` app that shows how to build different use cases using LLMs. It currently supports LLMs offered by OpenAI.

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://the-llm-playground.streamlit.app/)

**Features supported:**
- Chat using text, image and audio inputs while maintaining chat history
- Extracting structured outputs from text/audio/image inputs
- Streaming responses (both text and JSON)
- Changing the system prompt and temperature from the UI

TODO (coming soon):
- [ ] Chain-Of-Thought reasoning
- [ ] RAG over single and multiple documents
- [ ] Tool calling/agentic workflows
- [ ] Realtime API (audio-to-audio, advanced voice mode)
- [ ] Summarization
- [ ] Reasoning over videos and structured outputs from videos
- [ ] Text-to-video generation
- [ ] Speech-to-text and text-to-speech
- [ ] Transcription and translation
- [ ] Text-to-image generation, Image-to-text generation

## Installation
- Clone the repository
- Create a virtual environment (Python 3.10+)
  ```
  python -m venv venv
  ```
- Activate the virtual environment
  ```
  source venv/bin/activate
  ```
- Install the dependencies
  ```
  pip install -r requirements.txt
  ```
- Run the app
  ```
  streamlit run streamlit_app.py
  ```
