import re
from urllib.parse import urlparse

class PhishingDetector:
    def __init__(self):
        # מותגים ישראלים רגישים והדומיינים הרשמיים שלהם
        self.official_brands = {
            "כביש 6": ["kvish6.co.il"],
            "kvish 6": ["kvish6.co.il"],
            "דואר": ["israelpost.co.il"],
            "חברת החשמל": ["iec.co.il"],
            "מס הכנסה": ["gov.il"],
            "ביט": ["bitpay.co.il"],
            "bit": ["bitpay.co.il"],
            "פייפאל": ["paypal.com"],
            "paypal": ["paypal.com"]
        }
        
        self.suspicious_tlds = ['.vip', '.top', '.xyz', '.work', '.info', '.live', '.online', '.site', '.org'] # הוספנו .org כחשוד בהודעות SMS
        self.shorteners = ["bit.ly", "t.co", "tinyurl.com", "rebrand.ly", "cutt.ly", "qrcd.org", "tiny.one"]

    def analyze(self, text, sender_number=""):
        score = 0
        reasons = []
        text_lower = text.lower()
        
        # 1. בדיקת התאמת מותג ללינק (התיקון הכי חשוב!)
        url_match = re.search(r'http[s]?://[^\s]+', text)
        url = url_match.group(0) if url_match else ""
        domain = urlparse(url).netloc.lower() if url else ""

        for brand, official_domains in self.official_brands.items():
            if brand in text_lower:
                # אם המותג מוזכר אבל הלינק לא מכיל את הדומיין הרשמי
                is_official = any(off in domain for off in official_domains)
                if url and not is_official:
                    score += 70
                    reasons.append(f"שימוש בשם המותג '{brand}' עם קישור שאינו האתר הרשמי")

        # 2. זיהוי מילות לחץ ודחיפות ישראליות
        urgency_phrases = ["טיפול משפטי", "חוב", "יתרה פתוחה", "שטרם הוסדרה", "תשלום מיידי", "נחסם", "פעולה נדרשת"]
        for phrase in urgency_phrases:
            if phrase in text:
                score += 25
                reasons.append(f"שימוש בביטוי לחץ/איום: '{phrase}'")
                break

        # 3. ניתוח הקישור
        if url:
            # בדיקת שירותי קיצור (כולל qrcd.org)
            for sh in self.shorteners:
                if sh in domain:
                    score += 35
                    reasons.append(f"שימוש בשירות הסתרת קישורים ({sh})")
            
            # בדיקת סיומות חשודות
            for tld in self.suspicious_tlds:
                if domain.endswith(tld):
                    score += 20
                    reasons.append(f"סיומת דומיין חשודה ({tld})")

        # 4. ניתוח מספר השולח (אם לא ישראלי וההודעה בעברית)
        if sender_number and not sender_number.startswith('whatsapp:+972'):
            if bool(re.search(r'[א-ת]', text)):
                score += 40
                reasons.append("הודעה בעברית ממספר טלפון שאינו ישראלי")

        final_score = min(score, 100)
        return {
            "score": final_score,
            "reasons": reasons,
            "is_dangerous": final_score >= 45 
        }