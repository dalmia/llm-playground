from lib.llm import MessageHistory, ai_chat_has_audio_input, prepare_image_input_for_llm, prepare_audio_input_for_llm
import instructor
from typing import Literal, List
from openai import OpenAI
import streamlit as st
from pydantic import BaseModel, Field


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
    )

    ai_response = ""
    for chunk in stream:
        if chunk.choices[0].delta.content is not None:
            ai_response += chunk.choices[0].delta.content
            st.write(ai_response, end="")

    return ai_response


def get_user_message_for_ai(user_message):
    if isinstance(user_message, str):
        return user_message
    if isinstance(user_message, dict) and user_message["type"] == "text":
        return user_message["text"]
    if isinstance(user_message, list) and user_message[0]["type"] == "image":
        user_message_for_ai = [
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/png;base64,{prepare_image_input_for_llm(user_message[0]['image'])}",
                },
            }
        ]
        if len(user_message) > 1:
            user_message_for_ai.append({"type": "text", "text": user_message[1]["text"]})
        return user_message_for_ai
    elif isinstance(user_message, dict) and user_message["type"] == "audio":
        return[
            {
                "type": "input_audio",
                "input_audio": {
                    "data": prepare_audio_input_for_llm(user_message['audio'].read()),
                "format": "wav",
            },
        },
    ]
    


def sentiment_classifier(user_message: str | List, stream: bool, openai_api_key: str, max_completion_tokens: int = 256, temperature: float = 0):
    class Sentiment(BaseModel):
        sentiment: int | Literal[1, 2, 3] = Field(default=None, description="The sentiment of the comment, must be an integer, one of 1 (positive), 2 (negative), or 3 (neutral)")

    system_prompt = """You are a sentiment classifier. You are given an input from the user. You need to classify its sentiment as either 1 (positive), 2 (negative), or 3 (neutral). Make sure to return an integer value only."""
    
    client = instructor.from_openai(OpenAI(api_key=openai_api_key))

    messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": get_user_message_for_ai(user_message)}]

    if ai_chat_has_audio_input(messages):
        model = "gpt-4o-audio-preview-2024-12-17"
    else:
        model = "gpt-4o-mini-2024-07-18"

    if stream:
        llm_call = client.chat.completions.create_partial
    else:
        llm_call = client.chat.completions.create

    response = llm_call(
        model=model,
        messages=messages,
        response_model=Sentiment,
        max_completion_tokens=max_completion_tokens,
        temperature=temperature,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        store=True,
        stream=stream
    )

    response_to_sentiment = {1: "positive", 2: "negative", 3: "neutral"}

    if stream:
        for val in response:
            if val.sentiment:
                val.sentiment = response_to_sentiment[val.sentiment]

            st.write(val)
    else:
        st.write(response_to_sentiment[response.sentiment])

