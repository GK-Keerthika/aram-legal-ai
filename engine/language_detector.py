# engine/language_detector.py
# Purpose: Language detection + all conversation handling
# Handles: English, Tamil, Tanglish, General chat,
#          Offensive words, Irrelevant queries

import re
import json
import random
import os

# ── Tamil Unicode Pattern ─────────────────────────────────
TAMIL_UNICODE_PATTERN = re.compile(r'[\u0B80-\u0BFF]')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TAMIL_INTENTS_FILE = os.path.join(BASE_DIR, "data", "tamil_intents.json")


# ── Offensive Words ───────────────────────────────────────
OFFENSIVE_WORDS = [
    # English offensive
    "idiot", "stupid", "fool", "moron", "dumb", "shut up",
    "useless", "hate you", "damn", "bastard", "bloody hell",
    "shut up", "garbage", "trash", "worthless", "pathetic",
    # Tamil/Tanglish offensive
    "poda", "podi", "loosu", "naaye", "kazhuthai",
    "thevdiya", "otha", "omala", "koothi", "punda",# Additional Tamil offensive — found in logs
    "mairu", "poolu", "otha", "poda maadu", "poda otha",
    "sunni", "baadu", "thayoli", "myir", "sootha"
]

# ── Irrelevant Topics ─────────────────────────────────────
IRRELEVANT_TOPICS = [
    "weather", "cricket", "movie", "film", "actor", "actress",
    "food", "recipe", "cook", "restaurant", "hotel booking",
    "sports", "football", "music", "song", "dance",
    "love", "relationship", "boyfriend", "girlfriend",
    "homework", "study", "exam", "school", "college",
    "investment", "stock market", "crypto", "bitcoin",
    "health tips", "diet", "exercise", "gym",
    "astrology", "horoscope", "religion", "god",
    "politics", "election", "party", "vote",
    "joke", "comedy", "funny", "meme",
    "game", "gaming", "pubg", "freefire",
    "padham", "padam", "cinema", "serials"
]

