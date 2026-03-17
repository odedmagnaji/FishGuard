import os
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from detector import PhishingDetector

app = Flask(__name__)
detector = PhishingDetector()

# פונקציה לשמירת היסטוריית פישינג לניתוח עתידי
def log_suspicious_activity(sender, message, score):
    with open("fishing_logs.txt", "a", encoding="utf-8") as f:
        f.write(f"--- \nSender: {sender}\nRisk: {score}%\nMsg: {message}\n")

@app.route("/whatsapp", methods=['POST'])
def whatsapp_bot():
    incoming_msg = request.values.get('Body', '').strip()
    sender_number = request.values.get('From', '')
    
    resp = MessagingResponse()
    reply = resp.message()
    
    # חילוץ וניתוח
    url = detector.extract_url(incoming_msg)
    analysis = detector.analyze(incoming_msg, sender_number)
    
    # 1. טיפול בהודעת הצטרפות ל-Sandbox
    if "join all-fog" in incoming_msg.lower():
        reply.body("🐟 *FishGuard מחובר ומוכן לעבודה!* 🛡️\nשלחו לי כל הודעה חשודה לבדיקה.")
        return str(resp)

    # 2. נימוסים ושיח חופשי (Fuzzy Greeting Logic)
    greeting_keywords = [
        'היי', 'הי', 'שלום', 'אהלן', 'מה קורה', 'מה נשמע', 'מה איתך', 
        'מה הולך', 'בוקר טוב', 'ערב טוב', 'צהריים טובים', 'hi', 'hello', 'hey'
    ]
    is_greeting = any(greet in incoming_msg.lower() for greet in greeting_keywords)
    
    if is_greeting and not url and len(incoming_msg) < 40:
        reply.body(
            "🐟 **אהלן! אני FishGuard, המגן האישי שלך.**\n\n"
            "נעים להכיר! אם קיבלת הודעה חשודה, SMS מוזר או לינק שאתה לא בטוח לגביו - "
            "פשוט תעביר (Forward) לי את ההודעה ואני אבדוק אותה מיד. 🌊"
        )
        return str(resp)

    # 3. ניתוח הודעה עם קישור
    if url:
        if analysis['is_dangerous']:
            reasons_text = "\n• " + "\n• ".join(analysis['reasons'])
            reply.body(
                f"❌ *זהירות! זוהה ניסיון Fishing* (סיכון: {analysis['score']}%)\n"
                f"{reasons_text}\n\n"
                f"🛑 **המלצה:** אל תלחצו על הקישור ואל תמסרו פרטים!"
            )
            log_suspicious_activity(sender_number, incoming_msg, analysis['score'])
        else:
            reply.body(
                f"✅ **הבדיקה עברה בשלום.**\n"
                f"לא מצאנו סימנים מחשידים מובהקים (ציון סיכון: {analysis['score']}%).\n\n"
                f"💡 תמיד כדאי לוודא שהשולח מוכר לכם."
            )
        return str(resp)

    # 4. ניתוח הודעה ללא קישור אבל עם תוכן מחשיד
    if analysis['score'] > 30:
        reply.body(
            f"🧐 **זיהיתי תוכן מחשיד!**\n"
            f"ההודעה נראית כמו הונאה (ציון חשד: {analysis['score']}%), אבל לא מצאתי בה קישור.\n"
            f"אם יש קישור בהודעה המקורית, שלחו לי אותו כדי שאוכל לתת תשובה סופית."
        )
        return str(resp)

    # 5. הודעה לא מזוהה (Fallback)
    reply.body(
        "🐟 לא הצלחתי להבין את ההודעה או למצוא בה קישור.\n\n"
        "זכרו: אני יודע לנתח הודעות שכוללות כתובות אינטרנט. "
        "אם מדובר ב-SMS חשוד, פשוט תעבירו אותו אלי במלואו."
    )
    return str(resp)

if __name__ == "__main__":
    app.run()
