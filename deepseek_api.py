from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY")


@app.route('/analyze_vehicle', methods=['POST'])
def analyze_vehicle():
    data = request.json
    prompt = generate_prompt(data)

    response = requests.post(
        "https://api.deepseek.com/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7
        }
    )

    result = response.json()["choices"][0]["message"]["content"]
    return jsonify({"result": result})

def generate_prompt(data):
    prompt = "You are an AI vehicle diagnostic assistant. Here are the sensor readings:\n"
    for key, value in data.items():
        prompt += f"- {key}: {value}\n"
    prompt += "\nGenerate a report with:\n1. Explanation\n2. Detected Issues\n3. Fix Suggestions"
    return prompt

if __name__ == '__main__':
    app.run(debug=True)