# ── General Conversation Patterns ────────────────────────
GENERAL_PATTERNS = {
    # English greetings with name
    "hi aram": "greet_aram",
    "hello aram": "greet_aram",
    "hey aram": "greet_aram",
    "hai aram": "greet_aram",
    "vanakkam aram": "greet_aram",
    "வணக்கம் aram": "greet_aram",
    "வணக்கம் அறம்": "greet_aram",
    "ஹலோ aram": "greet_aram",
    "ஹலோ": "greet_aram",
    "ஹலோ அறம்": "greet_aram",

    # Greetings with அறம் — found in logs
    "வணக்கம் அறம்": "greet_aram",
    "வணக்கம்  aram": "greet_aram",
    "வணக்கம் aram": "greet_aram",
    "vanakkam aram": "greet_aram",

    # Short responses — found in logs
    "sorry": "general_sorry",
    "mm": "general_ok",
    "no": "general_ok",
    "nope": "general_ok",
    "yes": "general_ok",
    "yeah": "general_ok",
    "ok bye": "general_bye",
    "tata": "general_bye",
    "ta ta": "general_bye",
    "illai": "general_ok",
    "illa": "general_ok",

    # Who are you variants — found in logs
    "who are u": "general_identity",
    "who r u": "general_identity",
    "wat r u": "general_identity",

    # Laws question — found in logs
    "mm enna laws use pandra": "general_law_info",
    "enna laws use pandra": "general_law_info",
    "what laws do you use": "general_law_info",
    "which laws": "general_law_info",

    # Tamil casual — found in logs
    "என்ன பண்ற": "general_tamil_howru",
    "enna pandra": "general_tamil_howru",
    "enna pandra aram": "general_tamil_howru",

    # How are you — English
    "how are you": "general_howru",
    "how r u": "general_howru",
    "how are u": "general_howru",
    "hows it going": "general_howru",
    "how's it going": "general_howru",
    "how do you do": "general_howru",
    "hi how are you": "general_howru",
    "hello how are you": "general_howru",
    "hey how are you": "general_howru",
    "hi, how are you": "general_howru",
    "hello, how are you": "general_howru",
    "whats up": "general_howru",
    "what's up": "general_howru",
    "sup": "general_howru",
    "wassup": "general_howru",

    # How are you — Tamil/Tanglish
    "epdi irukkinga": "general_tamil_howru",
    "epdi iruka": "general_tamil_howru",
    "eppadi irukkingal": "general_tamil_howru",
    "neenga epdi irukkinga": "general_tamil_howru",
    "enna panra": "general_tamil_howru",
    "enna pandra": "general_tamil_howru",
    "enna pannureenga": "general_tamil_howru",
    "என்ன பண்ற": "general_tamil_howru",
    "என்ன பண்றீங்க": "general_tamil_howru",
    "எப்படி இருக்கீங்க": "general_tamil_howru",
    "எப்படி இருக்க": "general_tamil_howru",
    "நலமா": "general_tamil_howru",
    "சுகமா": "general_tamil_howru",

    # Tamil casual food chat
    "saaptiya": "general_tamil_casual",
    "saptiya": "general_tamil_casual",
    "saptu": "general_tamil_casual",
    "saapadu": "general_tamil_casual",
    "enna saapta": "general_tamil_casual",
    "சாப்பிட்டீங்களா": "general_tamil_casual",
    "சாப்பிட்டியா": "general_tamil_casual",

    # Who are you — English
    "who are you": "general_identity",
    "what are you": "general_identity",
    "what is aram": "general_identity",
    "who is aram": "general_identity",
    "tell me about yourself": "general_identity",
    "introduce yourself": "general_identity",
    "are you a bot": "general_identity",
    "are you ai": "general_identity",
    "are you robot": "general_identity",
    "are you human": "general_identity",

    # Who are you — Tamil/Tanglish
    "neenga yaar": "general_tamil_identity",
    "neega yaar": "general_tamil_identity",
    "nee yaar": "general_tamil_identity",
    "aram yaar": "general_tamil_identity",
    "நீங்க யாரு": "general_tamil_identity",
    "நீ யாரு": "general_tamil_identity",
    "உங்களை பத்தி சொல்லுங்க": "general_tamil_identity",

    # What can you do
    "what can you do": "general_capability",
    "what do you do": "general_capability",
    "how can you help": "general_capability",
    "what can you help with": "general_capability",
    "what topics": "general_capability",
    "enna help pannuvenga": "general_capability",
    "enna seyya mudiyum": "general_capability",
    "என்ன உதவி செய்வீங்க": "general_capability",

    # Compliments — English
    "you are good": "general_compliment",
    "you are great": "general_compliment",
    "i like you": "general_compliment",
    "i love you": "general_compliment",
    "you are helpful": "general_compliment",
    "you are amazing": "general_compliment",
    "you are awesome": "general_compliment",
    "well done": "general_compliment",
    "good job": "general_compliment",
    "nice": "general_compliment",
    "excellent": "general_compliment",
    "brilliant": "general_compliment",
    "perfect": "general_compliment",

    # Compliments — Tamil/Tanglish
    "romba nalla iruka": "general_compliment",
    "super aram": "general_compliment",
    "nalla iruka": "general_compliment",
    "romba thanks": "general_compliment",
    "உங்களுக்கு நன்றி": "general_compliment",
    "நல்லா இருக்கீங்க": "general_compliment",

    # Thanks — English
    "thank you": "general_thanks",
    "thanks": "general_thanks",
    "thank u": "general_thanks",
    "thanks a lot": "general_thanks",
    "many thanks": "general_thanks",
    "much appreciated": "general_thanks",
    "appreciate it": "general_thanks",

    # Thanks — Tamil/Tanglish
    "nandri": "general_thanks",
    "romba nandri": "general_thanks",
    "thanks da": "general_thanks",
    "நன்றி": "general_thanks",
    "மிக்க நன்றி": "general_thanks",

    # OK / Understood
    "ok": "general_ok",
    "okay": "general_ok",
    "alright": "general_ok",
    "got it": "general_ok",
    "understood": "general_ok",
    "i see": "general_ok",
    "noted": "general_ok",
    "seri": "general_ok",
    "seri da": "general_ok",
    "சரி": "general_ok",
    "புரிஞ்சது": "general_ok",

    # Bye — English
    "bye": "general_bye",
    "goodbye": "general_bye",
    "good bye": "general_bye",
    "see you": "general_bye",
    "see ya": "general_bye",
    "take care": "general_bye",
    "ttyl": "general_bye",
    "talk later": "general_bye",

    # Bye — Tamil/Tanglish
    "bye aram": "general_bye",
    "poren": "general_bye",
    "poga poren": "general_bye",
    "seri poren": "general_bye",
    "போறேன்": "general_bye",
    "வருகிறேன்": "general_bye",

    # Asking about laws
    "what is consumer protection": "general_law_info",
    "tell me about consumer protection": "general_law_info",
    "what is it act": "general_law_info",
    "tell me about it act": "general_law_info",
    "what is bns": "general_law_info",
    "tell me about bns": "general_law_info",
    "what laws does india have": "general_law_info",
    "indian laws": "general_law_info",
    "consumer rights india": "general_law_info"
}

