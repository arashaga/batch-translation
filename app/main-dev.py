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

@app.post("/translate/")
async def translate_text(request: TranslationRequest):
    sys_msg = '''You are a helpful assistant whose role is to translate English text to the languages below:
    1- French
    2- Spanish
    3- Italian
    4- German
    5- Portuguese
    6- Russian
    7- Chinese
    8- Japanese
    9- Korean
    10- Arabic

    Please provide the translations in a valid JSON format like this:
    {
        "French": "translation",
        "Spanish": "translation",
        "Italian": "translation",
        "German": "translation",
        "Portuguese": "translation",
        "Russian": "translation",
        "Chinese": "translation",
        "Japanese": "translation",
        "Korean": "translation",
        "Arabic": "translation"
    }
    '''

    try:
        response = client.chat.completions.create(
            model="gpt-4",
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
            raise HTTPException(status_code=500, detail="Invalid JSON format in response")

        return {"translated_text": translated_json}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
