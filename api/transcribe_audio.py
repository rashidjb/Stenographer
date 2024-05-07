from flask import Flask, request, send_file
import openai
from io import BytesIO
from pydub import AudioSegment
import os
import magic

app = Flask(__name__)

# Replace 'your-openai-api-key' with your actual OpenAI API key
openai.api_key = 'your-openai-api-key'

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return "No file part", 400
    file = request.files['file']
    if file.filename == '':
        return "No selected file", 400
    if file and allowed_file(file.filename):
        file_content = file.read()
        if not is_valid_audio(file_content):
            return "File is not a valid audio format", 400
        if file.content_length > 25 * 1024 * 1024:  # 25 MB size limit
            return "File size exceeds the 25 MB limit", 400
        duration = get_audio_duration(file_content, file.filename)
        if duration > 1800:  # 30 minutes limit
            return "Audio duration exceeds the 30 minute limit", 400
        return transcribe_audio(file_content)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ['mp3', 'wav', 'mpeg', 'flac']

def is_valid_audio(file_content):
    mime = magic.Magic(mime=True)
    file_type = mime.from_buffer(file_content)
    return 'audio' in file_type  # Checks if MIME type includes 'audio'

def get_audio_duration(file_content, filename):
    extension = filename.rsplit('.', 1)[1].lower()
    audio = AudioSegment.from_file(BytesIO(file_content), format=extension)
    return len(audio) / 1000  # Duration in seconds

def transcribe_audio(file_content):
    response = openai.Audio.transcribe(
        model="whisper-large",
        audio=file_content,
        format="mp3"  # Adjust according to the actual format of the uploaded audio file
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
