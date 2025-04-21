from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# 🔑 مفتاح DeepSeek API من متغير البيئة
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY")

# 🏠 نقطة اختبار رئيسية (رابط رئيسي يعرض أن الـ API شغالة)
@app.route('/')
def home():
    return "🚗 DeepSeek Vehicle Diagnostic API is running!"

# 🔍 نقطة تحليل البيانات
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

# 🧠 توليد الـ Prompt من البيانات
def generate_prompt(data):
    prompt = "You are an AI vehicle diagnostic assistant. Here are the sensor readings:\n"
    for key, value in data.items():
        prompt += f"- {key}: {value}\n"
    prompt += "\nGenerate a report with:\n1. Explanation\n2. Detected Issues\n3. Fix Suggestions"
    return prompt

# 🚀 تشغيل السيرفر على 0.0.0.0 علشان يشتغل على Render
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
