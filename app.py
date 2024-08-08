import streamlit as st
import requests
from sqlalchemy import create_engine, Column, String, Integer, DateTime, MetaData, Table, inspect
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import select
from datetime import datetime

# SQLAlchemy setup
DATABASE_URL = "sqlite:///translations.db"  # Example using SQLite
engine = create_engine(DATABASE_URL)
metadata = MetaData()

# Define the translations table
translations_table = Table(
    'translations', metadata,
    Column('id', Integer, primary_key=True),
    Column('project', String),
    Column('language', String),
    Column('translation', String),
    Column('date_added', DateTime)
)

# Create the table if it does not exist
inspector = inspect(engine)
if not inspector.has_table('translations'):
    metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()

# Function to save translation to the database
def save_translation(project, language, translation):
    insert_stmt = translations_table.insert().values(
        project=project,
        language=language,
        translation=translation,
        date_added=datetime.now()
    )
    session.execute(insert_stmt)
    session.commit()

# Function to update translation in the database
def update_translation(project, language, translation):
    update_stmt = translations_table.update().where(
        (translations_table.c.project == project) & 
        (translations_table.c.language == language)
    ).values(
        translation=translation,
        date_added=datetime.now()
    )
    session.execute(update_stmt)
    session.commit()

# Function to get saved translation from the database
def get_saved_translation(project, language):
    query = select(translations_table.c.translation).where(
        (translations_table.c.project == project) & 
        (translations_table.c.language == language)
    )
    result = session.execute(query).fetchone()
    return result[0] if result else None

# Function to get all translations for a project
def get_project_translations(project):
    query = select(translations_table.c.language, translations_table.c.translation).where(
        translations_table.c.project == project
    )
    result = session.execute(query).fetchall()
    return result

# Function to get translated text for a specific language from the URL
def get_translated_text(input_text, language):
    url = f"http://127.0.0.1:8000/translate/{language}/"
    payload = {"text": input_text}
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        try:
            translation = response.json().get('translated_text')
            if isinstance(translation, dict):
                return translation.get(language)
            return translation
        except ValueError:
            st.error("Error decoding JSON response")
            st.text(response.text)  # Debug: Show the raw response text
            return None
    else:
        st.error(f"Failed to fetch translation for {language}. Status code: {response.status_code}")
        st.text(response.text)  # Debug: Show the raw response text
        return None

# Streamlit app
st.title("Translation App")

# Select page
page = st.sidebar.selectbox("Select Page", ["Translate", "View Projects"])

if page == "Translate":
    # Initialize session state
    if 'translations' not in st.session_state:
        st.session_state.translations = {}

    # Initialize modified languages state
    if 'modified_languages' not in st.session_state:
        st.session_state.modified_languages = {}

    # Project name input
    project_name = st.text_input("Enter project name:")

    # Text input for user to enter text to be translated
    input_text = st.text_area("Enter text to translate:", height=200)

    # Languages list
    languages = ["French", "Spanish", "Italian", "German", "Portuguese", "Russian", "Chinese", "Japanese", "Korean", "Arabic"]

    # Button to trigger translation
    if st.button("Translate"):
        if project_name and input_text:
            st.session_state.translations = {}
            st.session_state.modified_languages = {}  # Reset modified languages
            
            progress_bar = st.progress(0)
            progress_step = 1 / len(languages)
            current_progress = 0
            
            status_text = st.empty()
            
            for idx, lang in enumerate(languages):
                status_text.text(f"Translating in {lang}...")
                translation = get_translated_text(input_text, lang)
                if translation:
                    st.session_state.translations[lang] = translation
                    save_translation(project_name, lang, translation)
                else:
                    st.error(f"No translation received for {lang}.")
                
                current_progress += progress_step
                progress_bar.progress(current_progress)
            
            status_text.text("Translation complete.")
            progress_bar.progress(1.0)  # Ensure the progress bar reaches 100% after completion
        else:
            st.warning("Please enter both project name and text to translate.")

    # Sidebar for language selection
    if st.session_state.translations:
        st.sidebar.title("Select Language")
        selected_language = st.sidebar.radio("Languages", list(st.session_state.translations.keys()))

        # Check if the translation is already saved
        saved_translation = get_saved_translation(project_name, selected_language)

        # Display the translation for the selected language
        st.subheader(f"Translation in {selected_language}")
        if saved_translation:
            translation_text = saved_translation
        else:
            translation_text = st.session_state.translations[selected_language]

        label_text = selected_language
        if selected_language in st.session_state.modified_languages:
            label_text = f"{selected_language} **:green[(Modified)]**"

        updated_translation = st.text_area(label=label_text, value=translation_text, height=200, key=selected_language)

        if st.button("Save Translation"):
            if saved_translation:
                update_translation(project_name, selected_language, updated_translation)
                st.success(f"Translation in {selected_language} updated successfully.")
            else:
                save_translation(project_name, selected_language, updated_translation)
                st.success(f"Translation in {selected_language} saved successfully.")
            st.session_state.modified_languages[selected_language] = updated_translation

elif page == "View Projects":
    st.header("View Project Translations")

    # Retrieve list of projects
    projects_query = select(translations_table.c.project).distinct()
    projects = [row[0] for row in session.execute(projects_query).fetchall()]

    selected_project = st.selectbox("Select Project", projects)

    if selected_project:
        translations = get_project_translations(selected_project)
        for language, translation in translations:
            st.subheader(f"Language: {language}")
            st.text_area(label=f"{language} Translation", value=translation, height=200, key=f"{selected_project}_{language}")
