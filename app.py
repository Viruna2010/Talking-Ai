import streamlit as st
from streamlit_webrtc import webrtc_streamer, WebRtcMode, AudioProcessorBase
from google import genai
import os

# API Key
genai.configure(api_key="AQ.Ab8RN6KO4M3SlxL3dmmjuUULylCZr-IZT1lxxXfIj7emV9_Fyw")

st.title("Viruna's Live AI")

# CSS - ඇස් පිල්ලම් ගැසීම (කලින් දුන්න එකම)
st.markdown("""
<style>
    @keyframes blink { 0%, 100% { transform: scaleY(1); } 50% { transform: scaleY(0.1); } }
    .avatar { animation: blink 4s infinite; width: 300px; display: block; margin: auto; }
</style>
""", unsafe_allow_html=True)

st.markdown('<img src="https://i.imgur.com/your_image.png" class="avatar">', unsafe_allow_html=True)

# Audio Processor
class AudioProcessor(AudioProcessorBase):
    def recv(self, frame):
        # මෙතනදී තමයි Microphone එකෙන් එන audio data එක Live API එකට යන්නේ
        # Native Audio Dialog සඳහා මෙතන logic එක connect කරන්න ඕන
        return frame

# WebRTC Streamer - Mobile/PC දෙකටම වැඩ
webrtc_streamer(
    key="ai-audio",
    mode=WebRtcMode.SENDRECV,
    audio_processor_factory=AudioProcessor,
    rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]},
)

st.info("දැන් කතා කරන්න (Phone එකේ Mic එකට අවසර දෙන්න).")
