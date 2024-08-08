import streamlit as st
import requests
from sqlalchemy import create_engine, Column, String, Integer, MetaData, Table
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import select

# SQLAlchemy setup
DATABASE_URL = "sqlite:///translations.db"  # Example using SQLite
engine = create_engine(DATABASE_URL)
metadata = MetaData()

translations_table = Table(
    'translations', metadata,
    Column('id', Integer, primary_key=True),
    Column('language', String),
    Column('translation', String)
)

metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

# Function to save translation to the database
def save_translation(language, translation):
    insert_stmt = translations_table.insert().values(language=language, translation=translation)
    session.execute(insert_stmt)
    session.commit()

# Function to update translation in the database
def update_translation(language, translation):
    update_stmt = translations_table.update().where(translations_table.c.language == language).values(translation=translation)
    session.execute(update_stmt)
    session.commit()

# Function to get saved translation from the database
def get_saved_translation(language):
    query = select(translations_table.c.translation).where(translations_table.c.language == language)
    result = session.execute(query).fetchone()
    return result[0] if result else None

# Function to get translated text from the URL
def get_translated_text(input_text):
    url = "http://127.0.0.1:8000/translate"
    payload = {"text": input_text}
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        try:
            return response.json().get('translated_text')
        except ValueError:
            st.error("Error decoding JSON response")
            st.text(response.text)  # Debug: Show the raw response text
            return None
    else:
        st.error(f"Failed to fetch translations. Status code: {response.status_code}")
        st.text(response.text)  # Debug: Show the raw response text
        return None

# Streamlit app
st.title("Translation App")

# Initialize session state
if 'translations' not in st.session_state:
    st.session_state.translations = {}

# Initialize saved languages state
if 'saved_languages' not in st.session_state:
    st.session_state.saved_languages = {}

# Text input for user to enter text to be translated
input_text = st.text_area("Enter text to translate:", height=200)

# Button to trigger translation
if st.button("Translate"):
    if input_text:
        st.session_state.translations = get_translated_text(input_text)
        st.session_state.saved_languages = {}  # Reset saved languages
        if not st.session_state.translations:
            st.error("No translation received.")
    else:
        st.warning("Please enter text to translate.")

# Sidebar for language selection
if st.session_state.translations:
    st.sidebar.title("Select Language")
    selected_language = st.sidebar.radio("Languages", list(st.session_state.translations.keys()))

    # Check if the translation is already saved
    saved_translation = get_saved_translation(selected_language)

    # Display the translation for the selected language
    st.subheader(f"Translation in {selected_language}")
    if saved_translation:
        translation_text = saved_translation
        label_text = f"{selected_language} **:green[(Saved)]**"
        st.session_state.saved_languages[selected_language] = translation_text
    else:
        translation_text = st.session_state.translations[selected_language]
        label_text = selected_language

    updated_translation = st.text_area(label=label_text, value=translation_text, height=200, key=selected_language)

    if updated_translation != translation_text:
        if saved_translation:
            update_translation(selected_language, updated_translation)
            st.success(f"Translation in {selected_language} updated successfully.")
        else:
            save_translation(selected_language, updated_translation)
            st.success(f"Translation in {selected_language} saved successfully.")
        st.session_state.saved_languages[selected_language] = updated_translation
