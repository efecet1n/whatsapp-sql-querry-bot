# ai_gemini.py
import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

GEMINI_MODEL = "gemini-2.5-flash-lite"
GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={API_KEY}"

def generate_sql_from_message(message):
    
    prompt = f"""
You are an SQL expert. Generate Microsoft SQL Server (T-SQL) queries for the AdventureWorks2022 database.

Rules:

    Generate a valid T-SQL query based on the user's input in Turkish.

    Translate any Turkish table or column names into their corresponding English names from the AdventureWorks2022 database.

    Use full schema names for all table and column references: Schema.Table.Column (e.g., Person.PersonPhone.PhoneNumber).

    Return only the SQL query. Do not include explanations, comments, or additional text.

    If a meaningful query cannot be generated, return only this: Yeterli bilgi yok

    All table and column names must be in English.

    Ensure the generated SQL query is syntactically correct and executable.

    Make sure the order of queries containing DISTINCT and TOP is correct.

    Example queries:
    SELECT DISTINCT TOP 10 ... FROM ...;
    SELECT TOP 5 ... ORDER BY ... DESC;
    SELECT ... FROM ... WHERE YEAR(...) = 2005 ORDER BY ... ASC;
    SELECT ..., COUNT(*) FROM ... GROUP BY ... HAVING COUNT(*) > 10;
    SELECT TOP 3 ... FROM ... WHERE ... > 100 ORDER BY ... DESC;
    SELECT DISTINCT ... FROM ...;
    SELECT ..., SUM(...) FROM ... JOIN ... ON ... = ... GROUP BY ...;


User Message:
Mesaj: "{message}"
"""
    body = {
        "contents": [
            {
                "parts": [{"text": prompt}],
                "role": "user"
            }
        ]
    }

    
    response = requests.post(GEMINI_API_URL, json=body)

    
    if response.status_code == 200:
        candidates = response.json().get("candidates", [])
        if candidates:
            output = candidates[0]["content"]["parts"][0]["text"]
            return output.strip().replace("```sql", "").replace("```", "").strip()
        else:
            return "Gemini yanıt vermedi."
    else:
        print("Hata:", response.text)
        return "Gemini API hatası"
