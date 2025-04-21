from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# 🔐 الحصول على API Key من متغيرات البيئة
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY")
print("🔐 USING API KEY:", DEEPSEEK_API_KEY)  # مؤقت للتأكيد، احذفه بعد التجربة

@app.route('/')
def home():
    return "🚗 DeepSeek Vehicle Diagnostic API is running!"

@app.route('/analyze_vehicle', methods=['POST'])
def analyze_vehicle():
    data = request.json
    prompt = generate_prompt(data)

    try:
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

        res_json = response.json()
        print("📩 DeepSeek Response:", res_json)  # 🐛 Debug Output

        if "choices" in res_json:
            result = res_json["choices"][0]["message"]["content"]
        else:
            result = f"❌ DeepSeek API Error: {res_json}"

    except Exception as e:
        result = f"🚨 Exception occurred: {str(e)}"

    return jsonify({"result": result})


def generate_prompt(data):
    prompt = "You are an AI vehicle diagnostic assistant. Here are the sensor readings:\n"
    for key, value in data.items():
        prompt += f"- {key}: {value}\n"
    prompt += "\nGenerate a report with:\n1. Explanation\n2. Detected Issues\n3. Fix Suggestions"
    return prompt


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
