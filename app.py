from flask import Flask, request, jsonify
import os
from tika import parser
import speech_recognition as sr
from pydub import AudioSegment

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Tika file analysis function
def analyze_with_tika(file_path):
    raw = parser.from_file(file_path)
    text = raw.get('content', '')
    return text

# Audio file analysis (MP3/WAV to text)
def audio_to_text(file_path):
    # Convert .mp3 to .wav if necessary
    if file_path.endswith(".mp3"):
        audio = AudioSegment.from_mp3(file_path)
        file_path = file_path.replace(".mp3", ".wav")
        audio.export(file_path, format="wav")

    recognizer = sr.Recognizer()
    with sr.AudioFile(file_path) as source:
        audio_data = recognizer.record(source)
    try:
        text = recognizer.recognize_google(audio_data)
        return text
    except sr.UnknownValueError:
        return "Audio could not be understood."
    except sr.RequestError:
        return "Could not request results from Google Speech Recognition."

# General analysis function that combines Tika and audio-to-text
def analyze_and_ask_model(file_path):
    # Determine file type
    if file_path.endswith(('.mp3', '.wav')):
        analysis_result = audio_to_text(file_path)
    else:
        analysis_result = analyze_with_tika(file_path)

    model_input = "Analyze the following content: " + analysis_result
    # Here you would send the model_input to your AI model (e.g., Ollama)
    response = {"response": "Model analysis result here"}  # Replace with your AI model query
    return response

# Flask route to handle file upload
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(file_path)

    # Process the file and analyze it
    response = analyze_and_ask_model(file_path)

    return jsonify({'response': response})

if __name__ == '__main__':
    app.run(debug=True)
