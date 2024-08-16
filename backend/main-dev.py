from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import openai
import os
import json
import re
from dotenv import load_dotenv

app = FastAPI()

use_azure_active_directory = False

if not use_azure_active_directory:
    load_dotenv()
    endpoint = os.getenv('AZURE_OPENAI_ENDPOINT')
    api_key = os.getenv('AZURE_OPENAI_API_KEY')
    api_version = os.getenv('AZURE_OPENAI_API_VERSION')

    client = openai.AzureOpenAI(
        azure_endpoint=endpoint,
        api_key=api_key,
        api_version=api_version,
    )

class TranslationRequest(BaseModel):
    text: str

supported_languages = [
    "French", "Spanish", "Italian", "German", "Portuguese",
    "Russian", "Chinese", "Japanese", "Korean", "Arabic",
    "Hindi", "Bengali", "Punjabi", "Tamil", "Telugu",
    "Turkish", "Vietnamese", "Thai", "Swedish", "Dutch",
    "Greek", "Hebrew", "Indonesian", "Malay", "Persian"
]

@app.post("/translate/{language}/")
async def translate_text(language: str, request: TranslationRequest):
    if language not in supported_languages:
        raise HTTPException(status_code=400, detail=f"Language '{language}' not found. Supported languages are: {', '.join(supported_languages)}")

    sys_msg = f'''You are a helpful assistant whose role is to translate English text to {language}.

    Please provide the translation in a valid JSON format like this:
    {{
        "{language}": "translation"
    }}
    '''

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": sys_msg},
                {"role": "user", "content": request.text},
            ],
            temperature=0,
        )

        # Clean the response content
        translated_text = response.choices[0].message.content.strip()

        # Use regex to remove unwanted characters
        cleaned_text = re.sub(r'```json|```', '', translated_text).strip()

        # Attempt to load the string as JSON
        try:
            translated_json = json.loads(cleaned_text)
        except json.JSONDecodeError:
            print("JSON Decode Error:", cleaned_text)
            raise HTTPException(status_code=500, detail="Invalid JSON format in response")

        return {"translated_text": translated_json}

    except Exception as e:
        print("Exception:", str(e))
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
