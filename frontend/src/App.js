import './App.css';
import {useState, useRef, useEffect} from "react";
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
    formData.append('image', file);

    try {
      const response = await axios.post("http://10.150.150.199:5000/upload", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });

      setGCode(response.data.gcode);
    } catch (error) {
      console.error("Upload failed", error);
    }
  };

  const handleSendToArduino = async () => {
    if (!gcode) {
      alert("G-code를 생성하지 못했습니다.");
      return;
    }
    try {
      const response = await axios.post("http://10.150.150.199:5000/send_gcode_to_arduino", { gcode }, {
        headers: {"Content-Type": "application/json"},
      });
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
