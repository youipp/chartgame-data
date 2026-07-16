# chartgame-data

차트게임 앱이 사용하는 국내주식 일봉 데이터 저장소.

- `data/` — 시가총액 상위 종목들의 일봉 OHLCV JSON (출처: 네이버 금융, FinanceDataReader)
- 매주 월요일 06:00 KST에 GitHub Actions가 자동으로 최신 데이터를 수집·커밋합니다
- 수동 갱신: Actions 탭 → "주가 데이터 자동 수집" → Run workflow

앱은 시작 시 이 저장소의 raw URL에서 최신 데이터를 받아오고, 오프라인이면 앱에 내장된 데이터로 동작합니다.
