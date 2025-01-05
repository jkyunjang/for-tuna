### 버전
python version 3.12.7 이상

### 설치
1. 파이썬 가상환경(venv) 실행  
2. 의존성 패키지 설치: pip install -r requirements.txt

### 실행
1. .env 파일 생성(env_sample 파일 참고하여 필요한 거래소의 key 입력)
2. main 함수에서 구현한 전략 스케쥴링
3. 명령어 실행: python -m strategy.main
4. ta 패키지에서 nan 관련 오류가 발생하는 경우, C:\Users\사용자\for_tuna\.venv\Lib\site-packages\pandas_ta\momentum\squeeze_pro.py 파일에서 
from numpy import NaN as npNaN 에서 NaN을 nan으로 수정
