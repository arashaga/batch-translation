from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import openai
import os
import json
import re
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

load_dotenv()
endpoint = os.getenv('AZURE_OPENAI_ENDPOINT')
api_key = os.getenv('AZURE_OPENAI_API_KEY')
api_version = os.getenv('AZURE_OPENAI_API_VERSION')

logger.info(f"Endpoint: {endpoint}")
logger.info(f"API Key: {'****' if api_key else 'Not set'}")
logger.info(f"API Version: {api_version}")

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
        logger.info(f"Translating text to {language}")
        logger.info(f"Request to OpenAI: {sys_msg}")

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": sys_msg},
                {"role": "user", "content": request.text},
            ],
            temperature=0,
        )

        logger.info(f"OpenAI response: {response}")

        translated_text = response.choices[0].message.content.strip()
        cleaned_text = re.sub(r'```json|```', '', translated_text).strip()

        try:
            translated_json = json.loads(cleaned_text)
        except json.JSONDecodeError:
            logger.error(f"JSON Decode Error: {cleaned_text}")
            raise HTTPException(status_code=500, detail="Invalid JSON format in response")

        return {"translated_text": translated_json}

    except Exception as e:
        logger.error(f"Exception for Arash: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=80)
