from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY")

@app.route('/analyze_vehicle', methods=['POST'])
def analyze_vehicle():
    data = request.json

    prompt = (
        "You are an automotive assistant helping users understand their vehicle's condition.\n"
        "Here are the sensor readings from an OBD2 device. "
        "Please note that a value of '-' means the data was not available or not supported by the vehicle.\n\n"
        "Summarize the following data into 3 parts:\n"
        "1. 🚨 Major issues (what's wrong)\n"
        "2. 📘 Simple explanation (easy to understand)\n"
        "3. 🛠 Suggested actions (clear & brief)\n\n"
        "Avoid technical terms and ignore missing values marked with '-'.\n\n"
    )

    for key, value in data.items():
        prompt += f"- {key}: {value}\n"

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

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
