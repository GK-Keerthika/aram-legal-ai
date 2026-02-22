# engine/model_trainer.py
# Purpose: Train ML model with maximum accuracy
# Uses expanded dataset + augmented sentences

import json
import pickle
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn import metrics
from config import INTENTS_FILE

MODEL_PATH = os.path.join("engine", "aram_model.pkl")


def prepare_training_data() -> tuple:
    """
    Builds training data from intents.json
    plus large augmented sentence bank.
    """
    with open(INTENTS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    # ── Augmented training sentences ─────────────────
    # These teach the model natural language patterns
    # More sentences = better accuracy
    augmented = {
        "CP001": [
            "I paid but got no refund",
            "my refund is still pending",
            "they are not returning my money",
            "refund request was rejected",
            "waiting for my money back",
            "seller not giving refund",
            "I want my refund back",
            "refund not processed yet",
            "money not returned to account",
            "how to get refund from seller",
            "they denied my refund request",
            "company is not refunding me",
            "I requested refund 2 weeks ago",
            "online store not giving money back",
            "my return was accepted but no refund",
            "flipkart not refunding my money",
            "amazon refund is pending",
            "meesho not giving refund",
            "I cancelled order but no refund",
            "refund showing in process for weeks"
        ],
        "CP002": [
            "product I received is broken",
            "item stopped working after 2 days",
            "received wrong product",
            "product quality is very bad",
            "goods are damaged",
            "item I bought is defective",
            "product not as described",
            "received faulty goods",
            "my purchase arrived damaged",
            "product arrived broken",
            "mobile phone not working properly",
            "laptop has defect",
            "appliance stopped working",
            "clothes have manufacturing defect",
            "shoes fell apart quickly",
            "product looks different from website",
            "received counterfeit product",
            "item has missing parts",
            "electronic item not functioning",
            "product broke within warranty period"
        ],
        "CP003": [
            "I ordered online but nothing came",
            "website took money but no delivery",
            "fake online store cheated me",
            "ordered product never arrived",
            "e-commerce fraud happened to me",
            "online seller disappeared after payment",
            "paid online but product not delivered",
            "shopping website is fake",
            "courier never delivered my item",
            "online purchase not received",
            "parcel shows delivered but not received",
            "tracking shows out for delivery but nothing came",
            "seller is not responding after payment",
            "fake seller on e-commerce platform",
            "I got scammed on online shopping",
            "product not delivered for 30 days",
            "seller account deactivated after I paid",
            "duplicate product sent instead of original",
            "cash on delivery item taken but not delivered",
            "wrong item sent and no resolution given"
        ],
        "CP004": [
            "service I paid for was not done",
            "very poor quality work done",
            "contractor did not finish work",
            "service provider cheated me",
            "paid for service but not completed",
            "work quality is terrible",
            "service not as promised",
            "I am not satisfied with service",
            "service center not helping",
            "paid but service incomplete",
            "plumber did poor quality work",
            "electrician took money did not come",
            "ac repair not done properly",
            "hospital service was very poor",
            "insurance company not providing service",
            "bank service is very bad",
            "tour operator cheated me",
            "gym membership service not provided",
            "coaching center not providing classes",
            "internet service provider giving bad service"
        ],
        "IT001": [
            "someone stole money from my account",
            "got fake call asking for otp",
            "I shared otp and money got deducted",
            "upi payment fraud happened",
            "bank account hacked and money gone",
            "received phishing message",
            "online scammer took my money",
            "fraud happened through phone call",
            "money transferred without my knowledge",
            "cyber fraud victim here",
            "someone called pretending to be bank",
            "I lost money through online fraud",
            "fake customer care called me",
            "received link and clicked it money gone",
            "someone did transaction from my account",
            "phonepe fraud happened",
            "google pay scam",
            "I got a fake prize call",
            "lottery scam money taken",
            "otp stolen online",
            "digital payment fraud",
            "net banking unauthorized transaction",
            "online money transfer fraud",
            "cyber crime financial loss",
            "virtual fraud happened",
            "internet banking cheated",
            "investment fraud happened to me"
        ],
        "IT002": [
            "someone made fake profile with my photos",
            "my identity is being misused online",
            "fake account created in my name",
            "someone is pretending to be me online",
            "my pictures are being misused",
            "fake social media profile of me exists",
            "impersonation on instagram",
            "someone using my name and photo",
            "digital identity stolen",
            "fake account with my information",
            "someone made whatsapp with my photo",
            "my profile photo used by someone else",
            "fake linkedin profile made with my details",
            "someone is messaging my contacts pretending to be me",
            "morphed photos of me circulating online",
            "my aadhaar details misused",
            "someone opened account in my name",
            "my pan card misused",
            "fake youtube channel using my identity",
            "someone doing fraud using my name"
        ],
        "IT003": [
            "getting abusive messages on instagram",
            "someone sending me vulgar texts on whatsapp",
            "cyberbullying happening on facebook",
            "being trolled online daily",
            "obscene messages received on telegram",
            "online bully targeting me on twitter",
            "someone posting abuse on my youtube videos",
            "digital harassment through social media",
            "someone sending me inappropriate images online",
            "harassment through online gaming chat",
            "someone making fake posts about me online",
            "abusive emails being received",
            "discord server harassment",
            "reddit harassment happening to me",
            "someone screenshotting my chats and sharing",
            "private conversation leaked online",
            "being doxxed online personal info shared",
            "mass reporting my social media account",
            "coordinated online attack against me",
            # Very specific IT003 online only
            "social media abuse",
            "internet harassment",
            "online platform bullying",
            "website comment abuse",
            "digital platform harassment",
            "revenge content shared online without consent"
        ],
        "IT004": [
            "my gmail was hacked by someone",
            "someone logged into my facebook account",
            "account password changed by someone else",
            "unauthorized person accessed my phone",
            "my instagram account got hacked",
            "someone broke into my email",
            "phone was compromised by hacker",
            "unknown login detected on my account",
            "my account was breached",
            "hacker got into my account",
            "two step verification disabled by hacker",
            "recovery email changed without my permission",
            "someone is posting from my account",
            "my twitter was hacked",
            "linkedin account taken over",
            "someone accessed my cloud storage",
            "icloud account compromised",
            "google account hacked",
            "bank app logged in from unknown device",
            # From real user logs
            "hacking happened to me",
            "hacking aana enna pannanum",
            "my account got hacked",
            "hacking aana",
            "account hacked what to do",
            "suspicious activity on my account"
        ],
        "BNS001": [
            "person took money with false promise",
            "business deceived me completely",
            "I was tricked and lost money",
            "someone made fake agreement",
            "contractor ran away with advance payment",
            "seller gave false information to sell",
            "I got conned by a person",
            "someone cheated me financially",
            "fake business took my money",
            "person disappeared after taking payment",
            "builder cheated me on property",
            "investment scheme was fraud",
            "chit fund company cheated",
            "broker took commission and disappeared",
            "fake job offer scam",
            "marriage fraud happened",
            "rental fraud by owner",
            "vehicle seller cheated me",
            "advance taken by employee and absconded",
            # Very specific BNS001 only phrases  
            "person physically cheated me in person",
            "face to face fraud happened",
            "met person who cheated me",
            "real world business fraud",
            "person ran away with cash payment",
            "paid for land but documents fake"
        ],
        "BNS002": [
            "receiving threatening phone calls daily",
            "someone is blackmailing me",
            "person threatening to harm me",
            "getting scary messages every day",
            "someone threatening my family members",
            "being extorted for money",
            "threats received on whatsapp",
            "person said they will hurt me physically",
            "criminal threatening behavior towards me",
            "fear for my life due to threats",
            "ex partner threatening me",
            "neighbour threatening with violence",
            "political person threatening me",
            "loan recovery agent threatening",
            "goon sent to threaten me",
            "threatening letter received",
            "death threat received online",
            "rowdy threatening my business",
            "gang threatening my family",
            # From real user logs
            "I am being threatened",
            "someone is threatening me daily",
            "getting threatening calls",
            "person threatening to harm me",
            "bayamaruku pannukiraan",
            "threats are coming every day",
            "employer threatening with false case"
        ],
       "BNS003": [
            "neighbour coming to my house and troubling me",
            "boss calling me names at office",
            "colleague physically harassing me at workplace",
            "landlord knocking at odd hours and troubling",
            "someone following me on the street",
            "person waiting outside my house daily",
            "coworker making offensive remarks in person",
            "husband harassing me mentally at home",
            "in laws torturing me daily",
            "domestic harassment at home",
            "person stalking me physically",
            "someone harassing my parents in person",
            "workplace bully in office",
            "sexual harassment by supervisor in person",
            "caste based harassment in village",
            "religious harassment by neighbour",
            "rowdy elements troubling my shop",
            "person spreading rumours in my area",
            "gang harassment in my neighbourhood",
            "property dispute harassment by neighbour"
        ],
        "GUIDE001": [
            "how do I file a police complaint",
            "where can I complain about this",
            "what is the process to file case",
            "I need help with my legal problem",
            "how to register a complaint online",
            "where to go for legal help",
            "what should I do now",
            "how to approach consumer forum",
            "guide me through the process please",
            "I need step by step guidance",
            "what documents do I need to file complaint",
            "can I file complaint online",
            "what are my legal options",
            "how long does complaint process take",
            "is there free legal help available",
            "I dont know what to do",
            "please help me with next steps",
            "which court should I go to",
            "how to get free lawyer",
            "what is consumer forum"
        ],
        "GREET001": [
            "hello there how are you",
            "hi I need some help",
            "hey good morning",
            "namaste aram",
            "vanakkam I need help",
            "greetings from Tamil Nadu",
            "hi aram good evening",
            "hello legal assistant",
            "good morning I have a question",
            "hey there I need guidance",
            "hi how does this work",
            "hello can you help me",
            "good afternoon need help",
            "hey aram what can you do",
            # From real user logs
            "வணக்கம் அறம்",
            "vanakkam aram",
            "hi aram good morning",
            "hi there first time using this"
        ]
    }

    X = []
    y = []

    for intent in data["intents"]:
        intent_id = intent["intent_id"]

        if intent_id == "UNKNOWN001":
            continue

        # Add keywords (each keyword = training example)
        for keyword in intent["keywords"]:
            X.append(keyword)
            y.append(intent_id)

        # Add intent description
        X.append(intent["intent_description"])
        y.append(intent_id)

        # Add recommended steps
        for step in intent.get("recommended_steps", []):
            X.append(step)
            y.append(intent_id)

        # Add augmented sentences
        for sentence in augmented.get(intent_id, []):
            X.append(sentence)
            y.append(intent_id)

    return X, y


def train_model():
    """
    Trains LinearSVC classifier with optimized settings.
    Evaluates with cross-validation for reliable accuracy.
    """
    print("\n🤖 ARAM ML Model Training Started...")
    print("─" * 50)

    X, y = prepare_training_data()
    print(f"✅ Training samples: {len(X)}")
    print(f"✅ Intent categories: {len(set(y))}")
    print(f"✅ Intents: {sorted(set(y))}")

    # Split with stratification
    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=0.15,
        random_state=42,
        stratify=y
    )
    print(f"✅ Training set: {len(X_train)} samples")
    print(f"✅ Test set: {len(X_test)} samples")

    # Build optimized pipeline
    pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(
            ngram_range=(1, 3),
            lowercase=True,
            min_df=1,
            sublinear_tf=True,
            analyzer="word"
        )),
        ("classifier", LinearSVC(
            C=1.0,
            max_iter=5000,
            random_state=42
        ))
    ])

    # Train
    pipeline.fit(X_train, y_train)
    print("✅ Model trained!")

    # Test accuracy
    y_pred = pipeline.predict(X_test)
    accuracy = metrics.accuracy_score(y_test, y_pred)
    print(f"\n📊 Test Accuracy: {accuracy * 100:.2f}%")

    # Cross validation for reliability
    cv_scores = cross_val_score(
        pipeline, X, y, cv=5, scoring="accuracy"
    )
    print(f"📊 Cross-Val Accuracy: "
          f"{cv_scores.mean() * 100:.2f}% "
          f"(±{cv_scores.std() * 100:.2f}%)")

    # Detailed report
    print("\n📋 Classification Report:")
    print(metrics.classification_report(y_test, y_pred))

    # Save model
    with open(MODEL_PATH, "wb") as f:
        pickle.dump(pipeline, f)
    print(f"✅ Model saved: {MODEL_PATH}")
    print("─" * 50)
    print("🎉 Training Complete!")

    return pipeline


if __name__ == "__main__":
    train_model()