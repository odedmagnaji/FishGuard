import re
from urllib.parse import urlparse

class PhishingDetector:
    def __init__(self):
        self.official_brands = {
            "כביש 6": ["kvish6.co.il"],
            "דואר": ["israelpost.co.il"],
            "חברת החשמל": ["iec.co.il"],
            "ביט": ["bitpay.co.il"],
            "מס הכנסה": ["gov.il"]
        }
        
        self.shorteners = ["did.li", "bit.ly", "t.co", "tinyurl", "qrcd.org", "f4u.biz", "lik5.vip", "1d.is", "weedil"]
        
        # סיווג הודעות - הלוואות עברו ל-DANGER
        self.categories = {
            "LOAN": {
                "keywords": ["הלוואה", "מיידית", "150000", "בחשבון תוך יום", "הלוואות", "אשראי לכולם"],
                "level": "DANGER",
                "label": "🛑 חשד להונאת הלוואה / שוק אפור",
                "warning": "זהירות! הודעות המציעות הלוואות מהירות הן לעיתים קרובות ניסיונות פישינג לגניבת פרטי אשראי או הונאות של השוק האפור. מומלץ מאוד לא להזין פרטים!"
            },
            "ILLEGAL_TRADE": {
                "keywords": ["מבצע אש", "שקיות", "בוטיק", "קנאביס", "וויד", "weed"],
                "level": "DANGER",
                "label": "🚫 חשד לסחר בחומרים אסורים / עוקץ",
                "warning": "זהירות! הצעה לסחר בחומרים אסורים. קישורים אלו משמשים לרוב כ'עוקץ' כספי או לגניבת פרטים אישיים."
            },
            "TAX": {
                "keywords": ["החזר מס", "בדיקה ללא תשלום", "החזר ממוצע"],
                "level": "ALERT",
                "label": "📑 פרסומת להחזרי מס",
                "warning": "זוהה שירות שיווקי. היזהרו ממסירת מסמכים רגישים לגורם שאינו מוכר ומפוקח."
            },
            "DONATION": {
                "keywords": ["מצווה", "חב״ד", "תרומה", "הגרלה", "מגדלור", "זכות"],
                "level": "INFO",
                "label": "🙏 בקשת תרומה או סיוע",
                "warning": "ההודעה נראית כבקשת תרומה. שימו לב שגם בתרומות קיימים ניסיונות התחזות - ודאו את זהות העמותה."
            }
        }

        self.red_flags = {"מיידי": 15, "אזהרה": 15, "הליכים משפטיים": 25, "נחסם": 20}

    def extract_url(self, text):
        url_pattern = r'(?:https?://)?(?:www\.)?([a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(?:/\S*)?)'
        match = re.search(url_pattern, text)
        return match.group(0) if match else None

    def analyze(self, text, sender_number=""):
        score = 0
        reasons = []
        found_category = None
        
        url = self.extract_url(text)
        domain = ""
        if url:
            full_url = url if url.startswith("http") else "http://" + url
            try: domain = urlparse(full_url).netloc.lower()
            except: domain = ""

        # 1. בדיקת קטגוריות
        for cat_id, data in self.categories.items():
            if any(key in text for key in data['keywords']):
                found_category = data
                if data['level'] == "DANGER": score += 60 # מקפיץ לסכנה
                break

        # 2. זיהוי התחזות
        for brand, official_domains in self.official_brands.items():
            if brand in text and url:
                if not any(off in domain for off in official_domains):
                    score += 70
                    reasons.append(f"חשד להתחזות ל'{brand}'")

        # 3. קישורים מקוצרים מוסיפים חשד
        if domain and any(sh in domain for sh in self.shorteners):
            score += 30
            reasons.append("שימוש בקישור מקוצר/חשוד")

        status = "SAFE"
        if score >= 45: status = "DANGER"
        elif found_category: status = found_category['level']
        
        return {
            "status": status,
            "score": min(score, 100),
            "reasons": reasons,
            "category_data": found_category
        }