# ── General Conversation Responses ───────────────────────
GENERAL_RESPONSES = {

    "greet_aram": [
        "வணக்கம்! நான் அறம், உங்கள் சட்ட விழிப்புணர்வு உதவியாளர். என்ன உதவி வேண்டும்?",
        "Hello! I'm ARAM — your legal awareness assistant. How can I help you today?",
        "Hi! Great to connect with you. I'm ARAM — here to help you understand your legal rights. What's on your mind?",
        "வணக்கம்! சட்ட விழிப்புணர்வுக்கு நான் எப்போதும் தயார். என்ன பிரச்சினை?",
        "Hey there! ARAM here — your legal guide. Tell me what's going on and I'll help you navigate it!"
    ],

    "general_howru": [
        "Hello! I'm doing well, thank you for asking! 😊 I'm ARAM — always ready to help. What's on your mind?",
        "Hi there! Functioning well and happy to help! What legal concern can I assist you with today?",
        "Hey! Thank you for asking — I'm great! As your legal awareness assistant, I'm ready. What would you like to know?",
        "I'm doing well, thanks! More importantly — how can I help YOU today?",
        "All good here! I'm ARAM, your legal awareness companion. What's your concern today?",
        "Doing great! Ready to help you understand your rights. What happened?",
        "I'm always ready to help! Tell me your situation and I'll guide you through it. 😊"
    ],

    "general_tamil_howru": [
        "நான் நலமாக இருக்கிறேன், நன்றி! 😊 உங்களுக்கு சட்ட உதவி தேவையா? சொல்லுங்கள்!",
        "நன்றாக இருக்கிறேன்! உங்கள் சட்ட கேள்விகளுக்கு உதவ தயாராக இருக்கிறேன். என்ன பிரச்சினை?",
        "நலமாக இருக்கிறேன்! நீங்கள் எப்படி இருக்கிறீர்கள்? ஏதாவது சட்ட உதவி தேவையா?",
        "நன்றாக இருக்கிறேன்! என்ன விஷயம் — என்னால் என்ன உதவி செய்யலாம்?",
        "நலம்! உங்கள் பிரச்சினை என்னவென்று சொல்லுங்கள் — நான் வழிகாட்டுகிறேன்! 😊"
    ],

    "general_tamil_casual": [
        "நான் சாப்பிட மாட்டேன் — ஆனால் உங்கள் சட்ட கேள்விகளுக்கு நிச்சயம் உதவுவேன்! என்ன விஷயம்? 😄",
        "அது கேட்கவே நல்லாயிருக்கு! நான் ஒரு AI — சாப்பாடு தேவையில்லை. உங்கள் பிரச்சினை சொல்லுங்கள்!",
        "என்னால் சாப்பிட முடியாது — ஆனால் உங்களுக்கு சட்ட உதவி தர முடியும்! என்ன தேவை? 😊",
        "நான் AI — சாப்பாடு வேண்டாம்! ஆனால் உங்கள் பிரச்சினை கேட்கணும். சொல்லுங்க! 😄",
        "ஹா! நான் சாப்பிடுவதில்லை — உதவுவதே என் வேலை! என்ன நடந்தது? 😊"
    ],

    "general_identity": [
        "I am ARAM — Legal Awareness Assistant. I help Indian citizens understand their rights under Consumer Protection Act, IT Act, and BNS. I provide calm guidance — not legal advice.",
        "I'm ARAM, an AI-powered legal awareness assistant built for everyday Indian citizens. Consumer issues, cyber crimes, general legal concerns — I've got you covered!",
        "Great question! I'm ARAM — your legal awareness companion. I make Indian law accessible in English, Tamil, and Tanglish!",
        "I'm ARAM! Think of me as your friendly legal guide — I won't represent you in court, but I'll help you understand what's happening and what to do next.",
        "ARAM here! I'm an AI trained to help you navigate Indian legal situations calmly. Describe your problem and I'll point you in the right direction."
    ],

    "general_tamil_identity": [
        "நான் அறம் — சட்ட விழிப்புணர்வு உதவியாளர். நுகர்வோர் பாதுகாப்பு, இணைய சட்டம், BNS ஆகியவற்றில் வழிகாட்டுகிறேன்.",
        "நான் அறம்! தமிழ், ஆங்கிலம், தங்கிலிஷ் மூன்றிலும் பேசுவேன். இந்திய சட்டங்களை எளிமையாக புரிந்துகொள்ள உதவுகிறேன்.",
        "அறம் என்பது நான் — உங்கள் சட்ட வழிகாட்டி! என்ன பிரச்சினை என்று சொல்லுங்கள், நான் சரியான வழி காட்டுகிறேன்.",
        "நான் அறம் — AI சட்ட உதவியாளர். வழக்கறிஞர் அல்ல, ஆனால் உங்கள் உரிமைகளை புரிந்துகொள்ள உதவுவேன்!"
    ],

    "general_capability": [
        "I can help you with:\n\n• 🛒 Consumer complaints — refunds, defective products, online shopping fraud\n• 💻 Cyber issues — fraud, hacking, identity theft, harassment\n• ⚖️ General legal — cheating, threats, harassment\n• 📋 Complaint guidance — where and how to file\n\nI support English, Tamil, and Tanglish! Just describe your situation.",
        "Here's what I can do:\n\n• Explain your legal rights in simple language\n• Tell you which law applies to your situation\n• Guide you through the complaint filing process\n• Give step-by-step practical actions\n\nJust tell me what happened!",
        "I specialize in:\n\n• 🛒 Consumer rights — shopping, refunds, services\n• 💻 Cyber law — fraud, hacking, online harassment\n• ⚖️ Criminal law — cheating, threats, intimidation\n\nDescribe your situation and I'll guide you!"
    ],

    "general_compliment": [
        "Thank you so much! I'm glad I could help. 😊 Anything else you'd like to know?",
        "That's very kind of you! I'm here whenever you need legal guidance. Feel free to ask anything!",
        "நன்றி! உங்கள் வார்த்தைகள் மகிழ்ச்சி தருகின்றன. 😊 வேறு ஏதாவது கேள்வி இருந்தால் கேளுங்கள்!",
        "Thank you! That means a lot. My purpose is to make legal awareness accessible to everyone.",
        "Aww, thank you! 😊 That motivates me to keep helping. What else can I do for you?",
        "So glad to hear that! Remember — knowing your rights is the first step to protecting them. 💪"
    ],

    "general_thanks": [
        "You're welcome! Stay informed about your legal rights. Take care! 😊",
        "Happy to help! Remember — knowing your rights is the first step to protecting them.",
        "நன்றி சொல்லியதற்கு நன்றி! உங்கள் உரிமைகளை அறிந்து கொள்வது மிக முக்கியம். 😊",
        "Anytime! That's exactly what I'm here for. Come back whenever you need guidance.",
        "My pleasure! Stay safe and know your rights. 😊",
        "Always happy to help! Don't hesitate to return if you need more guidance.",
        "Of course! Take care of yourself and stay informed. 💪"
    ],

    "general_sorry": [
        "No worries at all! I'm here to help whenever you're ready. What's on your mind?",
        "That's perfectly fine! Take your time. How can I help you today?",
        "No need to apologize! I'm here whenever you're ready. What happened?",
        "Don't worry about it! Just tell me what's going on and I'll guide you.",
        "All good! We can start fresh. What would you like to know? 😊"
    ],

    "general_ok": [
        "Alright! Feel free to ask if you need any legal guidance.",
        "Great! Is there anything else I can help you with?",
        "சரி! வேறு ஏதாவது தேவையா? நான் இங்கே இருக்கிறேன்.",
        "Got it! Let me know if anything comes up.",
        "Sure! I'm here whenever you need help. 😊",
        "No problem! Feel free to come back anytime.",
        "Understood! Anything else on your mind?",
        "புரிஞ்சது! வேறு கேள்வி இருந்தால் கேளுங்கள். 😊"
    ],

    "general_bye": [
        "Goodbye! Stay safe and always know your rights. Take care! 👋",
        "Take care! Remember — ARAM is here whenever you need legal awareness guidance. 😊",
        "போய் வாருங்கள்! உங்கள் உரிமைகளை மறவாதீர்கள். 👋",
        "See you! Stay informed and stay protected. Goodbye! 😊",
        "Bye! Come back anytime you need help. Stay safe! 👋",
        "Take care of yourself! Remember your rights and stay protected. 😊",
        "Goodbye! It was great helping you today. Come back anytime! 👋",
        "வருகிறேன் என்று சொல்லுங்கள்! 😊 உங்கள் உரிமைகளை பாதுகாத்துக்கொள்ளுங்கள்!",
        "Bye bye! Stay safe, stay informed, stay protected! 💪",
        "See you soon! The law is on your side — always remember that. 👋"
    ],

    "general_law_info": [
        "Great that you want to learn about Indian laws! Here's a quick overview:\n\n📋 Consumer Protection Act 2019 — Protects buyers of goods and services\n💻 IT Act 2000 — Covers cyber crimes and digital offences\n⚖️ BNS 2023 — Replaced IPC, covers criminal offences\n\nWant to know more about any specific law?",
        "Learning about your legal rights is the first step to protecting them! ARAM covers:\n\n• Consumer Protection Act — for shopping, refund, service issues\n• IT Act — for cyber fraud, hacking, online harassment\n• BNS — for cheating, threats, and harassment\n\nTell me your situation and I'll guide you to the right law!"
    ]
}

