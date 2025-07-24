# app.py
from flask import Flask, render_template, request, send_file, redirect, url_for
from pytube import YouTube
from moviepy.editor import *
import os
import uuid

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'downloads'

def create_download_folder():
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form['url']
        action = request.form['action']
        
        try:
            yt = YouTube(url)
            if action == 'download':
                stream = yt.streams.get_highest_resolution()
            elif action == 'convert':
                stream = yt.streams.get_audio_only()
            
            # Generate unique filename
            filename = f"{uuid.uuid4()}.{'mp4' if action == 'download' else 'mp3'}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            
            # Download the file
            stream.download(output_path=app.config['UPLOAD_FOLDER'], filename=filename)
            
            # If converting to MP3
            if action == 'convert':
                mp4_path = filepath
                mp3_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{uuid.uuid4()}.mp3")
                clip = AudioFileClip(mp4_path)
                clip.write_audiofile(mp3_path)
                clip.close()
                os.remove(mp4_path)  # Remove the temporary MP4 file
                filepath = mp3_path
            
            return redirect(url_for('download', filename=os.path.basename(filepath)))
        
        except Exception as e:
            return render_template('index.html', error=str(e))
    
    return render_template('index.html')

@app.route('/download/<filename>')
def download(filename):
    return send_file(
        os.path.join(app.config['UPLOAD_FOLDER'], filename),
        as_attachment=True
    )

@app.route('/clear_downloads')
def clear_downloads():
    for file in os.listdir(app.config['UPLOAD_FOLDER']):
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
        except Exception as e:
            print(f"Error deleting {file_path}: {e}")
    return "Downloads cleared"

if __name__ == '__main__':
    create_download_folder()
    app.run(debug=True)
