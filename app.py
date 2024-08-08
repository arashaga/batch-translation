import streamlit as st
import requests
import json

# Function to get translated text from the URL
def get_translated_text(input_text):
    url = "http://127.0.0.1:8000/translate/"
    payload = {"text": input_text}
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        try:
            return response.json().get('translated_text')
        except json.JSONDecodeError:
            st.error("Error decoding JSON response")
            st.text(response.text)  # Debug: Show the raw response text
            return None
    else:
        st.error(f"Failed to fetch translations. Status code: {response.status_code}")
        st.text(response.text)  # Debug: Show the raw response text
        return None

# Streamlit app
st.title("Translation App")

# Text input for user to enter text to be translated
input_text = st.text_area("Enter text to translate:", height=200)

# Button to trigger translation
if st.button("Translate"):
    if input_text:
        translated_text = get_translated_text(input_text)
        if translated_text:
            # Display each language in its own text area
            for language, text in translated_text.items():
                st.text_area(label=language, value=text, height=100)
        else:
            st.error("No translation received.")
    else:
        st.warning("Please enter text to translate.")
