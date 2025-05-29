import requests
from bs4 import BeautifulSoup
import re

def extract_email_from_notary_page(fio: str) -> str | None:
    base_url = "https://enis.kz/NotarySearch/Details/"
    params = {
        "fio": fio,
        "region": "0",
        "city": "",
        "phoneNumber": "",
        "licenseNumber": ""
    }
    
    response = requests.get(base_url, params=params)
    if response.status_code != 200:
        print("Ошибка запроса:", response.status_code)
        return None

    soup = BeautifulSoup(response.text, "html.parser")
    text_only = soup.get_text(separator="\n")
    

    if "Деятельность прекращена!" in text_only:
        return "Деятельность прекращена!"

    # Ищем полный адрес после "Адрес:"
    address_match = re.search(r"Адрес:\s*(.+)", text_only)
    if address_match:
        return address_match.group(1).strip()

    return None