# test_speak.py
import requests
response = requests.post(
    "http://127.0.0.1:8000/voice/speak",
    data={"text": "Hello, welcome to MedCare Clinic. How can I help you today?"}
)

print(f"Status: {response.status_code}")
print(f"Bytes received: {len(response.content)}")
print(f"Content-Type: {response.headers.get('content-type')}")

with open("test_output.mp3", "wb") as f:
    f.write(response.content)

print("Saved to test_output.mp3 — open and play it")