import pandas as pd
import requests
import time
import json

API_KEY = "sk-8hPbJO6sgDf3LfOs1b4d01F0A4E848269e1f652130Dc2cD9"  
BASE_URL = "https://api.apiyi.com/v1" 
MODEL = "gpt-3.5-turbo"  # или gpt-4o, если доступно
INPUT_FILE = "goods.xlsx"
OUTPUT_FILE = "goods_with_descriptions.xlsx"
# =============================================

def generate_description(product_name, features):
    prompt = f"Напиши красивое, продающее описание для интернет-магазина для товара '{product_name}'. Характеристики: {features}. Описание должно быть на русском, длиной 3-4 предложения, без воды."
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7
    }
    
    try:
        # Добавляем явный таймаут 30 секунд
        response = requests.post(
            f"{BASE_URL}/chat/completions",
            headers=headers,
            json=data,
            timeout=30
        )
        response.raise_for_status()
        result = response.json()
        description = result['choices'][0]['message']['content'].strip()
        return description
        
    except requests.exceptions.Timeout:
        print(f"Таймаут при запросе для товара {product_name}. Сервер не отвечает.")
        return "Ошибка: таймаут"
    except requests.exceptions.ConnectionError as e:
        print(f"Ошибка соединения для товара {product_name}: {e}")
        return "Ошибка соединения"
    except requests.exceptions.HTTPError as e:
        print(f"HTTP ошибка для товара {product_name}: {e}")
        if response is not None and response.status_code == 429:
            print("Слишком много запросов. Нужно подождать.")
        return f"Ошибка HTTP: {response.status_code if response else 'неизвестно'}"
    except (KeyError, json.JSONDecodeError) as e:
        print(f"Ошибка при разборе ответа для товара {product_name}: {e}")
        if response is not None:
            print("Ответ сервера:", response.text)
        return "Ошибка формата ответа"
    

# --- Основная часть программы ---
print("Загружаю файл...")
try:
    df = pd.read_excel(INPUT_FILE)
except FileNotFoundError:
    print(f"Ошибка: Файл {INPUT_FILE} не найден. Создай его в той же папке, что и скрипт.")
    exit()

# Проверяем, что нужные колонки есть
if 'name' not in df.columns or 'features' not in df.columns:
    print("Ошибка: В файле должны быть колонки 'name' и 'features'")
    exit()

print(f"Начинаю генерацию описаний для {len(df)} товаров...")

# Создаем новую колонку 'description' и заполняем её
descriptions = []
for index, row in df.iterrows():
    print(f"Обрабатываю товар {index+1}: {row['name']}...")
    desc = generate_description(row['name'], row['features'])
    descriptions.append(desc)
    # Небольшая задержка, чтобы не превысить лимиты API
    time.sleep(1.5)  # 1.5 секунды между запросами

df['description'] = descriptions

# Сохраняем результат в новый файл
df.to_excel(OUTPUT_FILE, index=False)
print(f"Готово! Результат сохранен в файл: {OUTPUT_FILE}")