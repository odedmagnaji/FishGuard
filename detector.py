import re
from urllib.parse import urlparse

class PhishingDetector:
    def __init__(self):
        # מותגים רשמיים (נשאר לזיהוי התחזות ישירה)
        self.official_brands = {
            "כביש 6": ["kvish6.co.il"], "דואר": ["israelpost.co.il"],
            "חברת החשמל": ["iec.co.il"], "ביט": ["bitpay.co.il"], "מס הכנסה": ["gov.il"]
        }
        
        self.shorteners = ["did.li", "bit.ly", "t.co", "tinyurl", "qrcd.org", "f4u.biz", "lik5.vip", "1d.is", "vip", "shop", "biz"]

        # 1. מילים שמעידות על "הצעה מפתה מדי" או שיווק אגרסיבי
        self.marketing_buzzwords = [
            "החזר", "כסף", "₪", "ש\"ח", "בדיקה", "זכאות", "ללא עלות", "ללא תשלום", 
            "הלוואה", "אשראי", "ריבית", "השקעה", "נדל\"ן", "דירה", "רווח", "תשואה",
            "הזדמנות", "בלעדי", "מבצע", "מתנה", "בונוס", "הגרלה", "פרס"
        ]

        # 2. מילים שמעידות על לחץ ודחיפות
        self.urgency_buzzwords = [
            "מיידי", "מהר", "תמהרו", "עכשיו", "אחרון", "מוגבל", "דחוף", "אזהרה", "חוב", "עיקול", "משפטי"
        ]

    def extract_url(self, text):
        url_pattern = r'(?:https?://)?(?:www\.)?([a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(?:/\S*)?)'
        match = re.search(url_pattern, text)
        return match.group(0) if match else None

    def analyze(self, text, sender_number=""):
        score = 0
        reasons = []
        text_lower = text.lower()
        url = self.extract_url(text)
        
        # --- שלב א: ניתוח תוכן גנרי ---
        
        # חיפוש מילים שיווקיות/כספיות
        found_marketing = [word for word in self.marketing_buzzwords if word in text]
        if len(found_marketing) >= 2:
            score += 30
            reasons.append(f"זוהתה תבנית של הצעה שיווקית/כספית ({', '.join(found_marketing[:2])})")

        # חיפוש מילות לחץ
        found_urgency = [word for word in self.urgency_buzzwords if word in text]
        if found_urgency:
            score += 25
            reasons.append("שימוש במילות לחץ או דחיפות")

        # חיפוש סכומי כסף (מספרים גדולים)
        if re.search(r'\d{3,}', text):
            score += 15
            reasons.append("הודעה הכוללת סכומים או מספרים גבוהים")

        # --- שלב ב: ניתוח הקישור והשולח ---

        if url:
            full_url = url if url.startswith("http") else "http://" + url
            try: domain = urlparse(full_url).netloc.lower()
            except: domain = ""
            
            # אם יש לינק מקוצר + תוכן שיווקי = חשד גבוה מאוד
            if any(sh in domain for sh in self.shorteners):
                score += 35
                reasons.append("שימוש בקישור מקוצר/חשוד להסתרת היעד")
            
            # בדיקת התחזות למותגים
            for brand, official_domains in self.official_brands.items():
                if brand in text:
                    if not any(off in domain for off in official_domains):
                        score += 50
                        reasons.append(f"חשד להתחזות ל-{brand}")

        # --- שלב ג: הצלבת נתונים ---
        # אם זה מספר לא מוכר (מחוץ לישראל) עם עברית שיווקית
        if sender_number and not sender_number.startswith('whatsapp:+972'):
            if len(found_marketing) > 0:
                score += 30
                reasons.append("הודעה שיווקית בעברית ממספר שאינו ישראלי")

        # קביעת סטטוס לפי ציון מצטבר
        status = "SAFE"
        if score >= 60: status = "DANGER"
        elif score >= 35: status = "ALERT"
        
        return {
            "status": status,
            "score": min(score, 100),
            "reasons": reasons
        }
