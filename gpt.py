from openai import OpenAI
from config import OPENAI_API_KEY
import json


client = OpenAI(api_key=OPENAI_API_KEY) 

def extract_notary_data(text: str) -> dict:
    system_prompt = "Твоя задача — найти дату уведомления (date_notification) в тексте. Если она найдена, верни её в формате ДД.ММ.ГГГГ. Если дата не найдена, верни строку ‘сегодня’. Ответ строго в формате Python dict: { 'date_notification': '19.04.2025' } без пояснений и без других полей."

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": text},
        ],
        temperature=0.2,
    )

    content = response.choices[0].message.content.strip()
    try:
        # Пытаемся привести к dict
        data = json.loads(content.replace("'", '"'))
    except json.JSONDecodeError:
        data = {"error": "Не удалось распарсить ответ", "raw": content}
    
    return data