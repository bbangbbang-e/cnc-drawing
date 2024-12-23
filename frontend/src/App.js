import "./App.css";
import { useState, useRef, useEffect } from "react";
import axios from "axios";

function App() {
  const [imgFile, setImgFile] = useState("");
  const [gcode, setGCode] = useState("");
  const imgRef = useRef();

  const saveImgFile = () => {
    const file = imgRef.current.files[0];
    const reader = new FileReader();

    reader.readAsDataURL(file);
    reader.onloadend = () => {
      setImgFile(reader.result);
    };
  };

  const handleUpload = async () => {
    const file = imgRef.current.files[0];

    if (!file) {
      alert("이미지를 선택하세요!");
      return;
    }

    const formData = new FormData();
    formData.append("image", file);

    try {
      const response = await axios.post(
        "http://10.150.150.199:5000/upload",
        formData,
        {
          headers: { "Content-Type": "multipart/form-data" },
        }
      );

      if (response.data.contours_path) {
        setImgFile(`http://10.150.150.199:5000/${response.data.contours_path}`);
        alert("외곽선 추출 성공!");
      } else {
        alert("외곽선 추출 실패!");
      }
    } catch (error) {
      console.error("Upload failed", error.response || error.message || error);
      alert("이미지 업로드 및 외곽선 추출에 실패했습니다.");
    }
  };

  const handleGenerateGCode = async () => {
    try {
      const response = await axios.get(
        "http://10.150.150.199:5000/generate_gcode"
      );
      if (response.data && response.data.gcode) {
        setGCode(response.data.gcode);
        alert("G-code가 성공적으로 생성되었습니다!");
      } else {
        alert("G-code 생성 실패!");
      }
    } catch (error) {
      console.error(
        "GCode generation failed:",
        error.response || error.message || error
      );
      alert("G-code 생성 중 오류가 발생했습니다.");
    }
  };

  const handleSendToArduino = async () => {
    if (!gcode) {
      alert("G-code를 생성하지 못했습니다.");
      return;
    }
    try {
      const response = await axios.post(
        "http://10.150.150.199:5000/send_gcode_to_arduino",
        { gcode },
        {
          headers: { "Content-Type": "application/json" },
        }
      );
      alert("아두이노로 전송 성공!");
    } catch (error) {
      console.error("Send to Arduino failed", error);
    }
  };

  return (
    <>
      <img
        src={imgFile ? imgFile : `/images/icon/user.png`}
        alt="프로필 이미지"
        className="ImgSize"
      />
      <input
        type="file"
        accept="image/*"
        id="profileImg"
        onChange={saveImgFile}
        ref={imgRef}
      />
      <button onClick={handleUpload}>이미지 업로드</button>
      <button onClick={handleGenerateGCode}>GCode로 추출하기</button>

      {gcode && (
        <div>
          <h3>Generated G-code:</h3>
          <pre>{gcode}</pre>
          <button onClick={handleSendToArduino}>아두이노로 전송</button>
        </div>
      )}
    </>
  );
}

export default App;
