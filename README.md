# 🤖 RealBot – Telegram AI Chatbot with Emotion Detection

RealBot is an AI-powered Telegram bot that chats with users using **Gemini AI** and detects emotions from messages to respond more empathetically.

---

## 🚀 Features

- 💬 Chat with Gemini AI on Telegram
- 😊 Emotion detection from user messages (keyword-based)
- 🤗 Contextual, empathetic replies
- 💡 Simple, lightweight, and easy to customize

---

## 🛠️ Installation & Setup

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/RealBot.git
cd RealBot
```

### 2. Install Python dependencies

```bash
 pip install -r requirements.txt
 ```

 ### 3. Create and set up a .env file
Create a .env file and add the following:

```bash
TELEGRAM_TOKEN=your_telegram_bot_token
GEMINI_API_KEY=your_gemini_api_key

 ```
 🔒 Don't commit this file to GitHub. It’s already in .gitignore.

 ### 4. Run the bot

 ```bash
 python bot.py

 ```
 ---

## 💬 Usage
- Start the bot on Telegram with `/start`
- Send a message
- Bot will:
   - Detect your emotion
   - Generate a relevant reply using Gemini
   - Respond empathetically

---

## 🔧 Customization
- Modify the `EMOTION_KEYWORDS` dictionary in `bot.py` to improve emotion detection.
- For better emotion accuracy:
   - Integrate HuggingFace models or sentiment APIs

---

## 📁 Project Structure
``` 
RealBot/
│
├── bot.py                 # Main bot script
├── .env                  # Environment variables (secret, not uploaded)
├── requirements.txt       # Python dependencies
├── README.md              # Project documentation
├── .gitignore             # Files/folders to ignore in Git
└── venv/                  # Virtual environment (ignored)
```   

---

## 👨‍💻 Author
Made with ❤️ by Your Tirth Babariya

---

Enjoy chatting with your smarter, kinder AI bot!
