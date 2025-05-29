from num2words import num2words
from datetime import datetime, timedelta
import re
import os
import json



MONTHS = {
    'января': '01', 'февраля': '02', 'марта': '03', 'апреля': '04',
    'мая': '05', 'июня': '06', 'июля': '07', 'августа': '08',
    'сентября': '09', 'октября': '10', 'ноября': '11', 'декабря': '12'
}

def clean(text):
    return re.sub(r'\s+', ' ', text.strip())

def normalize_amount(amount_str):
    """
    Приводит строку с суммой к строке.
    Убирает пробелы, заменяет запятые на точки.
    Если есть копейки — сохраняет их, иначе возвращает только целую часть.
    """
    if not amount_str:
        return None
    cleaned = amount_str.replace(' ', '').replace(',', '.')
    try:
        amount = float(cleaned)
        if amount.is_integer():
            return str(int(amount))  # без копеек
        else:
            return str(amount)  # с копейками
    except ValueError:
        return None

def normalize_name(name):
    return ' '.join(word.capitalize() for word in name.split())

def format_amount_with_words(amount_str):
    """
    Преобразует сумму в строку вида:
    "123456.78 тенге (сто двадцать три тысячи четыреста пятьдесят шесть тенге 78 тиынов)"
    """
    if not amount_str:
        return None
    try:
        parts = amount_str.split('.')
        tenge = int(parts[0])
        tiyn = int(parts[1]) if len(parts) > 1 else 0

        tenge_words = num2words(tenge, lang='ru')
        if tiyn > 0:
            tiyn_words = num2words(tiyn, lang='ru')
            return f"{amount_str} тенге ({tenge_words} тенге {tiyn_words} тиынов)"
        else:
            return f"{amount_str} тенге ({tenge_words} тенге)"
    except:
        return f"{amount_str} тенге"

def convert_date_format(day, month_word, year):
    month = MONTHS.get(month_word.lower())
    if not month:
        return f"{day} {month_word} {year}"  # fallback
    return f"{day.zfill(2)}.{month}.{year}"


def get_initials(full_name):
    if not full_name:
        return None
    parts = full_name.split()
    if len(parts) >= 3:
        return f"{parts[0]} {parts[1][0]}.{parts[2][0]}."
    elif len(parts) == 2:
        return f"{parts[0]} {parts[1][0]}."
    return full_name


def extract_company_core_name(company_full_name):
    if not company_full_name:
        return None
    # Удаляем юр. форму и всё до неё
    company_core = re.sub(
        r'^(Товарищество с ограниченной ответственностью|Акционерное общество)\s+', '', company_full_name
    )
    # Удаляем "Микрофинансовая организация" и всё до неё
    company_core = re.sub(r'^"?Микрофинансовая организация"?\s+', '', company_core)
    # Удаляем все кавычки
    company_core = company_core.replace('"', '').replace('«', '').replace('»', '')
    return company_core.strip()


USERS_FILE = "allowed_users.json"

def load_users():
    if not os.path.exists(USERS_FILE):
        return []
    with open(USERS_FILE, "r") as f:
        return json.load(f)

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f)



def add_user(user_id, first_name="", last_name="", username="", days=0):
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, "w") as f:
            json.dump({}, f)

    with open(USERS_FILE, "r") as f:
        users = json.load(f)

    access_until = None
    if days > 0:
        access_until = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")

    users[str(user_id)] = {
        "first_name": first_name,
        "last_name": last_name,
        "username": username,
        "access_until": access_until
    }

    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)

def remove_user(user_id):
    users = get_user_list()
    users.pop(str(user_id), None)
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)

def get_user_list():
    if not os.path.exists(USERS_FILE):
        return {}

    with open(USERS_FILE, "r") as f:
        return json.load(f)

def is_user_allowed(user_id):
    users = get_user_list()
    user = users.get(str(user_id))
    if not user:
        return False

    access_until = user.get("access_until")
    if access_until:
        try:
            return datetime.now().date() <= datetime.strptime(access_until, "%Y-%m-%d").date()
        except:
            return False
    return True


