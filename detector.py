import re
from urllib.parse import urlparse

class PhishingDetector:
    def __init__(self):
        # מותגים ישראליים רשמיים
        self.official_brands = {
            "כביש 6": ["kvish6.co.il"],
            "דואר": ["israelpost.co.il"],
            "חברת החשמל": ["iec.co.il"],
            "ביט": ["bitpay.co.il"],
            "מס הכנסה": ["gov.il"]
        }
        
        # רשימת מקצרי קישורים ודומיינים חשודים (הוספתי את weedil ו-1d.is)
        self.shorteners = ["did.li", "bit.ly", "t.co", "tinyurl", "qrcd.org", "f4u.biz", "lik5.vip", "1d.is", "weedil"]
        
        # סיווג הודעות (יועץ אבטחה)
        self.categories = {
            "ILLEGAL_TRADE": {
                "keywords": ["מבצע אש", "שקיות", "בוטיק", "משלוחים לכל הארץ", "קנאביס", "וויד", "weed"],
                "level": "DANGER",
                "label": "🚫 חשד לסחר בחומרים אסורים / עוקץ",
                "warning": "זהירות! ההודעה נראית כהצעה למכירת חומרים אסורים. מעבר לעובדה שמדובר בעבירה על החוק, קישורים אלו משמשים לעיתים קרובות כ'עוקץ' (גניבת כסף ללא תמורה) או לגניבת פרטים אישיים."
            },
            "LOAN": {
                "keywords": ["הלוואה", "מיידית", "150000", "בחשבון תוך יום", "הלוואות"],
                "level": "ALERT",
                "label": "💰 הצעה פיננסית",
                "warning": "זוהה תוכן של הלוואה חוץ-בנקאית. שים לב ששירותים אלו לעיתים אינם מפוקחים ועלולים לכלול ריביות גבוהות."
            },
            "TAX": {
                "keywords": ["החזר מס", "בדיקה ללא תשלום", "החזר ממוצע", "בדיקת זכאות"],
                "level": "ALERT",
                "label": "📑 פרסומת להחזרי מס",
                "warning": "זוהה שירות שיווקי להחזרי מס. מומלץ לוודא את זהות החברה לפני מסירת פרטים אישיים."
            },
            "DONATION": {
                "keywords": ["מצווה", "חב״ד", "תרומה", "הגרלה", "מגדלור", "זכות", "עמותה"],
                "level": "INFO",
                "label": "🙏 בקשת תרומה או סיוע",
                "warning": "ההודעה נראית כמו בקשה לתרומה או השתתפות בהגרלה. וודאו שהגוף המבקש מוכר לכם."
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

        # 1. בדיקת קטגוריות תוכן (כולל הסחר הלא חוקי החדש)
        for cat_id, data in self.categories.items():
            if any(key in text for key in data['keywords']):
                found_category = data
                if data['level'] == "DANGER": score += 80 # מקפיץ ישר לסכנה
                break

        # 2. זיהוי התחזות (למשל אם כתבו "דואר" בהודעת סמים)
        for brand, official_domains in self.official_brands.items():
            if brand in text and url:
                if not any(off in domain for off in official_domains):
                    score += 70
                    reasons.append(f"חשד להתחזות ל'{brand}'")

        # 3. ניקוד על בסיס דומיין וקיצורי דרך
        if domain and any(sh in domain for sh in self.shorteners):
            score += 30
            reasons.append(f"שימוש בקישור חשוד או מקוצר ({domain})")

        status = "SAFE"
        if score >= 45: status = "DANGER"
        elif found_category: status = found_category['level']
        
        return {
            "status": status,
            "score": min(score, 100),
            "reasons": reasons,
            "category_data": found_category
        }
