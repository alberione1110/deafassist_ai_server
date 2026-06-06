# DeafAssist AI Server (Windows 실행 방법)

## 1. 프로젝트 준비

최종 폴더 구조

```text
deafassist_ai_server/
├── app/
├── requirements.txt
├── KWS/
│   └── kws_infer.py
└── kws_doa/
    ├── KwsDoa.py
    ├── mic_stream.py
    ├── gcc_phat.py
    └── run.py
```

---

## 2. 프로젝트 폴더 이동

PowerShell 실행 후

```powershell
cd C:\Users\사용자명\Desktop\deafassist_ai_server
```

---

## 3. 가상환경 생성

```powershell
python -m venv .venv
```

생성 완료 후

```powershell
.\.venv\Scripts\Activate.ps1
```

정상 활성화 시

```text
(.venv)
```

가 앞에 표시됨

---

## 4. 패키지 설치

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

---

## 5. ReSpeaker 장치 번호 확인

```powershell
python -c "import sounddevice as sd; print(sd.query_devices())"
```

예시

```text
0 Microsoft Sound Mapper
1 Speaker
2 Microphone
3 ReSpeaker 4 Mic Array
```

---

## 6. mic_stream.py 수정

현재 코드

```python
DEVICE_INDEX = 1
```

ReSpeaker 번호가 3이라면

```python
DEVICE_INDEX = 3
```

으로 변경

---

## 7. 모델 단독 테스트

```powershell
python -m kws_doa.run
```

정상 동작 시

```text
Start streaming...
stream 진입
result: {'label': 'car_horn', 'direction': 'FL', 'score': 0.94}
```

---

## 8. FastAPI 서버 실행

프로젝트 루트에서

```powershell
uvicorn app.main:app --host 0.0.0.0 --port 8001
```

정상 실행 시

```text
INFO: Uvicorn running on http://0.0.0.0:8001
```

---

## 9. Health Check 확인

새 PowerShell 창

```powershell
curl http://127.0.0.1:8001/health
```

응답

```json
{
  "status":"ok",
  "app":"DeafAssist AI Server"
}
```

---

## 10. PC IP 확인

```powershell
ipconfig
```

IPv4 주소 확인

예시

```text
192.168.0.23
```

---

## 11. 모바일 프론트 연결

WebSocket

```text
ws://192.168.0.23:8001/ws
```

Health Check

```text
http://192.168.0.23:8001/health
```

---

## 12. 연결 흐름

프론트 연결

```json
{
  "type": "status",
  "message": "connected"
}
```

프론트 전송

```json
{
  "type": "start"
}
```

서버 응답

```json
{
  "type": "status",
  "message": "started"
}
```

추론 결과

```json
{
  "type": "inference",
  "label": "car_horn",
  "score": 0.94,
  "direction": "front_left",
  "is_risk": true,
  "timestamp": 1713420000
}
```

---

## 13. 서버 종료

```powershell
Ctrl + C
```

가상환경 종료

```powershell
deactivate
```
