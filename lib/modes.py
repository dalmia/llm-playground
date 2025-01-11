from lib.llm import MessageHistory, ai_chat_has_audio_input
# import instructor
from openai import OpenAI
import streamlit as st


def chat(ai_chat_history: MessageHistory, system_prompt: str, openai_api_key: str, max_completion_tokens: int = 2048, temperature: float = 0):
    # client = instructor.from_openai(OpenAI())
    client = OpenAI(api_key=openai_api_key)

    messages = [{"role": "system", "content": system_prompt}] + ai_chat_history.messages

    if ai_chat_has_audio_input(messages):
        model = "gpt-4o-audio-preview-2024-12-17"
    else:
        model = "gpt-4o-mini-2024-07-18"

    stream = client.chat.completions.create(
        model=model,
        messages=messages,
        stream=True,
        max_completion_tokens=max_completion_tokens,
        temperature=temperature,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        store=True,
    )

    ai_response = ""
    for chunk in stream:
        if chunk.choices[0].delta.content is not None:
            ai_response += chunk.choices[0].delta.content
            st.write(ai_response, end="")

    return ai_response