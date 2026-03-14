from flask import Flask, request, jsonify
import os, requests, inspect

app = Flask(__name__)

@app.route('/')
def home():
    return 'TikTok Uploader OK'

@app.route('/check', methods=['GET'])
def check():
    from tiktokautouploader import upload_tiktok
    sig = inspect.signature(upload_tiktok)
    return jsonify({'args': str(sig)})

@app.route('/publish', methods=['POST'])
def publish():
    try:
        data = request.get_json(force=True)
        video_url = data.get('video_url')
        caption = data.get('caption', '')
        accountname = data.get('accountname', '')

        r = requests.get(video_url, timeout=60)
        with open('/tmp/video.mp4', 'wb') as f:
            f.write(r.content)

        from tiktokautouploader import upload_tiktok
        result = upload_tiktok(
            video='/tmp/video.mp4',
            description=caption,
            accountname=accountname,
            headless=True,
            suppressprint=False
        )

        return jsonify({'status': 'published', 'result': result})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=port)
