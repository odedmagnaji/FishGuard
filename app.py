import os
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from detector import PhishingDetector

app = Flask(__name__)
detector = PhishingDetector()

@app.route("/whatsapp", methods=['POST'])
def whatsapp_bot():
    incoming_msg = request.values.get('Body', '').strip()
    sender_number = request.values.get('From', '')
    
    resp = MessagingResponse()
    reply = resp.message()
    
    url = detector.extract_url(incoming_msg)
    analysis = detector.analyze(incoming_msg, sender_number)
    status = analysis['status']

    # 1. נימוסים
    greeting_keywords = ['היי', 'שלום', 'אהלן', 'מה קורה', 'hi']
    if any(greet in incoming_msg.lower() for greet in greeting_keywords) and not url and len(incoming_msg) < 40:
        reply.body("🐟 *אהלן! אני FishGuard.* 🛡️\nשלחו לי הודעה חשודה או קישור ואבדוק אותם בשבילכם.")
        return str(resp)

    # 2. תגובות לפי סטטוס
    if status == "DANGER":
        # אם יש קטגוריה ספציפית (כמו סמים), נשתמש באזהרה שלה
        cat = analysis.get('category_data')
        warning_msg = cat['warning'] if cat else "🛑 מומלץ מאוד לא להיכנס לקישור ולא למסור פרטים!"
        label = cat['label'] if cat else "זהירות! זוהה ניסיון Fishing"
        
        reasons_text = ""
        if analysis['reasons']:
            reasons_text = "\n• " + "\n• ".join(analysis['reasons'])
            
        reply.body(f"❌ *{label}*\n{reasons_text}\n\n{warning_msg}")
        
    elif status == "ALERT":
        cat = analysis['category_data']
        reply.body(f"🟡 *{cat['label']}*\n{cat['warning']}\n\n💡 תמיד כדאי לבדוק מי עומד מאחורי ההצעה.")
        
    elif status == "INFO":
        cat = analysis['category_data']
        reply.body(f"🔵 *{cat['label']}*\n{cat['warning']}")
        
    elif url:
        reply.body(f"✅ *הבדיקה עברה בשלום.*\nהקישור נראה בטוח לשימוש (ציון חשד: {analysis['score']}%).")
        
    else:
        reply.body("🐟 לא זיהיתי קישור או כוונה מיוחדת. אם זו הודעה חשודה, פשוט תעבירו אותה אלי במלואו.")

    return str(resp)

if __name__ == "__main__":
    app.run()
