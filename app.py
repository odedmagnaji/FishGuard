@app.route("/whatsapp", methods=['POST'])
def whatsapp_bot():
    incoming_msg = request.values.get('Body', '').strip()
    sender_number = request.values.get('From', '')
    resp = MessagingResponse(); reply = resp.message()
    
    url = detector.extract_url(incoming_msg)
    analysis = detector.analyze(incoming_msg, sender_number)
    
    if analysis['status'] == "DANGER":
        reasons = "\n• " + "\n• ".join(analysis['reasons'])
        reply.body(f"❌ *זהירות! זוהה דפוס של הונאה*\n{reasons}\n\n🛑 **המלצה:** אל תלחצו על הקישור ואל תמסרו פרטים אישיים או כספיים. זה נראה כמו ניסיון דייג (Phishing) או עוקץ.")
        
    elif analysis['status'] == "ALERT":
        reasons = "\n• " + "\n• ".join(analysis['reasons'])
        reply.body(f"🟡 *הודעה חשודה / שיווק אגרסיבי*\n{reasons}\n\n💡 **שים לב:** זוהתה הודעה שיווקית ממקור לא מוכר. מומלץ לבדוק היטב מי עומד מאחורי ההצעה לפני שמתקדמים.")
        
    elif url:
        reply.body(f"✅ *הבדיקה עברה בשלום.*\nהקישור נראה בטוח לשימוש (ציון חשד: {analysis['score']}%).")
        
    # ... (המשך נימוסים ו-fallback כרגיל)
