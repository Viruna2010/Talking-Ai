# 🤖 Gemini AI Chat — Streamlit Version

## Features
- 💬 Text Chat (gemini-2.5-flash)
- 🎙️ Voice Chat (gemini-2.5-flash-preview-native-audio-dialog)

---

## Local Setup

```bash
# 1. .env හදන්න
cp .env.example .env
# .env ඇතුළේ API key paste කරන්න

# 2. Install
python -m venv venv
source venv/bin/activate      # Mac/Linux
venv\Scripts\activate         # Windows

pip install -r requirements.txt

# 3. Run
streamlit run app.py
```

Browser auto-open වෙනවා: http://localhost:8501

---

## Streamlit Cloud Deploy (Free & Easy!)

1. GitHub එකට push කරන්න
2. https://share.streamlit.io → New app → repo select
3. Settings → Secrets → add:
   ```
   GEMINI_API_KEY = "your_key_here"
   ```
4. Deploy! ✅

---

## ffmpeg (Voice Chat සඳහා)

Voice tab use කරන්න ffmpeg install කරන්න ඕන:

- **Windows:** https://ffmpeg.org/download.html → PATH add කරන්න
- **Mac:** `brew install ffmpeg`
- **Linux:** `sudo apt install ffmpeg`
