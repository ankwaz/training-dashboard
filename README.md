# HWP → PDF 변환기

`.hwp` 파일을 넣으면 `.pdf`로 바꿔주는 간단한 프로그램입니다.

## 필요 사항

- Python 3.9+
- LibreOffice (`soffice`) 설치

> 이 스크립트는 내부적으로 `soffice --headless --convert-to pdf` 명령을 사용합니다.

## 사용법

```bash
python3 hwp_to_pdf.py 문서1.hwp 문서2.hwp
```

기본 출력 폴더는 `./output_pdf` 입니다.

### 옵션

- `-o, --output-dir`: PDF 저장 폴더 지정
- `--soffice`: `soffice` 경로 직접 지정

예시:

```bash
python3 hwp_to_pdf.py sample.hwp -o ./pdf_result
python3 hwp_to_pdf.py sample.hwp --soffice /usr/bin/soffice
```

## 동작 방식

1. `soffice` 실행 파일을 찾습니다.
2. 입력된 `.hwp` 파일들을 순회합니다.
3. 각 파일을 PDF로 변환 후 출력 폴더에 저장합니다.
4. 실패/성공 결과를 콘솔에 표시합니다.

## 참고

- LibreOffice가 HWP 파일을 제대로 읽지 못하는 경우 변환이 실패할 수 있습니다.
- 변환 품질은 원본 HWP의 구성(글꼴, 표, 개체 등)에 따라 달라질 수 있습니다.
