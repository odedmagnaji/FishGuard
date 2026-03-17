import re
from urllib.parse import urlparse

class PhishingDetector:
    def __init__(self):
        # מותגים ישראליים רגישים והדומיינים הרשמיים שלהם
        self.official_brands = {
            "כביש 6": ["kvish6.co.il"],
            "דואר": ["israelpost.co.il"],
            "חברת החשמל": ["iec.co.il"],
            "ביט": ["bitpay.co.il"],
            "מס הכנסה": ["gov.il"]
        }
        
        # שירותי קיצור לינקים נפוצים (כולל did.li הישראלי)
        self.shorteners = ["did.li", "bit.ly", "t.co", "tinyurl", "qrcd.org", "tiny.one", "short.io"]
        
        # מילון "נורות אדומות" - מילים שמעלות את רמת החשד
        self.red_flags = {
            "מיידי": 20,
            "אזהרה": 20,
            "חוב": 15,
            "הליכים משפטיים": 30,
            "כפל תשלום": 25,
            "השעיה": 20,
            "פעולה נדרשת": 15,
            "נחסם": 20,
            "יתרה פתוחה": 20
        }

    def extract_url(self, text):
        """מזהה קישורים בטקסט גם אם הם ללא http/https"""
        url_pattern = r'(?:https?://)?(?:www\.)?([a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(?:/\S*)?)'
        match = re.search(url_pattern, text)
        return match.group(0) if match else None

    def analyze(self, text, sender_number=""):
        score = 0
        reasons = []
        text_lower = text.lower()
        
        url = self.extract_url(text)
        domain = ""
        if url:
            # הפיכת הקישור לפורמט ש-urlparse מבין כדי לחלץ דומיין
            full_url = url if url.startswith("http") else "http://" + url
            try:
                domain = urlparse(full_url).netloc.lower()
            except:
                domain = ""

        # 1. ניתוח רמת דחיפות (לוגיקה כללית)
        for phrase, points in self.red_flags.items():
            if phrase in text:
                score += points
                reasons.append(f"נמצא ביטוי מחשיד: '{phrase}'")

        # 2. זיהוי התחזות למותג (כביש 6, ביט וכו')
        for brand, official_domains in self.official_brands.items():
            if brand in text:
                if url:
                    is_official = any(off in domain for off in official_domains)
                    if not is_official:
                        score += 65 # ציון גבוה מאוד על חוסר התאמה
                        reasons.append(f"חשד להתחזות: הודעה בשם '{brand}' עם קישור לא רשמי ({domain})")
                else:
                    score += 15 # מותג רגיש מוזכר ללא לינק

        # 3. זיהוי שימוש במקצרי לינקים
        if domain and any(sh in domain for sh in self.shorteners):
            score += 30
            reasons.append(f"שימוש בקיצור דרך ({domain}) להסתרת היעד הסופי")

        # 4. בדיקת מספר השולח (אם ההודעה בעברית והמספר מחו"ל)
        if sender_number and not sender_number.startswith('whatsapp:+972'):
            if bool(re.search(r'[א-ת]', text)):
                score += 40
                reasons.append("הודעה בעברית שהתקבלה ממספר טלפון שאינו ישראלי")

        final_score = min(score, 100)
        return {
            "score": final_score,
            "reasons": reasons,
            "is_dangerous": final_score >= 45 
        }
