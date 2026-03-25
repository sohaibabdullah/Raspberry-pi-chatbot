import subprocess
import os
import speech_recognition as sr
import google.generativeai as genai
from dotenv import load_dotenv
import requests


load_dotenv()


# --- CONFIGURATION ---
DEVICE = "hw:2,0"
DURATION = 5
FILENAME = "voice_capture.wav"
RATE = 48000


GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")   

def record_audio():
    print(f"--- Starting Recording ({DURATION} seconds) ---")
    cmd = ["arecord", "-D", DEVICE, "-d", str(DURATION), "-f", "S16_LE", "-r", str(RATE), "-c", "1", FILENAME]
    try:
        subprocess.run(cmd, check=True)
        print(f"--- Finished! File saved as: {FILENAME} ---")
        if os.path.exists(FILENAME) and os.path.getsize(FILENAME) > 0:
            print("Recording successful.")
        else:
            print("Error: File was created but is empty.")
    except subprocess.CalledProcessError as e:
        print(f"Error during recording: {e}")
    except FileNotFoundError:
        print("Error: 'arecord' command not found.")

# Converts wav file to text using Whisper (runs locally)
def transcribe_audio(filename):
    print("--- Transcribing audio... ---")
    recognizer = sr.Recognizer()
    with sr.AudioFile(filename) as source:
        audio = recognizer.record(source)
    try:
        text = recognizer.recognize_google(audio)  
        print(f"--- You said: {text} ---")
        return text
    except sr.UnknownValueError:
        print("Could not understand the audio.")
        return ""
    except sr.RequestError as e:
        print(f"Google Speech service error: {e}")
        return ""

# Sends text to LLM and returns the response
def ask_llm(question):
    print("--- Sending to Gemini... ---")
    api_key = os.getenv("GEMINI_API_KEY")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"
    
    payload = {
        "contents": [{"parts": [{"text": question}]}]
    }
    
    response = requests.post(url, json=payload)
    answer = response.json()["candidates"][0]["content"]["parts"][0]["text"]
    return answer


if __name__ == "__main__":
    # Step 1: Record
    record_audio()

    # Step 2: Transcribe 
    question = transcribe_audio(FILENAME)

    # Step 3: Ask LLM and print answer 
    if question:
        answer = ask_llm(question)
        print("\n--- LLM's Answer ---")
        print(answer)
    else:
        print("Could not understand audio, please try again.")