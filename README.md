# 📸 SnapLog - 자연스러운 일상 기록

> 사진을 업로드하면 AI가 자연스러운 일기를 생성해주는 Streamlit 웹앱

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-green.svg)
![Streamlit](https://img.shields.io/badge/streamlit-1.28+-red.svg)

## ✨ 주요 기능

- 📷 **최대 10장의 사진 업로드** - JPEG, PNG 형식 지원
- 🎨 **4가지 일기 스타일** - 자연스러운, 감성적, 간결한, 상세한
- 🤖 **AI 기반 일기 생성** - Google Gemini 2.5 Pro 모델 사용
- 💾 **날짜별 일기 저장** - JSON 형태로 로컬 저장
- 📚 **과거 일기 조회** - 사이드바에서 쉽게 접근
- 🌙 **다크모드 지원** - Streamlit 기본 테마 사용

## 🚀 빠른 시작

### 1. 저장소 클론
```bash
git clone https://github.com/your-username/snaplog-web.git
cd snaplog-web
```

### 2. 의존성 설치
```bash
pip install -r requirements.txt
```

### 3. 환경 변수 설정
```bash
cp .env.example .env
```

`.env` 파일을 열고 Google API Key를 설정하세요:
```
GOOGLE_API_KEY=your_google_api_key_here
```

### 4. 앱 실행
```bash
streamlit run app_simple.py
```

## 🔑 Google API Key 발급

1. [Google AI Studio](https://makersuite.google.com/app/apikey)에 접속
2. "Create API Key" 클릭
3. 생성된 API Key를 `.env` 파일에 추가

## 📁 프로젝트 구조

```
snaplog_web/
├── app_simple.py          # 메인 애플리케이션 (권장)
├── app_refactored.py      # 리팩토링된 버전
├── snaplog_natural.py     # AI 처리 모듈
├── requirements.txt       # 의존성 목록
├── .env.example          # 환경 변수 예시
├── .env                  # 환경 변수 (생성 필요)
├── .gitignore           # Git 제외 파일
├── diaries/             # 일기 저장 폴더 (자동 생성)
└── README.md            # 이 파일
```

## 🎯 사용 방법

1. **사진 업로드**: 왼쪽 사이드바에서 사진을 업로드 (최대 10장)
2. **스타일 선택**: 원하는 일기 스타일을 선택
3. **날짜 설정**: 일기를 저장할 날짜를 선택
4. **일기 생성**: "일기 생성하기" 버튼 클릭
5. **저장**: 생성된 일기를 확인하고 저장

## 🎨 일기 스타일

- **자연스러운**: 친구에게 말하듯 편안한 톤
- **감성적**: 서정적이고 감성적인 표현
- **간결한**: 핵심만 담은 명확한 기록
- **상세한**: 구체적이고 자세한 서술

## 🛠️ 기술 스택

- **Frontend**: Streamlit
- **AI Model**: Google Gemini 2.5 Pro
- **Language**: Python 3.9.11
- **Storage**: Local JSON files
- **Image Processing**: PIL (Pillow)

## 📝 의존성

```
streamlit>=1.28.0
google-generativeai>=0.3.0
langchain-google-genai>=1.0.0
langchain>=0.1.0
pillow>=10.0.0
python-dotenv>=1.0.0
```

## 🔒 보안 고려사항

- ✅ API Key는 환경 변수로 관리
- ✅ `.env` 파일은 Git에서 제외
- ✅ 일기 데이터는 로컬에만 저장
- ✅ 업로드된 이미지는 임시 파일로 처리 후 삭제

## 🐛 문제 해결

### 일기가 생성되지 않는 경우
- Google API Key가 올바르게 설정되었는지 확인
- API 할당량이 남아있는지 확인
- 네트워크 연결 상태 확인

### 저장된 일기가 보이지 않는 경우
- `diaries/` 폴더 권한 확인
- 해당 날짜에 저장된 일기가 있는지 확인

### 사진 업로드 실패
- 파일 형식이 JPEG, PNG인지 확인
- 파일 크기가 너무 크지 않은지 확인
- 최대 10장 제한 확인

## 📄 라이선스

MIT License - 자세한 내용은 [LICENSE](LICENSE) 파일 참조

## 🤝 기여하기

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📞 지원

- **Issues**: GitHub Issues를 통해 버그 리포트 및 기능 요청
- **Email**: kimsol1134@naver.com

---

*Made with ❤️ by kimsol1134*