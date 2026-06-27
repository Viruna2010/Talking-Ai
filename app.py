import os
import asyncio
import base64
import streamlit as st
from google import genai
from google.genai import types
from audiorecorder import audiorecorder

# ── API Key ───────────────────────────────────────────────────────────────────
GEMINI_API_KEY = ""
try:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
except:
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(page_title="Gemini AI Chat", page_icon="🤖", layout="centered")

if not GEMINI_API_KEY:
    GEMINI_API_KEY = st.sidebar.text_input("🔑 Gemini API Key", type="password")
    if not GEMINI_API_KEY:
        st.warning("⚠️ Sidebar එකේ Gemini API Key paste කරන්න.")
        st.stop()

client = genai.Client(api_key=GEMINI_API_KEY)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("⚙️ Settings")
    mode = st.radio("Mode", ["💬 Text Chat", "🎙️ Voice Chat"])
    if st.button("🔄 Chat Reset"):
        st.session_state.messages = []
        st.session_state.audio_history = []
        st.session_state.history = []
        st.rerun()
    st.markdown("---")
    st.caption("gemini-2.5-flash · native-audio-dialog")

# ── Session state ─────────────────────────────────────────────────────────────
if "messages"      not in st.session_state: st.session_state.messages      = []
if "audio_history" not in st.session_state: st.session_state.audio_history = []
if "history"       not in st.session_state: st.session_state.history       = []

# ── Title ─────────────────────────────────────────────────────────────────────
st.title("🤖 Gemini AI Chat")
st.caption("Powered by Gemini 2.5 Flash · Native Audio Dialog")
st.divider()

# ═══════════════════════════════════════════════════════════════════════════════
#  TEXT CHAT
# ═══════════════════════════════════════════════════════════════════════════════
if mode == "💬 Text Chat":

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    user_input = st.chat_input("Message ලියන්න...")
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        st.session_state.history.append(
            types.Content(role="user", parts=[types.Part.from_text(text=user_input)])
        )

        with st.chat_message("user"):
            st.markdown(user_input)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    response = client.models.generate_content(
                        model="gemini-2.5-flash",
                        contents=st.session_state.history,
                    )
                    reply = response.text
                    st.session_state.history.append(
                        types.Content(role="model", parts=[types.Part.from_text(text=reply)])
                    )
                except Exception as e:
                    reply = f"❌ Error: {e}"
            st.markdown(reply)

        st.session_state.messages.append({"role": "assistant", "content": reply})

# ═══════════════════════════════════════════════════════════════════════════════
#  VOICE CHAT
# ═══════════════════════════════════════════════════════════════════════════════
else:
    st.info("🎙️ Record button eka click කරලා කතා කරන්න.")

    audio = audiorecorder("🔴 Record", "⏹️ Stop")

    if len(audio) > 0:
        st.audio(audio.export().read(), format="audio/wav")

        with st.spinner("🧠 Gemini processing..."):
            wav_bytes = audio.export(format="wav").read()
            b64_audio = base64.b64encode(wav_bytes).decode()

            async def run_audio():
                config = types.GenerateContentConfig(
                    response_modalities=["AUDIO"],
                    speech_config=types.SpeechConfig(
                        voice_config=types.VoiceConfig(
                            prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name="Aoede")
                        )
                    ),
                )
                response = await client.aio.models.generate_content(
                    model="gemini-2.5-flash-preview-native-audio-dialog",
                    contents=types.Content(
                        role="user",
                        parts=[types.Part.from_bytes(
                            data=base64.b64decode(b64_audio),
                            mime_type="audio/wav"
                        )]
                    ),
                    config=config,
                )
                out_audio_b64 = ""
                transcript    = ""
                for part in response.candidates[0].content.parts:
                    if part.inline_data and part.inline_data.mime_type.startswith("audio/"):
                        out_audio_b64 = base64.b64encode(part.inline_data.data).decode()
                    if hasattr(part, "text") and part.text:
                        transcript = part.text
                return out_audio_b64, transcript

            try:
                out_audio_b64, transcript = asyncio.run(run_audio())
                st.session_state.audio_history.append({
                    "transcript": transcript,
                    "audio_b64":  out_audio_b64,
                })
            except Exception as e:
                st.error(f"❌ Error: {e}")

    if st.session_state.audio_history:
        st.divider()
        st.subheader("📼 Conversation History")
        for i, item in enumerate(reversed(st.session_state.audio_history)):
            with st.expander(f"Turn {len(st.session_state.audio_history) - i}", expanded=(i == 0)):
                if item["transcript"]:
                    st.markdown(f"**📝 Transcript:** {item['transcript']}")
                if item["audio_b64"]:
                    st.audio(base64.b64decode(item["audio_b64"]), format="audio/wav")
