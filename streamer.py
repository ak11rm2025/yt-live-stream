import os
import time
import subprocess
import requests


def main():
    playlist_url = os.environ.get("PLAYLIST_URL")
    yt_stream_key = os.environ.get("YT_STREAM_KEY")
    bg_video_url = os.environ.get("BG_VIDEO_URL")

    if not playlist_url or not yt_stream_key:
        print("❌ PLAYLIST_URL أو YT_STREAM_KEY غير موجودين")
        return

    if not bg_video_url:
        print("⚠️ BG_VIDEO_URL غير موجود، استخدم قيمة افتراضية")
        bg_video_url = "https://quran-stream-zeta.vercel.app/bg.mp4"

    youtube_rtmp = f"rtmp://a.rtmp.youtube.com/live2/{yt_stream_key}"

    while True:
        try:
            print("🔄 جلب قائمة التشغيل من:", playlist_url)
            resp = requests.get(playlist_url, timeout=15)
            resp.raise_for_status()
            videos = resp.json()

            if not isinstance(videos, list) or not videos:
                print("⚠️ القائمة فارغة، الانتظار 30 ثانية...")
                time.sleep(30)
                continue

            for item in videos:
                audio_url = item.get("file_url")
                title = item.get("title", "بدون عنوان")

                if not audio_url:
                    continue

                print(f"▶️ بدء بث المقطع: {title}")
                print(f"🎧 الصوت من: {audio_url}")
                print(f"🎬 الخلفية من: {bg_video_url}")

                # FFmpeg command (مضبوطة 100%)
                cmd = [
                    "ffmpeg",
                    "-stream_loop", "-1",
                    "-re", "-ss", "25", "-i", bg_video_url,  # الفيديو يبدأ من الثانية 23
                    "-re", "-i", audio_url,                  # صوت القرآن
                    "-map", "0:v",
                    "-map", "1:a",
                    "-shortest",
                    "-c:v", "libx264",
                    "-preset", "veryfast",
                    "-c:a", "aac",
                    "-ar", "44100",
                    "-b:a", "128k",
                    "-f", "flv",
                    youtube_rtmp
                ]

                process = subprocess.run(cmd)
                print(f"⏹ انتهى المقطع: {title} (code={process.returncode})")

            print("🔁 إعادة تشغيل القائمة من البداية...")

        except Exception as e:
            print("❌ خطأ:", e)
            time.sleep(10)


if __name__ == "__main__":
    main()
