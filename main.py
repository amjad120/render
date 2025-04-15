from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/obd-data', methods=['POST'])
def receive_obd_data():
    data = request.json
    print("📥 البيانات المستلمة من Flutter:", data)
    
    # تقدر هنا تخزن البيانات أو تعالجها أو ترسلها لفirebase
    return jsonify({"message": "✅ تم استلام البيانات بنجاح"}), 200

@app.route('/', methods=['GET'])
def home():
    return "🚀 API شغالة تمام"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
