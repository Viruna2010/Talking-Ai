import os
import asyncio
import base64
import streamlit as st
import streamlit.components.v1 as components
from google import genai
from google.genai import types

# ── API Key ───────────────────────────────────────────────────────────────────
st.set_page_config(page_title="Gemini AI Chat", page_icon="🤖", layout="centered")

GEMINI_API_KEY = ""
try:
    GEMINI_API_KEY = str(st.secrets["GEMINI_API_KEY"]).strip()
except Exception:
    pass

if not GEMINI_API_KEY:
    GEMINI_API_KEY = str(os.getenv("GEMINI_API_KEY", "")).strip()

if not GEMINI_API_KEY:
    GEMINI_API_KEY = st.sidebar.text_input("🔑 Gemini API Key", type="password")
    if not GEMINI_API_KEY:
        st.warning("⚠️ Sidebar එකේ Gemini API Key paste කරන්න.")
        st.stop()

# Strip any accidental quotes from secrets
GEMINI_API_KEY = GEMINI_API_KEY.strip('"').strip("'")

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
if "audio_b64_input" not in st.session_state: st.session_state.audio_b64_input = ""

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
#  VOICE CHAT — browser-native MediaRecorder (no pydub/pyaudioop needed)
# ═══════════════════════════════════════════════════════════════════════════════
else:
    st.info("🎙️ Record button eka click කරලා කතා කරන්න. Gemini audio වලින් reply කරයි.")

    # Browser records and returns base64 webm via query param trick using st.query_params
    recorder_html = """
    <style>
      button { padding:12px 28px; font-size:1rem; border:none; border-radius:8px; cursor:pointer; }
      #recBtn { background:#e84545; color:#fff; }
      #recBtn.recording { background:#ff2222; }
      #status { margin-top:8px; font-size:.9rem; color:#aaa; }
    </style>
    <button id="recBtn" onclick="toggle()">🔴 Record</button>
    <div id="status">Button click කරන්න</div>
    <script>
      let recorder, chunks=[], recording=false;
      async function toggle(){
        if(!recording){
          const stream = await navigator.mediaDevices.getUserMedia({audio:true});
          recorder = new MediaRecorder(stream);
          chunks=[];
          recorder.ondataavailable = e => chunks.push(e.data);
          recorder.onstop = () => {
            const blob = new Blob(chunks,{type:'audio/webm'});
            const reader = new FileReader();
            reader.onloadend = () => {
              const b64 = reader.result.split(',')[1];
              // Send to Streamlit via postMessage
              window.parent.postMessage({type:'audio_b64', data: b64}, '*');
            };
            reader.readAsDataURL(blob);
          };
          recorder.start();
          recording=true;
          document.getElementById('recBtn').textContent='⏹️ Stop';
          document.getElementById('recBtn').classList.add('recording');
          document.getElementById('status').textContent='🔴 Recording...';
        } else {
          recorder.stop();
          recorder.stream.getTracks().forEach(t=>t.stop());
          recording=false;
          document.getElementById('recBtn').textContent='🔴 Record';
          document.getElementById('recBtn').classList.remove('recording');
          document.getElementById('status').textContent='✅ Done — processing...';
        }
      }
    </script>
    """

    components.html(recorder_html, height=120)

    # Receive audio via st.query_params workaround using a text_input hidden bridge
    audio_input = st.text_input("audio_bridge", key="audio_bridge", label_visibility="collapsed")

    st.markdown("""
    <script>
    window.addEventListener('message', function(e){
      if(e.data && e.data.type==='audio_b64'){
        const inputs = window.parent.document.querySelectorAll('input[data-testid="stTextInput"]');
        inputs.forEach(i=>{
          const nativeInput = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype,'value');
          nativeInput.set.call(i, e.data.data);
          i.dispatchEvent(new Event('input', {bubbles:true}));
        });
      }
    });
    </script>
    """, unsafe_allow_html=True)

    if audio_input and audio_input != st.session_state.audio_b64_input:
        st.session_state.audio_b64_input = audio_input

        with st.spinner("🧠 Gemini processing..."):
            async def run_audio(b64):
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
                            data=base64.b64decode(b64),
                            mime_type="audio/webm"
                        )]
                    ),
                    config=config,
                )
                out_b64, transcript = "", ""
                for part in response.candidates[0].content.parts:
                    if part.inline_data and part.inline_data.mime_type.startswith("audio/"):
                        out_b64 = base64.b64encode(part.inline_data.data).decode()
                    if hasattr(part, "text") and part.text:
                        transcript = part.text
                return out_b64, transcript

            try:
                out_b64, transcript = asyncio.run(run_audio(audio_input))
                st.session_state.audio_history.append({
                    "transcript": transcript,
                    "audio_b64": out_b64,
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
