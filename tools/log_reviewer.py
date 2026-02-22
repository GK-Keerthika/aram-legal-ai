# tools/log_reviewer.py
# Purpose: Review conversation logs to improve ARAM
# Run weekly: python -m tools.log_reviewer

import json
import os
from datetime import datetime, timedelta
from collections import Counter

LOGS_FILE = os.path.join("logs", "conversations.json")

# ── Color codes for terminal ──────────────────────────
GREEN  = "\033[92m"
YELLOW = "\033[93m"
RED    = "\033[91m"
BLUE   = "\033[94m"
GOLD   = "\033[33m"
RESET  = "\033[0m"
BOLD   = "\033[1m"


def load_logs() -> list:
    """Loads all conversation logs."""
    if not os.path.exists(LOGS_FILE):
        print(f"{RED}No logs found at {LOGS_FILE}{RESET}")
        return []
    with open(LOGS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    # Handle both formats — plain list or wrapped object
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        for key in ["conversations", "logs", "data"]:
            if key in data:
                return data[key]
        return list(data.values())[0] if data else []
    return []


def parse_ts(ts_string: str) -> datetime:
    """Safely parse timestamp string in any format."""
    try:
        return datetime.strptime(ts_string, "%Y-%m-%d %H:%M:%S")
    except Exception:
        try:
            return datetime.fromisoformat(ts_string)
        except Exception:
            return datetime.now()


def get_intent(log: dict) -> str:
    """Gets intent from log — handles both key names."""
    return log.get("detected_intent") or log.get("intent", "UNKNOWN")


def print_header():
    print(f"\n{GOLD}{BOLD}")
    print("═" * 60)
    print("   அறம் (ARAM) — Log Reviewer & Training Suggester")
    print("   Weekly Review Tool for Continuous Improvement")
    print("═" * 60)
    print(f"{RESET}")


def print_section(title: str):
    print(f"\n{BLUE}{BOLD}{'─' * 60}")
    print(f"  {title}")
    print(f"{'─' * 60}{RESET}")


def summary_stats(logs: list):
    """Shows overall conversation statistics."""
    print_section("📊 OVERALL STATISTICS")

    total = len(logs)
    print(f"  Total conversations logged : {GREEN}{BOLD}{total}{RESET}")

    today = datetime.now().date()
    today_logs = [
        l for l in logs
        if parse_ts(l.get("timestamp", "")).date() == today
    ]
    print(f"  Conversations today        : {GREEN}{len(today_logs)}{RESET}")

    week_ago = datetime.now() - timedelta(days=7)
    week_logs = [
        l for l in logs
        if parse_ts(l.get("timestamp", "")) >= week_ago
    ]
    print(f"  Conversations this week    : {GREEN}{len(week_logs)}{RESET}")

    # Intent distribution
    intents = [get_intent(l) for l in logs]
    intent_counts = Counter(intents)

    print(f"\n  {BOLD}Intent Distribution:{RESET}")
    for intent, count in intent_counts.most_common():
        bar = "█" * min(count, 30)
        color = RED if intent in [
            "UNKNOWN001", "OFFENSIVE", "IRRELEVANT"
        ] else GREEN
        print(f"    {intent:<15} {color}{bar}{RESET} {count}")


def weekly_trend(logs: list):
    """Shows day-by-day trend for last 7 days."""
    print_section("📈 LAST 7 DAYS TREND")

    for i in range(6, -1, -1):
        day = datetime.now().date() - timedelta(days=i)
        count = sum(
            1 for l in logs
            if parse_ts(l.get("timestamp", "")).date() == day
        )
        bar = "█" * count if count > 0 else "·"
        label = "Today" if i == 0 else day.strftime("%a %d %b")
        color = GOLD if i == 0 else RESET
        print(f"  {color}{label:<12}{RESET} {GREEN}{bar}{RESET} {count}")


def language_breakdown(logs: list):
    """Shows language distribution."""
    print_section("🌐 LANGUAGE BREAKDOWN")

    tamil_count    = 0
    tanglish_count = 0
    english_count  = 0

    tanglish_words = [
        "panam", "emattu", "hack", "thondara",
        "pannittaan", "kudukala", "varala", "pochu"
    ]

    for l in logs:
        inp = l.get("user_input", "")
        if any(ord(c) > 0x0B80 for c in inp):
            tamil_count += 1
        elif any(w in inp.lower() for w in tanglish_words):
            tanglish_count += 1
        else:
            english_count += 1

    total = len(logs) or 1
    print(f"  English  : {GREEN}{english_count}{RESET} "
          f"({english_count * 100 // total}%)")
    print(f"  Tamil    : {GREEN}{tamil_count}{RESET} "
          f"({tamil_count * 100 // total}%)")
    print(f"  Tanglish : {GREEN}{tanglish_count}{RESET} "
          f"({tanglish_count * 100 // total}%)")


def popular_queries(logs: list):
    """Shows most common successful legal queries."""
    print_section("🔥 MOST POPULAR QUERIES (Successful)")

    skip = ["UNKNOWN001", "OFFENSIVE", "IRRELEVANT", "GENERAL", "GREET001"]
    successful = [
        l for l in logs
        if get_intent(l) not in skip
    ]

    if not successful:
        print(f"  {YELLOW}No successful legal queries yet.{RESET}")
        return

    queries = [
        l.get("user_input", "").lower().strip()
        for l in successful
    ]
    query_counts = Counter(queries)

    print(f"  Top queries users are asking:\n")
    for query, count in query_counts.most_common(10):
        print(f"  {GREEN}×{count}{RESET}  \"{query}\"")


def missed_queries(logs: list):
    """Shows queries ARAM couldn't understand — training opportunities."""
    print_section("⚠️  MISSED QUERIES — Add These to Training Data!")

    unknown = [
        l for l in logs
        if get_intent(l) == "UNKNOWN001"
    ]

    if not unknown:
        print(f"  {GREEN}✅ No missed queries! ARAM understood everything.{RESET}")
        return

    print(f"  {YELLOW}Found {len(unknown)} queries ARAM didn't understand:{RESET}")
    print(f"  {YELLOW}Add these to model_trainer.py augmented data!{RESET}\n")

    seen = set()
    for log in unknown:
        query = log.get("user_input", "").strip()
        if query and query not in seen:
            seen.add(query)
            ts = log.get("timestamp", "")[:10]
            print(f"  {RED}✗{RESET} [{ts}] \"{query}\"")

    print(f"\n  {BOLD}💡 Action: Copy these to the correct intent in{RESET}")
    print(f"  {BOLD}   engine/model_trainer.py → retrain model{RESET}")


def offensive_queries(logs: list):
    """Shows offensive and irrelevant queries."""
    print_section("🚨 OFFENSIVE / IRRELEVANT QUERIES")

    offensive = [
        l for l in logs
        if get_intent(l) == "OFFENSIVE"
    ]
    irrelevant = [
        l for l in logs
        if get_intent(l) == "IRRELEVANT"
    ]

    if offensive:
        print(f"  {RED}Offensive queries ({len(offensive)}):{RESET}")
        for log in offensive[-5:]:
            print(f"    • \"{log.get('user_input', '')}\"")

    if irrelevant:
        print(f"\n  {YELLOW}Irrelevant queries ({len(irrelevant)}):{RESET}")
        for log in irrelevant[-5:]:
            print(f"    • \"{log.get('user_input', '')}\"")

    if not offensive and not irrelevant:
        print(f"  {GREEN}✅ No offensive or irrelevant queries found.{RESET}")


def training_suggestions(logs: list):
    """Suggests which intent unknown queries might belong to."""
    print_section("💡 TRAINING SUGGESTIONS")

    unknown = [
        l.get("user_input", "").strip()
        for l in logs
        if get_intent(l) == "UNKNOWN001"
        and l.get("user_input", "").strip()
    ]

    if not unknown:
        print(f"  {GREEN}✅ No training suggestions needed right now!{RESET}")
        return

    consumer_hints = [
        "refund", "product", "delivery", "order", "money back",
        "shopping", "amazon", "flipkart", "meesho", "panam",
        "return", "exchange", "damaged", "service"
    ]
    cyber_hints = [
        "hack", "fraud", "otp", "account", "password", "cyber",
        "online", "scam", "phishing", "upi", "bank", "gpay",
        "phonepe", "transfer", "deducted"
    ]
    bns_hints = [
        "cheat", "threat", "harass", "blackmail", "trick",
        "extort", "ematt", "mirat", "bully", "intimidat",
        "stalk", "abuse", "threaten"
    ]

    print(f"  Review these unknown queries and add to training:\n")
    for query in unknown[:20]:
        q_lower = query.lower()
        if any(h in q_lower for h in consumer_hints):
            hint = f"{BLUE}→ Possible CP intent (consumer){RESET}"
        elif any(h in q_lower for h in cyber_hints):
            hint = f"{GREEN}→ Possible IT intent (cyber){RESET}"
        elif any(h in q_lower for h in bns_hints):
            hint = f"{YELLOW}→ Possible BNS intent (criminal){RESET}"
        else:
            hint = f"{RED}→ New category or truly irrelevant{RESET}"
        print(f"  • \"{query}\" {hint}")

    print(f"\n  {BOLD}Steps to improve ARAM:{RESET}")
    print(f"  1. Review queries above")
    print(f"  2. Add to correct intent in engine/model_trainer.py")
    print(f"  3. Run: python -m engine.model_trainer")
    print(f"  4. Restart: python app.py")
    print(f"  5. Run this reviewer again to verify improvement!")


def general_breakdown(logs: list):
    """Shows what kind of general conversations happened."""
    print_section("💬 GENERAL CONVERSATION BREAKDOWN")

    general = [
        l for l in logs
        if get_intent(l) == "GENERAL"
    ]

    if not general:
        print(f"  {YELLOW}No general conversations yet.{RESET}")
        return

    print(f"  Total general conversations: {GREEN}{len(general)}{RESET}")

    # Show sample general queries
    queries = [l.get("user_input", "").strip() for l in general]
    query_counts = Counter(queries)

    print(f"\n  Most repeated general queries:")
    for query, count in query_counts.most_common(5):
        print(f"  {GREEN}×{count}{RESET}  \"{query}\"")


def export_unknown(logs: list):
    """Exports unknown queries to a text file for easy review."""
    unknown = list(set([
        l.get("user_input", "").strip()
        for l in logs
        if get_intent(l) == "UNKNOWN001"
        and l.get("user_input", "").strip()
    ]))

    if not unknown:
        return

    export_path = os.path.join("logs", "missed_queries.txt")
    with open(export_path, "w", encoding="utf-8") as f:
        f.write("அறம் (ARAM) — Missed Queries Export\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
        f.write(f"Total missed: {len(unknown)}\n")
        f.write("=" * 50 + "\n\n")
        f.write("ACTION: Add these to engine/model_trainer.py\n")
        f.write("        under the correct intent category\n")
        f.write("        Then run: python -m engine.model_trainer\n\n")
        f.write("─" * 50 + "\n\n")
        for i, q in enumerate(unknown, 1):
            f.write(f"{i}. {q}\n")

    print_section("📁 EXPORT COMPLETE")
    print(f"  {GREEN}✅ Missed queries saved to:{RESET}")
    print(f"  {BOLD}logs/missed_queries.txt{RESET}")
    print(f"  Open this file to review and add to training!")


def run_review():
    """Main review runner — runs all checks."""
    print_header()

    logs = load_logs()

    if not logs:
        print(f"\n{YELLOW}No conversations logged yet.")
        print(f"Start chatting with ARAM and run this again!{RESET}\n")
        return

    summary_stats(logs)
    weekly_trend(logs)
    language_breakdown(logs)
    popular_queries(logs)
    general_breakdown(logs)
    missed_queries(logs)
    offensive_queries(logs)
    training_suggestions(logs)
    export_unknown(logs)

    print(f"\n{GOLD}{BOLD}{'═' * 60}")
    print(f"  ✅ Review Complete!")
    print(f"  Run this weekly to keep ARAM improving.")
    print(f"  Retrain after adding new queries:")
    print(f"  → python -m engine.model_trainer")
    print(f"{'═' * 60}{RESET}\n")


if __name__ == "__main__":
    run_review()