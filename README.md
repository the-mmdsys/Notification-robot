# Notification robot — (ِDorf) (clean & ready)

> A tiny, badass Telegram notifier/broadcast bot. Simple, reliable, and made for people who want stuff done — not fiddled with.

![status-badge](https://img.shields.io/badge/status-alpha-orange) ![python](https://img.shields.io/badge/python-3.9%2B-blue) ![license](https://img.shields.io/badge/license-MIT-green)

---

## What is this?

Dorf is a minimal Telegram bot that lets users subscribe/unsubscribe and lets the admin broadcast messages (or forward a replied message) to all subscribers. No fluff, no overengineering — just useful features and an easy local GUI for starting/stopping and creating DB backups.

---

## Features

* `/start` with inline buttons: **Subscribe / Unsubscribe**
* `/subscribe` and `/unsubscribe` commands
* Admin-only `/broadcast` (text or forward by replying)
* Async SQLite (`aiosqlite`) backend — small & portable
* `gui.py`(in main) — lightweight Tkinter controller for start/stop, logs, and DB backups
* Docker-ready 

---

## Quick start (local)

1. Clone repo:

```bash
git clone https://github.com/your-username/dorf-bot.git
cd dorf-bot
```

2. Create & activate virtualenv (recommended):

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Linux / macOS
python -m venv .venv
source .venv/bin/activate
```

3. Install requirements:

```bash
pip install -r requirements.txt
```

4. Edit `config.py` (see below) with your TOKEN and ADMIN\_ID. **Do not commit credentials to public git.**

5. Run:

```bash
python bot.py
```

6. (Optional) Start the GUI controller:

```bash
python main.py
```

---

## Docker 

If you want Docker, make sure `config.py` has the correct values **before** building the image (do **not** commit them).

Build and run:

```bash
docker build -t dorf-bot .
docker run -d --name dorf-bot dorf-bot
# follow logs:
docker logs -f dorf-bot
```

> Tip: Keep `config.py` out of your git history (`.gitignore` it) — or mount a safe file into the container at runtime.

---

## Safe & simple config (edit `config.py`)

This project expects `config.py`. To keep the README clean, populate `config.py` directly:

## Commands & Usage

* `/start` — welcome message with inline subscribe/unsubscribe buttons
* `/subscribe` — subscribe (same as button)
* `/unsubscribe` — unsubscribe (same as button)
* `/broadcast <text>` — admin-only: send `<text>` to all subscribers
* `reply` to some message + `/broadcast` — forwards that message to all subscribers

**Behavior:** Bot stores subscribers in `dorf_bot.db` (SQLite). GUI shows subscriber count and can backup DB into `backups_gui/`.

---

## Files you care about

* `mian.py` — main bot code
* `database.py` — async SQLite wrapper
* `config.py` — set `TOKEN` and `ADMIN_ID` here
* `gui.py`(in main) — Tkinter controller for start/stop/logs/backups
* `Dockerfile` & `.dockerignore` — containerization



```
python-telegram-bot==20.5
aiosqlite==0.17.0
python-dotenv==0.21.0
```

---

## Troubleshooting (common stuff)

* `TOKEN not set` or auth errors → you forgot to edit `config.py` or used a wrong token. Fix it and restart the bot.
* Bot doesn't send messages to some users → they may have blocked the bot or privacy settings prevent messages. Can't help Telegram drama.
* DB errors → check file permissions and that `dorf_bot.db` exists in the working directory.
* Docker container crashes → `docker logs <container>` is your friend. Check config values and working directory.

---

## Development & contrib

Want to add features? Nice.

1. Fork, branch name `feature/your-thing`
2. Keep code & comments in **English**
3. Make small, testable commits
4. Open PR with clear description & screenshots/GIF if helpful

Code style: clean, simple, readable. Tests welcome.

---

## Good practices (read this — you’ll thank me later)

* Never commit secrets. Ever. Use a private repo, or better: mount a secrets file on the server.
* Backup DB regularly (GUI or cron/copy).
* If token leaks: regenerate it NOW. Don’t be lazy.

---

## License

MIT — do whatever, just don’t pretend you wrote the whole thing if you forked it and added a typo.



Say which one you want and I’ll spit out the file right here. No drama, no waiting — do it now. 😎
