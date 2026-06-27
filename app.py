import streamlit as st
from streamlit_webrtc import webrtc_streamer, WebRtcMode, AudioProcessorBase
from google import genai
import av

# අලුත් SDK එක පාවිච්චි කරලා Client එක හදමු
# (ඔයාගේ API Key එක මෙතන තියෙනවා)
client = genai.Client(api_key="AQ.Ab8RN6KO4M3SlxL3dmmjuUULylCZr-IZT1lxxXfIj7emV9_Fyw")

# Page Layout එක ලස්සන කරන්න
st.set_page_config(page_title="Viruna's Live AI", page_icon="🤖", layout="centered")
st.title("Viruna's Live AI")

# CSS - ඇස් පිල්ලම් ගැසීම සහ Avatar ස්ටයිල් එක
st.markdown("""
<style>
    @keyframes blink { 
        0%, 100% { transform: scaleY(1); } 
        50% { transform: scaleY(0.1); } 
    }
    .avatar { 
        animation: blink 4s infinite; 
        width: 300px; 
        display: block; 
        margin: auto; 
        border-radius: 20px;
        box-shadow: 0px 4px 15px rgba(0,0,0,0.5);
    }
</style>
""", unsafe_allow_html=True)

# Avatar රූපය 
# (ඔයාගේ රූපයේ ලින්ක් එක මේ https://i.imgur.com/your_image.png වෙනුවට දාන්න)
st.markdown('<img src="https://i.imgur.com/your_image.png" class="avatar">', unsafe_allow_html=True)
st.write("---")

# Audio Processor එක (මයික් එකෙන් හඬ අරගෙන සකස් කරන කොටස)
class AudioProcessor(AudioProcessorBase):
    def recv(self, frame: av.AudioFrame) -> av.AudioFrame:
        # Microphone එකෙන් එන data මෙතනදී binary format එකට ගන්නවා
        audio_data = frame.to_ndarray().tobytes()
        
        # දැනට අපි frame එක ඒ විදිහටම ආපසු යවනවා 
        return frame

# WebRTC Streamer - Mobile/PC දෙකටම වැඩ කරන මයික්‍රොෆෝනය
webrtc_ctx = webrtc_streamer(
    key="ai-audio",
    mode=WebRtcMode.SENDRECV,
    audio_processor_factory=AudioProcessor,
    rtc_configuration={
        "iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]
    },
    media_stream_constraints={"video": False, "audio": True},
)

# මයික් එකේ තත්ත්වය පෙන්වීම
if webrtc_ctx.state.playing:
    st.success("🟢 මයික් එක සක්‍රියයි! දැන් කතා කරන්න...")
else:
    st.info("👆 'START' ඔබලා මයික් එකට අවසර දෙන්න.")
