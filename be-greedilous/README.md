# BE GREEDILOUS

반복과 연결을 중심으로 제안하는 GREEDILOUS 브랜드 아이덴티티 사례 페이지.

공개 주소: https://greedilous.github.io/brand/be-greedilous/

## 페이지 구성

- 전체 폭의 연결형 키비주얼
- 왼쪽 섹션 제목과 오른쪽 설명으로 구성한 Project Overview
- 딥레드 배경의 세 가지 브랜드 가치
- 삼각형 심볼, 접합부 디테일, 조립 과정
- 레드·딥레드·아이보리·실버 컬러 전개
- 심볼 한 개를 적용한 가방과 자켓
- 연결형 오브제를 적용한 패키지와 쇼윈도

Plus X UNNI 사례의 전체 폭 이미지, 넓은 흰 여백, 약 24:76 비율의 설명 행, 중앙 브랜드 가치, 이미지 전개 방식을 참고했습니다. 본문과 그래픽은 GREEDILOUS를 위해 새로 구성했습니다.

GNB, 목차, 고정 진행 표시, 발표 도구, 모션 버튼, 이전·다음 버튼이 없는 자연스러운 스크롤 페이지입니다. 별도 계정, 분석 도구, 외부 스크립트를 사용하지 않습니다.

## 편집

- index.html: 본문과 이미지 배치
- case-study.css: 현재 페이지의 모든 스타일과 반응형 구성
- app.js: 한 번만 재생하는 등장 효과와 작은 장식 이미지의 스크롤 이동
- assets/connection-20261018/: 게시용 WebP 이미지와 단일 심볼 SVG
- asset-sources.json: 이미지 출처와 콘셉트 범위

기존 스타일 파일은 현재 페이지에서 불러오지 않습니다. 루트 홈페이지와 기존 영상 파일은 이 페이지와 별개로 유지합니다.

## 이미지와 구조

가방과 자켓은 삼각형 심볼 한 개만 부착한 최종 시안입니다. 연결형 이미지는 판 두께와 슬롯 너비를 정의하고 이상적인 3D 형상의 간섭을 확인한 기준 모델에서 출발했습니다. 적용 사진은 ImageGen으로 생성한 콘셉트이며, 픽셀 단위 제작 도면이나 실물 시제품의 검증을 대신하지 않습니다.

원본 PNG를 구도 변경 없이 WebP로 변환하고, 640px·960px·원본 너비로 제공합니다. 첫 이미지는 우선 로드하며 나머지는 지연 로드합니다. 원본 이미지, 생성 프롬프트, 3D 자료는 로컬 creative/interlocking-triangle-20261018-v2/에 보존하며 이번 게시에는 웹용 자산만 포함합니다.

## 접근성 및 검증

이미지 설명, 의미 있는 제목 구조, 동작 줄이기 설정, JavaScript가 꺼진 환경을 지원합니다. 작은 화면에서는 설명을 한 열로, 가방과 자켓을 세로로 배치합니다. 구조 도해와 전체 적용 이미지는 잘리지 않게 표시합니다.

브라우저 검증: 1440px·768px·390px·320px, 이미지 로딩, 가로 넘침, 스크립트 오류, 동작 줄이기, JavaScript 비활성화.

## 게시

별도 빌드가 필요 없는 HTML·CSS·JavaScript 사이트입니다. 저장소 main의 기존 GitHub Pages 배포를 사용합니다. 필요한 파일만 커밋하고 GitHub Desktop에서 Push origin으로 게시합니다.

## 출처

- 레이아웃 참고: https://www.plus-ex.com/experience#unni
- 실제 참고 본문: https://www.plus-ex.com/source/iframe/portfolio/unni.html
- 사진: 이번 프로젝트에서 내장 ImageGen으로 생성한 GREEDILOUS 콘셉트 이미지
- 심볼: 사용자 제공 삼각형 심볼
- 구조 도해: 동일한 파라미터를 가진 조각을 조립한 Blender 렌더
- Pretendard: SIL Open Font License, assets/Pretendard-LICENSE.txt

색상값은 사용자 설명을 바탕으로 제안한 팔레트이며 기존 공식 색상값을 복원한 것은 아닙니다.
