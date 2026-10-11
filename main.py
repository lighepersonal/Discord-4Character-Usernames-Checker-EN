import requests
import random
import string
import time
from datetime import datetime

# ========== Settings ==========
# Free version: no proxies. Every check comes straight from your own internet
# connection, so it checks one name at a time and slows down whenever Discord asks.
DEFAULT_DELAY = 3    # seconds between checks
MIN_DELAY = 1        # never go faster than this
MAX_DELAY = 30       # upper limit for the automatic slow-down
FALLBACK_WAIT = 60   # wait this long if Discord rate-limits without saying for how long

API_URL = "https://discord.com/api/v9/unique-username/username-attempt-unauthed"
ALLOWED_CHARS = string.ascii_lowercase + string.digits + "_."

total_checked = 0
available_count = 0
taken_count = 0
error_count = 0
rate_limit_count = 0

# Stores usernames already checked (prevents checking the same one twice)
tried_usernames = set()

def load_tried_usernames():
    global tried_usernames
    for filename in ("available.txt", "taken.txt"):
        try:
            with open(filename, "r", encoding="utf-8") as f:
                for line in f:
                    # Format: [timestamp] username
                    parts = line.strip().split("] ")
                    if len(parts) == 2:
                        tried_usernames.add(parts[1])
        except FileNotFoundError:
            continue
    if tried_usernames:
        print(
            f"📂 Loaded {len(tried_usernames)} previously "
            f"checked usernames (they will be skipped)"
        )

def generate_username(length=4):
    while True:
        username = ''.join(
            random.choice(ALLOWED_CHARS)
            for _ in range(length)
        )
        if ".." in username:
            continue
        # If this username was already checked, generate a new one
        if username in tried_usernames:
            continue
        tried_usernames.add(username)
        return username

def save_available(username):
    with open("available.txt", "a", encoding="utf-8") as f:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"[{timestamp}] {username}\n")

def save_taken(username):
    with open("taken.txt", "a", encoding="utf-8") as f:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"[{timestamp}] {username}\n")

def get_retry_after(response):
    # Discord says how long to wait, either in the JSON body or the Retry-After header
    try:
        return float(response.json()["retry_after"])
    except (ValueError, KeyError, TypeError):
        pass
    try:
        return float(response.headers["Retry-After"])
    except (KeyError, ValueError):
        return FALLBACK_WAIT

def check_username(username):
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Linux; Android 15; Pixel 9) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/151.0.0.0 Mobile Safari/537.36"
        ),
        "Content-Type": "application/json",
        "Accept": "*/*",
        "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
        "Origin": "https://discord.com",
        "Referer": "https://discord.com/register",
        "X-Discord-Locale": "ko",
        "X-Discord-Timezone": "Asia/Seoul"
    }

    payload = {
        "username": username
    }

    try:
        response = requests.post(
            API_URL,
            json=payload,
            headers=headers,
            timeout=10
        )

        if response.status_code == 200:
            try:
                data = response.json()
            except ValueError:
                return "error", 0

            if "taken" not in data:
                return "error", 0

            if data["taken"] is True:
                return "taken", 0

            if data["taken"] is False:
                return "available", 0

            return "error", 0

        elif response.status_code == 429:
            return "rate_limit", get_retry_after(response)

        else:
            return "error", 0

    except requests.exceptions.Timeout:
        return "timeout", 0

    except requests.exceptions.RequestException:
        return "exception", 0

    except Exception:
        return "exception", 0

def print_stats():
    print(
        f"📊 Checked: {total_checked} | "
        f"✅ Available: {available_count} | "
        f"❌ Taken: {taken_count} | "
        f"⚠️ Errors: {error_count} | "
        f"⏳ Rate limits: {rate_limit_count}"
    )

def scan(delay=DEFAULT_DELAY):
    global total_checked
    global available_count
    global taken_count
    global error_count
    global rate_limit_count

    print("=" * 60)
    print("Discord 4-Character Username Checker | Made by Koda")
    print("Free version: no proxies, one check at a time")
    print("=" * 60)
    print(f"Delay   : {delay:g}s between checks (slows down automatically)")
    print("Length  : 4 characters")
    print("Output  : available.txt / taken.txt")
    print("Stop    : Ctrl + C")
    print("=" * 60)

    load_tried_usernames()

    print("=" * 60)
    print()

    try:
        while True:
            username = generate_username(4)
            retry_count = 0

            while True:
                result, wait = check_username(username)

                if result == "rate_limit":
                    # Wait as long as Discord asks, go a bit slower from now on,
                    # then check the same name again (it is not skipped)
                    rate_limit_count += 1
                    delay = min(delay + 1, MAX_DELAY)
                    print(
                        f"⏳ Rate limited, waiting {wait:.1f}s "
                        f"(delay is now {delay:g}s)"
                    )
                    time.sleep(wait + 1)
                    continue

                if result in ("exception", "timeout") and retry_count < 3:
                    retry_count += 1
                    time.sleep(2 ** retry_count)
                    continue

                break

            total_checked += 1

            if result == "available":
                available_count += 1
                save_available(username)
                print(
                    f"[{total_checked:5d}] "
                    f"✅ Available {username}"
                )

            elif result == "taken":
                taken_count += 1
                save_taken(username)
                print(
                    f"[{total_checked:5d}] "
                    f"❌ Taken {username}"
                )

            else:
                error_count += 1
                print(
                    f"[{total_checked:5d}] "
                    f"⚠️ Error {username} ({result})"
                )

            if total_checked % 10 == 0:
                print_stats()

            time.sleep(delay)

    except KeyboardInterrupt:
        print("\n\n⏹️ Stopping...")

    print()
    print("=" * 60)
    print("Final results")
    print("=" * 60)
    print(f"Total checked : {total_checked}")
    print(f"✅ Available   : {available_count}")
    print(f"❌ Taken       : {taken_count}")
    print(f"⚠️ Errors      : {error_count}")
    print(f"⏳ Rate limits : {rate_limit_count}")
    print("=" * 60)

if __name__ == "__main__":
    try:
        delay = float(
            input(f"Seconds between checks (recommended: {DEFAULT_DELAY}): ")
        )

    except ValueError:
        delay = DEFAULT_DELAY

    scan(max(delay, MIN_DELAY))
