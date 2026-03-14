from flask import Flask, request, jsonify
import os, requests, time

app = Flask(__name__)

@app.route('/')
def home():
    return 'TikTok Uploader OK'

@app.route('/publish', methods=['POST'])
def publish():
    try:
        data = request.get_json(force=True)
        video_url = data.get('video_url')
        caption = data.get('caption', '')
        sessionid = data.get('sessionid', '')

        # Скачай видео
        r = requests.get(video_url, timeout=60)
        with open('/tmp/video.mp4', 'wb') as f:
            f.write(r.content)

        from tiktokautouploader import upload_tiktok
        upload_tiktok(
            video='/tmp/video.mp4',
            description=caption,
            cookies={'sessionid': sessionid},
            headless=True
        )

        return jsonify({'status': 'published'})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=port)
