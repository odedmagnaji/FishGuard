import re
from urllib.parse import urlparse

class FishingDetector:
    def __init__(self):
        # מותגים רשמיים - לזיהוי התחזות ישירה
        self.official_brands = {
            "כביש 6": ["kvish6.co.il"],
            "דואר": ["israelpost.co.il"],
            "חברת החשמל": ["iec.co.il"],
            "ביט": ["bitpay.co.il"],
            "מס הכנסה": ["gov.il"]
        }
        
        # רשימת מקצרי קישורים וסיומות "שיווקיות" חשודות
        self.shorteners = [
            "did.li", "bit.ly", "t.co", "tinyurl", "qrcd.org", "f4u.biz", 
            "lik5.vip", "1d.is", "vip", "shop", "biz", "online", "weedil"
        ]

        # תבנית א: מילים שיווקיות/כספיות אגרסיביות (הבטחות לרווח)
        self.marketing_buzzwords = [
            "החזר", "כסף", "₪", "ש\"ח", "בדיקה", "זכאות", "ללא עלות", "ללא תשלום", 
            "הלוואה", "אשראי", "ריבית", "השקעה", "נדל\"ן", "דירה", "רווח", "תשואה",
            "הזדמנות", "בלעדי", "מבצע", "מתנה", "בונוס", "הגרלה", "פרס", "שקיות"
        ]

        # תבנית ב: מילים שמעידות על לחץ ודחיפות (שיטות דייג פסיכולוגי)
        self.urgency_buzzwords = [
            "מיידי", "מהר", "תמהרו", "עכשיו", "אחרון", "מוגבל", "דחוף", 
            "אזהרה", "חוב", "עיקול", "משפטי", "חובה", "מיידית"
        ]

    def extract_url(self, text):
        """מזהה כתובות אינטרנט גם ללא http/https"""
        url_pattern = r'(?:https?://)?(?:www\.)?([a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(?:/\S*)?)'
        match = re.search(url_pattern, text)
        return match.group(0) if match else None

    def analyze(self, text, sender_number=""):
        score = 0
        reasons = []
        text_lower = text.lower()
        url = self.extract_url(text)
        
        # 1. ניתוח תוכן גנרי (זיהוי "ריח" של הונאה)
        found_marketing = [word for word in self.marketing_buzzwords if word in text]
        if len(found_marketing) >= 2:
            score += 35
            reasons.append(f"זוהה דפוס שיווקי/כספי אגרסיבי ({', '.join(found_marketing[:2])})")

        # 2. ניתוח לחץ ודחיפות
        found_urgency = [word for word in self.urgency_buzzwords if word in text]
        if found_urgency:
            score += 25
            reasons.append("שימוש במילות לחץ או דחיפות פסיכולוגית")

        # 3. זיהוי מספרים וסכומים גבוהים
        if re.search(r'\d{3,}', text):
            score += 15
            reasons.append("הודעה הכוללת סכומי כסף או מספרים גבוהים")

        # 4. ניתוח הקישור (ה"חכה")
        if url:
            full_url = url if url.startswith("http") else "http://" + url
            try:
                domain = urlparse(full_url).netloc.lower()
            except:
                domain = ""
            
            # קישור מקוצר בשילוב תוכן שיווקי = חשד גבוה
            if any(sh in domain for sh in self.shorteners):
                score += 35
                reasons.append(f"שימוש בקישור מקוצר/חשוד להסתרת היעד ({domain})")
            
            # בדיקת התחזות למותגים (למשל "דואר" עם לינק לא רשמי)
            for brand, official_domains in self.official_brands.items():
                if brand in text:
                    if not any(off in domain for off in official_domains):
                        score += 60
                        reasons.append(f"חשד להתחזות ל-{brand} (הקישור אינו מוביל לאתר הרשמי)")

        # 5. בדיקת שולח (מספר זר ששולח עברית שיווקית)
        if sender_number and not sender_number.startswith('whatsapp:+972'):
            if len(found_marketing) > 0:
                score += 30
                reasons.append("הודעה שיווקית בעברית שהתקבלה ממספר שאינו ישראלי")

        # קביעת סטטוס סופי
        status = "SAFE"
        if score >= 60:
            status = "DANGER"
        elif score >= 35:
            status = "ALERT"
        
        return {
            "status": status,
            "score": min(score, 100),
            "reasons": list(set(reasons))
        }