# ── Offensive Responses ───────────────────────────────────
OFFENSIVE_RESPONSES = [
    "I understand you might be feeling frustrated right now. I'm here to help you calmly. Please share your legal concern and I'll do my best to guide you.",
    "It seems like you're going through a difficult time. I'm here to help — please describe your situation and I'll guide you properly.",
    "நீங்கள் கோபமாக இருக்கிறீர்கள் என்று தெரிகிறது. நான் உங்களுக்கு உதவ இங்கே இருக்கிறேன். தயவுசெய்து உங்கள் பிரச்சினையை சொல்லுங்கள்.",
    "I'm here to help you, not judge you. Whatever you're going through, please share your concern and I'll guide you to the right solution."
]

# ── Irrelevant Topic Responses ────────────────────────────
IRRELEVANT_RESPONSES = [
    "That's outside my area of expertise! I specialize in legal awareness for Indian citizens. Could you tell me about a legal concern you have?",
    "I'm specifically designed to help with legal awareness — consumer issues, cyber crimes, and general legal rights. How can I help you with a legal matter?",
    "I'd love to help but that topic is outside what I cover. I'm best at guiding you through legal situations. Do you have a legal concern I can help with?",
    "அது என்னுடைய தொழில் இல்லை! நான் சட்ட விழிப்புணர்வுக்கு மட்டுமே உதவுகிறேன். சட்ட பிரச்சினை ஏதாவது இருந்தால் சொல்லுங்கள்."
]

