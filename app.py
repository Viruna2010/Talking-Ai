import streamlit as st
from streamlit_webrtc import webrtc_streamer, WebRtcMode, AudioProcessorBase
from google import genai
import av

# අලුත් SDK එක පාවිච්චි කරලා Client එක හදමු
client = genai.Client(api_key="AQ.Ab8RN6KO4M3SlxL3dmmjuUULylCZr-IZT1lxxXfIj7emV9_Fyw")

st.title("Viruna's Live AI")

# CSS - ඇස් පිල්ලම් ගැසීම
st.markdown("""
<style>
    @keyframes blink { 0%, 100% { transform: scaleY(1); } 50% { transform: scaleY(0.1); } }
    .avatar { animation: blink 4s infinite; width: 300px; display: block; margin: auto; }
</style>
""", unsafe_allow_html=True)

# Avatar එක (ඔයාගේ ලින්ක් එක දාගන්න)
st.markdown('<img src="https://i.imgur.com/your_image.png" class="avatar">', unsafe_allow_html=True)

# Audio Processor එක
class AudioProcessor(AudioProcessorBase):
    def recv(self, frame: av.AudioFrame) -> av.AudioFrame:
        # මෙතනට ඔයාගේ audio frame එක ලැබෙනවා.
        # දැනට අපි frame එක ඒ විදිහටම ආපසු යවනවා (Pass-through)
        return frame

# WebRTC Streamer - Mobile/PC දෙකටම වැඩ
webrtc_streamer(
    key="ai-audio",
    mode=WebRtcMode.SENDRECV,
    audio_processor_factory=AudioProcessor,
    rtc_configuration={
        "iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]
    },
    media_stream_constraints={"video": False, "audio": True},
)

st.info("Mic එකට අවසර දීලා කතා කරන්න.")
