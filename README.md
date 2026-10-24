# reinforced-robofuzz — RoIFuzz 이전 단계의 RoboFuzz IDL 오라클 강화 실험

> **한눈에 보기**
> - **문제**: RoboFuzz의 IDL 오라클은 보낸 메시지와 되돌아온 메시지가 같은지 정도만 봐서, 범위를 벗어난 값이나 타입이 다른 값을 넣어도 걸러지지 않았다.
> - **접근**: `oracles/rosidl.py`에 값 범위 검사, 타입 일치 검사, 배열 원소 단위 비교를 추가하고, 기대한 오류가 잡히지 않은 경우를 모아 보는 `reporting.py`를 만들었다.
> - **결과**: `error-report`에 기대한 범위·타입 오류가 잡히지 않은 사례 118건을 정리(예: `Int8FixedArray`에 128 입력 시 오류 미발생). 이 결과를 바탕으로 [RoIFuzz](https://github.com/DevMinGeonPark/RoIFuzz)로 이어졌다.
> - **내 역할**: 세종대 정보보호학과 ISLab(2024.04–2024.12) 연구 중 오라클 수정과 리포팅 스크립트 작성(2024.10 커밋).
> - **발표·특허**: 최종 결과는 RoIFuzz로 한국정보보호학회 CISC-W'24 구두발표, 특허 출원 10-2024-0197496(공동 발명자).

RoboFuzz(FSE '22) 코드를 기반으로 한 연구 중간 단계 코드입니다. 정리된 설명과 실행 방법은 [RoIFuzz](https://github.com/DevMinGeonPark/RoIFuzz) README를 참고하세요.

```bash
pip install -r requirements.txt
python fuzzer.py      # 설정은 config.py, constants.py
python reporting.py   # error-* 로그를 모아 error-report 생성
```