# ── Tamil Responses ───────────────────────────────────────
TAMIL_RESPONSES = {
    "GREET001": """வணக்கம்! நான் ARAM, உங்கள் சட்ட விழிப்புணர்வு உதவியாளர்.

இந்திய சட்டங்களை தெளிவாகவும் அமைதியாகவும் புரிந்துகொள்ள உதவுவேன்.

நான் இவற்றில் உதவ முடியும்:
- நுகர்வோர் புகார்கள் (பணம் திரும்ப, குறைபாடுள்ள பொருட்கள்)
- இணைய பிரச்சினைகள் (மோசடி, ஹேக்கிங், தொல்லை)
- பொது சட்ட கவலைகள் (ஏமாற்றுதல், மிரட்டல், துன்புறுத்தல்)

உங்கள் பிரச்சினையை சொல்லுங்கள்! 😊""",

    "CP001": """உங்கள் நிலை புரிகிறது — பணம் திரும்ப கிடைக்கவில்லை.

⚖️ சட்டம்: நுகர்வோர் பாதுகாப்பு சட்டம், 2019

💡 உங்கள் உரிமை என்னவென்றால்:
குறைபாடுள்ள பொருள் அல்லது சேவைக்கு பணம் திரும்ப கோரும்
உரிமை உங்களுக்கு உண்டு. விற்பனையாளர் மறுக்க முடியாது.

🟠 தீவிரம்: நடுத்தரம்

✅ நீங்கள் செய்ய வேண்டியவை:
1. ரசீது, ஆர்டர் confirmation சேகரிக்கவும்
2. விற்பனையாளருக்கு எழுத்துப்பூர்வமாக கோரிக்கை அனுப்பவும்
3. 7 நாட்களில் பதில் இல்லை என்றால் grievance officer அணுகவும்
4. consumerhelpline.gov.in இல் புகார் செய்யவும்
5. மாவட்ட நுகர்வோர் மன்றம் அணுகலாம்

🏛️ உதவி: 1800-11-4000 | consumerhelpline.gov.in

⚖️ இது சட்ட விழிப்புணர்வு மட்டுமே — சட்ட ஆலோசனை அல்ல.""",

    "CP002": """பொருள் குறைபாடுடன் வந்திருக்கிறது என்று தெரிகிறது.

⚖️ சட்டம்: நுகர்வோர் பாதுகாப்பு சட்டம், 2019

💡 உங்கள் உரிமை:
மாற்றம், பழுதுபார்ப்பு, அல்லது பணம் திரும்ப கோரலாம்.

🟠 தீவிரம்: நடுத்தரம்

✅ நீங்கள் செய்ய வேண்டியவை:
1. பொருளின் புகைப்படம், வீடியோ எடுக்கவும்
2. packaging வீசாதீர்கள்
3. விற்பனையாளரிடம் மாற்றம் கோரவும்
4. consumerhelpline.gov.in இல் புகார் செய்யவும்

🏛️ உதவி: 1800-11-4000

⚖️ இது சட்ட விழிப்புணர்வு மட்டுமே — சட்ட ஆலோசனை அல்ல.""",

    "CP003": """Online ஆர்டர் வரவில்லை அல்லது மோசடி நடந்திருக்கிறது.

⚖️ சட்டம்: நுகர்வோர் பாதுகாப்பு சட்டம், 2019

🔴 தீவிரம்: அதிகம்

✅ நீங்கள் செய்ய வேண்டியவை:
1. order confirmation, payment proof சேகரிக்கவும்
2. e-commerce platform-ல் எழுத்துப்பூர்வமாக புகார் செய்யவும்
3. consumerhelpline.gov.in இல் பதிவு செய்யவும்
4. மோசடி என்றால் cybercrime.gov.in-லும் புகார் செய்யவும்
5. card payment என்றால் bank-ல் chargeback கோரவும்

🏛️ உதவி: 1800-11-4000 | cybercrime.gov.in

⚖️ இது சட்ட விழிப்புணர்வு மட்டுமே — சட்ட ஆலோசனை அல்ல.""",

    "CP004": """சேவை சரியாக கிடைக்கவில்லை என்று தெரிகிறது.

⚖️ சட்டம்: நுகர்வோர் பாதுகாப்பு சட்டம், 2019

🟡 தீவிரம்: குறைவு

✅ நீங்கள் செய்ய வேண்டியவை:
1. வாக்குறுதி vs கிடைத்தது என்று எழுதி வையுங்கள்
2. சேவை வழங்குனரிடம் எழுத்துப்பூர்வமாக புகார் செய்யவும்
3. consumerhelpline.gov.in இல் பதிவு செய்யவும்

🏛️ உதவி: 1800-11-4000

⚖️ இது சட்ட விழிப்புணர்வு மட்டுமே — சட்ட ஆலோசனை அல்ல.""",

    "IT001": """இணைய மோசடி நடந்திருக்கிறது என்று தெரிகிறது.

⚖️ சட்டம்: தகவல் தொழில்நுட்ப சட்டம், 2000

🔴 தீவிரம்: அதிகம் — உடனே செயல்படுங்கள்!

✅ உடனடியாக செய்யுங்கள்:
1. உங்கள் வங்கியை உடனே அழைக்கவும் — account freeze செய்யவும்
2. 1930 என்ற cyber crime helpline அழைக்கவும்
3. cybercrime.gov.in இல் 24 மணி நேரத்தில் பதிவு செய்யவும்
4. அனைத்து screenshots, messages சேகரிக்கவும்
5. அருகிலுள்ள காவல் நிலையத்திலும் புகார் செய்யவும்

🏛️ Cyber Crime: 1930 | cybercrime.gov.in

⚖️ இது சட்ட விழிப்புணர்வு மட்டுமே — சட்ட ஆலோசனை அல்ல.""",

    "IT002": """உங்கள் அடையாளம் தவறாக பயன்படுத்தப்படுகிறது.

⚖️ சட்டம்: தகவல் தொழில்நுட்ப சட்டம், 2000

🔴 தீவிரம்: அதிகம்

✅ நீங்கள் செய்ய வேண்டியவை:
1. போலி profile-இன் screenshot உடனே எடுக்கவும்
2. Platform-ல் (Facebook/Instagram) நேரடியாக report செய்யவும்
3. cybercrime.gov.in இல் புகார் செய்யவும்
4. 1930 அழைக்கவும்
5. நெருங்கிய நண்பர்களுக்கு தெரியப்படுத்துங்கள்

🏛️ Cyber Crime: 1930 | cybercrime.gov.in

⚖️ இது சட்ட விழிப்புணர்வு மட்டுமே — சட்ட ஆலோசனை அல்ல.""",

    "IT003": """Online-ல் துன்புறுத்தல் நடக்கிறது என்று தெரிகிறது.

⚖️ சட்டம்: தகவல் தொழில்நுட்ப சட்டம், 2000

🟠 தீவிரம்: நடுத்தரம்

✅ நீங்கள் செய்ய வேண்டியவை:
1. பதில் சொல்லாதீர்கள் — ஆதாரங்களை பாதுகாக்கவும்
2. Timestamp-உடன் screenshots எடுக்கவும்
3. Platform-ல் block செய்து report செய்யவும்
4. cybercrime.gov.in இல் புகார் செய்யவும்
5. தீவிரமாக இருந்தால் காவல் நிலையம் செல்லுங்கள்

🏛️ பெண்கள்: 1091 | Cyber Crime: 1930

⚖️ இது சட்ட விழிப்புணர்வு மட்டுமே — சட்ட ஆலோசனை அல்ல.""",

    "IT004": """உங்கள் கணக்கு hack ஆனது என்று தெரிகிறது.

⚖️ சட்டம்: தகவல் தொழில்நுட்ப சட்டம், 2000

🔴 தீவிரம்: அதிகம் — உடனே செயல்படுங்கள்!

✅ உடனடியாக செய்யுங்கள்:
1. உடனே password மாற்றவும்
2. Two-factor authentication இயக்கவும்
3. தெரியாத devices remove செய்யவும்
4. cybercrime.gov.in இல் புகார் செய்யவும்
5. வங்கி கணக்கு பாதிக்கப்பட்டால் வங்கியை அழைக்கவும்

🏛️ Cyber Crime: 1930 | cybercrime.gov.in

⚖️ இது சட்ட விழிப்புணர்வு மட்டுமே — சட்ட ஆலோசனை அல்ல.""",

    "BNS001": """யாரோ உங்களை ஏமாற்றியிருக்கிறார்கள் என்று தெரிகிறது.

⚖️ சட்டம்: பாரதிய நியாய சங்கிதா (BNS), 2023

🔴 தீவிரம்: அதிகம்

💡 இது என்னவென்றால்:
வேண்டுமென்றே ஏமாற்றி பணம் பறித்தால் அது குற்றம்.

✅ நீங்கள் செய்ய வேண்டியவை:
1. நடந்தவற்றை தேதியுடன் எழுதி வையுங்கள்
2. Messages, receipts, agreements சேகரிக்கவும்
3. நபரிடம் எழுத்துப்பூர்வமாக பணம் திரும்ப கேளுங்கள்
4. பதில் இல்லை என்றால் காவல் நிலையத்தில் புகார் செய்யவும்
5. இலவச சட்ட உதவிக்கு 15100 அழைக்கவும்

🏛️ இலவச சட்ட உதவி: 15100

⚖️ இது சட்ட விழிப்புணர்வு மட்டுமே — சட்ட ஆலோசனை அல்ல.""",

    "BNS002": """யாரோ உங்களை மிரட்டுகிறார்கள் என்று தெரிகிறது.

⚖️ சட்டம்: பாரதிய நியாய சங்கிதா (BNS), 2023

🔴 தீவிரம்: அதிகம் — உங்கள் பாதுகாப்பு முக்கியம்!

✅ உடனடியாக செய்யுங்கள்:
1. மிரட்டல் செய்திகளை delete செய்யாதீர்கள்
2. நம்பகமான குடும்பத்தினரிடம் சொல்லுங்கள்
3. அருகிலுள்ள காவல் நிலையத்தில் புகார் செய்யுங்கள்
4. உயிருக்கு ஆபத்து என்றால் 112 அழைக்கவும்

🏛️ அவசர உதவி: 112 | பெண்கள்: 1091

⚖️ இது சட்ட விழிப்புணர்வு மட்டுமே — சட்ட ஆலோசனை அல்ல.""",

    "BNS003": """யாரோ உங்களை தொந்தரவு செய்கிறார்கள் என்று தெரிகிறது.

⚖️ சட்டம்: பாரதிய நியாய சங்கிதா (BNS), 2023

🟠 தீவிரம்: நடுத்தரம்

✅ நீங்கள் செய்ய வேண்டியவை:
1. ஒவ்வொரு சம்பவத்தையும் தேதியுடன் குறித்து வையுங்கள்
2. சாட்சிகள் இருந்தால் பெயர் வையுங்கள்
3. Workplace என்றால் HR-ஐ அணுகவும்
4. காவல் நிலையத்தில் புகார் செய்யவும்
5. பெண்களுக்கு: 1091 அழைக்கவும்

🏛️ பெண்கள்: 1091 | சட்ட உதவி: 15100

⚖️ இது சட்ட விழிப்புணர்வு மட்டுமே — சட்ட ஆலோசனை அல்ல.""",

    "GUIDE001": """புகார் செய்வது உங்கள் உரிமை!

💡 உங்கள் பிரச்சினை வகையை பொறுத்து:

🛒 நுகர்வோர் பிரச்சினை:
- consumerhelpline.gov.in
- அழைப்பு: 1800-11-4000 (இலவசம்)

💻 இணைய பிரச்சினை:
- cybercrime.gov.in
- அழைப்பு: 1930

👮 குற்றவியல் பிரச்சினை:
- அருகிலுள்ள காவல் நிலையம்
- இலவச சட்ட உதவி: 15100

⚖️ இது சட்ட விழிப்புணர்வு மட்டுமே — சட்ட ஆலோசனை அல்ல.""",

    "UNKNOWN001": """மன்னிக்கவும், உங்கள் கேள்வி சரியாக புரியவில்லை.

நான் இவற்றில் உதவ முடியும்:
- நுகர்வோர் புகார்கள் (பணம் திரும்ப, குறைபாடுள்ள பொருட்கள்)
- இணைய பிரச்சினைகள் (மோசடி, ஹேக்கிங், தொல்லை)
- பொது சட்ட கவலைகள் (ஏமாற்றுதல், மிரட்டல், துன்புறுத்தல்)

தயவுசெய்து உங்கள் பிரச்சினையை கொஞ்சம் விளக்கமாக சொல்லுங்கள்."""
}

