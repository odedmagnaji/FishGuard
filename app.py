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

    # נימוסים
    greeting_keywords = ['היי', 'שלום', 'אהלן', 'מה קורה', 'hi']
    if any(greet in incoming_msg.lower() for greet in greeting_keywords) and not url and len(incoming_msg) < 40:
        reply.body("🐟 *אהלן! אני FishGuard.* 🛡️\nשלחו לי הודעה חשודה או קישור ואבדוק אותם.")
        return str(resp)

    # לוגיקת תגובה משופרת
    if status == "DANGER":
        cat = analysis.get('category_data')
        # אם זו קטגוריה מסוכנת (הלוואה/סמים/התחזות)
        label = cat['label'] if cat else "❌ זהירות! זוהה ניסיון Fishing"
        warning_msg = cat['warning'] if cat else "🛑 אל תלחצו על הקישור ואל תמסרו פרטים!"
        
        reasons_text = ""
        if analysis['reasons']:
            reasons_text = "\n• " + "\n• ".join(analysis['reasons'])
            
        reply.body(f"{label}\n{reasons_text}\n\n{warning_msg}")
        
    elif status == "ALERT":
        cat = analysis['category_data']
        reply.body(f"🟡 *{cat['label']}*\n{cat['warning']}\n\n💡 מומלץ לבדוק היטב מי עומד מאחורי ההודעה.")
        
    elif status == "INFO":
        cat = analysis['category_data']
        reply.body(f"🔵 *{cat['label']}*\n{cat['warning']}")
        
    elif url:
        reply.body(f"✅ *הבדיקה עברה בשלום.*\nהקישור נראה בטוח (ציון חשד: {analysis['score']}%).")
        
    else:
        reply.body("🐟 לא זיהיתי קישור או כוונה מיוחדת. אם זו הודעה חשודה, העבירו אותה אלי במלואו.")

    return str(resp)

if __name__ == "__main__":
    app.run()
