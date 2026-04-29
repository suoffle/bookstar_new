## LitMatch
- 개인화된 도서 리뷰 및 추천 서비스를 제공하는 웹 플랫폼입니다.  
- 사용자의 도서 리뷰를 피드 형태로 다른 사용자들과 공유할 수 있으며, 사용자의 데이터를 바탕으로 취향에 맞는 도서를 추천합니다.

### 프로젝트 개요
LitMatch에서는 NFC(Neural Collaborative Filtering)와 KoBERT 두 가지 방식을 결합하여 사용자 맞춤형 도서 추천 기능을 제공합니다.
최종 추천 점수는 NCF : KoBERT = 7 : 3 의 비율로 반영하여 계산하였습니다.

### 사용 기술
- Django
- AWS
- NFC(Neural Collaborative Filtering)
- KoBERT
- Naver Book API
- Web Crawling
- SQLite
---
### 담당 역할
- 프론트엔드 웹 사이트 구현
- 사용자, 게시글(Feed), 좋아요, 북마크, 팔로워 Table 설계 및 구현
- KoBERT 기반 사용자 리뷰와 책 소개글 유사도 분석

### Features
- 회원가입 / 로그인 / 로그아웃
- 도서 리뷰 피드 작성/수정/업데이트/삭제
- 좋아요 / 북마크
- 팔로우
- 사용자 및 리뷰 검색
- 개인화 도서 추천
- 온보딩 기반 Cold-Start 완화
