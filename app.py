from flask import Flask, request, jsonify
import os, requests, time, json

app = Flask(__name__)

@app.route('/')
def home():
    return 'TikTok Publisher OK'

@app.route('/publish', methods=['POST'])
def publish():
    try:
        data = request.get_json(force=True)
        video_url = data.get('video_url')
        caption = data.get('caption', '')
        cookies = data.get('cookies', '')

        if not video_url:
            return jsonify({'error': 'video_url required'}), 400

        h = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36',
            'Referer': 'https://www.tiktok.com/',
            'Cookie': cookies,
            'X-Secsdk-Csrf-Token': cookies.split('tt_csrf_token=')[-1].split(';')[0] if 'tt_csrf_token' in cookies else ''
        }

        # Скачай видео
        r = requests.get(video_url, timeout=60)
        with open('/tmp/video.mp4', 'wb') as f:
            f.write(r.content)
        sz = os.path.getsize('/tmp/video.mp4')

        # Получи upload url
        init = requests.post(
            'https://upload.tiktok.com/file/v2/upload/video/?biz_name=tiktok_video&version=v2',
            json={'upload_type': 'UPLOAD_BY_FILE', 'video_size': sz},
            headers=h
        )
        init_data = init.json()
        upload_url = init_data.get('upload_url', '')
        upload_id = init_data.get('upload_id', str(int(time.time()*1000)))

        # Загрузи видео
        with open('/tmp/video.mp4', 'rb') as f:
            requests.put(upload_url, data=f, headers={**h, 'Content-Type': 'video/mp4'}) if upload_url else None

        # Опубликуй
        pub = requests.post(
            'https://www.tiktok.com/api/post/item/create/',
            json={
                'video_id': upload_id,
                'caption': caption,
                'privacy_level': 'PUBLIC_TO_EVERYONE'
            },
            headers=h
        )

        return jsonify({'status': 'ok', 'response': pub.text})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7860)
