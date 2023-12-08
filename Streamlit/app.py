import streamlit as st
import speech_recognition as sr
from pydub import AudioSegment
from pydub.silence import split_on_silence
import os
import tempfile
from pytube import YouTube

# Speech Recognition and Transcription Functions
def transcribe_audio(path):
    r = sr.Recognizer()
    with sr.AudioFile(path) as source:
        audio_listened = r.record(source)
        try:
            text = r.recognize_google(audio_listened)
            return text
        except sr.UnknownValueError as e:
            return "Error: " + str(e)
        except sr.RequestError as e:
            return "API Error: " + str(e)

def get_large_audio_transcription_on_silence(path):
    sound = AudioSegment.from_file(path)  
    chunks = split_on_silence(sound, min_silence_len=500, silence_thresh=sound.dBFS-14, keep_silence=500)

    folder_name = tempfile.mkdtemp()
    whole_text = ""
    for i, audio_chunk in enumerate(chunks, start=1):
        chunk_filename = os.path.join(folder_name, f"chunk{i}.wav")
        audio_chunk.export(chunk_filename, format="wav")
        text = transcribe_audio(chunk_filename)
        if not text.startswith("Error"):
            text = f"{text.capitalize()}. "
            whole_text += text

    # Clean up
    for file in os.listdir(folder_name):
        os.remove(os.path.join(folder_name, file))
    os.rmdir(folder_name)

    return whole_text

# Function to download audio from YouTube
def download_audio_from_youtube(url):
    yt = YouTube(url)
    audio_stream = yt.streams.filter(only_audio=True).first()
    output_path = tempfile.gettempdir()
    audio_stream.download(output_path=output_path)
    return os.path.join(output_path, audio_stream.default_filename)

# Streamlit App
st.title("Youtube Transcription App")

# YouTube URL input
youtube_url = st.text_input("Enter YouTube URL")

if youtube_url:
    if st.button('Transcribe Audio from YouTube'):
        audio_path = download_audio_from_youtube(youtube_url)
        transcription = get_large_audio_transcription_on_silence(audio_path)
        st.write("Transcription:")
        for line in transcription.split('.'):
            st.write(line)


# File uploader
uploaded_file = st.file_uploader("Upload an audio file", type=["wav", "mp3", "flac"])

if uploaded_file is not None:
    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        tmp_file.write(uploaded_file.read())
        transcription = get_large_audio_transcription_on_silence(tmp_file.name)
        st.write("Transcription:")
        st.text(transcription)
