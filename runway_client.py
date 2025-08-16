# runway_client.py
import requests
import os
import time

RUNWAY_API_KEY = os.getenv("RUNWAY_API_KEY")

def generate_video_from_prompt(prompt: str):
    try:
        url = "https://api.runwayml.com/v1/generations"
        headers = {
            "Authorization": f"Bearer {RUNWAY_API_KEY}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": "gen3",   # Runway text-to-video model
            "prompt": prompt
        }

        # Step 1: Create generation job
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        result = response.json()
        print("➡️ Runway create response:", result)

        generation_id = result.get("id")
        if not generation_id:
            print("❌ No generation ID returned")
            return None

        # Step 2: Poll for status (max 2 minutes)
        status_url = f"https://api.runwayml.com/v1/generations/{generation_id}"
        for _ in range(24):  # 24 * 5s = 120s
            time.sleep(5)
            status_res = requests.get(status_url, headers=headers)
            status_res.raise_for_status()
            status_data = status_res.json()
            print("➡️ Runway status:", status_data)

            if status_data.get("status") == "completed":
                # Try different possible keys
                output = status_data.get("output")
                if output:
                    if isinstance(output, list) and "url" in output[0]:
                        return output[0]["url"]
                    if isinstance(output, dict) and "url" in output:
                        return output["url"]

                # Some models use 'assets'
                if "assets" in status_data and "video" in status_data["assets"]:
                    return status_data["assets"]["video"]

                print("❌ No video URL in response")
                return None

            if status_data.get("status") == "failed":
                print("❌ Generation failed:", status_data)
                return None

        print("❌ Timeout waiting for video")
        return None

    except Exception as e:
        print("❌ Error in generate_video_from_prompt:", e)
        return None
