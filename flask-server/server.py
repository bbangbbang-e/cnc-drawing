from flask import Flask, request, jsonify
import serial
import time

app = Flask(__name__)

# 아두이노 시리얼 포트 및 보드레이트를 실제 환경에 맞게 설정
ARDUINO_PORT = '/dev/ttyACM0'
BAUDRATE = 115200

@app.route("/send_gcode_to_arduino", methods=['POST'])
def send_gcode_to_arduino():
    data = request.get_json()
    if not data or 'gcode' not in data:
        return jsonify({"status": "error", "message": "gcode 값이 없어!"}), 400

    gcode = data['gcode']
    if not gcode.strip():
        return jsonify({"status": "error", "message": "gcode 내용이 비어있어!"}), 400

    # 아두이노에 G-code 전송
    try:
        # 시리얼 포트 열기
        with serial.Serial(ARDUINO_PORT, BAUDRATE, timeout=2) as ser:
            lines = gcode.strip().split('\n')
            for line in lines:
                line = line.strip()
                if line:
                    # G-code 한 줄 전송
                    ser.write((line + '\n').encode('utf-8'))
                    # 아두이노가 명령 처리할 시간 약간 대기
                    time.sleep(0.1)

        return jsonify({"status": "success", "message": "G-code를 아두이노로 전송 완료!"}), 200
    except serial.SerialException as e:
        return jsonify({"status": "error", "message": f"시리얼 포트에 접근할 수 없음: {e}"}), 500
    except Exception as e:
        return jsonify({"status": "error", "message": f"예상치 못한 에러 발생: {e}"}), 500


if __name__ == "__main__":
    # 호스트와 포트는 필요에 따라 변경
    app.run(debug=True, host='0.0.0.0', port=5000)
