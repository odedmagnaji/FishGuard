# 🐟 FishGuard - WhatsApp Phishing Protector 🛡️

<p align="center">
  <img src="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcR6f9Y89oY8h-vR_M-zS6-V2q-J8E4g9k6Q-g&s" width="200" alt="FishGuard Logo">
</p>

> **Don't be the bait!** FishGuard is an intelligent WhatsApp bot designed to safeguard users against phishing and SMS scams in real-time.

---

## 🚀 Overview
In an era of sophisticated social engineering, FishGuard acts as a personal cybersecurity shield. The project focuses on identifying malicious patterns in messages, specifically targeting common scams in Israel by analyzing message content, URL structures, and sender metadata.

## ✨ Key Features
- **🔍 Smart URL Inspection:** Detects suspicious TLDs (.vip, .top, .org) and identifies link-shortening services used to hide malicious destinations.
- **🏢 Brand Consistency Check:** Cross-references brand names mentioned in text with the actual URL domain to detect impersonation (e.g., Kvish 6, Israel Post, Bit).
- **🚩 Linguistic Analysis:** Flags urgency-based tactics and common phishing phrases such as "Legal Action" or "Account Blocked".
- **🌍 Metadata Analysis:** Inspects international sender prefixes to flag suspicious origins for Hebrew-based messages.

## 🛠️ Tech Stack
- **Python 3.10** - Core detection logic.
- **Flask** - Web framework for handling incoming WhatsApp webhooks.
- **Twilio WhatsApp API** - Integration for real-time messaging.
- **PythonAnywhere** - Cloud deployment for 24/7 availability.

---
*Developed by Oded as a practical cybersecurity and software engineering project.*
