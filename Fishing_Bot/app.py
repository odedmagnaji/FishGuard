from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from detector import PhishingDetector

app = Flask(__name__)
detector = PhishingDetector()

@app.route("/", methods=['GET'])
def home():
    return "<h1>FishGuard Server is Running!</h1>"

@app.route("/whatsapp", methods=['POST'])
def whatsapp_bot():
    # שליפת תוכן ההודעה ומספר השולח (הכרחי לזיהוי קידומות חשודות)
    incoming_msg = request.values.get('Body', '').strip()
    sender_number = request.values.get('From', '') # יחזיר פורמט של whatsapp:+972...
    
    resp = MessagingResponse()
    reply = resp.message()

    # 1. טיפול בהודעת ההצטרפות (join)
    if "join all-fog" in incoming_msg.lower():
        reply.body(
            "🐟 *FishGuard הופעל בהצלחה!* 🛡️\n"
            "--------------------------\n"
            "שמח שהצטרפתם למים הבטוחים שלי! מעכשיו, כל הודעה חשודה, SMS מהבנק או לינק מוזר - פשוט תעבירו (Forward) אלי.\n\n"
            "💡 *איך זה עובד?* אני סורק את הלינקים, בודק את זהות השולח ומחפש סימני התחזות למותגים כמו כביש 6, דואר ישראל ועוד."
        )
        return str(resp)

    # 2. סינון מילות נימוס או הודעות קצרות מדי
    greetings = ['היי', 'שלום', 'מה קורה', 'מה נשמע', 'hi', 'hello']
    if any(word == incoming_msg.lower() for word in greetings) or len(incoming_msg) < 3:
        reply.body("🐟 הכל דבש! כדי שאוכל לעזור, שלחו לי הודעה שחשודה כפישינג (הודעה הכוללת קישור).")
        return str(resp)

    # 3. הרצת הניתוח המשודרג (כולל בדיקת התאמת מותג ללינק וניתוח מספר השולח)
    analysis = detector.analyze(incoming_msg, sender_number)
    
    if analysis['is_dangerous']:
        reasons_formatted = "\n• " + "\n• ".join(analysis['reasons'])
        response_text = (
            f"❌ *זהירות! זוהה ניסיון הונאה* ❌\n"
            f"--------------------------\n"
            f"רמת סיכון: *{analysis['score']}%*\n\n"
            f"🔍 *למה FishGuard חושד?*{reasons_formatted}\n\n"
            f"🛑 *המלצת אבטחה:* אל תלחצו על הקישור, אל תמסרו פרטים אישיים ומחקו את ההודעה."
        )
    else:
        # הודעה רגועה יותר עבור קישורים שנראים תקינים
        response_text = (
            f"✅ *הבדיקה עברה בשלום*\n"
            f"--------------------------\n"
            f"לא מצאנו סימנים מחשידים מובהקים בהודעה זו (רמת סיכון: {analysis['score']}%).\n\n"
            f"💡 *טיפ:* גם במים שקטים, תמיד כדאי להיות עירניים ולוודא מי השולח האמיתי."
        )

    reply.body(response_text)
    return str(resp)

if __name__ == "__main__":
    app.run()