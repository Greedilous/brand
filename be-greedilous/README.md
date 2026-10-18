# BE GREEDILOUS — 반복과 연결

공개 주소: https://greedilous.github.io/brand/be-greedilous/

## 구성
세 섹션을 표시합니다.
1. 다섯 시안의 공통 도입부. 딥 레드 키컬러를 적용한 체크·플라워 패브릭 패턴 배경을 배치하고, ‘화려함의 정의’라는 제목과 함께, 화려함을 반복이라는 언어로 정의하고 반복의 규칙으로 아이덴티티를 구체화한다는 내용을 하단 고스트 텍스트로 설명합니다.
2. 풀스크린 금속 이미지 시퀀스. 동일한 삼각형 세 조각이 순차 결합하고, REPEAT / CONNECT와 “반복되는 나. 연결되는 그리디어스.”가 반투명하게 겹칩니다.
3. 가방·자켓·패키지·쇼윈도 네 이미지를 한 화면에 모은 그리드.

화면 상단 중앙에 시안을 전환하는 01·02·03·04·05 고스트 링크만 고정합니다. 현재 시안은 밝게 표시합니다. 진행 표시, 추가 컬러·심볼 설명 섹션, 푸터는 없습니다. 자연스러운 브라우저 스크롤을 사용하며 입력을 가로채지 않습니다. 기존 편집형 페이지 파일은 보존하지만 로드하지 않습니다.

## 금속 이미지 모션
Blender Cycles에서 실제 조명과 반사, 브러시 결을 렌더한 144장의 투명 배경 WebP를 스크롤 위치에 맞춰 표시합니다. 레드 아노다이징 메탈, 브러시드 실버, 폴리시드 실버 소재를 사용했습니다. 이미지 사이에 부품을 변형하거나 크로스페이드하지 않습니다.

첫 화면은 이전보다 크게 배치합니다. 첫 번째와 두 번째 접합부 각각의 정확한 홈 끝 좌표로 카메라가 이동하며, 58mm 범위를 보여주는 매크로 장면으로 천천히 전환합니다. 마지막 12mm를 삽입하는 구간에 긴 스크롤을 배정하고, 결합 직후 잠시 가까이 머문 뒤 전체 형태로 돌아옵니다. 클로즈업 중 문구는 옅어집니다. 데스크톱 스크롤 장면은 500svh, 모바일은 460svh입니다.

- index.html: 공통 도입부, 심볼 시퀀스, 어플리케이션의 세 섹션
- brand-origin.css: 화면을 가득 채우는 패브릭 패턴 이미지와 하단 고스트 오버뷰. 번호 링크는 각 페이지의 #cover로 이동해 도입부를 다시 스크롤할 필요 없이 시안을 비교합니다.
- proposal-nav.js / proposal-nav.css: 첫 섹션에서는 시안 버튼을 숨기고, 두 번째 섹션부터 표시합니다. 첫 섹션으로 돌아오면 다시 숨깁니다.
- assembly.css: 풀스크린 스테이지, 고스트 텍스트, 반응형 그리드
- app.js: Canvas 2D 이미지 시퀀스, 우선 로딩, 디코딩 캐시 제한, 스크롤 연동
- assets/metal-closeup-20261018/: 1400px 데스크톱 / 720px 모바일 이미지 각 144장 및 manifest.json / camera-timeline.json
- assets/assembly-20261018/module.json: 검증용 메시, 결합 변환, 삽입축, 치수
- assets/assembly-20261018/validation.json: 전체 삽입 구간의 간섭 검사
- tools/export-assembly.py: Blender로 형상 생성·검사
- tools/render-metal-sequence.py: 기존 검증 모델을 동일한 변환으로 조립하며 금속 이미지 렌더
- assets/connection-20261018/: 기존 어플리케이션 사진

## 결합 구조
기준 한 변 100mm, 판 두께 4.6mm, 홈 너비 4.9mm, 홈 깊이 15.3mm, 끝 간극 0.08mm.
판의 상대 각도를 고정합니다. B가 첫 홈 축을 따라 65mm 이동한 후 C가 다음 홈 축을 따라 이동합니다. 되돌아 스크롤하면 같은 경로를 역순으로 표시합니다. 카메라가 구도에 맞춰 이동하지만 부품은 회전·변형·확대하지 않습니다.

Blender EXACT Boolean으로 0.5mm 간격, 786개 조합을 검사했고 이상적 강체의 겹침 부피는 0입니다. 동일 물체를 겹치는 양성 대조군과 폐곡면 검사도 통과했습니다. 이는 이상적 형상과 샘플 경로의 검사이며, 실물 고정력·하중·재료 공차 검증을 뜻하지 않습니다. 금속 렌더에 사용하는 원본 모델의 변환이 검증 데이터와 같은지도 비교합니다.

## 접근성과 성능
- 동작 줄이기: 마지막 금속 이미지만 로드하고 긴 스크롤 구간을 제거
- JavaScript 또는 이미지 시퀀스 실패: 같은 금속 소재의 조립 완료 이미지를 표시
- WebGL과 외부 렌더링 라이브러리 없이 Canvas 2D 사용
- 시작·완료 이미지 우선 로딩, 최대 4개 동시 요청, 디코딩 이미지 12장 내외로 캐시 제한
- 화면 밖·비활성 탭·스크롤 정지 시 렌더 중지
- 모바일에 작은 WebP 세트 제공. 제품 적용 이미지는 심볼을 중심으로 크롭
- 어플리케이션 네 장은 작은 화면에서도 하나의 화면 안에 표시

## 출처
- 심볼: 사용자 제공 삼각형을 바탕으로 만든 정확한 반복 형상
- 금속 시퀀스: Blender로 직접 렌더한 이 프로젝트의 검증 모델
- 적용 사진: 프로젝트에서 ImageGen으로 생성한 리브랜딩 콘셉트
- Pretendard: SIL Open Font License, assets/Pretendard-LICENSE.txt
- 기존 레이아웃 참고: https://www.plus-ex.com/experience#unni

## 게시
빌드 없는 정적 페이지이며 저장소 main의 GitHub Pages를 유지합니다. 필요한 변경만 커밋하고 GitHub Desktop의 Push로 게시합니다. 원본 렌더와 .blend는 로컬 creative/에 보존합니다.

## Alternative proposal 02

[Oval connection — proposal 02](https://greedilous.github.io/brand/be-greedilous/proposal-02/) is a separate two-section presentation using the supplied four-slot ellipse. The original triangle proposal remains at the existing URL. Source, application prompts and geometry verification are in proposal-02/.

## Alternative proposal 03

[Reflection lettering — proposal 03](https://greedilous.github.io/brand/be-greedilous/proposal-03/) preserves the supplied paired script wordmark and presents a metallic camera reveal followed by four application concepts. Source and image prompts are in proposal-03/.

## Alternative proposal 04 and shared navigation

[Symmetry — proposal 04](https://greedilous.github.io/brand/be-greedilous/proposal-04/) uses the supplied four-lobed symmetric emblem, a metallic detail sequence, and four fashion applications. The shared proposal-nav.css and five plain links in each index page provide top-center 01–05 navigation, active page state and keyboard focus. All five concepts remain directly addressable.

## Alternative proposal 05

[Interlace — proposal 05](https://greedilous.github.io/brand/be-greedilous/proposal-05/) uses the supplied crossing curves with an open central diamond, an exact traced metallic camera reveal, and four new fashion application images. The 05 link is available across all five concepts from the second section onward.
