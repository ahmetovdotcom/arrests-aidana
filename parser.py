import fitz
import re
from utils import clean, normalize_amount, normalize_name, format_amount_with_words, convert_date_format, get_initials, extract_company_core_name


def parse(file_path):
    # Открытие PDF
    doc = fitz.open(file_path)
    full_text = ""
    for page in doc:
        full_text += page.get_text()
    full_text = clean(full_text)

    # Уникальный номер
    register_number_match = re.search(r"Зарегистрировано в реестре за\s*№\s*(\d+)", full_text)
    register_number_match = clean(register_number_match.group(1)) if register_number_match else None

    # Дата составления
    date_created_match = re.search(r'«(\d{1,2})»\s+([а-яА-ЯёЁ]+)\s+(\d{4})г', full_text)
    if date_created_match:
        date_created = f'«{date_created_match.group(1)}» {date_created_match.group(2)} {date_created_match.group(3)}г'
    else:
        date_created = None
        
    # ФИО нотариуса
    notary_fio = re.search(r'Я,\s+([А-ЯӘІҢҒҮҰҚӨЁа-яәіңғүұқөё\s]+?),\s+нотариус', full_text)
    notary_fio = normalize_name(clean(notary_fio.group(1))) if notary_fio else None

    # Лицензия нотариуса
    notary_license = re.search(r'лицензия №(\S+) от (\d{2}\.\d{2}\.\d{4})', full_text)
    notary_license = f"№{notary_license.group(1)} от {notary_license.group(2)}" if notary_license else None

    # ФИО заёмщика
    debtor_fio = re.search(r'с\s+([А-ЯӘІҢҒҮҰҚӨЁа-яәіңғүұқөё\s]+?),\s+\d{2}\.\d{2}\.\d{4}г\.р\.', full_text)
    debtor_fio = normalize_name(clean(debtor_fio.group(1))) if debtor_fio else None

    # ИИН
    iin_match = re.search(r'ИИН\s*[:\-]?\s*(\d{12})', full_text)
    iin = iin_match.group(1) if iin_match else None

    # Юр. лицо с представителем/руководителем
    company_full_match = re.search(
        r'((?:Товарищество с ограниченной ответственностью|Акционерное общество)[^,]+?\((?:руководитель|представитель)\s+[^)]+\))',
        full_text)
    company_with_ceo = clean(company_full_match.group(1)) if company_full_match else None

    # Название юр. лица отдельно (без представителя)
    company_name_match = re.search(
        r'(Товарищество с ограниченной ответственностью|Акционерное общество)\s+["«]?(.*?)["»]?(?=,|\s+\()', full_text)
    company_name = f'{company_name_match.group(1)} "{company_name_match.group(2)}"' if company_name_match else None

    # Тип юр. лица (новое поле)
    company_type = company_name_match.group(1) if company_name_match else None

    # ФИО руководителя или представителя
    ceo = re.search(r'(?:руководитель|представитель)[\s:]+([А-ЯӘІҢҒҮҰҚӨЁа-яәіңғүұқөё\s]+?)[),\.]', full_text)
    ceo = normalize_name(clean(ceo.group(1))) if ceo else None

    # БИН
    bin_number = re.search(r'БИН\s+(\d{12})', full_text)
    bin_number = clean(bin_number.group(1)) if bin_number else None

    # Адрес компании
    company_address_match = re.search(
        r'БИН\s+\d{12},\s+местонахождение:\s+(.*?)(?:КОНТАКТЫ|ИИК|Контакты)',
        full_text, re.DOTALL)
    company_address = clean(company_address_match.group(1)) if company_address_match else None

    # Сумма основного долга
    main_debt = re.search(r'(?:взыскать|взысканию)\s+задолженность.*?(?:на\s+)?сумму\s+([\d\s.,]+)\s*тенге', full_text)
    if not main_debt:
        main_debt = re.search(r'задолженность в сумме\s+([\d\s.,]+)\s*тенге', full_text)
    main_debt_clean = normalize_amount(main_debt.group(1)) if main_debt else None
    main_debt = format_amount_with_words(main_debt_clean)

    # Сумма расходов
    expenses = re.search(r'расходы.*?в сумме\s+([\d\s.,]+)', full_text)
    expenses = normalize_amount(expenses.group(1)) if expenses else None

    # Итого к взысканию
    total = re.search(r'Общая сумма.*?составляет\s+([\d\s.,]+)\s*тенге', full_text)
    total_clean = normalize_amount(total.group(1)) if total else None
    total = format_amount_with_words(total_clean)

    # инициалы 
    debtor_initials = get_initials(debtor_fio)

    birth_date_match = re.search(r"\b\d{2}\.\d{2}\.\d{4}(?=г\.р)", full_text)
    birth_date = clean(birth_date_match.group()) if birth_date_match else None
    

    # Результат
    result = {
        "Зарегистрировано в реестре": register_number_match,
        "Дата составления": date_created,
        "ФИО нотариуса": notary_fio,
        "Лицензия нотариуса": notary_license,
        "ФИО заёмщика": debtor_fio,
        "ФИО заёмщика (инициалы)": debtor_initials,
        "ИИН": iin,
        "Юр. лицо с представителем/руководителем": company_with_ceo,
        "Юр. лицо": company_name,
        "Название компании": extract_company_core_name(company_name),
        "Тип юр. лица": company_type,
        "ФИО представителя": ceo,
        "БИН": bin_number,
        "Адрес компании": company_address,
        "Сумма долга": main_debt,
        "Сумма расходов": expenses,
        "Итого к взысканию": total,
        "Дата рождения": birth_date
    }

    return result

