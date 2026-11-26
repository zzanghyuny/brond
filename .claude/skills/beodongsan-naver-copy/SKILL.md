---
name: "beodongsan-naver-copy"
description: "브동산 청약·분양(부동산정보) 포스팅의 네이버 블로그 발행본을 작성하거나 기존 포스팅을 네이버용으로 변환할 때 사용. 결론부터(예상 프리미엄) → 왜 이 가격인가 → 한줄평 → 지역 최근 분양단지 → 분양 사이트 자료 → 결론의 6섹션 표준(2026.11.09 Paul 승인)을 따른다. 네이버에 올리려고, 복사해서 붙여넣게, 태그도 뽑아줘 같은 말과 함께 slug나 몇 번째 포스팅이라고 지칭하면 바로 이 스킬을 쓴다. 사이트 원문을 그대로 복사하거나 구버전(D안·C안) 방식으로 만들지 않는다."
---

# 브동산 청약단지 글 → 네이버 블로그 발행본 작성 표준

2026.11.09 확정 (Paul 승인 샘플: 광교 자연앤 센트레빌, gwanggyo-jayeon-centreville). 이 문서가 네이버 발행본의 유일한 기준이다.

## 0. 이 문서의 지위

- 브동산 청약·분양(부동산정보) 포스팅의 네이버 발행본은 전부 아래 6섹션 구조로 쓴다. 이전의 D안(원문 그대로 복사), C안(핵심요약 100% 그대로 + 입지·상품·공급 표현만 재구성), 레이더·브릿지 차트를 막대 차트 A·B로 교체하던 방식, 2026.10.31 서식 생존 규칙 중 구조에 관한 부분은 모두 이 문서로 대체되어 폐기됐다(12번 참고). 충돌하면 이 문서가 이긴다.
- 사이트 글(posts/*.html)은 건드리지 않는다. 사이트 글의 양식과 적정가 산출은 beodongsan-realestate-post 스킬 그대로다. 이 스킬은 네이버용 사본만 새로 만든다.
- 사실과 수치(평점, 보정, 가격, 세대수, 일정)는 사이트 원본 그대로 쓴다. 바꾸는 것은 구조·표현·부가 정보뿐이다. 원본에 없는 수치를 지어내지 않는다.

## 1. 왜 이렇게 쓰나

1. 중복 문서 회피: 같은 글이 자체 도메인(brandongsan.com)과 네이버에 똑같이 올라가면 구글 캐노니컬화와 네이버 D.I.A. 판정에서 한쪽이 묻힌다. 목표는 사이트 글과 약 50% 달라 보이게 하는 것이다. 방법은 ① 섹션 순서·묶음 재편 ② 네이버 전용 섹션(지역 최근 분양단지, 한줄평) 추가 ③ 문장 재서술. 점검 방법은 10번.
2. 네이버 에디터 서식 생존: 네이버 블로그 에디터는 붙여넣기 때 style 블록과 박스형 CSS(테두리·배경·padding)를 걷어내고, 굵게·줄바꿈·이미지·단순 표만 살려둔다. 그래서 핵심 정보는 항상 글자 서식으로도 남긴다(8번).

## 2. 입력 수집

- 사이트 원본 posts/<slug>.html에서 가져온다: 평점표(입지/브랜드/상품성/종합), 보정표(기준 거래, 평점 보정, 연령 보정, 보정가격), 적정가격, 실제 분양가 표, 공급 구성·규제, 일정, 이미지 파일 목록. Paul이 HTML을 채팅에 붙여넣어 줄 수도 있다. 그 경우 작업공간에 저장해서 쓴다.
- 사이트 글이 없는 단지라면 beodongsan-realestate-post 절차로 분석을 먼저 끝내고 그 수치로 쓴다.
- 이미지: 원본의 상대경로 images/<slug>/파일명을 https://www.brandongsan.com/posts/images/<slug>/파일명 으로 바꿔 쓴다. data: URI는 네이버가 거부하므로 금지. 원본 이미지가 base64라면 11번 절차로 먼저 실제 파일화한다. 원본에 없는 이미지 파일명을 지어내지 않는다.
- 평점·보정 수치가 페이지에서 확인되지 않으면 추정하지 말고 Paul에게 요청한다.

## 3. 용어 (고정)

- 브동산 분석 적정가격 (줄여 쓸 때는 적정가격). 브동산 적정가 같은 줄임 표현은 독자가 뜻을 모르므로 쓰지 않는다 (2026.11.09 Paul).
- 실제 분양가, 예상 프리미엄, 브동산 판정(저평가 / 적정 / 고평가), 보정가격, SITE(사업지), 비교단지.
- (2026.11.21 Paul) 예상 프리미엄은 금액만 먼저 쓰고("예상 프리미엄은 +5,960만이다."), 판정은 따로 쓴다("브동산 판정은 저평가다."). "+5,960만(약 7% 저평가)"처럼 금액 괄호에 판정·%를 붙이지 않는다. 판정 기준은 차이율(프리미엄÷분양가) +3% 이상 저평가, ±3% 미만 적정, −3% 이하 고평가(beodongsan-realestate-post 6-2번).
- 예상 프리미엄 표기: 계산값을 십만원 단위로 반올림한 값을 쓴다. 1억 이상은 억 단위 소수 둘째 자리(+5.52억), 1억 미만은 만원 단위(2,330만원, 마피는 -2,330만원). 상세 규칙은 beodongsan-realestate-post 6-1.
- 마피 조정이 적용된 단지는 realestate-post 6-1의 공개 원칙대로 근거 ①(계약금 하한) ②(선분양 수요 프리미엄)를 한두 문장 언급한다.

## 4. 글 구조 (6개 번호 섹션, 순서 고정)

제목: {단지명} | 예상프리미엄 {부호}{금액}, 분양가 평면 총정리
예) 광교 자연앤 센트레빌 | 예상프리미엄 +5.52억, 분양가 평면 총정리
지역 접두어(OO시 - 같은 것)는 따로 붙이지 않고, 단지명 안의 지명은 그대로 둔다. 금액은 본문의 값과 같아야 한다. 구분자는 슬래시가 아니라 세로선(|)이다.

본문 첫 문장 (검색 노출용, 2026.11.21 Paul 신설): 네이버 검색 결과에는 본문 첫 문장이 미리보기로 뜬다. 그래서 본문은 항상 아래 두 문장으로 시작한다. 이 두 문장이 본문의 맨 처음이다. 그 앞에 이미지·바이라인·스탯 박스·소제목을 두지 않는다.

패턴 (존댓말, 일반 글자로 쓴다. 굵게·표·박스 안에 넣지 않는다):
{단지명}은 {동·지역}에서 {일반분양 세대수}세대를 분양합니다. 전용 {기준타입}㎡ {세대수}세대의 가중평균 분양가는 {X.XX억 원}이며 {M월 D일} 1순위입니다.

예) 고양 한신더휴 퍼스트원은 행신동에서 102세대를 분양합니다. 전용 84㎡ 31세대의 가중평균 분양가는 8.08억 원이며 12월 1일 1순위입니다.

작성 규칙:
- 단지명은 제목과 같은 표기로, 첫 문장 맨 앞에 쓴다.
- 세대수·분양가·1순위 날짜는 사이트 원본과 입주자모집공고 그대로 쓴다. 지어내지 않는다.
- 기준타입은 포스팅의 적정가격 비교 기준 타입(84㎡가 기본, 없으면 59㎡ 등)과 같게 한다.
- 분양가는 같은 타입의 가중평균이다. 평당가·㎡당가는 쓰지 않는다. 예상 프리미엄 수치는 이 문장에 넣지 않는다(섹션 1의 스탯 박스와 굵은 문장이 맡는다).
- 무순위·잔여세대·선착순처럼 1순위가 없는 공급은 접수일로 바꿔 쓴다(예: "…가중평균 분양가는 9.68억 원이며 11월 24일 하루 접수합니다.").
- 공급이 전 세대 같은 타입이거나 일반분양만 있어 세대수 구분이 필요 없으면 "전용 84㎡ 499세대"처럼 해당 값으로 바꾼다.

이 두 문장 바로 다음 줄에 바이라인을 둔다(이전에는 바이라인이 맨 위였으나 순서를 바꿨다):

바이라인: 브동산 · 청약 언박싱 No.NNN · 발행일 (공고 기준일)
예) 브동산 · 청약 언박싱 No.109 · 2026. 11. 18 (2026.11.19 공고 기준)

순서 정리: 본문 첫 두 문장 → 바이라인 → 1번 섹션(결론부터) 이하. 제목(네이버 글 제목 칸)은 그대로 `{단지명} | 예상프리미엄 {부호}{금액}, 분양가 평면 총정리`다.

섹션 제목(h2) 형식: 번호. 제목. 각 섹션 사이 빈 문단 필수(8번).

1. 결론부터 — 이 단지 예상 프리미엄은 +X.XX억
- 한두 문장 도입 → **적정가격·분양가·예상 프리미엄 막대 그래프 이미지(chart-b) + 회색 캡션** → 대표 조감도(cover 이미지) + 캡션 → 단지 개요 표. (2026.11.21 Paul: 스탯 박스 3개와 세 숫자 굵은 문장은 쓰지 않고 그래프 이미지로 대신한다. 이미지 alt 텍스트에 수치를 넣는다. 그래프는 섹션 2에서 옹겨 온 것이라 섹션 2에는 다시 넣지 않는다.)
- 단지 개요는 어디? / 언제? / 얼마? / 주의 같은 줄글 나열 대신 항목|내용 2열 표로 정리한다(2026.11.12 Paul). 표는 대표 조감도 캡션 바로 아래에 소제목 없이 곧바로 둔다. 행 순서와 내용은 아래 기준을 따른다.
  1) 위치: 주소 + 가장 가까운 역·핵심 입지 한 줄
  2) 규모: 총 세대수·동수·층수, 일반분양 세대수
  3) 평형 구성: 타입별(59㎡A~D, 84㎡A~C 등) 세대수. 지분적립형 같은 특수 타입은 타입명 옆에 표기
  4) 분양가: 타입별 분양가 범위(최저~최고) 또는 가중평균. 숫자는 사이트 원본 그대로
  5) 청약 일정: 공고일 / 특별공급 / 1순위 / 2순위 / 당첨자 발표 / 계약. 날짜는 br로 줄바꿈해 한 칸에 담는다
  6) 공급 구성: 특별공급(유형별 세대수)과 일반공급 세대수
  7) 시공사·시행사
  8) 입주 예정
  9) 규제·전매제한: 분양가상한제, 전매제한, 거주의무, 재당첨 제한 등 원본에 있는 것만
  10) 주의: 분석에서 제외한 타입(지분적립형 등), 청약 자격 요건 확인, 접수 전이라 경쟁률 확인 불가 등. 이 행은 반드시 마지막에 둔다
  원본에 없는 항목은 행 자체를 뺀다. 지어내서 채우지 않는다.
- 표는 th/td 단순 구조만 쓴다(8번 규칙 6). 첫 열(항목)은 th로 쓴다.
- 표 예시(대괄호는 포스팅 원본 값으로 교체, 숫자는 광교 자연앤 센트레빌 기준 예시):

<table><tbody>
<tr><th>위치</th><td>[원문 주소] ([가장 가까운 역·핵심 입지])</td></tr>
<tr><th>규모</th><td>총 360세대 · 일반분양 90세대 · 특별공급 270세대</td></tr>
<tr><th>평형 구성</th><td>84㎡A 40세대 · 84㎡B 278세대 · 84㎡C 42세대 · 59㎡ 지분적립형 A~D</td></tr>
<tr><th>분양가</th><td>84㎡ 가중평균 9.37억 (84A 9.02~9.49억 · 84B 9.02~9.49억 · 84C 8.92~9.39억)</td></tr>
<tr><th>청약 일정</th><td>공고 10.30<br>특별공급 11.09 · 1순위 11.10 · 2순위 11.11<br>당첨자 발표 11.17</td></tr>
<tr><th>시공사</th><td>[원문 값]</td></tr>
<tr><th>입주 예정</th><td>2029.10</td></tr>
<tr><th>주의</th><td>지분적립형(59㎡)은 분석에서 제외했습니다. 청약 자격 요건은 입주자모집공고문에서 확인하세요.</td></tr>
</tbody></table>

2. 왜 이 가격이 나왔을까 — 입지와 가격 비교
- 입지(h3): 입지 한 문단(사이트 입지 분석을 재서술, 입지 점수 근거 포함) → 위치 개략도(사이트의 chart-map.png) + 캡션 → 예정 교통·학교 한 문단(개통·배정 단정 금지 원칙 유지).
- 비교단지(h3): 비교단지 선정과 기준 거래 한 문단(같은 타입, 거래일, 층, 완전히 맞추지 못한 한계) → 평점 비교표 이미지(chart-a) + 캡션 → 굵은 문장(종합평점 3개 + 보정 %) → 가격 비교 HTML 표(기준 거래 / 평점 보정 / 연령 보정 / 보정가격) + 연령 보정 설명 note → 굵은 문장(두 보정가격, 평균 = 적정가격, 차이 = 예상 프리미엄)으로 끝낸다. 적정가격 막대 그래프(chart-b)는 섹션 1로 옮겼으므로 여기에 두지 않는다(2026.11.21 Paul). 평점 비교는 그래프 이미지(chart-a)가 표 역할을 하므로 입지·브랜드·상품성 점수 HTML 표는 만들지 않는다(중복, 2026.11.21 Paul). 이미지 아래 굵은 종합평점 문장과 가격 비교 표는 그대로 둔다.

3. 브동산 한줄평
- 굵은 한 문장 + 근거 두세 문장 + 한계(전매제한, 청약 요건 확인 등). 톤 판단은 6번.

4. 해당 지역 최근 분양단지, 같은 타입은 얼마였나
- 조사 절차는 7번. 표 + 굵은 요약 한 줄.

5. 분양 사이트 자료로 한 번에 보기
- 별도 설명 문단 없이 **한줄평 한 줄(굵게)** 다음에 자료를 쫙 나열한다. 순서와 규칙은 9번(2026.11.21 Paul).

6. 결론
- 한줄평을 섹션 3과 다른 표현으로 굵게 + 홈페이지 링크 문장(6번 하단) + 면책 문구 한 줄.

## 5. 문체

- 평서형(-다)이 기본이다. 본문 첫 두 문장(검색 노출용, 4번 참고), 스탯 박스 바로 아래 요약 문장과 홈페이지 링크 문장은 입니다/습니다체를 쓴다(샘플 기준).
- 담백하고 과장 없이 쓴다. 전매제한, 지분적립형 구조, 청약 자격 요건 같은 리스크도 한 번은 적는다.
- 본문 중간에 투자 조언이 아니라는 면책을 반복하지 않는다. 면책은 맨 아래 한 번만. 과거에 쓰던 팀장님 연락처 문의 안내문은 쓰지 않는다.

## 6. 한줄평 로직 (섹션 3과 6)

판단 기준은 예상 프리미엄(또는 마피)의 크기와 분양가 대비 비중이다. 세 가지 톤:

- 프리미엄이 뚜렷한 플러스 → 투자로도 실거주로도 모두 만족. 청약 자격이 되면 무조건 넣어야 한다는 단정 톤. 예) 예상 프리미엄 +5.52억 — 투자로도, 실거주로도 놓치기 아까운 단지다.
- 프리미엄이 미약하거나 무피·약한 마피 → 투자로는 애매하지만 실거주라면 괜찮을 듯. 어떤 가구에 맞는지 한 단어로 짚는다(신혼부부, 학령기 자녀 가족 등).
- 마피 폭이 큼 → 실거주하면서 버틴다는 각오가 있다면 해볼 만하다. 단정하지 않고 시장 변곡점과 판촉 조건을 지켜보라는 취지를 담는다. 마피 조정이 적용된 단지면 3번의 공개 원칙 문장을 함께 넣는다.

수치 경계는 정해진 숫자가 없다. 분양가 대비 비중과 단지 등급·입지를 보고 판단하고, 애매하면 Paul에게 어느 톤으로 쓸지 짧게 확인한다.

섹션 3에는 굵은 한줄평 + 근거(공공분양, 분양가상한제 등) + 한계(전매제한, 청약 요건 확인)를 쓰고, 섹션 6에는 같은 판단을 다른 표현으로 굵게 쓴다(복사 금지). 홈페이지 링크 문장은 그 포스팅의 실제 URL로 건다:

<p>자세한 평가표와 적정가격 산출 과정은 <a href='https://www.brandongsan.com/posts/SLUG.html'>브동산 홈페이지</a>에서 확인하실 수 있습니다.</p>

(SLUG 자리에 실제 slug를 넣는다. 홈페이지 첫 화면이 아니라 해당 포스팅 URL이어야 한다.)

## 7. 섹션 4 — 지역 최근 분양단지 조사 절차

- 대상: SITE와 같은 시·군·구(없으면 인접 구·시로 넓히고 본문에 밝힘)에서 최근 약 12개월 안에 청약을 받은 단지 2곳. 오래된 단지는 제외한다(광교 사례에서 2024년 분양 단지를 뺐다).
- 같은 타입 기준: SITE 대표 타입(84㎡ 등)의 분양가 범위(최저~최고)를 쓴다. 해당 타입이 2가구뿐인 단지는 대표성이 없어 제외한다. 평당가 환산은 하지 않고 총액만 쓴다.
- 검증: 분양가는 가능하면 두 개 이상 출처(뉴스 + 분양 공고·집계 글)에서 일치하는 값만 쓴다. 출처가 하나뿐이면 표에서 빼거나, 쓰더라도 전달 메시지에서 Paul에게 알린다. 경쟁률은 두 출처 이상 일치할 때만 쓰고, 아니면 생략한다. 한 글 안에서 수치가 모순되면(세대수 불일치 등) 다수 출처 값을 따른다.
- 표 열: 단지 / 위치·규모 / 청약 시기 / 입주예정 / 84㎡ 분양가. 마지막 행에 이번 SITE 행을 굵게 넣어 비교한다. 일반분양과 공공분양(분양가상한제)처럼 규제가 다르면 도입 문장에서 밝힌다. 표 아래 note: 최초 분양가 기준, 발코니 확장비·유상옵션·취득세 제외, 타입 범위.
- 표 아래 굵은 요약 한 줄(두 단지의 분양가대 + 이번 단지 평가). 시세 수치는 본문에 이미 있는 비교단지 실거래값만 쓴다.
- 확인이 덜 된 항목(출처마다 청약 시기가 다름 등)은 전달 메시지에서 따로 알린다.

## 8. 네이버 에디터 서식 생존 규칙

1. (2026.11.21 개정) 섹션 1의 적정가격·분양가·예상 프리미엄은 스탯 박스와 아래 굵은 문장 대신 그래프 이미지 한 장으로 표현한다. 나머지 구간의 핵심 수치는 굵은 문장으로도 쓴다. 예전 규칙(섹션 1에 스탯 박스 바로 아래 문장): <p>브동산이 분석한 이 단지의 적정가격은 <b>14.88억원</b>, 실제 분양가는 <b>9.37억원</b>으로, <b>예상 프리미엄은 +5.52억원(약 59% 저평가)</b>입니다.</p> 예상 프리미엄은 항상 마지막에 가장 강조한다. 이 문장은 섹션 1, 평점 비교표 이미지 아래(종합평점), 가격 비교표 아래에 각각 둔다.
2. 번호 섹션(h2) 직전마다 빈 문단 <p> </p>을 하나 넣는다. CSS 간격은 네이버에서 사라진다.
2-1. (2026.11.21 Paul) 숫자가 붙은 소제목(h2: "1. 결론부터 …" ~ "6. 결론")은 볼드체에 본문보다 약간 큰 글자로 쓴다. 네이버 에디터는 style을 걷어내므로 글자 자체에 서식을 입힌다: `<h2><b><span style="font-size:20px;">1. …</span></b></h2>` (미리보기 CSS는 h2{font-size:20px;font-weight:800}). 붙여넣기 후 에디터 글자 크기가 기본(15·16)보다 크고 굵은지 확인하고, 안 맞으면 네이버 19 사이즈 + 굵게로 직접 지정한다. h3는 기존대로 둔다.
3. 사진 묶음마다: 이미지 → 작은 회색 캡션(<p class='note'>이미지 NN · 설명</p>) → 빈 문단. 캡션은 절대 굵게 쓰지 않는다(굵음은 핵심 수치 문장 전용, 2026.11.09 Paul). 사진이 2장 이상 연속되면 빈 문단은 필수. 캡션은 사진 종류 + 한 줄 설명(예: 84B 평면도 (278세대, 주력 타입)).
4. 표 아래에는 굵은 요약 문장을 둔다(표 테두리가 사라져도 숫자가 남도록): 평점 비교표 이미지 아래(종합평점), 가격 비교표 아래(두 보정가격·적정가격·예상 프리미엄), 분양가 표 아래(가중평균), 최근 분양단지 표 아래.
5. 단지 개요(위치·일정·가격·평형 구성·시공사 등)는 줄글로 나열하지 않고 항목|내용 2열 표로 정리한다. 어디? / 언제? / 얼마? / 주의 식의 줄글 4줄은 쓰지 않는다(2026.11.12 Paul).
6. 표(table)는 th/td 단순 구조만 쓴다. 셀 병합·배경색에 의존하지 않는다. 두 줄 셀은 br.
6-1. (2026.11.21 Paul) 네이버에 붙여넣으면 표가 깨지므로, **전달 전에 모든 표를 모바일 폭 PNG 이미지로 바꾼다**(13-1번 스크립트). HTML 표는 작성용 원본일 뿐 네이버에는 이미지로 들어간다.
7. 미리보기용 style 블록(.note 13px 회색, .stat 테두리 박스, table 테두리)은 넣되, 붙여넣기 후엔 사라진다고 가정하고 중요한 정보는 모두 글자 서식으로도 남긴다.
8. 차트 이미지 3장(chart-a/b/c)은 사이트에 올리지 않은 로컬 PNG다. HTML에는 자리표시 주석 <!-- [이미지 삽입 자리] chart-a-score.png : 설명 --> 과 상대경로 img 태그를 함께 둔다. 붙여넣으면 이미지가 깨져 보이므로 Paul이 네이버 에디터에서 그 위치에 직접 업로드한다.

## 9. 섹션 5 — 분양 사이트 자료 순서

(2026.11.21 Paul 개정) 섹션 5는 **한줄평 한 줄 + 분양 사이트 자료 전체 나열**이다. 별도 설명 문단은 쓰지 않는다. 소제목(h3)은 아래 순서로 두고, 이미지는 이미지 NN 연번 캡션을 붙인다.

1. 타입별 분양가 정리 — 타입별 표(세대수·분양가 범위·가중평균) + 주력 타입의 층·라인별 공급금액 표 + 납부 조건 굵은 한 문장
2. 입지 — 공식 위치도·주변 정비계획 지도·광역 조감도 등 공식 사이트 이미지(대표 조감도는 섹션 1에서 쓰므로 반복하지 않는다)
3. 단지 배치도
4. 동·호수 배치 — 공식 동호수 배치도가 없으면 공고 공급금액표의 타입별 동·호수 라인·층 구성 표로 대신하고 "공고 기준으로 브동산이 정리한 표"라고 밝힌다
5. 커뮤니티 — 공식 커뮤니티 이미지 + 공고의 부대복리시설 굵은 한 문장
6. 평면 — 타입별 평면도(모든 타입을 하나씩, 주력 타입은 세대수 표기). 특수 타입(지분적립형 등)은 구조 설명 한 줄 + 평면도
7. 청약 일정 — 직접 그린 일정 타임라인 이미지(chart-c, 13번). 공동 일정은 공고에 나온 날짜만 쓴다

공식 홈페이지에 아직 올라오지 않은 항목(견본주택 오픈 전 배치도·평면·커뮤니티 등)은 소제목을 유지한 채 `<!-- [이미지 삽입 자리] -->` 주석과 "공식 홈페이지 미공개(오픈 예정일)" 한 줄만 남기고, 지어내지 않는다.

- 모든 이미지에 이미지 NN 연번 캡션을 붙인다. 대표 조감도는 섹션 1에서 쓰므로 여기서는 다른 조감도·광역 조감도를 쓴다.
- 청약 일정 이미지: 공식 분양 사이트 캡처가 저장돼 있으면 그것을 쓰고, 없으면 13번의 chart-c 타임라인을 만든다(공고에 나온 날짜만 사용).
- 사이트 저장소에 없는 이미지를 지어내지 않는다. 부족하면 Paul에게 요청한다.

## 10. 중복도 점검 (전달 전)

사이트 원문과 네이버 본문을 문장 단위로 나눠 difflib.SequenceMatcher로 각 네이버 문장의 최고 유사도를 구하고, 0.8 이상(사실상 동일)인 문장 비율을 본다. 광교 샘플은 118문장 중 34문장(29%), 평균 최고 유사도 0.64였다(표 셀·캡션·면책 포함). 이 수준보다 같은 문장이 많아지지 않게 하고, 서술형 문단에서 0.8을 넘는 문장이 보이면 그 문단을 다시 쓴다. 표·수치·고정 면책 문구는 제외하고 판단한다.

## 11. 사이트 쪽 사전 확인 (기존 절차 유지)

- 원본 이미지가 base64(data:)면 먼저 scripts/migrate_base64_images.py list / apply로 실제 파일화한다. 사이트에 반영되는 변경이므로 자동 commit·push 금지: 변경 목록 제시 → 사용자 확인 → push 직전 git fetch → 반영 후 curl로 새 이미지 URL이 200인지 확인.
- 위치 개략도 chart-map.png가 사이트에 없으면 scripts/capture_chart_images.js로 .map-wrap을 캡처한 뒤 같은 안전 절차로 반영한다. chart-radar·chart-bridge는 네이버에 쓰지 않는다.
- scripts/build_naver_copies.py와 assets/copy-template.html은 D안 시절 자료다. 더 이상 쓰지 않는다(카드로는 삭제할 수 없어 폴더에 남아 있을 뿐이다).

## 12. 폐기된 규칙 (되살리지 말 것)

- D안: 사이트 원문을 형식만 바꿔 그대로 복사.
- C안의 핵심요약·결론 처리: 핵심요약 100% 그대로 옮기기, 결론을 한줄평 한 문장으로만 교체해 맨 끝에 두기, 입지/상품/공급분석을 같은 순서로 표현만 바꾸기, 5섹션 구조.
- 차트 A(항목별 평점 막대)·차트 B(적정가 산출 막대)로 레이더·브릿지를 대체하던 구성 → 평점 비교표 이미지 + 적정가격 막대 그래프(13번)로 교체.
- 브동산 적정가 라는 줄임 용어 → 브동산 분석 적정가격.
- 굵은 사진 캡션 → 작은 회색 비굵은 캡션.
- 제목의 슬래시 구분자 → 세로선(|) 구분자.
- 하단 팀장님 연락처 문의 안내문.
- 섹션 1의 어디? / 언제? / 얼마? / 주의 줄글 4줄 → 단지 개요 표로 교체(2026.11.12).

## 13. 차트 스크립트 (matplotlib, 모노톤, 폰트 NotoSansCJK)

DATA만 포스팅 값으로 교체해 실행한다. 점수는 [입지, 브랜드, 상품성] 순서. 비교단지가 2곳이 아니면 열 구성을 맞게 조정한다. 팔레트는 beodongsan-design-guideline의 모노톤(#111111 / #555555 / #8A8A8A / #E3E3E3)이며 컬러는 쓰지 않는다. 마피(고평가)인 경우 premium_text를 -1.30억처럼, pct_text를 약 N% 고평가로 바꾼다.

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''브동산 청약단지 네이버 발행본용 차트 3장 (모노톤, beodongsan-design-guideline 준수)
  chart-a-score.png    : 평점 비교표 이미지 (입지/브랜드/상품성/종합, SITE vs 비교단지 2곳)
  chart-b-price.png    : 비교단지 2곳 보정가격 + SITE 브동산 분석 적정가격 + 실제 분양가 막대 그래프
  chart-c-schedule.png : 청약 일정 타임라인 (공식 분양 사이트에 일정 이미지가 없을 때만 사용)
사용법: python3 make_naver_charts.py <out_dir>   (아래 DATA만 해당 포스팅 값으로 교체)
숫자는 반드시 사이트 원본 포스팅의 평점표/보정표에서 그대로 옮긴다(새로 계산/추정 금지).
'''
import sys, os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.font_manager import FontProperties

# ============ 포스팅마다 교체하는 값 (예시: 광교 자연앤 센트레빌) ============
# 점수는 [입지(40), 브랜드(20), 상품성(40)] 순서
DATA = {
    'site': {'name': '광교 자연앤 센트레빌', 'note': 'SITE · 2029.10 입주예정', 'scores': [13, 12, 25]},
    'comps': [
        {'name': '광교호반베르디움', 'note': '비교단지 · 2014.06 입주', 'scores': [17, 12, 29], 'short': '베르디움', 'mult': 0.920},
        {'name': '광교더샵', 'note': '비교단지 · 2018.08 입주', 'scores': [17, 20, 29], 'short': '더샵', 'mult': 0.840},
    ],
    'price': {                      # 단위: 억원, 같은 타입 총액
        'comp_adjusted': [15.49, 14.27],   # 비교단지 보정가격 2개
        'fair': 14.88,                     # 브동산 분석 적정가격(두 보정가격의 평균)
        'actual': 9.37,                    # 실제 분양가(본문과 동일한 값)
        'premium_text': '+5.52억',         # 십만원 반올림 규칙을 거친 최종 표기(마이너스면 -1.30억)
        'pct_text': '브동산 판정 · 저평가',  # 판정은 금액과 따로: 저평가 / 적정(±3% 미만) / 고평가 (2026.11.21)
        'type': '84㎡',
    },
    'schedule': {
        'note': '입주자모집공고(2026.10.30) 기준 · 84㎡ 공공분양',
        'events': [('10.30', '입주자모집공고', False), ('11.09', '특별공급', True), ('11.10', '1순위', True),
                   ('11.11', '2순위', True), ('11.17', '당첨자 발표', True)],
        'footer': '날짜는 청약홈 공고 기준이며 접수 시간·자격 요건은 입주자모집공고문에서 반드시 확인한다.',
    },
}
# ====================================================================

OUT = sys.argv[1] if len(sys.argv) > 1 else '.'
os.makedirs(OUT, exist_ok=True)
BOLD = FontProperties(fname='/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc')
REG = FontProperties(fname='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc')
INK, MID, SOFT, HAIR, PANEL = '#111111', '#555555', '#8A8A8A', '#E3E3E3', '#F5F5F5'
DPI = 200


def T(ax, x, y, s, size=10, bold=False, color=INK, ha='left', va='center', **kw):
    fp = (BOLD if bold else REG).copy()
    fp.set_size(size)
    ax.text(x, y, s, fontproperties=fp, color=color, ha=ha, va=va, **kw)


def chart_a(path):
    W, H = 7.75, 5.75
    fig = plt.figure(figsize=(W, H), dpi=DPI, facecolor='white')
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, W)
    ax.set_ylim(H, 0)
    ax.axis('off')
    lx = 0.35
    cols = [(1.95, 3.78), (3.78, 5.61), (5.61, 7.44)]
    cen = [(a + b) / 2 for a, b in cols]
    T(ax, lx, 0.38, '평점 비교표', 14, True)
    T(ax, 7.44, 0.38, '100점 만점 · 브동산 모형 자체 산정', 8.2, False, SOFT, ha='right')
    ax.add_patch(Rectangle((cols[0][0], 0.75), cols[0][1] - cols[0][0], H - 1.3, fc=PANEL, ec='none', zorder=0))
    ents = [DATA['site']] + DATA['comps']
    for i, (c, e) in enumerate(zip(cen, ents)):
        site = i == 0
        T(ax, c, 1.12, e['name'], 10.6 if site else 10.2, True, INK if site else MID, ha='center')
        T(ax, c, 1.43, e['note'], 7.8, False, MID if site else SOFT, ha='center')
    ax.plot([lx, 7.44], [1.70, 1.70], color=INK, lw=1.3)
    y, bar_w = 1.70, 1.15
    for name, mx, k in [('입지', 40, 0), ('브랜드', 20, 1), ('상품성', 40, 2)]:
        h = 0.80
        yc = y + h / 2
        T(ax, lx, yc - 0.10, name, 11.5, True)
        T(ax, lx, yc + 0.17, str(mx) + '점 만점', 7.8, False, SOFT)
        for i, (c, e) in enumerate(zip(cen, ents)):
            v, site = e['scores'][k], i == 0
            T(ax, c - 0.06, yc - 0.12, str(v), 20, True, INK if site else MID, ha='right')
            T(ax, c - 0.02, yc - 0.06, '/' + str(mx), 8.5, False, SOFT, ha='left')
            bx, by = c - bar_w / 2, yc + 0.17
            ax.add_patch(Rectangle((bx, by), bar_w, 0.07, fc=HAIR, ec='none'))
            ax.add_patch(Rectangle((bx, by), bar_w * v / mx, 0.07, fc=INK if site else SOFT, ec='none'))
        y += h
        ax.plot([lx, 7.44], [y, y], color=HAIR, lw=0.8)
    h = 1.25
    ax.plot([lx, 7.44], [y, y], color=INK, lw=1.3)
    yc = y + h / 2
    T(ax, lx, yc - 0.08, '종합평점', 12.5, True)
    T(ax, lx, yc + 0.2, '입지 + 브랜드 + 상품성', 7.8, False, SOFT)
    totals = [sum(e['scores']) for e in ents]
    for i, (c, v) in enumerate(zip(cen, totals)):
        site = i == 0
        T(ax, c - 0.07, yc - 0.06, str(v), 28, True, INK if site else MID, ha='right')
        T(ax, c - 0.02, yc + 0.02, '/100', 9, False, SOFT, ha='left')
        bx, by = c - bar_w / 2, yc + 0.30
        ax.add_patch(Rectangle((bx, by), bar_w, 0.07, fc=HAIR, ec='none'))
        ax.add_patch(Rectangle((bx, by), bar_w * v / 100, 0.07, fc=INK if site else SOFT, ec='none'))
    y += h
    ax.plot([lx, 7.44], [y, y], color=HAIR, lw=0.8)
    c1, c2 = DATA['comps']
    foot = '점수 차이에 따라 비교단지 시세를 보정한다 (SITE %d점 기준: %s ×%.3f, %s ×%.3f).' % (
        totals[0], c1['short'], c1['mult'], c2['short'], c2['mult'])
    T(ax, lx, H - 0.22, foot, 7.8, False, SOFT)
    fig.savefig(path, facecolor='white')
    plt.close(fig)


def chart_b(path):
    P = DATA['price']
    c1, c2 = DATA['comps']
    tp = P['type']
    W, H = 7.75, 5.6
    fig = plt.figure(figsize=(W, H), dpi=DPI, facecolor='white')
    ax = fig.add_axes([0.04, 0.17, 0.92, 0.66])
    xs = [0.0, 1.0, 2.35, 3.35]
    vals = P['comp_adjusted'] + [P['fair'], P['actual']]
    top = max(vals) * 1.28
    u = top / 19.0
    ax.bar(xs, vals, width=0.62, color=[MID, SOFT, INK, '#C4C4C4'], zorder=3)
    for x, v in zip(xs, vals):
        T(ax, x, v + u * 0.35, '%.2f억' % v, 13, True, INK, ha='center', va='bottom')
    ax.set_xlim(-0.6, 5.35)
    ax.set_ylim(0, top)
    ax.set_xticks(xs)
    ax.set_xticklabels([])
    names = [c1['name'], c2['name'], 'SITE', 'SITE']
    subs = ['보정가격', '보정가격', '브동산 분석 적정가격', '실제 분양가']
    for x, a, b in zip(xs, names, subs):
        T(ax, x, -0.9 * u, a, 9.4, True, INK, ha='center', clip_on=False)
        T(ax, x, -2.0 * u, b, 9.4, False, MID, ha='center', clip_on=False)
    ax.set_yticks([])
    for s in ['top', 'right', 'left']:
        ax.spines[s].set_visible(False)
    ax.spines['bottom'].set_color(HAIR)
    ax.tick_params(axis='x', length=0)
    ax.plot([1.68, 1.68], [0, 17.2 * u], color=HAIR, lw=1, ls=(0, (4, 3)), zorder=1)
    T(ax, 0.5, 17.9 * u, '비교단지 (%s 실거래 → 보정)' % tp, 8.6, False, SOFT, ha='center')
    T(ax, 2.85, 17.9 * u, 'SITE (%s 기준)' % tp, 8.6, False, SOFT, ha='center')
    ax.plot([2.66, 4.35], [P['fair']] * 2, color=SOFT, lw=1, ls=(0, (2, 2)), zorder=2)
    ax.plot([3.66, 4.35], [P['actual']] * 2, color=SOFT, lw=1, ls=(0, (2, 2)), zorder=2)
    ax.annotate('', xy=(4.35, P['fair']), xytext=(4.35, P['actual']),
                arrowprops=dict(arrowstyle='<->', color=INK, lw=1.6, shrinkA=0, shrinkB=0), zorder=4)
    mid = (P['fair'] + P['actual']) / 2
    T(ax, 4.55, mid + 1.15 * u, '예상 프리미엄', 9.5, False, MID)
    T(ax, 4.55, mid, P['premium_text'], 17, True, INK)
    T(ax, 4.55, mid - 1.1 * u, P['pct_text'], 8.6, False, SOFT)
    f1 = BOLD.copy()
    f1.set_size(14)
    f2 = REG.copy()
    f2.set_size(8.2)
    fig.text(0.045, 0.93, '적정가격 산출 비교', fontproperties=f1, color=INK, ha='left', va='center')
    fig.text(0.955, 0.93, '단위: 억원 · 전용 %s 총액 기준' % tp, fontproperties=f2, color=SOFT, ha='right', va='center')
    fig.savefig(path, facecolor='white')
    plt.close(fig)


def chart_c(path):
    S = DATA['schedule']
    ev = S['events']
    W, H = 7.75, 2.9
    fig = plt.figure(figsize=(W, H), dpi=DPI, facecolor='white')
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, W)
    ax.set_ylim(H, 0)
    ax.axis('off')
    T(ax, 0.35, 0.40, '청약 일정', 14, True)
    T(ax, 7.40, 0.40, S['note'], 8.2, False, SOFT, ha='right')
    x0, x1, ly = 0.95, 6.80, 1.65
    ax.plot([x0, x1], [ly, ly], color=HAIR, lw=2.2, zorder=1)
    ax.plot([x0 + 0.6, x1], [ly, ly], color=INK, lw=2.2, zorder=1)
    step = (x1 - x0) / (len(ev) - 1)
    for i, (d, n, filled) in enumerate(ev):
        x = x0 + i * step
        ax.scatter([x], [ly], s=170, zorder=3, facecolor=INK if filled else 'white', edgecolor=INK, linewidth=1.8)
        T(ax, x, ly - 0.52, d, 17, True, INK, ha='center')
        T(ax, x, ly + 0.50, n, 10.5, False, MID, ha='center')
    T(ax, 0.35, H - 0.22, S['footer'], 7.8, False, SOFT)
    fig.savefig(path, facecolor='white')
    plt.close(fig)


if __name__ == '__main__':
    chart_a(os.path.join(OUT, 'chart-a-score.png'))
    chart_b(os.path.join(OUT, 'chart-b-price.png'))
    chart_c(os.path.join(OUT, 'chart-c-schedule.png'))
    print('done', OUT)
```

## 13-1. 표는 전부 이미지로 (2026.11.21 Paul)

네이버 에디터에 HTML 표를 붙여넣으면 칸 폭·줄바꿈·테두리가 제멋대로 바뀐다. 그래서 **네이버 발행본의 모든 표는 휴대폰 폭에 맞춘 PNG 이미지로 바꿔 넣는다.** HTML은 평소대로 표로 작성하고, 전달 직전에 아래 스크립트를 한 번 돌린다.

- 디자인: 흑백 모노톤(위 2px 검정선, 칸 사이 #E3E3E3 가는 선, 머리행 #F5F5F5, 굵은 행은 회색 강조), Noto Sans CJK KR, 폭 360 CSS px × 3배 = 1080px.
- 표 종류별 처리(스크립트가 자동 판단):
  - 항목|내용 2칸 표(단지 개요): 왼쪽 항목 칸은 회색 굵게, 폭 28%, 글자 15px.
  - 3칸 표: 14px. 4칸 표: 13px.
  - 4칸 이상이면서 긴 글(15자 넘는 칸)이 있는 표(지역 최근 분양단지 등): 휴대폰에서 칸이 좁아지므로 **카드형**(행마다 단지명 굵게 + "머리글: 값" 줄)으로 그린다.
  - 모든 칸이 굵은 행(이번 단지 등)은 회색 배경으로 강조.
- 결과 파일명: `naver-table-01.png`부터 표 순서대로. 저장 위치는 사이트 저장소 `posts/images/{slug}/`(이미지 주소가 열려야 하므로 사이트와 함께 배포).
- HTML의 각 `<table>`은 `<!-- [이미지 삽입 자리] naver-table-NN.png -->` 주석 + `<img src="https://www.brandongsan.com/posts/images/{slug}/naver-table-NN.png" alt="표 글자 전체">`로 바뀐다. alt에 표 글자를 한 줄로 넣어 숫자가 검색·접근성용으로 남게 한다.
- 표 아래 회색 캡션과 굵은 요약 문장(8번 규칙 4)은 그대로 둔다. 이미지 아래에서도 핵심 숫자가 글자로 남아야 한다.
- 돌린 뒤 이미지를 한 장씩 열어 글자 잘림·과한 줄바꿈이 없는지 눈으로 확인한다. 이상하면 원본 표의 글을 줄이거나(예: 칸 안 문장을 짧게), 표를 둘로 나눈 뒤 다시 돌린다.
- 발행 때는 다른 이미지처럼 네이버 에디터에서 그 자리에 직접 올린다.

```bash
pip install playwright --break-system-packages   # 없을 때만. 크로미움이 없으면: python3 -m playwright install chromium
python3 naver_tables_to_png.py naver-html/{slug}.html posts/images/{slug} {slug}
```

```python
# -*- coding: utf-8 -*-
"""네이버 발행본 HTML의 모든 <table>을 모바일 폭 PNG 이미지로 바꾼다.

사용법:
  python3 naver_tables_to_png.py <naver.html> <out_dir> <slug>
결과:
  - out_dir/naver-table-01.png ... (표 순서대로)
  - <naver.html> 안의 각 <table>이 이미지 자리 주석 + <img>로 교체됨
    (src = https://www.brandongsan.com/posts/images/<slug>/naver-table-NN.png)
  - 이미지 alt에는 표의 글자를 한 줄로 이어 붙여 숫자가 검색·접근성용으로 남게 한다.
디자인: 흑백 모노톤(Paul 기준), 폭 360 CSS px, 3배 해상도(1080px), Noto Sans CJK KR.
"""
import re, sys, html as H
from pathlib import Path
from playwright.sync_api import sync_playwright

W = 360          # 휴대폰 본문 폭(CSS px)
SCALE = 3        # 출력 해상도 배수 → 1080px

CSS = """
*{box-sizing:border-box;margin:0;padding:0}
html,body{background:#fff}
body{width:%dpx;padding:14px 12px 16px;font-family:'Noto Sans CJK KR','Pretendard','Apple SD Gothic Neo',sans-serif;
     color:#111;-webkit-font-smoothing:antialiased;word-break:keep-all;overflow-wrap:anywhere}
table{width:100%%;border-collapse:collapse;border-top:2px solid #111;border-bottom:1px solid #111}
th,td{padding:10px 8px;font-size:%dpx;line-height:1.5;text-align:left;vertical-align:middle;border-bottom:1px solid #E3E3E3}
tr:last-child td{border-bottom:0}
thead th{background:#F5F5F5;font-weight:700;font-size:%dpx;color:#555;border-bottom:1px solid #111}
td:first-child,th:first-child{font-weight:700}
tbody tr.hl td{background:#F5F5F5}
td b,td strong{font-weight:800}
.lbl td:first-child{width:28%%;color:#555;font-weight:700}
.cards{border-top:2px solid #111;border-bottom:1px solid #111}
.card{padding:13px 4px 12px;border-bottom:1px solid #E3E3E3}
.card:last-child{border-bottom:0}
.card.hl{background:#F5F5F5;padding-left:10px;padding-right:10px}
.ct{font-size:%dpx;font-weight:800;margin-bottom:7px}
.card dl{display:grid;grid-template-columns:30%% 1fr;row-gap:4px;column-gap:8px}
.card dt{font-size:%dpx;color:#8A8A8A}
.card dd{font-size:%dpx;line-height:1.5}
"""


def text_of(fragment):
    t = re.sub(r'<br\s*/?>', ' ', fragment)
    t = re.sub(r'<[^>]+>', '', t)
    return re.sub(r'\s+', ' ', H.unescape(t)).strip()


def alt_of(table_html):
    rows = re.findall(r'<tr[^>]*>(.*?)</tr>', table_html, flags=re.S)
    out = []
    for r in rows:
        cells = [text_of(c) for c in re.findall(r'<t[hd][^>]*>(.*?)</t[hd]>', r, flags=re.S)]
        out.append(' · '.join(c for c in cells if c))
    return ' / '.join(out).replace('"', "'")


def ncols(table_html):
    first = re.search(r'<tr[^>]*>(.*?)</tr>', table_html, flags=re.S)
    return len(re.findall(r'<t[hd][^>]*>', first.group(1))) if first else 0


def cells_of(row):
    return re.findall(r'<t[hd][^>]*>(.*?)</t[hd]>', row, flags=re.S)


def as_cards(table_html):
    """칸이 많고 글이 긴 표는 휴대폰에서 칸이 좁아지므로 카드형(행마다 블록)으로 그린다."""
    head = re.search(r'<thead[^>]*>.*?<tr[^>]*>(.*?)</tr>', table_html, flags=re.S)
    heads = [text_of(c) for c in cells_of(head.group(1))] if head else []
    body = re.search(r'<tbody[^>]*>(.*?)</tbody>', table_html, flags=re.S)
    rows = re.findall(r'<tr[^>]*>(.*?)</tr>', body.group(1) if body else table_html, flags=re.S)
    out = ['<div class="cards">']
    for r in rows:
        cs = cells_of(r)
        if not cs:
            continue
        hl = all(re.search(r'<(b|strong)>', c) for c in cs)
        out.append(f'<div class="card{" hl" if hl else ""}"><div class="ct">{cs[0]}</div><dl>')
        for j, c in enumerate(cs[1:], 1):
            out.append(f'<dt>{heads[j] if j < len(heads) else ""}</dt><dd>{c}</dd>')
        out.append('</dl></div>')
    out.append('</div>')
    return ''.join(out)


def prepare(table_html):
    """표 종류에 맞게 클래스·글자 크기를 정한다."""
    n = ncols(table_html)
    longest = max((len(text_of(c)) for c in re.findall(r'<td[^>]*>(.*?)</td>', table_html, flags=re.S)), default=0)
    if n >= 4 and longest > 14 and '<thead' in table_html:
        return as_cards(table_html), 14
    has_head = '<thead' in table_html
    t = table_html
    # 굵은 행(<b>가 모든 칸에 있는 행)은 회색 강조 배경
    def mark(m):
        row = m.group(0)
        cells = re.findall(r'<td[^>]*>(.*?)</td>', row, flags=re.S)
        if cells and all(re.search(r'<(b|strong)>', c) for c in cells):
            return row.replace('<tr', '<tr class="hl"', 1)
        return row
    t = re.sub(r'<tr[^>]*>.*?</tr>', mark, t, flags=re.S)
    if n == 2 and not has_head:          # 항목 | 내용 표
        t = t.replace('<table', '<table class="lbl"', 1)
    fs = 15 if n <= 2 else (14 if n == 3 else 13)
    return t, fs


def main(src, out_dir, slug):
    src = Path(src); out = Path(out_dir); out.mkdir(parents=True, exist_ok=True)
    doc = src.read_text(encoding='utf-8')
    tables = list(re.finditer(r'<table[^>]*>.*?</table>', doc, flags=re.S))
    base = f'https://www.brandongsan.com/posts/images/{slug}/'
    made = []
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={'width': W, 'height': 200}, device_scale_factor=SCALE)
        for i, m in enumerate(tables, 1):
            t, fs = prepare(m.group(0))
            css = CSS % (W, fs, fs - 1, fs + 1, fs - 1, fs)
            pg.set_content(f'<html><head><meta charset="utf-8"><style>{css}</style></head><body>{t}</body></html>')
            pg.wait_for_timeout(150)
            name = f'naver-table-{i:02d}.png'
            pg.locator('body').screenshot(path=str(out / name))
            made.append((m, name))
        b.close()
    # 뒤에서부터 교체(인덱스 보존)
    for m, name in reversed(made):
        alt = alt_of(m.group(0))
        rep = (f'<!-- [이미지 삽입 자리] {name} : 표 이미지(모바일 폭) -->\n'
               f'<img src="{base}{name}" alt="{alt}" style="width:100%;display:block;">')
        doc = doc[:m.start()] + rep + doc[m.end():]
    src.write_text(doc, encoding='utf-8')
    print(f'{len(made)} tables -> {out}')