# ── Tanglish Keyword Map ──────────────────────────────────
TANGLISH_KEYWORD_MAP = {
    "vanakkam": "hello", "vanakam": "hello",
    "hai": "hello", "helo": "hello",
    "panam": "money", "thirumba": "return",
    "thirupa": "refund", "porul": "product",
    "kedu": "defective", "keduthal": "damaged",
    "vaanginen": "purchased", "kudukala": "not given",
    "hackku": "hacked", "hack": "hacked",
    "fraud": "fraud", "kavardu": "stolen",
    "emaandhu": "cheated", "emattinaan": "cheated",
    "emaathitanga": "cheated", "poi": "false",
    "poiyaa": "fake", "thondara": "harassment",
    "thondaravu": "harassment", "pidutham": "harassment",
    "bayamurutural": "threatening", "mirattal": "threatening",
    "mirattukiraan": "threatening", "mirattukiranga": "threatening",
    "udhavi": "help", "problem": "problem",
    "complaint": "complaint", "pannittaan": "did it",
    "pannittaanga": "they did", "account": "account",
    "password": "password", "panam pochu": "money gone",
    "otp kuduthen": "gave otp", "bank fraud": "bank fraud",
    "mosadi": "fraud", "pramandam": "fraud",
    "azhuthal": "pressure",
     "bayamaruku": "threatening",
    "bayam": "fear threat",
    "hacking": "hacked",
    "hack aana": "hacked",
    "in tamil": "tamil", "kastam": "trouble"
}


