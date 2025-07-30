

import os
from flask import Flask, request
from flask_cors import CORS
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
from ai_gemini import generate_sql_from_message
from database import run_sql_query
from dotenv import load_dotenv

load_dotenv()


app = Flask(__name__)
CORS(app)

# Twilio REST API kimlik bilgileri .env'den alınır
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID").replace('"','').strip()
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN").replace('"','').strip()
TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER", "whatsapp:+YOUR_TWILIO_NUMBER").replace('"','').strip()
client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# SQL Server bağlantısı
conn_str = (
    'DRIVER={ODBC Driver 17 for SQL Server};'
    'SERVER=localhost\\SQLEXPRESS;'
    'DATABASE=AdventureWorks2022;'
    'Trusted_Connection=yes;'
)

@app.route("/", methods=["GET"])
def home():
    return "Bot başarıyla çalışıyor!"


@app.route("/webhook", methods=["POST"])
def whatsapp_webhook():
    import traceback
    try:
        message = request.form.get("Body")
        from_number = request.form.get("From")

        print(f"Gelen mesaj: {message} - Gönderen: {from_number}")

        twilio_response = MessagingResponse()

        if not message:
            twilio_response.message("Mesaj alınamadı.")
            return str(twilio_response)

        # SQL sorgusunu üret
        sql = generate_sql_from_message(message)
        print("AI tarafından üretilen SQL:", sql)

        if sql.strip().lower() == "yeterli bilgi yok":
            twilio_response.message("SQL sorgusu üretmek için yeterli bilgi yok.")
            return str(twilio_response)

        try:
            # SQL sorgusunu çalıştır
            result = run_sql_query(sql, conn_str)
            print("SQL sonucu:", result)

            if isinstance(result, list) and result:
                table_name = sql.split("FROM")[1].split()[0] if "FROM" in sql else "UnknownTable"
                formatted_rows = "\n\n".join([
                    "\n".join([f"{k}: {str(v)}" for k, v in row.items()])
                    for row in result
                ])
                response_text = f" *Tablo: {table_name}*\n\n{formatted_rows}"
            else:
                response_text = "Veri bulunamadı."

        except Exception as e:
            print("Hata oluştu:", e)
            response_text = f"Hata oluştu:\n{str(e)}"


        # Mesaj uzunluğunu kontrol et ve parçala
        MAX_MSG_LENGTH = 1600


        def split_message(text, max_length, header_len=10):
            # Her parça başlıkla birlikte max_length'i aşmaz!
            chunk_size = max_length - header_len
            return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]


        if len(response_text) > MAX_MSG_LENGTH:
            # Maksimum başlık uzunluğunu 10 karakter olarak alıyoruz 
            parts = split_message(response_text, MAX_MSG_LENGTH, header_len=10)
            total = len(parts)
            
            first_part = f"(1/{total})\n{parts[0]}"
            twilio_response.message(first_part)
            client.messages.create(
                body=first_part,
                from_=TWILIO_WHATSAPP_NUMBER,
                to=from_number
            )
            # Diğer parçaları Twilio REST API ile gönder
            for idx, part in enumerate(parts[1:], 2):
                client.messages.create(
                    body=f"({idx}/{total})\n{part}",
                    from_=TWILIO_WHATSAPP_NUMBER,
                    to=from_number
                )
        else:
            twilio_response.message(response_text)

        return str(twilio_response)
    except Exception as e:
        
        tb = traceback.format_exc()
        print("GENEL HATA:\n", tb)
        return f"GENEL HATA:\n{tb}", 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
