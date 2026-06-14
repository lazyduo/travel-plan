# Travel Plan

여행 일정 페이지 모음. GitHub Pages로 서빙.
URL: https://lazyduo.github.io/travel-plan/

## 핵심 규칙

**HTML을 직접 편집하지 말 것.** YAML만 편집하고 푸시하면 GitHub Actions가 HTML을 자동 재생성한다.

```
# YAML만 편집 후 푸시하면 끝
git add east-europe-2026/europe_2026.yaml
git commit -m "update: ..."
git push
# → Actions가 index.html 자동 생성 & 커밋 → Pages 배포
```

로컬에서 미리 확인하고 싶을 때만 직접 실행:
```
pip install pyyaml
python3 east-europe-2026/generate_itinerary.py \
  east-europe-2026/europe_2026.yaml \
  east-europe-2026/index.html
```

## 구조

```
travel-plan/
├── .github/workflows/generate.yml   # YAML 변경 시 HTML 자동 생성
├── index.html                       # 여행 목록 홈 (직접 편집 가능)
└── east-europe-2026/
    ├── index.html                   # 생성된 파일 — 직접 편집 금지
    ├── europe_2026.yaml             # 데이터 원본 — 여기만 편집
    └── generate_itinerary.py        # HTML 생성기
```

## YAML 구조

```yaml
meta:          # 제목, 날짜, 기간
flights:       # outbound / return 항공편 정보
cities:        # 도시별 정보 (숙소, 팁, 볼거리 목록)
days:          # 날짜별 일정 (activities 리스트)
```

### activity 타입

| type   | 용도               |
|--------|--------------------|
| flight | 항공편 이동        |
| hotel  | 체크인             |
| sight  | 관광지             |
| art    | 미술관/갤러리      |
| nature | 자연/정원/호수     |
| music  | 공연/음악 관련     |
| spa    | 온천/스파          |
| boat   | 유람선/보트        |
| drive  | 차량 이동          |
| night  | 야경 감상          |
| shop   | 쇼핑               |
| cafe   | 카페               |

### activity 필드

```yaml
- type: sight
  name: "장소명"
  desc: "설명 (선택)"
  map_url: "https://maps.google.com/?q=..."   # 선택
  tag: "선택 | 미정 | 오전 | 20:10 ..."       # 선택
```

### transfer (이동일에 추가)

```yaml
transfer:
  type: flight   # flight | drive | train | bus
  from: "출발지"
  to: "도착지"
  note: "메모"
```
