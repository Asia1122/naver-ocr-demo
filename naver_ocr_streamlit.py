import streamlit as st
import requests
import uuid
import json
import time
import base64
from PIL import Image
import io

# st.secrets에서 OCR URL과 SECRET KEY를 가져옵니다.
OCR_URL = st.secrets["OCR_URL"]         # ex) "https://xxx.apigw.ntruss.com/custom/v1/xxxx/xxx"
OCR_SECRET_KEY = st.secrets["OCR_SECRET_KEY"]  # ex) "xxxxxxxxxxxxxxxx"

def call_naver_ocr_api(image_data: bytes, extension: str = "jpg") -> dict:
    # 이미지 파일을 base64로 인코딩
    encoded_data = base64.b64encode(image_data).decode("utf-8")

    request_json = {
        "images": [
            {
                "format": extension,
                "name": "demo",
                "data": encoded_data
            }
        ],
        "requestId": str(uuid.uuid4()),
        "version": "V2",
        "timestamp": int(round(time.time() * 1000))
    }

    headers = {
        "Content-Type": "application/json",
        "X-OCR-SECRET": OCR_SECRET_KEY
    }

    # 네이버 OCR API 호출
    response = requests.post(OCR_URL, headers=headers, json=request_json)

    if response.status_code == 200:
        return response.json()
    else:
        return {
            "error": f"Request failed with status code {response.status_code}",
            "details": response.text
        }

def main():
    st.title("네이버 OCR 데모 with Streamlit")
    st.write("이미지를 업로드하면 네이버 클라우드 OCR API로 인식 결과를 보여줍니다.")

    # 1) 이미지 업로더
    uploaded_file = st.file_uploader("이미지를 업로드하세요", type=["jpg", "jpeg", "png"])
    
    if uploaded_file is not None:
        # 2) 업로드된 파일을 '바이트' 형태로 한 번만 읽기
        file_bytes = uploaded_file.read()

        # 3) 파일 바이트를 통해 Pillow 이미지 객체 만들기
        image = Image.open(io.BytesIO(file_bytes))
        st.image(image, caption="업로드된 이미지", use_container_width=True)

        # 4) "OCR 실행" 버튼
        if st.button("OCR 실행"):
            with st.spinner("OCR 처리 중..."):
                # 확장자 파악
                file_extension = uploaded_file.name.split('.')[-1].lower()

                # OCR API 호출
                result_json = call_naver_ocr_api(file_bytes, extension=file_extension)

            # 5) OCR 결과 표시
            if "images" in result_json and result_json["images"]:
                fields = result_json["images"][0].get("fields", [])
                if fields:
                    extracted_texts = [field["inferText"] for field in fields]
                    final_text = " ".join(extracted_texts)
                    st.subheader("인식된 텍스트:")
                    st.write(final_text)
                else:
                    st.warning("인식된 텍스트가 없습니다.")
            elif "error" in result_json:
                st.error(f"오류 발생: {result_json['error']}\n상세: {result_json['details']}")
            else:
                st.warning("OCR 결과가 예상과 다릅니다.")
    else:
        st.info("이미지를 업로드해주세요.")

if __name__ == "__main__":
    main()
