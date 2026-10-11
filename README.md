# Discord 4-Character Username Checker (Free Version)

A Python **username checker** that randomly generates 4-character Discord usernames and checks whether they are available.

It sends each generated username to Discord's username API and saves available and already-taken usernames to separate files.

> This is an English translation of [camt4372/Discord-4Character-Usernames-Checker](https://github.com/camt4372/Discord-4Character-Usernames-Checker) (made by Koda), changed so it runs **without paid proxies**.

---

## 🆓 What's Different From the Original

| Original | Free version |
| -------- | ------------ |
| Requires paid ThorData proxies | No proxies — runs from your own internet connection |
| Several threads at once (3–5 recommended) | One check at a time, with a pause between checks |
| On a rate limit: switches proxy and skips the name | On a rate limit: waits as long as Discord asks, slows down, and re-checks the same name |
| SSL certificate verification turned off | SSL certificate verification on (normal HTTPS) |
| Korean on-screen text | English on-screen text |

Because everything comes from your own connection, it is much slower than the proxy version. Discord allows only about 20 checks from one IP before making it wait roughly 30 minutes, so expect around 40 checks per hour no matter what delay you choose.

---

## ✨ Main Features

* Automatically generates 4-character Discord usernames
* Uses lowercase letters, digits, `_`, and `.` (never `..`)
* Never checks the same username twice, even across runs
* Automatically waits and slows down when Discord rate-limits
* Retries on network errors (up to 3 times, waiting 2s, 4s, then 8s)
* Saves available and taken usernames to files
* Prints live stats every 10 checks and final results when stopped

---

## 🖥️ Requirements

* Python **3.8 or later**
* An internet connection
* The `requests` library

---

## 🚀 Setup and Running

### 1. Create a virtual environment and install `requests`

Run these inside the project folder:

```bash
python3 -m venv .venv
.venv/bin/pip install requests
```

### 2. Run the checker

```bash
.venv/bin/python main.py
```

### 3. Choose the speed

You'll be asked:

```text
Seconds between checks (recommended: 3):
```

Press Enter for the default of 3 seconds, or type a number. Anything below 1 second is raised to 1.

### 4. Stop it

Press **Ctrl + C**. The final results are printed and everything found so far is already saved.

---

## ⚙️ Settings

These are at the top of `main.py`:

| Setting | Default | What it does |
| ------- | ------- | ------------ |
| `DEFAULT_DELAY` | `3` | Seconds between checks if you just press Enter |
| `MIN_DELAY` | `1` | The fastest it will ever go |
| `MAX_DELAY` | `30` | The slowest the automatic slow-down will go |
| `FALLBACK_WAIT` | `60` | Seconds to wait if Discord rate-limits without saying for how long |

---

## 📡 How the Checker Works

For each username it sends this to `https://discord.com/api/v9/unique-username/username-attempt-unauthed` — the same check Discord's sign-up page does when you type a username:

```json
{
    "username": "abcd"
}
```

| Response | Handling |
| -------- | -------- |
| `200` with `"taken": false` | Saved to `available.txt` |
| `200` with `"taken": true` | Saved to `taken.txt` |
| `429` (rate limited) | Waits as long as Discord asks, adds 1 second to the delay (up to `MAX_DELAY`), then re-checks the same name |
| Timeout / network error | Retries up to 3 times (waiting 2s, 4s, 8s), then counts it as an error |
| Anything else | Counted as an error |

> Discord's API endpoint, response format and username rules may change, so there is no guarantee this keeps working.

---

## 💾 Output Files

Created in the folder you run the checker from.

### ✅ `available.txt`

```text
[2026-08-16 14:30:21] ab1_
[2026-08-16 14:30:25] x9_z
```

### ❌ `taken.txt`

```text
[2026-08-16 14:30:22] abc1
[2026-08-16 14:30:23] zzzz
```

On the next run, every username in these files is skipped.

---

## 📊 Live Output

Each check prints a line, with a summary every 10 checks:

```text
[    9] ❌ Taken babx
[   10] ✅ Available 3bcj
📊 Checked: 10 | ✅ Available: 1 | ❌ Taken: 9 | ⚠️ Errors: 0 | ⏳ Rate limits: 0
⏳ Rate limited, waiting 2.5s (delay is now 4s)
```

Final results when you press Ctrl + C:

```text
⏹️ Stopping...

============================================================
Final results
============================================================
Total checked : 1000
✅ Available   : 5
❌ Taken       : 993
⚠️ Errors      : 2
⏳ Rate limits : 4
============================================================
```

---

## 🔧 Troubleshooting

### Lots of rate limits

This is normal. Discord allows only about 20 checks per IP before a wait of roughly 30 minutes, and the checker waits it out by itself. A higher delay won't get you through more names; it just spreads the same checks out.

### Every check is an error

1. Check your internet connection
2. Discord may have changed or blocked the endpoint
3. Discord may have changed the response format

---

## 📞 Original Author

Questions about the original program go to the author's Discord:

* [Discord support server](https://discord.gg/6c5H5dEEmG)
* [zzp.kr/discord](https://zzp.kr/discord)

---

# 📚 For Study and Learning Purposes

> ⚠️ **From the original author:** please use this program only to study and learn skills such as Python programming, HTTP requests, API communication and multithreading.
>
> Using it to send excessive requests to Discord or third-party services, to get around a service's usage restrictions or security policies, or for any other inappropriate purpose is not recommended.
>
> Before using the program, be sure to check the service's terms of use and related policies.
