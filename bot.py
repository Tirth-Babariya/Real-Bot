import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from dotenv import load_dotenv
import google.generativeai as genai

# --- LOAD ENVIRONMENT VARIABLES FROM .env ---
load_dotenv()

# --- CONFIG ---
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN', 'YOUR_TELEGRAM_BOT_TOKEN')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', 'YOUR_GEMINI_API_KEY')

# --- GEMINI SETUP ---
genai.configure(api_key=GEMINI_API_KEY)
gemini_model = genai.GenerativeModel("models/gemini-2.5-flash")

# --- LOGGING ---
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# --- EMOTION DETECTION (simple keyword-based) ---
EMOTION_KEYWORDS = {
    'happy': ['happy', 'joy', 'glad', 'excited', 'delighted'],
    'sad': ['sad', 'down', 'unhappy', 'depressed', 'cry'],
    'angry': ['angry', 'mad', 'furious', 'annoyed', 'irritated'],
    'fear': ['afraid', 'scared', 'fear', 'terrified', 'nervous'],
    'surprised': ['surprised', 'amazed', 'astonished', 'shocked'],
    'neutral': []
}

def detect_emotion(text):
    text = text.lower()
    for emotion, keywords in EMOTION_KEYWORDS.items():
        for word in keywords:
            if word in text:
                return emotion
    return 'neutral'

# --- USER LANGUAGE PREFERENCES ---
user_lang = {}

LANG_OPTIONS = {
    'en': 'English',
    'hi': 'Hindi using English letters',
    'gu': 'Gujarati using English letters'
}

def get_user_lang(user_id):
    return user_lang.get(user_id, 'en')

async def set_lang(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args and context.args[0] in LANG_OPTIONS:
        user_lang[update.effective_user.id] = context.args[0]
        await update.message.reply_text(f"Language set to {LANG_OPTIONS[context.args[0]]}.")
    else:
        await update.message.reply_text("Usage: /lang en|hi|gu\n'en' for English (default), 'hi' for Hinglish, 'gu' for Gujlish.")

# --- IN-MEMORY CONTEXT STORAGE ---
user_context = {}  # user_id: list of (role, message)
CONTEXT_LENGTH = 8  # Number of messages to remember

# --- CONTEXT-AWARE GEMINI CALL ---
def ask_gemini(user_message, emotion, lang_code, user_name=None, context_list=None):
    if lang_code == 'hi':
        lang_instruction = (
            "Reply ONLY in Hindi using English letters (Hinglish, not Devanagari script, not English, not Gujarati). "
            "Do NOT use Devanagari script. Example: 'Aap kaise ho?' "
        )
    elif lang_code == 'gu':
        lang_instruction = (
            "Reply ONLY in Gujarati using English letters (Gujlish, not Gujarati script, not English, not Hindi). "
            "Do NOT use Gujarati script. Example: 'Tame kem cho?' "
        )
    else:
        lang_instruction = "Reply ONLY in English."
    name_part = f"Their name is {user_name}. " if user_name else ""
    # Build conversation history
    history = ""
    if context_list:
        for role, msg in context_list:
            if role == 'user':
                history += f"User: {msg}\n"
            else:
                history += f"Buddy: {msg}\n"
    prompt = (
        f"You are the user's real, friendly buddy. {name_part}Reply in a casual, warm, and natural way, as if you are a real person. "
        f"The user is feeling {emotion}. {lang_instruction} "
        f"Always respond in a way that fits the user's mood and message, and adapt to any feeling or topic they share. "
        f"Break your reply into 2 to 4 short, realistic, consecutive messages, as if you are texting. Separate each message with three vertical bars: |||. "
        f"Here is the recent conversation:\n{history}"
        f"Respond to what the user said: '{user_message}'"
    )
    try:
        response = gemini_model.generate_content(prompt)
        return response.text
    except Exception as e:
        print("Gemini API error:", e)
        return "Sorry, there was an error contacting the AI service."

# --- TELEGRAM HANDLERS ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hi! I'm RealBot. Tell me how you feel or just talk to me!\nUse /lang en|hi|gu to set reply language.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    emotion = detect_emotion(user_message)
    lang_code = get_user_lang(update.effective_user.id)
    user_name = update.effective_user.first_name if update.effective_user else None
    user_id = update.effective_user.id if update.effective_user else None
    # Get context for this user
    context_list = user_context.get(user_id, [])
    # Add the new user message to context
    context_list.append(('user', user_message))
    # Keep only the last CONTEXT_LENGTH messages
    context_list = context_list[-CONTEXT_LENGTH:]
    ai_response = ask_gemini(user_message, emotion, lang_code, user_name, context_list)
    # Split the response on '|||' and send each as a separate message
    bot_messages = [msg.strip() for msg in ai_response.split('|||') if msg.strip()]
    for part in bot_messages:
        await update.message.reply_text(part)
    # Add the bot's reply to context (as one string)
    context_list.append(('bot', ' '.join(bot_messages)))
    # Keep only the last CONTEXT_LENGTH messages
    context_list = context_list[-CONTEXT_LENGTH:]
    user_context[user_id] = context_list

# --- MAIN ---
def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('lang', set_lang))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print('Bot is running...')
    app.run_polling()

if __name__ == '__main__':
    main() 