if __name__ == '__main__':
    main(*sys.argv[1:4])
```

## 13-2. 네이버 에디터 입력 규칙 (발행할 때 반드시, 2026.11.21 Paul)

누가 발행하든(Paul·Aside·Claude) 네이버 글쓰기 에디터에 입력할 때 아래를 모두 지킨다. HTML에는 미리보기용으로만 반영돼 있고, 붙여넣으면 사라지는 것이 많으므로 에디터에서 직접 맞춘다.

1. **사진은 전부 에디터에서 직접 업로드한다.** `<!-- [이미지 삽입 자리] -->` 주석이 있던 자리마다 해당 파일(차트, 표 이미지 naver-table-NN, 조감도, 공식 자료)을 올린다. 외부 주소 이미지(brandongsan.com)가 붙여넣기로 들어갔다면 지우고 다시 올린다. 발행 후 모든 이미지 주소가 네이버 저장소(pstatic.net)여야 한다.
2. **대표사진은 입지 개략도**(`chart-map-naver.png`)로 지정한다. 조감도가 아니다. HTML 메타 주석과 posts-manifest의 `cover_candidates`도 `chart-map-naver.png`를 첫 번째로 적는다.
3. **글꼴은 명조(나눔명조)**로 전체 적용한다(본문 전체 선택 → 글꼴 나눔명조). HTML 미리보기 CSS도 `font-family:'Nanum Myeongjo','NanumMyeongjo','AppleMyungjo',serif`로 둔다.
4. **번호 콘텐츠 사이는 충분히 띄운다.** 각 번호 소제목("1. 결론부터" ~ "6. 결론") 앞에 빈 줄 3개를 둔다(HTML은 `<p> </p>` 3개). 붙여넣은 뒤 빈 줄이 줄어들었으면 에디터에서 Enter로 다시 맞춘다.
5. **번호 콘텐츠 제목은 볼드**다. 굵게 + 본문보다 한 단계 큰 글자(네이버 19)로 지정한다(8번 규칙 2-1). 소제목 스타일이 풀렸으면 에디터에서 다시 입힌다.
6. 발행 전 미리보기(모바일)로 위 1~5를 한 번 더 확인한다.

## 14. 전달

1. 작업 폴더 /mnt/user-data/outputs/<slug>-naver/ 에 HTML(<slug>-naver.html)과 차트 PNG(해당 시)를 같은 폴더로 저장한다.
2. SendUserFile로 HTML + PNG를 보내고, 연결된 폴더가 있으면 거기에도 쓴다. 안내문: HTML과 PNG를 같은 폴더에 두고 브라우저로 열어 Ctrl+A → Ctrl+C → 네이버 글쓰기 화면에 Ctrl+V. 차트 이미지 자리(주석 표시)는 네이버 에디터에서 PNG를 직접 업로드한다.
3. 전달 직전 체크리스트: ① h2 직전마다 빈 문단이 있는가 ② 사진 묶음 사이 빈 문단이 있고 캡션이 굵지 않은가 ③ 섹션 1에 적정가격 그래프 이미지(chart-b)가 있고, 평점 그래프 아래와 가격 비교표 아래에 굵은 문장이 있는가 ④ 브동산 적정가 같은 줄임 표현이 남아 있지 않은가 ⑤ 한줄평이 섹션 3과 6에서 서로 다른 표현인가 ⑥ 홈페이지 링크가 해당 포스팅의 실제 URL인가 ⑦ 수치가 사이트 원본과 정확히 일치하는가 ⑧ 섹션 1의 단지 개요가 표로 정리돼 있고 어디?/언제?/얼마?/주의 줄글이 남아 있지 않은가 ⑨ 중복도 점검(10번) ⑩ 표가 모두 이미지(naver-table-NN)로 바뀌었는가(13-1번) ⑪ 메타 cover_candidates가 chart-map-naver.png이고, 번호 소제목 앞 빈 줄이 3개이며, 미리보기 글꼴이 명조인가(13-2번).
4. 확인이 덜 된 항목(최근 분양단지의 출처 불일치, 공식 일정 이미지 부재 등)은 전달 메시지에 정리해 Paul에게 알린다. 출처 링크(Sources)를 함께 남긴다.

## 15. 태그 (요청받았을 때만)

쉼표로 구분한 12~15개 한글 키워드를 한 줄로 준다. 단지명(붙여쓰기), 역명, 브랜드·시공사·시행사, 지역구, 청약·분양가·공공분양 같은 상황 키워드, 부동산정보. # 기호는 붙이지 않는다.

## 16. 여러 편을 한 번에 요청받으면

한 편씩 순서대로 끝낸다(최근 분양단지 조사와 한줄평은 포스팅마다 사람이 다시 판단). 차트 DATA는 편마다 새로 채운다. 마지막에 폴더별로 묶어 전달하고, 체크리스트는 편마다 빠짐없이 적용한다.

## 17. 변경 이력

- 2026.11.21: 예상 프리미엄은 금액만 먼저, 판정(저평가·적정·고평가, ±3% 기준)은 따로 쓰도록 변경. 차트 프리미엄 박스의 보조 글도 '브동산 판정 · 저평가'로. (Paul)

- 2026.11.21: 네이버 에디터 입력 규칙(13-2번) 신설 — 사진 직접 업로드, 대표사진 = 입지 개략도, 글꼴 나눔명조, 번호 콘텐츠 사이 빈 줄 3개, 번호 제목 볼드(19). 전달 체크리스트 ③ 갱신, ⑩⑪ 추가. (Paul)

- 2026.11.21: 모든 표를 모바일 폭(360px×3) 흑백 PNG 이미지로 바꿔 넣는 규칙과 변환 스크립트(13-1번) 추가. 긴 4칸 표는 카드형으로 그린다. (Paul, 고양 한신더휴 퍼스트원에서 첫 적용)

- 2026.11.21: (1) 섹션 1의 스탯 박스·세 숫자 문장을 chart-b 그래프 이미지로 교체(섹션 2의 chart-b는 이동). (2) 평점 비교 점수 HTML 표 삭제(chart-a 그래프와 중복). (3) 섹션 5를 한줄평 한 줄 + 자료 나열(분양가 → 입지 → 배치도 → 동호수 → 커뮤니티 → 평면 → 청약일정)로 개정. (4) 번호 소제목 h2를 볼드+약간 큰 글자로. (Paul, 고양 한신더휴 퍼스트원 수정본에서 확정)
- 2026.11.21: 본문 첫 문장 규칙 신설(Paul). 검색 미리보기에 뜨도록 본문을 "{단지명}은 {동}에서 N세대를 분양합니다. 전용 84㎡ N세대의 가중평균 분양가는 X.XX억 원이며 M월 D일 1순위입니다."로 시작하고, 바이라인은 그 아래로 내렸다.

- 2026.10.02: C안(재구성형) 도입 — 중복 문서 회피.
- 2026.10.31: 네이버 에디터 서식 생존 규칙 신설(핵심 수치 굵은 문장, 빈 문단 간격).
- 2026.11.09: 사진 캡션은 굵지 않게 처리(Paul 피드백).
- 2026.11.12: 섹션 1의 어디?/언제?/얼마?/주의 줄글을 단지 개요 표(위치·규모·평형 구성·분양가·청약 일정·공급 구성·시공사·입주·규제·주의)로 교체. 섹션 5의 중복 개요 표는 삭제.
- 2026.11.09: 6섹션 표준으로 전면 개편 — 결론부터, 평점 비교표 이미지, 적정가격 막대 그래프, 한줄평 강조, 지역 최근 분양단지, 분양 사이트 자료 순서, 용어를 브동산 분석 적정가격으로 통일, 제목 구분자를 | 로 변경. 이전 구조(D안·C안)는 폐기.