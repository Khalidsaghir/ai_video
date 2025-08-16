# app.py
import os, time, requests
from flask import Flask, request, jsonify

app = Flask(__name__)

RUNWAY_API_KEY = os.getenv("RUNWAY_API_KEY")
BASE = "https://api.runwayml.com/v1"
HEADERS = {"Authorization": f"Bearer {RUNWAY_API_KEY}", "Content-Type": "application/json"}

def poll_task(task_id, timeout=300, interval=5):
    """Poll a Runway task until it finishes."""
    end = time.time() + timeout
    while time.time() < end:
        r = requests.get(f"{BASE}/tasks/{task_id}", headers=HEADERS)
        data = r.json()
        status = data.get("status")
        if status in ("SUCCEEDED", "completed"):
            return data
        if status in ("FAILED", "CANCELED"):
            raise Exception(f"Task failed: {data}")
        time.sleep(interval)
    raise Exception("Timeout waiting for task")

def text_to_image(prompt: str):
    """Generate an image from text."""
    r = requests.post(f"{BASE}/text_to_image",
                      headers=HEADERS,
                      json={"promptText": prompt, "model": "gen4_image"})
    task_id = r.json().get("id")
    done = poll_task(task_id)
    return done["output"]["image"]["url"]

def image_to_video(prompt: str, image_url: str, duration: int = 5):
    """Generate a video from an image + prompt."""
    r = requests.post(f"{BASE}/image_to_video",
                      headers=HEADERS,
                      json={"promptText": prompt,
                            "promptImage": image_url,
                            "duration": duration,
                            "model": "gen4_turbo"})
    task_id = r.json().get("id")
    done = poll_task(task_id)
    return done["output"]["video"]["url"]

@app.route("/generate-video", methods=["POST"])
def generate_video():
    """API endpoint: prompt → video."""
    data = request.json
    prompt = data.get("prompt")
    duration = data.get("duration", 5)

    try:
        keyframe = text_to_image(prompt)
        video_url = image_to_video(prompt, keyframe, duration)
        return jsonify({"status": "done", "video_url": video_url})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    app.run(port=5000, debug=True)
