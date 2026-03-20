import os
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from detector import PhishingDetector

app = Flask(__name__)
detector = PhishingDetector()

def log_activity(sender, message, status, score):
    with open("fishing_logs.txt", "a", encoding="utf-8") as f:
        f.write(f"--- \nSender: {sender}\nStatus: {status} ({score}%)\nMsg: {message[:50]}...\n")

@app.route("/whatsapp", methods=['POST'])
def whatsapp_bot():
    incoming_msg = request.values.get('Body', '').strip()
    sender_number = request.values.get('From', '')
    
    resp = MessagingResponse()
    reply = resp.message()
    
    # הפעלת מנוע הניתוח הגנרי
    url = detector.extract_url(incoming_msg)
    analysis = detector.analyze(incoming_msg, sender_number)
    status = analysis['status']

    # 1. נימוסים ושיח חופשי
    greeting_keywords = ['היי', 'שלום', 'אהלן', 'מה קורה', 'מה נשמע', 'hi', 'hello']
    if any(greet in incoming_msg.lower() for greet in greeting_keywords) and not url and len(incoming_msg) < 40:
        reply.body("🐟 *אהלן! אני FishGuard.* 🛡️\nשלחו לי כל הודעה חשודה או קישור שקיבלתם ואבדוק אותם בשבילכם.")
        return str(resp)

    # 2. תגובות לפי רמת סיכון
    if status == "DANGER":
        reasons_text = "\n• " + "\n• ".join(analysis['reasons'])
        reply.body(
            f"❌ *זהירות! זוהה דפוס של הונאה*\n{reasons_text}\n\n"
            f"🛑 **המלצה:** אל תלחצו על הקישור ואל תמסרו פרטים אישיים או כספיים. "
            f"זה נראה כמו ניסיון דייג (Phishing) או עוקץ."
        )
        log_activity(sender_number, incoming_msg, status, analysis['score'])
        
    elif status == "ALERT":
        reasons_text = "\n• " + "\n• ".join(analysis['reasons'])
        reply.body(
            f"🟡 *הודעה חשודה / שיווק אגרסיבי*\n{reasons_text}\n\n"
            f"💡 **שים לב:** זוהתה הודעה ממקור לא מוכר עם מאפיינים שיווקיים/כספיים חשודים. "
            f"מומלץ לבדוק היטב מי עומד מאחורי ההצעה לפני שמתקדמים."
        )
        
    elif url:
        reply.body(
            f"✅ *הבדיקה עברה בשלום.*\nהקישור נראה בטוח לשימוש (ציון חשד נמוך: {analysis['score']}%).\n"
            f"💡 תמיד כדאי להישאר עירניים."
        )
        
    else:
        reply.body(
            "🐟 לא הצלחתי לזהות קישור או כוונה מיוחדת בהודעה.\n"
            "אני יודע לנתח הודעות שכוללות כתובות אינטרנט. אם זו הודעה חשודה, העבירו אותה אלי במלואו."
        )

    return str(resp)

if __name__ == "__main__":
    app.run()
