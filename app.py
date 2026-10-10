import os
import json
import streamlit as st
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")
MODEL = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")

client = genai.Client(api_key=API_KEY)


def ask_llm(prompt: str, as_json: bool = False) -> str:
    """One reusable function for every AI call in your app."""
    config = types.GenerateContentConfig(
        response_mime_type="application/json" if as_json else "text/plain"
    )
    response = client.models.generate_content(
        model=MODEL, contents=prompt, config=config
    )
    return response.text


st.set_page_config(page_title="Study Helper", page_icon="📚")
st.title(" AI Study Helper")
st.write("Paste your notes and get a summary, key points and a quiz.")

notes = st.text_area("Your notes", height=250)

if st.button("Generate") and notes.strip():
    with st.spinner("Thinking..."):
        prompt = f"""You are a helpful study assistant.
From the notes below, return ONLY valid JSON in this exact shape:
{{
  "summary": "3-4 sentence summary",
  "key_points": ["point 1", "point 2", "point 3"],
  "quiz": [
    {{"question": "...", "answer": "..."}},
    {{"question": "...", "answer": "..."}},
    {{"question": "...", "answer": "..."}}
  ]
}}

Notes:
{notes}
"""
        try:
            data = json.loads(ask_llm(prompt, as_json=True))
        except Exception as e:
            st.error(f"Something went wrong: {e}")
            st.stop()

    st.subheader("Summary")
    st.write(data["summary"])

    st.subheader("Key points")
    for p in data["key_points"]:
        st.markdown(f"- {p}")

    st.subheader("Quiz")
    for i, q in enumerate(data["quiz"], 1):
        with st.expander(f"Q{i}. {q['question']}"):
            st.write(q["answer"])