from flask import Flask, request, jsonify
import flask_cors as cors
import serial
import cv2
import time
from PIL import Image
import pymysql
from modules.db import Database
from werkzeug.utils import secure_filename

app = Flask(__name__)
cors = cors.CORS(app)

# 아두이노 시리얼 포트 및 보드레이트를 실제 환경에 맞게 설정
ARDUINO_PORT = '/dev/ttyACM0' # 실제 포트 번호 입력
BAUDRATE = 115200
UPLOAD_FORDER = './upload'
os.makedirs(UPLOAD_FORDER, exist_ok=True)

app.config['UPLOAD_FORDER'] = UPLOAD_FORDER

def extract_contours(image_path):
    try:
        # OpenCV를 사용하여 이미지 읽기
        image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        if image is None:
            raise ValueError("이미지를 읽을 수 없습니다.")

        # 외곽선 검출
        blurred = cv2.GaussianBlur(image, (5, 5), 0)
        edges = cv2.Canny(blurred, 50, 150)

        # 외곽선만 있는 이미지 저장
        contours_path = os.path.join(app.config['UPLOAD_FOLDER'], "contours.png")
        cv2.imwrite(contours_path, edges)

        return contours_path
    except Exception as e:
        return f"Contour extraction error: {str(e)}"

@app.route("/upload", methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return jsonify({"status": "error", "message": "image file not found"}), 400

    image = request.files['image']
    filename = secure_filename(image.filename)
    image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    image.save(image_path)

    # 외곽선 추출
    contours_path = extract_contours(image_path)
    if "error" in contours_path:
        return jsonify({"status": "error", "message": contours_path}), 500

    return jsonify({"status": "success", "contours_path": contours_path}), 200


def convert_imgage_to_gcode(image_path):
		try:
				img = Image.open(image_path).convert('L')
				img = img.resize((100, 100))

				gcode_lines = []
				gcode_lines.append("G21 ; Set units to millimeters")
				gcode_lines.append("G90 ; Absolute positioning")

				for y in range(img.height):
					row = ""
					for x in range(img.width):
						pixel_brightness = img.getpixel((x, y)) / 255.0
						if pixel_brightness > 0.5:
							gcode_lines.append(f"G1 X{x} Y{y} Z{pixel_brightness:.2f}")
				gcode_lines.append("M30 ; End of program")
				return "\n".join(gcode_lines)
		except Exception as e:
			return f"Image conversion error: {str(e)}"

@app.route("/upload", methods=['POST'])
def upload_image():
	if 'image' not in request.files:
		return jsonify({"status": "error", "message": "image file not found"}), 400

	image = request.files['image']
	image_path = f"./upload/{image.filename}"
	image.save(image_path)

	gcode = convert_imgage_to_gcode(image_path)
	if not gcode:
		return jsonify({"status": "error", "message": "create fail G-code"}), 500

    # G-code DB 저장
	try:
			connection = Database()
			with connection.cursor() as cursor:
					sql = "INSERT INTO gcode_data (gcode_content) VALUES (%s)"
					cursor.execute(sql, (gcode,))
			connection.commit()
	except Exception as db_error:
			return f"Database error: {db_error}"
	finally:
			connection.close()

	return jsonify({"status": "success", "gcode": gcode}), 200

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
