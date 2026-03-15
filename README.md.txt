# 🐟 FishGuard - WhatsApp Fishing Protector 🛡️

**Don't be the bait!** FishGuard is an AI-powered WhatsApp bot designed to detect and alert users about phishing attempts in real-time.

## 🚀 Overview
fishing attacks are becoming increasingly sophisticated. FishGuard analyzes incoming messages, URL structures, and sender metadata to provide a risk score and clear security recommendations.

## ✨ Key Features
- **URL Analysis:** Detects suspicious TLDs (.vip, .top, .org) and link-shortening services.
- **Brand Protection:** Matches brand names (e.g., Kvish 6, Israel Post, Bit) against official domains to detect impersonation.
- **Urgency Detection:** Identifies social engineering tactics and pressure words like "Immediate Payment" or "Legal Action".
- **WhatsApp Integration:** Works directly within WhatsApp via Twilio API.

## 🛠️ Tech Stack
- **Language:** Python 3.10
- **Framework:** Flask
- **API:** Twilio WhatsApp API
- **Deployment:** PythonAnywhere