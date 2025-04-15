import obd
import time
from datetime import datetime

# قاموس أكواد الأعطال (مختصر للعرض)
DTC_DESCRIPTIONS = {
    "P0172": {"title": "خليط وقود غني", "action": "فحص حساس الأكسجين - تنظيف حساس الهواء"},
    "P0300": {"title": "اشتعال عشوائي", "action": "فحص شمعات الإشعال - كابلات البواجي"},
    "P0420": {"title": "كفاءة محفز منخفضة", "action": "فحص العادم - قد يحتاج استبدال المحفز"}
}

# المعدلات الطبيعية
NORMAL_RANGES = {
    "FUEL_LEVEL": (15, 100, "النطاق الطبيعي: 15%-100%"),
    "SHORT_FUEL_TRIM_1": (-5, 5, "المثالي: بين -5% إلى +5%"),
    "LONG_FUEL_TRIM_1": (-10, 10, "المسموح: بين -10% إلى +10%"),
    "CONTROL_MODULE_VOLTAGE": (13.5, 14.8, "المعدل الطبيعي: 13.5-14.8V"),
    "COOLANT_TEMP": (85, 105, "المثالي: 85-105°م"),
    "RPM": (600, 3000, "الخمول: 600-3000 دورة/د"),
    "SPEED": (0, 120, "السرعة الحالية"),
    "THROTTLE_POS": (0, 100, "وضعية دواسة البنزين"),
    "TIRE_PRESSURE_FL": (32, 36, "ضغط الإطار الأمامي الأيسر (psi)"),
    "TIRE_PRESSURE_FR": (32, 36, "ضغط الإطار الأمامي الأيمن (psi)")
}


# إعداد الاتصال
def setup_connection():
    try:
        connection = obd.OBD("COM6", protocol="6", fast=True, timeout=30)
        if not connection.is_connected():
            print("❌ فشل الاتصال! تأكد من:")
            print("- تشغيل المحرك/وضع المفتاح ON")
            print("- إقران الجهاز بالبلوتوث")
            return None
        return connection
    except Exception as e:
        print(f"❌ خطأ في الاتصال: {str(e)}")
        return None


# الأوامر المدعومة (بدون ALTERNATOR_VOLTAGE)
ALL_COMMANDS = {
    "الوقود": [
        obd.commands.FUEL_LEVEL,
        obd.commands.FUEL_STATUS,
    ],
    "الضبط": [
        obd.commands.SHORT_FUEL_TRIM_1,
        obd.commands.LONG_FUEL_TRIM_1,
    ],
    "الأعطال": [
        obd.commands.GET_DTC,
    ],
    "الكهرباء": [
        obd.commands.CONTROL_MODULE_VOLTAGE,  # جهد البطارية فقط
    ],
    "الأداء": [
        obd.commands.SPEED,
        obd.commands.RPM,
        obd.commands.THROTTLE_POS,

    ],
    "الحرارة": [
        obd.commands.COOLANT_TEMP,
        obd.commands.INTAKE_TEMP,
    ],

}


def get_dtc_advice(code):
    return DTC_DESCRIPTIONS.get(code, {
        "title": f"كود غير معروف ({code})",
        "action": "1. البحث في دليل السيارة 2. مراجعة مركز صيانة"
    })


def get_value_advice(cmd_name, value):
    if cmd_name in NORMAL_RANGES:
        min_val, max_val, advice = NORMAL_RANGES[cmd_name]
        try:
            num_value = float(value.split()[0])
            if num_value < min_val:
                return f"⬇️ أقل من الطبيعي! {advice}"
            elif num_value > max_val:
                return f"⬆️ أعلى من الطبيعي! {advice}"
            return f"✅ طبيعي ({advice})"
        except:
            return advice
    return ""


def scan_vehicle(connection):
    results = {}
    for category, commands in ALL_COMMANDS.items():
        results[category] = {}
        for cmd in commands:
            try:
                if cmd not in connection.supported_commands:
                    results[category][cmd.name] = "غير مدعوم"
                    continue

                response = connection.query(cmd)
                if response.is_null():
                    results[category][cmd.name] = "لا توجد بيانات"
                    continue

                if cmd == obd.commands.GET_DTC:
                    results[category][cmd.name] = ", ".join(response.value) if response.value else "لا توجد"
                elif cmd == obd.commands.FUEL_STATUS:
                    val = response.value[0] if isinstance(response.value, tuple) else response.value
                    results[category][cmd.name] = str(val)
                else:
                    unit = f" {response.unit}" if response.unit else ""
                    results[category][cmd.name] = f"{response.value.magnitude:.2f}{unit}" if hasattr(response.value,
                                                                                                     'magnitude') else str(
                        response.value)
            except Exception as e:
                results[category][cmd.name] = f"خطأ: {str(e)}"
    return results


def print_report(data):
    print("\n" + "=" * 60)
    print(f"📊 تقرير فحص السيارة - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    for category, values in data.items():
        print(f"\n📌 {category.upper()}")
        for name, value in values.items():
            advice = get_value_advice(name, value)
            print(f"  → {name.replace('_', ' '):<25}: {value} {advice}")

    if "الأعطال" in data and data["الأعطال"]["GET_DTC"] != "لا توجد":
        print("\n🔧 تفاصيل الأعطال:")
        for code in data["الأعطال"]["GET_DTC"].split(", "):
            if code.strip():
                advice = get_dtc_advice(code.strip())
                print(f"  🔴 {code}: {advice['title']}")
                print(f"     🛠️ الإجراء: {advice['action']}\n")


def main():
    connection = setup_connection()
    if not connection:
        return

    try:
        print("🚗 بدء الفحص الشامل للسيارة...")
        while True:
            vehicle_data = scan_vehicle(connection)
            print_report(vehicle_data)
            print("\n🔄 جاري التحديث... (اضغط Ctrl+C للإيقاف)")
            time.sleep(5)
    except KeyboardInterrupt:
        print("\nتم إيقاف الفحص بنجاح")
    finally:
        connection.close()


if __name__ == "__main__":
    main()