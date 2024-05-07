import os
from flask import Flask, request, send_file
import openai
from io import BytesIO
from pydub import AudioSegment

app = Flask(__name__)

# Fetch the OpenAI API key from environment variables
openai.api_key = os.environ.get('OPENAI_API_KEY', 'Your_Default_API_Key_if_any')

@app.route('/', methods=['GET'])
def hello_world():
    return 'Hello, World!'

@app.route('/', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return "No file part", 400
    file = request.files['file']
    if file.filename == '':
        return "No selected file", 400
    if file and allowed_file(file.filename):
        if file.content_length > 25 * 1024 * 1024:  # 25 MB size limit
            return "File size exceeds the 25 MB limit", 400
        audio_content = file.read()
        duration = get_audio_duration(audio_content, file.filename)
        if duration > 1800:  # 30 minutes limit
            return "Audio duration exceeds the 30 minute limit", 400
        return transcribe_audio(audio_content, file.filename)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ['mp3', 'wav', 'mpeg', 'flac']

def get_audio_duration(audio_content, filename):
    extension = get_extension(filename)
    audio = AudioSegment.from_file(BytesIO(audio_content), format=extension)
    return len(audio) / 1000  # Duration in seconds

def get_extension(filename):
    return filename.rsplit('.', 1)[1].lower()

def transcribe_audio(audio_content, filename):
    extension = get_extension(filename)
    response = openai.Audio.transcribe(
        model="whisper-large",
        audio=audio_content,
        format=extension  # Use the dynamically determined file extension
    )
    transcript = response['text']
    return save_transcript_to_file(transcript)

def save_transcript_to_file(transcript):
    buffer = BytesIO()
    buffer.write(transcript.encode())
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name='transcript.txt')

if __name__ == '__main__':
    app.run(debug=True)