def load_tamil_intents() -> list:
    """Loads tamil_intents.json for keyword matching."""
    try:
        with open(TAMIL_INTENTS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("tamil_intents", [])
    except Exception:
        return []


def detect_language(text: str) -> str:
    """Detects: tamil, tanglish, or english."""
    if TAMIL_UNICODE_PATTERN.search(text):
        return "tamil"
    text_lower = text.lower()
    for word in TANGLISH_KEYWORD_MAP:
        if word in text_lower:
            return "tanglish"
    return "english"


def is_offensive(text: str) -> bool:
    """Returns True if text contains offensive words."""
    text_lower = text.lower()
    return any(word in text_lower for word in OFFENSIVE_WORDS)


def is_irrelevant(text: str) -> bool:
    """Returns True if text is clearly off-topic."""
    text_lower = text.lower()
    return any(topic in text_lower for topic in IRRELEVANT_TOPICS)


def is_general_conversation(text: str) -> str | None:
    """
    Checks all general conversation patterns.
    Returns conversation type key or None.
    """
    text_lower = text.lower().strip()
    # Check exact and partial matches
    for phrase, conv_type in GENERAL_PATTERNS.items():
        if phrase in text_lower:
            return conv_type
    return None


def get_general_response(conv_type: str) -> str:
    """Returns random response for conversation type."""
    responses = GENERAL_RESPONSES.get(conv_type, [])
    if responses:
        return random.choice(responses)
    return "I'm here to help with legal awareness. Please describe your concern!"


def get_offensive_response() -> str:
    """Returns calm response to offensive input."""
    return random.choice(OFFENSIVE_RESPONSES)


def get_irrelevant_response() -> str:
    """Returns polite redirect for off-topic queries."""
    return random.choice(IRRELEVANT_RESPONSES)


def translate_tanglish(text: str) -> str:
    """Converts Tanglish keywords to English."""
    text_lower = text.lower()
    for tanglish, english in TANGLISH_KEYWORD_MAP.items():
        text_lower = text_lower.replace(tanglish, english)
    return text_lower


def detect_tamil_intent(text: str) -> str | None:
    """
    Detects intent from Tamil/Tanglish keywords.
    Returns intent_id or None.
    """
    tamil_intents = load_tamil_intents()
    text_lower = text.lower()

    for intent in tamil_intents:
        all_keywords = (
            intent.get("tamil_keywords", []) +
            intent.get("tanglish_keywords", [])
        )
        for keyword in all_keywords:
            if keyword.lower() in text_lower:
                return intent["intent_id"]
    return None


def get_tamil_response(intent_id: str) -> str:
    """Returns Tamil response for given intent."""
    return TAMIL_RESPONSES.get(
        intent_id,
        TAMIL_RESPONSES.get("UNKNOWN001", "")
    )


if __name__ == "__main__":
    tests = [
        "hi, how are you?",
        "saaptiya",
        "என்ன பண்ற",
        "who are you",
        "நீ யாரு",
        "thank you",
        "what is cricket",
        "poda loosu",
        "bye",
        "what can you do",
        "vanakkam aram",
        "account hack pannittaan"
    ]

    print("\n🧪 Language Detector Test")
    print("─" * 50)
    for text in tests:
        lang = detect_language(text)
        offensive = is_offensive(text)
        irrelevant = is_irrelevant(text)
        general = is_general_conversation(text)

        print(f"\nInput     : {text}")
        print(f"Language  : {lang}")
        print(f"Offensive : {offensive}")
        print(f"Irrelevant: {irrelevant}")
        print(f"General   : {general}")