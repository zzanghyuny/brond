/*
  포스팅 데이터 — 새 포스팅을 추가할 때는 이 배열에 객체 하나만 추가하면
  홈("최근 포스팅")과 해당 카테고리 페이지(청약·분양 / 브랜드이야기 / 호치민이야기)에
  자동으로 최신순으로 나타납니다. 순서는 상관없음 — date 기준으로 정렬됩니다.

  각 항목:
  - id        : 파일명과 동일한 슬러그 (참고용)
  - category  : "realestate" 또는 "brand" 또는 "space" 또는 "city"(도시이야기) (vietnam은 보관·비노출)
  - region    : realestate 전용, 2글자 지역명("서울"·"경기"·"인천"·"부산"·"경남" 등).
                brand 포스팅은 생략(비워둠). 청약·분양 페이지의 지역 서브카테고리
                필터와, 포스팅 제목 맨 앞의 "지역 - 단지명" 표기에 함께 쓰입니다.
  - tag       : 카드 상단 태그 문구 (예: "청약 언박싱 No.002")
  - title     : 포스팅 제목. realestate는 "지역 - 단지명 | 한줄평, 예상 프리미엄은 X"
                형식을 반드시 지킵니다(1억 이상은 "X.X억", 1억 미만은 "X천만").
  - date      : "YYYY-MM-DD" (정렬용, 반드시 이 형식)
  - dateLabel : 화면에 보여줄 날짜 문구 (예: "2026. 8. 27")
  - url       : 실제 포스팅 파일 경로 (posts/ 로 시작)
  - preview   : 카드에 보여줄 미리보기 HTML. <p> 1~2개 정도로,
                포스팅 도입부 ~ 핵심요약 수준까지만 담습니다.
                (전체 본문을 넣지 않아도 됩니다 — 어차피 카드 높이만큼만
                보이고 나머지는 흐림 효과로 가려집니다.)
*/

const POSTS = [
  {
    id: "chongqing-city-structure",
    category: "city",
    tag: "도시이야기 No.002",
    title: "충칭은 왜 8D 도시가 됐을까 — 두 강과 산이 만든 입체 도시",
    date: "2026-11-27",
    dateLabel: "2026. 11. 27",
    url: "posts/chongqing-city-structure.html",
    preview: `<p>충칭시는 서울의 136배, 인구 3,187만 명. 장강과 자링강이 만나는 좁은 반도에서 시작해 강 건너편과 북쪽 신도시로 커지면서, 길과 집과 철도를 층층이 쌓은 '8D 도시'가 됐다.</p>`
  },
  {
    id: "yongin-dongil-hivill-parkvalley-2",
    category: "realestate",
    region: "경기",
    tag: "청약 언박싱 No.126",
    title: "경기 - 용인반도체클러스터 동일하이빌 파크밸리 2단지 | SK하이닉스 산단 D1-2블록 661세대, 84㎡ 평균 분양가 5.63억, 예상 프리미엄 -3,170만",
    date: "2026-11-27",
    dateLabel: "2026. 11. 27",
    url: "posts/yongin-dongil-hivill-parkvalley-2.html",
    preview: `
      <p>2026년 11월 27일 입주자모집공고가 나왔다. 용인 처인구 원삼면 용인반도체클러스터 일반산업단지 D1-2블록 661세대 가운데 84㎡A 176세대의 가중평균 분양가는 5.63억원으로, 브동산 적정가 5.31억원보다 높아 예상 프리미엄은 -3,170만이다. 브동산 판정은 고평가다.</p><p>분양가상한제·전매제한 3년·거주의무 없음, 특별공급 12월 7~8일, 1순위 12월 9일, 당첨자 발표 12월 16일, 입주 2029년 5월 예정이다.</p>
    `
  },
  {
    id: "gyeongbuk-docheong-prugio-firstion",
    category: "realestate",
    region: "경북",
    tag: "청약 언박싱 No.125",
    title: "경북 - 경북도청 푸르지오 퍼스티온 | 도청신도시 2단계 1,165세대, 84㎡ 평균 분양가 4.39억, 예상 프리미엄 -2,440만",
    date: "2026-11-27",
    dateLabel: "2026. 11. 27",
    url: "posts/gyeongbuk-docheong-prugio-firstion.html",
    preview: `
      <p>2026년 11월 27일 입주자모집공고가 나왔다. 예천군 호명읍 경북도청신도시 2단계 B-10BL, 전 세대 84㎡ 1,165세대의 가중평균 분양가는 4.39억원으로 브동산 적정가 4.15억원보다 높아 예상 프리미엄은 -2,440만이다. 브동산 판정은 고평가다. 분양가상한제·전매제한 1년, 1순위 12월 8일, 당첨자 발표 12월 15일, 입주 2029년 8월 예정.</p>
    `
  },
  { id: "byeongjeom-bokhap-jubok1-public", category: "realestate", region: "경기", tag: "청약 언박싱 No.123", title: "경기 - 병점복합타운 주복1블록 공공분양 | 병점역 초역세권 LH 726세대, 84㎡ 평균 분양가 6.77억, 예상 프리미엄 +2.70억", date: "2026-11-26", dateLabel: "2026. 11. 26", url: "posts/byeongjeom-bokhap-jubok1-public.html", preview: `<p>화성 병점역 앞 병점복합타운 주복1블록 LH 공공분양 726세대가 11월 26일 공고를 냈다. 분양가상한제로 84A 평균 분양가는 6.77억원, 특별공급 12월 7~8일·일반공급 9~10일 접수한다.</p><p>병점역아이파크캐슬·반정아이파크캐슬5단지 KB 시세로 계산한 브동산 적정가는 9.48억원, 예상 프리미엄은 +2.70억(저평가)이다. 거주의무 3년, 공급금액 중 9,000만원은 주택도시기금 융자금이다.</p>` },
  { id: "sacheon-seonin-hanlim-fullever", category: "realestate", region: "경남", tag: "청약 언박싱 No.122", title: "경남 - 사천선인 한림풀에버 | 선인지구 첫 분양 562세대, 84㎡ 평균 분양가 4.64억, 예상 프리미엄 -4,630만", date: "2026-11-26", dateLabel: "2026. 11. 26", url: "posts/sacheon-seonin-hanlim-fullever.html", preview: `<p>경남 사천시 사천선인 공공주택지구 S-4블록 한림풀에버 562세대가 11월 26일 공고를 냈다. 1순위는 12월 8일, 비규제지역이라 유주택자도 청약할 수 있지만 당첨되면 재당첨 제한 10년이 붙는다.</p><p>전용 84㎡ 321세대 가중평균 분양가는 4.64억원, 사천KCC스위첸·사천삼정그린코아포레스트 KB 시세로 계산한 브동산 적정가는 4.17억원으로 예상 프리미엄은 -4,630만(고평가)이다.</p>` },
  { id: "sinbunpyeong-efete-thewaycity-musunwi", category: "realestate", region: "충북", tag: "청약 언박싱 No.121", title: "충북 - 신분평 에피트 더웨이시티 무순위 | 992세대 중 395세대 다시 나왔다, 84㎡ 평균 분양가 4.98억, 예상 프리미엄 -4,450만", date: "2026-11-26", dateLabel: "2026. 11. 26", url: "posts/sinbunpyeong-efete-thewaycity-musunwi.html", preview: `<p>청주 서원구 장성동 신분평 에피트 더웨이시티 992세대 가운데 395세대가 11월 25일 무순위(사후)로 다시 나왔다. 1순위 2.19대 1로 마감됐던 84A만 254세대다. 전국 무주택세대구성원이면 통장 없이 11월 30일 하루 신청할 수 있다.</p><p>84A 무순위 254세대 가중평균 분양가는 4.98억원, 브동산 적정가는 4.54억원으로 예상 프리미엄은 -4,450만(고평가)이다.</p>` },
  { id: "thesharp-firstworld-seoul-officetel", category: "realestate", region: "서울", tag: "청약 언박싱 No.120", title: "서울 - 더샵 퍼스트월드 서울 오피스텔 | 상봉역 옛 상봉터미널 308실, 84㎡ 평균 분양가 9.80억, 예상 프리미엄 +1.45억", date: "2026-11-26", dateLabel: "2026. 11. 26", url: "posts/thesharp-firstworld-seoul-officetel.html", preview: `<p>서울 중랑구 상봉동 옛 상봉터미널 부지 더샵 퍼스트월드 서울 오피스텔 308실(전 실 전용 84㎡)이 11월 26일 공고를 냈다. 308실 가중평균 분양가는 9.80억원, 청약은 12월 1일 하루, 통장이 필요 없다.</p><p>오피스텔 84㎡를 주변 아파트 59㎡(e편한세상화랑대·사가정센트럴아이파크) 시세로 계산한 12.50억원에서 10%를 감액한 브동산 적정가는 11.25억원, 예상 프리미엄은 +1.45억(저평가)이다.</p>` },
  { id: "dec-2026-move-in", category: "realestate", region: "전국", tag: "입주 리포트 No.001", title: "전국 - 12월 아파트 입주 1만6,486가구 총정리 | 인천 3,812·부산 3,686·서울 903, 1년 전의 절반", date: "2026-11-26", dateLabel: "2026. 11. 26", url: "posts/dec-2026-move-in.html", preview: `<p>2026년 12월 전국 아파트 입주 예정은 22개 단지 1만6,486가구로 11월보다 45% 많지만 1년 전의 절반이다.</p><p>인천 3,812가구, 부산 3,686가구, 경기 2,965가구 순이고 서울은 903가구다. 최대 단지는 부산 해링턴마레(2,205가구).</p>` },
  { id: "wirye-xi-the-park", category: "realestate", region: "경기", tag: "청약 언박싱 No.119", title: "경기 - 위례자이더파크 12월 입주 | 1,309세대 중 650세대는 군관사, 55㎡ 6.2억 신혼희망타운의 수익공유형 모기지", date: "2026-11-26", dateLabel: "2026. 11. 26", url: "posts/wirye-xi-the-park.html", preview: `<p>성남 위례 A2-7블록 위례자이더파크(1,309세대)가 2026년 12월 입주한다. 650세대는 군관사이고 일반 분양분은 신혼희망타운 공공분양 55㎡ 440세대다.</p><p>분양가는 6억원 안팎(55A 15층 6.20억)이지만 총자산 기준을 넘어 수익공유형 모기지 의무가입 대상이라, 팔 때 시세차익의 10~50%를 기금과 나눈다. 거주의무 5년, 위례선 트램은 2027년으로 연기됐다.</p>` },
  {"id": "jeongja-thesharp-bundanghighest-musunwi", "category": "realestate", "region": "경기", "tag": "청약 언박싱 No.117", "title": "경기 - 더샵 분당하이스트 무순위 | 정자역 34세대 재공급 시세차익 점검, 84㎡ 평균 분양가 27.82억, 예상 프리미엄 -6.89억", "date": "2026-11-23", "dateLabel": "2026. 11. 23", "url": "posts/jeongja-thesharp-bundanghighest-musunwi.html", "preview": "<p>분당 정자동 더샵 분당하이스트(1,149세대, 리모델링)에 무순위(사후) 2차 34세대가 나왔다. 1차 무순위와 같은 동·호수이고, 수도권 무주택세대구성원이면 청약통장 없이 11월 30일 하루 신청할 수 있다.</p><p>84㎡ 무순위 32세대 가중평균 27.82억원은 브동산 적정가 20.93억원보다 6.89억원 높아 예상 프리미엄은 -6.89억이다. 9월 기존 글(+9천만) 이후 바뀐 분양가·경쟁률·시세를 함께 정리했다.</p>"},
  {"id": "dongtan-geumgang-penterium-7-musunwi", "category": "realestate", "region": "경기", "tag": "청약 언박싱 No.116", "title": "경기 - 동탄 금강펜테리움 7차 센트럴파크 무순위·불법행위 재공급 | 2023년 분양가 그대로 5세대, 84㎡ 평균 분양가 5.53억, 예상 프리미엄 +1.48억", "date": "2026-11-23", "dateLabel": "2026. 11. 23", "url": "posts/dongtan-geumgang-penterium-7-musunwi.html", "preview": "<p>동탄2신도시 신동 금강펜테리움 7차 센트럴파크 무순위 4세대와 불법행위 재공급 1세대. 2023년 분양가 그대로인 84㎡ 평균 5.53억원으로, 단지 시세(리치고 7.01억) 기준 예상 프리미엄은 +1.48억이다.</p><p>접수는 11월 30일 하루, 잔금 80%를 2027년 1월 8일에 한 번에 낸다.</p>"},
  {"id": "sangok-xi-hillstate-haneulchae-musunwi", "category": "realestate", "region": "인천", "tag": "청약 언박싱 No.115", "title": "인천 - 산곡역자이힐스테이트앤하늘채 무순위 | 잔여 550세대 전국 무주택 추첨, 84㎡ 평균 분양가 9.68억, 예상 프리미엄 -480만", "date": "2026-11-20", "dateLabel": "2026. 11. 20", "url": "posts/sangok-xi-hillstate-haneulchae-musunwi.html", "preview": "<p>인천 부평구 산곡6구역 산곡역자이힐스테이트앤하늘채(2,706세대)에 무순위(사후) 550세대가 나왔다. 전국 무주택세대구성원이면 청약통장 없이 11월 24일 하루 신청할 수 있다.</p><p>84㎡ 무순위 57세대 가중평균 9.68억원은 브동산 적정가 9.63억원과 거의 같아 예상 프리미엄은 -480만이다. 59B는 적정가보다 약 3,930만원 높다.</p>"},
  {"id": "gochang-desian", "category": "realestate", "region": "전북", "tag": "청약 언박싱 No.114", "title": "전북 - 고창 데시앙 | 덕산지구 888세대 공공·민영 동시 공급, 84㎡ 평균 분양가 4.22억, 예상 프리미엄 +1,360만", "date": "2026-11-20", "dateLabel": "2026. 11. 20", "url": "posts/gochang-desian.html", "preview": "<p>2026년 11월 20일 입주자모집공고가 나왔다. 고창 덕산지구 2·3블록 888세대 중 84㎡ 공공분양 711세대의 가중평균 분양가는 4.22억원으로 브동산 적정가 4.36억원보다 낮아 예상 프리미엄은 +1,360만이다. 브동산 판정은 저평가다. 청약은 11월 30일~12월 2일, 당첨자 발표 12월 8일, 입주 2030년 2월 예정.</p>"},
  {"id": "doosan-weve-signature-gwangyang", "category": "realestate", "region": "전남", "tag": "청약 언박싱 No.113", "title": "전남 - 두산위브 시그니처 광양 | 중마동 120세대 공급, 84㎡ 평균 분양가 4.03억, 예상 프리미엄 −1,320만원", "date": "2026-11-20", "dateLabel": "2026. 11. 20", "url": "posts/doosan-weve-signature-gwangyang.html", "preview": "<p>광양시 중동 575세대 중 120세대 분양. 전용 84㎡ 평균 4.03억 원. 11월 30일 특별공급.</p>"},
  {"id": "sosa-humanville", "category": "realestate", "region": "경기", "tag": "청약 언박싱 No.112", "title": "경기 - 소사 휴먼빌 | 59㎡ 평균 5.31억·84㎡ 7.51억, 청약 일정", "date": "2026-11-20", "dateLabel": "2026. 11. 20", "url": "posts/sosa-humanville.html", "preview": "<p>부천 소사본동 79세대 중 45세대 분양. 59㎡ 평균 5.31억 원, 84㎡ 7.51억 원. 11월 30일 특별공급.</p>"},
  {"id": "yeonsan-sujain-centrio", "category": "realestate", "region": "부산", "tag": "청약 언박싱 No.111", "title": "부산 - 연산역 수자인 센트리오 | 59㎡ 평균 분양가 6.32억, 예상 프리미엄 +2,540만원", "date": "2026-11-20", "dateLabel": "2026. 11. 20", "url": "posts/yeonsan-sujain-centrio.html", "preview": "<p>부산 연제구 연산역 수자인 센트리오는 139세대를 분양한다. 전용 59㎡ 평균 분양가 6.32억 원, 브동산 적정가 6.57억 원, 예상 프리미엄 +2,540만원이다. 11월 30일 특별공급부터다.</p>"},
  {"id":"xi-beyond-living","category":"space","tag":"공간이야기 No.005","title":"거실이 침실로 바뀐다면? 자이가 공개한 미래 아파트의 가변형 설계","date":"2026-11-20","dateLabel":"2026. 11. 20","url":"posts/xi-beyond-living.html","preview":"<p>자이 비욘드 리빙의 가변형 벽 IX 월은 거실과 방의 경계를 어떻게 바꿀까. 실제 적용 시 확인할 채광·소음·관리와 AI 홈의 도입 계획을 살펴봅니다.</p>"},
  { id: "gyeyang-a2-a3-first-move-in", category: "realestate", region: "인천", tag: "청약 언박싱 No.118", title: "인천 - 계양신도시 첫 입주 루시안트·리프포레 | 3기 신도시 첫 1,285가구, 84㎡ 분양가 5.84억, 예상 프리미엄 +2,720만", date: "2026-11-25", dateLabel: "2026. 11. 25", url: "posts/gyeyang-a2-a3-first-move-in.html", preview: `<p>3기 신도시 가운데 처음으로 2026년 12월 인천계양 A2블록 계양루시안트(공공분양 747가구)와 A3블록 계양리프포레(신혼희망타운 359가구·행복주택 179가구)가 입주한다.</p><p>2024년 본청약 84㎡ 분양가 5.84억원(5층 이상)을 계양하늘채파크포레·힐스테이트자이계양 KB 시세로 보정한 브동산 적정가 6.11억원과 비교하면 예상 프리미엄은 +2,720만(저평가)이다.</p>` },
  { id: "thesharp-cheonan-lac-one", category: "realestate", region: "충남", tag: "청약 언박싱 No.110", title: "충남 - 더샵 천안라크원 | 84㎡ 평균 분양가 6.17억, 예상 프리미엄 -5,420만", date: "2026-11-19", dateLabel: "2026. 11. 19", url: "posts/thesharp-cheonan-lac-one.html", preview: "<p>천안 부대동 1,032세대 분양. 전용 84㎡ 평균 6.17억, 특별공급 11월 30일.</p>" },
  { id: "goyang-hanshin-thehue-firstone", category: "realestate", region: "경기", tag: "청약 언박싱 No.109", title: "경기 - 고양 한신더휴 퍼스트원 | 덕양구 행신동 일반분양 102세대, 84㎡ 평균 분양가 8.08억, 예상 프리미엄 +5,960만", date: "2026-11-18", dateLabel: "2026. 11. 18", url: "posts/goyang-hanshin-thehue-firstone.html", preview: `<p>2026년 11월 19일 입주자모집공고가 나왔다. 고양 덕양구 행신2의1구역 재건축 272세대 중 일반분양 102세대, 84㎡ 31세대의 가중평균 분양가는 8.08억원으로 브동산 적정가 8.68억원보다 낮아 예상 프리미엄은 +5,960만이다. 브동산 판정은 저평가다. 청약은 11월 30일~12월 2일, 당첨자 발표 12월 9일, 입주 2029년 5월 예정.</p>` },
  { id: "gumi-parkone-desian", category: "realestate", region: "경북", tag: "청약 언박싱 No.108", title: "경북 - 구미 파크원 데시앙 | 도량동 1단지 1,355세대, 84㎡ 평균 분양가 5.18억, 예상 프리미엄 +2,730만", date: "2026-11-18", dateLabel: "2026. 11. 18", url: "posts/gumi-parkone-desian.html", preview: `<p>2026년 11월 18일 입주자모집공고가 나왔다. 84㎡ 654세대의 가중평균 분양가는 5.18억원으로 브동산 적정가 5.45억원보다 낮아 예상 프리미엄은 +2,730만이다. 브동산 판정은 저평가다. 청약은 11월 23~25일, 당첨자 발표 12월 2일, 입주 2030년 2월 예정.</p>` },
  { id: "doosan-weve-trezium-iksan", category: "realestate", region: "전북", tag: "청약 언박싱 No.107", title: "전북 - 두산위브 트레지움 익산 | 동산동 591세대 중 일반분양 251세대, 84㎡ 평균 분양가 4.53억, 예상 프리미엄 -500만", date: "2026-11-18", dateLabel: "2026. 11. 18", url: "posts/doosan-weve-trezium-iksan.html", preview: `<p>익산 동산동 세경1차 재건축, 591세대 중 일반분양 251세대. 84㎡ 가중평균 분양가 4.53억 대비 브동산 적정가는 4.48억으로, 예상 프리미엄은 -500만 수준이다. 브동산 판정은 적정이다.</p>` },
  { id: "gyeongnam-honam-jeju-firstcome-20261117", category: "realestate", region: "경남·호남·제주", tag: "미분양 랭킹 No.005", title: "경남·호남·제주 - 미분양 선착순 단지 TOP16 | 실거주로 해볼 만한 곳은?, 1위 힐스테이트 양산더스카이 예상 프리미엄은 +3,370만", date: "2026-11-17", dateLabel: "2026. 11. 17", url: "posts/gyeongnam-honam-jeju-firstcome-20261117.html", preview: `<p>청약통장 없이 동·호수를 골라 계약할 수 있는 경남·광주·전북·전남·제주 미분양 선착순 단지 16곳을 브동산 모형으로 계산해 분양가 대비 증감률 순으로 정리했다. 1위는 힐스테이트 양산더스카이(+6.4%, +3,370만)다.</p>` },
  { id: "daegu-gyeongbuk-gangwon-firstcome-20261117", category: "realestate", region: "대구·경북·강원", tag: "미분양 랭킹 No.004", title: "대구·경북·강원 - 미분양 선착순 단지 TOP7 | 실거주로 해볼 만한 곳은?, 1위 달서자이 제니크 예상 프리미엄은 +120만", date: "2026-11-17", dateLabel: "2026. 11. 17", url: "posts/daegu-gyeongbuk-gangwon-firstcome-20261117.html", preview: `<p>청약통장 없이 동·호수를 골라 계약할 수 있는 대구·경북·강원 미분양 선착순 단지 7곳을 브동산 모형으로 계산해 분양가 대비 증감률 순으로 정리했다. 1위는 달서자이 제니크(+0.2%, +120만)다.</p>` },
  { id: "busan-ulsan-firstcome-20261117", category: "realestate", region: "부산·울산", tag: "미분양 랭킹 No.003", title: "부산·울산 - 미분양 선착순 단지 TOP20 | 시세 수준에 고를 수 있는 곳은?, 1위 그랑라크 에일린의 뜰 예상 프리미엄은 +7,380만", date: "2026-11-17", dateLabel: "2026. 11. 17", url: "posts/busan-ulsan-firstcome-20261117.html", preview: `<p>청약통장 없이 동·호수를 골라 계약할 수 있는 부산·울산 미분양 선착순 단지 20곳을 브동산 모형으로 계산해 분양가 대비 증감률 순으로 정리했다. 1위는 그랑라크 에일린의 뜰(+9.6%, +7,380만)다.</p>` },
  { id: "chungcheong-firstcome-20261117", category: "realestate", region: "충청권", tag: "미분양 랭킹 No.002", title: "충청권 - 미분양 선착순 단지 TOP22 | 실거주로 해볼 만한 곳은?, 1위 대전 문화공원 수자인 예상 프리미엄은 +2,900만", date: "2026-11-17", dateLabel: "2026. 11. 17", url: "posts/chungcheong-firstcome-20261117.html", preview: `<p>청약통장 없이 동·호수를 골라 계약할 수 있는 충남·대전·충북·세종 미분양 선착순 단지 22곳을 브동산 모형으로 계산해 분양가 대비 증감률 순으로 정리했다. 1위는 대전 문화공원 수자인(+5.4%, +2,900만)다.</p>` },
  { id: "sudogwon-firstcome-top30-202611", category: "realestate", region: "수도권", tag: "미분양 랭킹 No.001", title: "수도권 - 미분양 선착순 단지 TOP30 | 지금 해볼 만한 단지가 있을까?, 1위 오산헤리티지자이 예상 프리미엄은 +1,450만", date: "2026-11-16", dateLabel: "2026. 11. 16", url: "posts/sudogwon-firstcome-top30-202611.html", preview: `<p>청약통장 없이 동·호수를 골라 계약할 수 있는 수도권 미분양 선착순 단지 30곳을 브동산 모형으로 계산해 분양가 대비 증감률 순으로 정리했다. 분양가보다 적정가격이 높게 나온 곳은 2곳뿐이고, 1위 오산헤리티지자이가 +1.8%(+1,450만)다.</p>` },
  { id: "gold-vs-apartment-trading-costs", category: "realestate", region: "전국", tag: "청약 언박싱 No.102", title: "전국 - 금과 아파트 | 금 1돈 사고팔 때 10만 원 차이, 부동산 거래비용과 비교하면", date: "2026-11-14", dateLabel: "2026. 11. 14", url: "posts/gold-vs-apartment-trading-costs.html", preview: `<p>금값이 내려왔다는 뉴스 뒤에는 늘 같은 질문이 따라온다. 지금 금을 살까, 집을 살까? 어디가 오를지 맞히기 전에 먼저 확인할 것이 있다. 사고팔 때 얼마가 드는가다.</p>` },
  {
    id: "ulsan-hwajeong1-arel",
    category: "realestate",
    region: "울산",
    tag: "청약 언박싱 No.103",
    title: "울산 - 화정1지구 아르엘 | 동구 화정동 802세대, 84㎡ 평균 분양가 5.56억, 예상 프리미엄 -4,930만",
    date: "2026-11-14",
    dateLabel: "2026. 11. 14",
    url: "posts/ulsan-hwajeong1-arel.html",
    preview: `<p>2026년 11월 13일 입주자모집공고가 나왔다. 84㎡ 580세대의 가중평균 분양가는 5.56억원으로 브동산 적정가 5.07억원보다 높아 예상 프리미엄은 -4,930만이다. 브동산 판정은 고평가다. 청약은 11월 23~25일, 입주는 2029년 11월 예정이다.</p>`
  },
  { id: "gyeongsan-richel-eduforet", category: "realestate", region: "경북", tag: "청약 언박싱 No.106", title: "경북 - 리첼 에듀포레 경산역 | 경산역 도보권 일반분양 201세대, 84㎡ 평균 분양가 6.03억, 예상 프리미엄 -1.19억", date: "2026-11-14", dateLabel: "2026. 11. 14", url: "posts/gyeongsan-richel-eduforet.html", preview: `<p>경산역 도보권 지역주택조합 아파트, 일반분양 201세대. 84㎡ 공고 분양가 가중평균 6.03억 대비 브동산 적정가는 4.83억으로 산출됐다.</p>` },
  { id: "ansan-sinkil2-a6-newlywed", category: "realestate", region: "경기", tag: "청약 언박싱 No.105", title: "경기 - 안산신길2 A-6블록 신혼희망타운 | 공공분양 251세대, 55㎡ 분양가 4.47억, 예상 프리미엄 -1,300만", date: "2026-11-14", dateLabel: "2026. 11. 14", url: "posts/ansan-sinkil2-a6-newlywed.html", preview: `<p>LH 신혼희망타운 공공분양 251세대. 55㎡ 분양가 4.47억 대비 브동산 적정가는 4.34억으로, 예상 프리미엄은 -1,300만 수준이다.</p>` },
  { id: "hoban-summit-choryang", category: "realestate", region: "부산", tag: "청약 언박싱 No.102", title: "부산 - 호반써밋 초량 | 초량3구역 재개발 일반분양 236세대, 84㎡ 평균 분양가 7.25억, 예상 프리미엄 -4,900만", date: "2026-11-14", dateLabel: "2026. 11. 14", url: "posts/hoban-summit-choryang.html", preview: `<p>부산 동구 초량3구역 재개발 일반분양 236세대. 84㎡A 세대수 가중평균 분양가 7.25억 대비 브동산 적정가는 6.76억으로, 예상 프리미엄은 -4,900만 수준이다.</p>` },
  { id: "bucheon-daejang-haustory-decent", category: "realestate", region: "경기", tag: "청약 언박싱 No.101", title: "경기 - 부천대장 하우스토리 디센트 | 84㎡ 평균 분양가 8.47억, 예상 프리미엄 -5,640만", date: "2026-11-14", dateLabel: "2026. 11. 14", url: "posts/bucheon-daejang-haustory-decent.html", preview: `<p>분양가상한제가 적용된 3기 신도시 공공분양이라 싸다는 말이 많다. 그런데 역세권·초품아와 3기 신도시 개발잠재력을 반영해 계산한 84㎡ 적정가는 7.91억, 분양가는 8.47억이다. 이 차이는 어떻게 읽어야 할까?</p>` },
  { id: "anyang-xi-the-forest-unranked", category: "realestate", region: "경기", tag: "청약 언박싱 No.100", title: "경기 - 안양자이 더 포레스트 | 무순위 청약, 59㎡ 잔여 1세대 자격과 일정 총정리", date: "2026-11-12", dateLabel: "2026. 11. 12", url: "posts/anyang-xi-the-forest-unranked.html", preview: `<p>3년 전 청약했던 단지에 이번에는 딱 한 세대가 무순위로 나왔다. 안양자이 더 포레스트 59㎡, 접수는 11월 16일 하루다. 자격과 가격부터 확인하자.</p>` },
  { id: "hannam-the-hill-190", category: "realestate", region: "서울", tag: "청약 언박싱 No.099", title: "서울 - 한남더힐 | 옥주현 190억 거래, 역대 최고가를 숫자로 뜯어보기", date: "2026-11-11", dateLabel: "2026. 11. 11", url: "posts/hannam-the-hill-190.html", preview: `<p>서울 한남동 한남더힐에서 190억 원짜리 거래가 나왔다는 보도가 있었다. 한남더힐 역대 최고가라는데, 이 숫자를 어떻게 읽어야 할까?</p>` },
  { id: "elementary-enrollment-30man", category: "space", tag: "공간이야기 No.004", title: "초등 입학생 30만 명 붕괴, 내 집값에는 어떤 영향이 있을까", date: "2026-11-09", dateLabel: "2026. 11. 9", url: "posts/elementary-enrollment-30man.html", preview: `<p>올해 초등학교에 입학한 아이가 30만 명 안팎이라고 한다. 통계를 낸 이래 처음 보는 숫자라는데, 이 숫자가 우리 집값과는 어떤 관계가 있을까?</p>` },
  { id: "mullae-lottecastle-newstay", category: "realestate", region: "서울", tag: "청약 언박싱 No.098", title: "서울 - 문래 롯데캐슬 | 8년 임대 끝나면 내 집 될까? 분양전환·임대조건 총정리", date: "2026-11-08", dateLabel: "2026. 11. 8", url: "posts/mullae-lottecastle-newstay.html", preview: "<p>문래 롯데캐슬의 임대조건과 분양전환 여부를 정리했다. 2020년 4월 입주 시작을 기준으로 2028년 무렵 추정하며, 법정 입주지정기간 개시일 및 계약 확인이 필요하다. 공식 분양전환 계획과 가격은 미확정이다.</p>" },
  { id: "siheung-geomo-artera", category: "realestate", region: "경기", tag: "청약 언박싱 No.094", title: "경기 - 시흥 거모 아테라 | 59㎡ 평균 분양가 4.58억, 예상 프리미엄 -9,900만", date: "2026-11-08", dateLabel: "2026. 11. 8", url: "posts/siheung-geomo-artera.html", preview: `<p>시흥 거모 아테라의 공식 공고·분양가·청약 조건을 정리했다.</p><p>59㎡ 평균 4.58억원 · 예상 프리미엄 -9,900만</p>` },
  { id: "gwangju-jeil-foredu", category: "realestate", region: "경기", tag: "청약 언박싱 No.095", title: "경기 - 제일풍경채 광주 포에듀 | 84㎡ 평균 분양가 6.71억, 예상 프리미엄 -7,100만", date: "2026-11-08", dateLabel: "2026. 11. 8", url: "posts/gwangju-jeil-foredu.html", preview: `<p>제일풍경채 광주 포에듀의 공식 공고·분양가·청약 조건을 정리했다.</p><p>84㎡ 가중평균 6.71억원 · 예상 프리미엄 -7,100만</p>` },
  { id: "namchuncheon-centreville", category: "realestate", region: "강원", tag: "청약 언박싱 No.096", title: "강원 - 남춘천 센트레빌 | 84㎡ 평균 분양가 5.96억, 예상 프리미엄 +8,900만", date: "2026-11-08", dateLabel: "2026. 11. 8", url: "posts/namchuncheon-centreville.html", preview: `<p>남춘천 센트레빌의 공식 공고·분양가·청약 조건을 정리했다.</p><p>84㎡ 가중평균 5.96억원 · 예상 프리미엄 +8,900만</p>` },
  { id: "jeju-samdo-land-lease", category: "realestate", region: "제주", tag: "청약 언박싱 No.097", title: "제주 - 삼도이동 토지임대부 분양주택 | 건물만 분양받는 72세대, 꼭 알아야 할 조건", date: "2026-11-08", dateLabel: "2026. 11. 8", url: "posts/jeju-samdo-land-lease.html", preview: `<p>삼도이동 토지임대부 분양주택의 공식 공고·분양가·청약 조건을 정리했다.</p><p>59A 건물분양가 2.90~3.02억원 · 월 토지임대료 298,840원</p>` },
  { id: "gwanggyo-centreville-general-vs-equity", category: "realestate", region: "경기", tag: "청약 언박싱 No.093", title: "경기 - 광교 자연앤 센트레빌 | 일반분양 vs 지분적립형, 실제로 얼마가 필요할까", date: "2026-11-06", dateLabel: "2026. 11. 6", url: "posts/gwanggyo-centreville-general-vs-equity.html", preview: "<p>84㎡ 일반분양은 입주까지 9.49억원, 59㎡ 지분적립형은 입주 때 2.37억~5.01억원. 같은 단지, 다른 돈의 구조를 공고문 기준으로 계산했다.</p>" },
  { id: "guri-galmae-insville-decent", category: "realestate", region: "경기", tag: "청약 언박싱 No.087", title: "경기 - 구리갈매역세권 신안인스빌 디센트 | 213세대, 84㎡ 적정가 7.83억, 예상 프리미엄 +2,960만", date: "2026-11-05", dateLabel: "2026. 11. 5", url: "posts/guri-galmae-insville-decent.html", preview: "<p>갈매역세권 B-1블록 213세대. 84㎡ 공고 분양가 7.2~7.9억 대비 브동산 적정가는 7.83억으로 산출됐다.</p>" },
  { id: "ansan-sinkil2-b1-public", category: "realestate", region: "경기", tag: "청약 언박싱 No.088", title: "경기 - 안산신길2 B-1블록 | LH 공공분양 387세대(사전청약 263세대), 84㎡ 평균 분양가 5.84억, 예상 프리미엄 -1,680만", date: "2026-11-05", dateLabel: "2026. 11. 5", url: "posts/ansan-sinkil2-b1-public.html", preview: "<p>LH 공공분양 387세대 중 신규 청약 124세대. 84㎡ 평균 분양가 5.84억 대비 브동산 적정가는 5.67억이다.</p>" },
  { id: "yongin-jungang-hights-guseong", category: "realestate", region: "경기", tag: "청약 언박싱 No.089", title: "경기 - 중앙하이츠 구성 플랫폼시티 | 용인 마북동 가로주택정비 일반분양 76세대, 59㎡ 평균 분양가 6.11억, 예상 프리미엄 +2.42억", date: "2026-11-05", dateLabel: "2026. 11. 5", url: "posts/yongin-jungang-hights-guseong.html", preview: "<p>용인 마북동 가로주택정비 일반분양 76세대. 59㎡ 평균 분양가 6.11억 대비 브동산 적정가는 8.53억으로 산출됐다.</p>" },
  { id: "gyeyang-daebang-elium-eduhpark", category: "realestate", region: "인천", tag: "청약 언박싱 No.090", title: "인천 - 계양신도시 대방 엘리움 에듀파크 | 공고 전 536세대, 84㎡ 적정가 6.49억(분양가 미공개)", date: "2026-11-05", dateLabel: "2026. 11. 5", url: "posts/gyeyang-daebang-elium-eduhpark.html", preview: "<p>모집공고 전 계양 A21블록 536세대. 84㎡ 브동산 적정가는 6.49억이며 분양가는 공고 후 업데이트한다.</p>" },
  { id: "wangsuk-hanshin-theh-centum", category: "realestate", region: "경기", tag: "청약 언박싱 No.091", title: "경기 - 왕숙 한신더휴 센텀 | 59㎡ 평균 분양가 6.02억, 예상 프리미엄 +1.74억", date: "2026-11-19", dateLabel: "2026. 11. 19", url: "posts/wangsuk-hanshin-theh-centum.html", preview: "<p>남양주 왕숙 A-17 공공분양 379세대. 전용 59㎡ 평균 6.02억, 특별공급 11월 30일.</p>" },
  { id: "songdo-the-sharp-granter-g5-6-musunwi", category: "realestate", region: "인천", tag: "청약 언박싱 No.092", title: "인천 - 더샵 송도그란테르 G5-6블록 | 무순위 118K 1세대 17.64억, 예상 프리미엄 +3.57억", date: "2026-11-05", dateLabel: "2026. 11. 5", url: "posts/songdo-the-sharp-granter-g5-6-musunwi.html", preview: "<p>송도 G5-6블록 무순위 118K 1세대의 공급금액 17.64억, 타입별 평면·커뮤니티와 브동산 적정가 21.21억을 한 글에 정리했다.</p>" },
  { id: "balcony-story", category: "space", tag: "공간이야기 No.003", title: "우리 집 베란다는 어디로 사라졌을까", date: "2026-11-05", dateLabel: "2026. 11. 5", url: "posts/balcony-story.html", preview: `<p>예전 집에는 빨래도 널고 화분도 두던 베란다가 있었다. 요즘 집에서는 그 자리가 거실이 된 것 같다. 우리 집 베란다는 어디로 사라졌을까?</p>` },
  { id: "same-84-different-space", category: "space", tag: "공간이야기 No.002", title: "같은 84㎡인데 왜 우리 집은 더 좁을까", date: "2026-11-05", dateLabel: "2026. 11. 5", url: "posts/same-84-different-space.html", preview: `<p>같은 84㎡라는데 친구 집에 가면 왜 더 넓게 느껴질까? 이유는 계약서에 적히지 않는 면적에 있었다.</p>` },
  {
    id: "songdo-logebien-moaelgaa",
    category: "realestate",
    region: "인천",
    tag: "청약 언박싱 No.086",
    title: "인천 - 송도 대광로제비앙 모아엘가 | 11공구 워터프론트 앞 592세대, 84㎡ 평균 분양가 8.80억, 예상 프리미엄 -1,870만",
    date: "2026-11-27",
    dateLabel: "2026. 11. 27",
    url: "posts/songdo-logebien-moaelgaa.html",
    preview: `
      <p>인천 송도국제도시 11공구 RC2블록 송도 대광로제비앙 모아엘가, 전 세대 전용 84㎡ 592세대. 84㎡ 분양가 가중평균 8.80억원 대비 브동산 적정가는 8.61억원으로 예상 프리미엄은 -1,870만이다. 브동산 판정은 적정이다.</p><p>2026년 11월 27일 입주자모집공고, 특별공급 12월 7일·1순위 12월 8일, 입주는 2030년 1월 예정이며 비규제지역·전매제한 6개월·재당첨제한 없음이다.</p>
    `
  },
  {
    id: "yongdu-lottecastle",
    category: "realestate",
    region: "서울",
    tag: "청약 언박싱 No.085",
    title: "서울 - 용두동 롯데캐슬 | 홈플러스 동대문점 부지 417세대, 84㎡ 적정가 20.75억(분양가 미공개)",
    date: "2026-11-04",
    dateLabel: "2026. 11. 4",
    url: "posts/yongdu-lottecastle.html",
    preview: `
      <p>서울 동대문구 용두동 33-1 일대 옛 홈플러스 동대문점 부지의 '용두동 롯데캐슬'은 지하 7층~지상 49층 3개 동 417세대(일반분양 340세대 보도) 주상복합이다. 브동산 모형 84㎡ 적정가는 20.75억원이다.</p><p>2026년 12월 분양 예정이며 공사 예정기간은 2027년 1월~2032년 2월이다. 분양가·청약일정·입주예정월은 미정이라 예상 프리미엄은 산출하지 않았고, 공고 후 갱신한다.</p>
    `
  },
  {
    id: "switzen-civilization-clash",
    category: "brand",
    tag: "브랜드 언박싱 No.003",
    title: "아이를 키워본 사람이라면, 이 광고를 그냥 지나치기 어렵다 — 스위첸 ‘문명의 충돌’에서 ‘식구의 부활’까지",
    date: "2026-11-03",
    dateLabel: "2026. 11. 3",
    url: "posts/switzen-civilization-clash.html",
    preview: `
      <p>문명의 충돌 2를 보다가 울었다. 아파트 광고였는데, 단지 이름도 평면도도 분양가도 나오지 않는 2분 10초짜리 영상이 왜 이렇게 오래 남는지 궁금해서 스위첸의 세 캠페인을 다시 돌려 봤다.</p>
    `
  },
  {
    id: "why-84-and-59-sqm",
    category: "space",
    tag: "공간이야기 No.001",
    title: "85도 60도 아닌 84와 59 — 국민평형 숫자는 어디서 나왔을까",
    date: "2026-11-03",
    dateLabel: "2026. 11. 3",
    url: "posts/why-84-and-59-sqm.html",
    preview: `
      <p>아파트 타입표에서 84.99는 봐도 85.01은 한 번도 못 봤다. 85도 아니고 왜 84일까, 59는 왜 60이 아닐까. 찾아보니 생각보다 사람 냄새 나는 이유였다.</p>
    `
  },
  {
    id: "uijeongbu-feliztower-yangwoo",
    category: "realestate",
    region: "경기",
    tag: "청약 언박싱 No.084",
    title: "경기 - 의정부역 펠리스타워 양우내안애 | 49층 1,252세대 중 일반분양 414세대, 84㎡ 평균 분양가 7.98억, 예상 프리미엄 -290만",
    date: "2026-11-02",
    dateLabel: "2026. 11. 2",
    url: "posts/uijeongbu-feliztower-yangwoo.html",
    preview: `<p>11월 6일 모집공고가 나왔다. 84㎡ 가중평균 분양가 7.98억원 대비 브동산 적정가는 7.95억원, 예상 프리미엄은 -290만으로 사실상 무피다. 입주는 2031년 1월 예정이다.</p>`
  },
  {
    id: "armusee-xi-ansan",
    category: "realestate",
    region: "경기",
    tag: "청약 언박싱 No.083",
    title: "경기 - 아르뮤제자이 | 안산 성포동 984세대 49층, 84㎡ 평균 분양가 10.86억, 예상 프리미엄 -1.03억",
    date: "2026-11-02",
    dateLabel: "2026. 11. 2",
    url: "posts/armusee-xi-ansan.html",
    preview: `<p>2026년 11월 12일 입주자모집공고가 나왔다. 84㎡ 가중평균 분양가는 10.86억원으로 브동산 적정가 9.83억원보다 높아 예상 프리미엄은 -1.03억이다. 브동산 판정은 고평가다. 청약은 11월 23~25일, 입주는 2031년 3월 예정이다.</p>`
  },
  {
    id: "nonsan-elif-the-edition",
    category: "realestate",
    region: "충남",
    tag: "청약 언박싱 No.104",
    title: "충남 - 엘리프 논산 디에디션 | 499세대 84㎡, 평균 분양가 5.05억, 예상 프리미엄 -5,290만",
    date: "2026-11-14",
    dateLabel: "2026. 11. 14",
    url: "posts/nonsan-elif-the-edition.html",
    preview: `<p>2026년 11월 13일 입주자모집공고가 나왔다. 전 세대 전용 84㎡ 499세대의 가중평균 분양가는 5.05억원으로 브동산 적정가 4.52억원보다 높아 예상 프리미엄은 -5,290만이다. 브동산 판정은 고평가다. 전매제한·재당첨제한·거주의무는 없고, 청약은 11월 23~25일, 입주는 2030년 1월 예정이다.</p>`
  },
  {
    id: "pyeongtaek-godeok-woomi-lynn-premier",
    category: "realestate",
    region: "경기",
    tag: "청약 언박싱 No.082",
    title: "경기 - 평택 고덕 우미 린 더 프리미어 | 고덕 국제화계획지구 623세대 분양가상한제, 84㎡ 평균 분양가 5.82억, 예상 프리미엄 +1.1억",
    date: "2026-11-02",
    dateLabel: "2026. 11. 2",
    url: "posts/pyeongtaek-godeok-woomi-lynn-premier.html",
    preview: `
      <p>경기 평택시 고덕 국제화계획지구 Abc-33블록의 '평택 고덕 우미 린 더 프리미어'는 623세대 전 가구가 일반분양이며 84㎡ 평균 분양가는 가중평균 5.82억원이다. 브동산 적정가는 6.93억원으로 예상 프리미엄은 +1.1억이다. 브동산 판정은 저평가다.</p><p>2026년 10월 30일 입주자모집공고 후 11월 9일 특별공급, 10~11일 일반공급 청약, 17일 당첨자 발표를 거쳐 11월 29일~12월 1일 계약하며 입주는 2029년 5월 예정이다. 분양가상한제 적용 단지다.</p>
    `
  },
  {
    id: "hanwha-forena-jije",
    category: "realestate",
    region: "경기",
    tag: "청약 언박싱 No.081",
    title: "경기 - 한화포레나 지제역 | 평택 세교동 1,098세대, 84㎡ 평균 분양가 6.95억, 예상 프리미엄 +0.58억",
    date: "2026-11-02",
    dateLabel: "2026. 11. 2",
    url: "posts/hanwha-forena-jije.html",
    preview: `
      <p>경기 평택시 세교동 725번지 일원의 '한화포레나 지제역'은 1,098세대 전 가구가 일반분양이며 84㎡ 평균 분양가는 가중평균 6.95억원이다. 브동산 적정가는 7.53억원으로 예상 프리미엄은 +0.58억이다. 브동산 판정은 저평가다.</p><p>2026년 10월 29일 입주자모집공고 후 11월 9일 특별공급, 10~11일 일반공급 청약, 18일 당첨자 발표를 거쳐 11월 29일~12월 1일 계약하며 입주는 2029년 11월 예정이다. 분양가상한제 미적용·비규제지역이다.</p>
    `
  },
  {
    id: "hillstate-isu-central",
    category: "realestate",
    region: "서울",
    tag: "청약 언박싱 No.080",
    title: "서울 - 힐스테이트 이수역센트럴 | 사당동 931세대 중 일반분양 170세대, 84㎡ 평균 분양가 21.67억, 예상 프리미엄 +3.08억",
    date: "2026-11-01",
    dateLabel: "2026. 11. 1",
    url: "posts/hillstate-isu-central.html",
    preview: `
      <p>서울 동작구 사당동 155-4, 사당3동 지역주택조합이 현대건설을 통해 공급한 '힐스테이트 이수역센트럴'은 931세대 중 170세대가 일반분양이며 84㎡ 평균 분양가는 가중평균 21.67억원이다. 브동산 적정가는 24.75억원으로 예상 프리미엄은 +3.08억이다. 브동산 판정은 저평가다.</p><p>2025년 10월 2일 입주자모집공고 후 10월 15일 1순위 청약(평균 326.74대 1)을 거쳐 11월 2~4일 계약까지 이미 끝났고 입주는 2028년 4월 예정이다. 정당계약 개시 8일 만에 전 세대 계약이 완료됐다.</p>
    `
  },
  {
    id: "acro-de-seocho",
    category: "realestate",
    region: "서울",
    tag: "청약 언박싱 No.079",
    title: "서울 - 아크로 드 서초 | 강남역 더블역세권 59㎡ 56가구, 예상 프리미엄 +14.50억",
    date: "2026-11-01",
    dateLabel: "2026. 11. 1",
    url: "posts/acro-de-seocho.html",
    preview: `
      <p>서울 서초구 서초동 1333번지 일원, DL이앤씨가 짓는 '아크로 드 서초'다. 1,161세대 중 일반분양은 전용 59㎡대 56세대뿐이며, 2026년 3월 20일 입주자모집공고 후 청약이 이미 끝났다.</p><p>56세대 가중평균 분양가는 18.12억원, 브동산 적정가는 32.62억원으로 예상 프리미엄은 +14.50억이다. 브동산 판정은 저평가다. 1순위 평균 경쟁률 1,099.1대1, 59C형은 당첨 가점 만점(84점) 사례까지 나왔다.</p>
    `
  },
  {
    id: "raemian-trinion",
    category: "realestate",
    region: "서울",
    tag: "청약 언박싱 No.078",
    title: "서울 - 래미안 트리니원 | 반포주공1단지 3주구 506세대, 84㎡ 평균 분양가 26.64억(상한제), 예상 프리미엄 +36.44억",
    date: "2026-11-01",
    dateLabel: "2026. 11. 1",
    url: "posts/raemian-trinion.html",
    preview: `
      <p>서울 서초구 반포동 1109, 반포주공1단지 3주구를 삼성물산이 재건축한 '래미안 트리니원'은 2,091세대 중 506세대가 일반분양이며 84㎡ 평균 분양가는 분양가상한제 적용으로 26.64억원에 그쳤다. 브동산 적정가는 63.08억원으로 예상 프리미엄은 +36.44억이다. 브동산 판정은 저평가다.</p><p>2025년 10월 31일 입주자모집공고 후 11월 청약·당첨자 발표, 12월 계약까지 이미 끝났고 입주는 2026년 8월 예정이다. 1순위 평균 237.5대 1, 최고 당첨가점 82점을 기록했다.</p>
    `
  },
  {
    id: "junghwa-raon-private-centro",
    category: "realestate",
    region: "서울",
    tag: "청약 언박싱 No.077",
    title: "서울 - 중화역 라온프라이빗 센트로 | 7호선 중화역 초역세권 176세대, 84㎡ 평균 분양가 12.51억, 예상 프리미엄 +6,380만",
    date: "2026-11-25",
    dateLabel: "2026. 11. 25",
    url: "posts/junghwa-raon-private-centro.html",
    preview: `
      <p>서울 중랑구 중화동 303-9번지, 7호선 중화역 도보 2분 거리에 라온건설이 짓는 176세대(일반분양 113세대) 단지다. 2026년 11월 6일 입주자모집공고 기준 84㎡ 세대수 가중평균 분양가는 12.51억원이고, 1순위는 53세대 모집에 1,052건이 접수됐다.</p><p>브동산이 e편한세상화랑대·사가정센트럴아이파크 2곳의 84㎡ KB 시세를 평점·연식 보정해 산출한 적정가는 13.15억원, 예상 프리미엄은 +6,380만(저평가)이다.</p>
    `
  },
  {
    id: "dh-sinbanpo-esterra",
    category: "realestate",
    region: "서울",
    tag: "청약 언박싱 No.076",
    title: "서울 - 디에이치 신반포에스테라 | 잠원동 160세대 중 84㎡ 28세대 최고가 입찰, 입찰기준가 평균 43.06억, 예상 프리미엄 +3.2억(입찰기준가 대비)",
    date: "2026-11-01",
    dateLabel: "2026. 11. 1",
    url: "posts/dh-sinbanpo-esterra.html",
    preview: `
      <p>서초구 잠원동 신반포22차 재건축 '디에이치 신반포에스테라'가 10월 30일 입찰공고를 냈다. 160세대 중 84㎡ 28세대만 최고가 입찰로 공급되며 입찰기준가 평균은 43.06억원이다.</p><p>브동산 적정가는 46.23억원으로 예상 프리미엄은 +3.2억이지만, 최고가 입찰이라 낙찰가가 기준가보다 오르면 이 폭은 줄어든다. 브동산 판정은 저평가다.</p>
    `
  },
  {
    id: "seocho-lottecastle-artpalace",
    category: "realestate",
    region: "서울",
    tag: "청약 언박싱 No.075",
    title: "서울 - 서초 롯데캐슬 아트팰리스 | 835세대 소형 청년안심주택, 브동산 적정가는 4.55억 (분양가는 공고 후 업데이트)",
    date: "2026-11-01",
    dateLabel: "2026. 11. 1",
    url: "posts/seocho-lottecastle-artpalace.html",
    preview: `
      <p>서울 서초구 서초동 1448-1 일원, 롯데건설이 시공하는 '서초 롯데캐슬 아트팰리스'다. 지하 5층~지상 36층 2개 동 835세대 중 전용 35~46㎡ 146세대가 일반분양되며, 남부터미널역 167m 초역세권에 분양가상한제가 적용된다.</p><p>11월 2일 모집공고 예정으로 아직 분양가는 공개되지 않았다. 브동산은 주력 면적인 37㎡ 타입군 기준 적정가 4.55억원을 먼저 산출했다.</p>
    `
  },
  {
    id: "gwacheon-detre-prestige",
    category: "realestate",
    region: "경기",
    tag: "청약 언박싱 No.074",
    title: "경기 - 과천 디에트르 퍼스티지 | 과천 거주 무주택세대주 대상 2세대, 예상 프리미엄 +9.67억",
    date: "2026-11-01",
    dateLabel: "2026. 11. 1",
    url: "posts/gwacheon-detre-prestige.html",
    preview: `
      <p>과천지식정보타운 S2BL 과천 디에트르 퍼스티지의 불법행위재공급 2세대. 전용 59㎡ 공고문상 총 공급비용 평균 8.9132억원을 기준으로, 브동산 적정가 18.58억원과의 평균 예상 프리미엄은 +9.67억원이다.</p><p>과천시 거주 무주택세대주가 청약통장 없이 추첨으로 신청할 수 있으며, 11월 2일 접수·11월 5일 당첨자 발표·11월 12일 계약 일정이다.</p>
    `
  },
  {
    id: "gwanggyo-jayeon-centreville",
    category: "realestate",
    region: "경기",
    tag: "청약 언박싱 No.073",
    title: "경기 - 광교 자연앤 센트레빌 | 84㎡ 공공분양, 예상 프리미엄 +5.52억",
    date: "2026-11-01",
    dateLabel: "2026. 11. 1",
    url: "posts/gwanggyo-jayeon-centreville.html",
    preview: `
      <p>광교 A17BL에 공급되는 600세대 국민주택이다. 84㎡ 공공분양 360세대의 공고문 분양가를 층별 세대수로 가중평균했다.</p><p>광교호반베르디움·광교더샵 84㎡ 실거래를 평점·연령 보정한 적정가와 59㎡ 지분적립형의 구조·리스크를 함께 정리했다.</p>
    `
  },
  {
    id: "geomdan-centreville-grandforet",
    category: "realestate",
    region: "인천",
    tag: "청약 언박싱 No.072",
    title: "인천 - 검단 센트레빌 그랑포레 | 검단 첫 민간공원 특례사업 843세대, 브동산 적정가는 6.2억 (분양가는 공고 후 업데이트)",
    date: "2026-10-31",
    dateLabel: "2026. 10. 31",
    url: "posts/geomdan-centreville-grandforet.html",
    preview: `
      <p>인천 검단구 오류동 검단 센트레빌 그랑포레, 동부건설이 짓는 843세대로 검단 최초 민간공원 특례사업이다. 입주자모집공고 전 브동산 84㎡ 적정가는 6.2억원이다.</p><p>분양가와 청약 일정이 공개되면 업데이트하며 예상 프리미엄을 추가할 예정이다.</p>
    `
  },
  {
    id: "sejong-smartcity-el-sujain",
    category: "realestate",
    region: "세종",
    tag: "청약 언박싱 No.071",
    title: "세종 - 세종스마트시티 엘 수자인 | 5-1생활권 국가시범도시 2,191세대, 브동산 적정가는 5.9억 (분양가는 공고 후 업데이트)",
    date: "2026-10-31",
    dateLabel: "2026. 10. 31",
    url: "posts/sejong-smartcity-el-sujain.html",
    preview: `
      <p>세종 합강동 5-1생활권 스마트시티 선도지구, BS한양이 짓는 '세종스마트시티 엘 수자인'은 아파트 2,191세대 전 가구 전용 84㎡ 단일 면적이며 11월 분양 예정이다. 입주자모집공고 전 브동산 84㎡ 적정가는 5.91억원이다.</p><p>분양가와 청약 일정이 공개되면 업데이트하며 예상 프리미엄을 추가할 예정이다.</p>
    `
  },
  {
    id: "siheung-elif-theprime",
    category: "realestate",
    region: "경기",
    tag: "청약 언박싱 No.070",
    title: "경기 - 엘리프 시흥 더프라임 | 시흥거모지구 B-5블록 338세대, 84㎡ 평균 분양가 5.95억(상한제), 예상 프리미엄 -1,190만",
    date: "2026-10-31",
    dateLabel: "2026. 10. 31",
    url: "posts/siheung-elif-theprime.html",
    preview: `
      <p>경기 시흥시 거모동 시흥거모 공공주택지구 B-5블록 '엘리프 시흥 더프라임'은 총 338세대 중 일반분양 304세대가 모두 전용 84㎡이며, 84㎡ 평균 분양가는 약 5.95억원(분양가상한제 적용)이다. 브동산 적정가는 5.83억원으로 예상 프리미엄은 -1,190만이다. 브동산 판정은 적정이다.</p><p>청약은 2026년 11월 9~11일이며 당첨자는 11월 17일 발표되고, 결과(경쟁률)는 아직 나오지 않았다.</p>
    `
  },
  {
    id: "mullae-harrington-place",
    category: "realestate",
    region: "서울",
    tag: "청약 언박싱 No.069",
    title: "서울 - 해링턴 플레이스 문래 | 문래동 218세대 전 가구 84㎡, 평균 분양가 17.92억, 예상 프리미엄 +9,060만",
    date: "2026-11-16",
    dateLabel: "2026. 11. 16",
    url: "posts/mullae-harrington-place.html",
    preview: `
      <p>서울 영등포구 문래동3가 해링턴 플레이스 문래, 효성중공업 시공 218세대 전 가구 전용 84㎡. 84㎡ 평균 분양가는 약 17.92억원이며 브동산 적정가는 18.83억원으로 예상 프리미엄은 +9,060만이다. 브동산 판정은 저평가다.</p><p>청약은 2026년 11월 23일 특별공급, 11월 24~25일 1순위로 진행되고 당첨자는 12월 2일 발표된다. 투기과열지구로 전매제한 3년이 적용되며 경쟁률은 접수 전이다.</p>
    `
  },
  {
    id: "gyeyang-kive-yubora-ac34",
    category: "realestate",
    region: "인천",
    tag: "청약 언박싱 No.068",
    title: "인천 - 계양신도시 카이브 유보라 | 3기 신도시 첫 민간분양 1,110세대, 84㎡ 평균 분양가 7.77억(상한제), 예상 프리미엄 -1.1억",
    date: "2026-10-31",
    dateLabel: "2026. 10. 31",
    url: "posts/gyeyang-kive-yubora-ac34.html",
    preview: `
      <p>인천 계양구 동양동 계양테크노밸리 AC3·AC4블록에 반도건설이 짓는 3기 신도시 첫 민간분양 1,110세대로 분양가상한제가 적용된다. 84㎡ 평균 분양가는 약 7.77억원이고 브동산 적정가는 6.70억원으로 예상 프리미엄은 -1.07억이다. 브동산 판정은 고평가다.</p><p>청약은 11월 2일 특별공급, 3일 1순위, 4일 2순위이며 결과는 아직 나오지 않았다.</p>
    `
  },
  {
    id: "hyangnam-lottecastle-signature",
    category: "realestate",
    region: "경기",
    tag: "청약 언박싱 No.067",
    title: "경기 - 화성 향남 롯데캐슬 시그니처 | 향남 첫 메이저 브랜드 1,542세대, 84㎡ 5.3억 분양가, 예상 프리미엄 +5,570만",
    date: "2026-10-31",
    dateLabel: "2026. 10. 31",
    url: "posts/hyangnam-lottecastle-signature.html",
    preview: `
      <p>경기 화성시 향남읍 상신리 롯데건설 '향남 롯데캐슬 시그니처', 향남 첫 롯데캐슬 1,542세대 대단지다. 84㎡ 분양가는 층별 가중평균 5.28억원이고 브동산 적정가는 5.84억원으로 예상 프리미엄은 +5,570만이다. 브동산 판정은 저평가다.</p><p>청약은 11월 2일 특별공급, 3일 1순위, 4일 2순위이며 계약은 11월 23~25일, 입주는 2029년 12월 예정이다. 청약 결과는 미정이다.</p>
    `
  },
  {
    id: "cheongna-arcone-prugio",
    category: "realestate",
    region: "인천",
    tag: "청약 언박싱 No.066",
    title: "인천 - 청라 아크원 푸르지오 | 청라국제업무단지 868세대 분양가상한제, 84㎡ 평균 분양가 8.75억, 예상 프리미엄 +7,780만",
    date: "2026-10-31",
    dateLabel: "2026. 10. 31",
    url: "posts/cheongna-arcone-prugio.html",
    preview: `
      <p>인천 서해구(옛 서구) 청라동 청라국제업무단지 M5블록에 대우건설이 공급하는 분양가상한제 푸르지오 아파트 868세대로, 84㎡ 평균 분양가는 8.75억원이고 브동산 적정가는 9.53억원으로 예상 프리미엄은 +7,780만이다. 브동산 판정은 저평가다.</p><p>청약은 11월 2일 특별공급, 3일 1순위, 4일 2순위 접수이며 입주는 2031년 8월 예정이다.</p>
    `
  },
  {
    id: "sangdaewon2-redevelopment",
    category: "realestate",
    region: "경기",
    tag: "청약 언박싱 No.065",
    title: "경기 - 상대원2구역 재개발 | 성남 중원구 4,885세대 대단지, 브동산 적정가는 15.2억 (분양 시기 미정)",
    date: "2026-10-05",
    dateLabel: "2026. 10. 5",
    url: "posts/sangdaewon2-redevelopment.html",
    preview: `
      <p>경기 성남 중원구 상대원2구역 재개발, 4,885가구 초대형 단지. 시공사 갈등으로 분양 시기는 미정이며 브동산 84㎡ 적정가는 15.2억원이다.</p><p>분양 시기와 분양가가 정해지면 업데이트하며 예상 프리미엄을 추가할 예정이다.</p>
    `
  },
  {
    id: "godeokgangil3-land-lease",
    category: "realestate",
    region: "서울",
    tag: "청약 언박싱 No.064",
    title: "서울 - 고덕강일3단지 토지임대부 | SH 공공분양 1,305세대, 59㎡ 건물분양가 3.7억에 월 임대료 51만원, 예상 프리미엄 +6.4억(토지 미소유·전매 10년 반영 전 이론치)",
    date: "2026-10-05",
    dateLabel: "2026. 10. 5",
    url: "posts/godeokgangil3-land-lease.html",
    preview: `
      <p>서울 강동구 강일동 고덕강일3단지 토지임대부 분양주택, SH 공급 1,305세대(전용 49㎡ 590·59㎡ 715)로 59㎡ 건물분양가는 평균 3.75억원에 월 토지임대료 51만 1,500원이다. 브동산 적정가는 12.63억원으로 토지임대부 환산 예상 프리미엄은 +6.4억이나, 토지 소유권이 없고 전매제한 10년이 걸린 구조라 시세차익으로 읽을 수 없는 이론치다. 브동산 판정은 저평가다.</p><p>청약은 특별공급 11월 2~3일, 일반공급 11월 4~6일이며 결과는 미정이다.</p>
    `
  },
  {
    id: "bangbae-forest-xi",
    category: "realestate",
    region: "서울",
    tag: "청약 언박싱 No.063",
    title: "서울 - 방배 포레스트자이 | 방배13구역 GS건설 2,228세대, 브동산 적정가는 36.3억 (분양가는 공고 후 업데이트)",
    date: "2026-10-05",
    dateLabel: "2026. 10. 5",
    url: "posts/bangbae-forest-xi.html",
    preview: `
      <p>서울 서초구 방배13구역 방배 포레스트자이, GS건설 2,228세대 대단지. 입주자모집공고 전 브동산 84㎡ 적정가는 36.3억원이다.</p><p>분양가는 공고 후 업데이트하며 예상 프리미엄을 추가할 예정이다.</p>
    `
  },
  {
    id: "bangbae-leel",
    category: "realestate",
    region: "서울",
    tag: "청약 언박싱 No.062",
    title: "서울 - 방배 르엘 | 방배14구역 롯데건설 492세대, 브동산 적정가는 34.1억 (분양가는 공고 후 업데이트)",
    date: "2026-10-05",
    dateLabel: "2026. 10. 5",
    url: "posts/bangbae-leel.html",
    preview: `
      <p>서울 서초구 방배14구역 방배 르엘, 롯데건설 492세대 소단지. 입주자모집공고 전 브동산 84㎡ 적정가는 34.1억원이다.</p><p>분양가는 공고 후 업데이트하며 예상 프리미엄을 추가할 예정이다.</p>
    `
  },
  {
    id: "heukseok-dh-kentronine",
    category: "realestate",
    region: "서울",
    tag: "청약 언박싱 No.061",
    title: "서울 - 디에이치 켄트로나인 | 흑석뉴타운 1,500세대 대단지, 브동산 적정가는 33.4억 (분양가는 공고 후 업데이트)",
    date: "2026-10-05",
    dateLabel: "2026. 10. 5",
    url: "posts/heukseok-dh-kentronine.html",
    preview: `
      <p>서울 동작구 흑석9구역 디에이치 켄트로나인, 현대건설 흑석뉴타운 1,500세대대 단지. 입주자모집공고 전 브동산 84㎡ 적정가는 33.4억원이다.</p><p>분양가는 공고 후 업데이트하며 예상 프리미엄을 추가할 예정이다.</p>
    `
  },
  {
    id: "paju-unjeong-jungang-city-pradium",
    category: "realestate",
    region: "경기",
    tag: "청약 언박싱 No.060",
    title: "경기 - GTX 운정중앙역 시티프라디움 | 파주 운정3지구 GTX 역세권 944세대, 84㎡ 평균 분양가 7.52억(상한제), 예상 프리미엄 -1,160만",
    date: "2026-10-02",
    dateLabel: "2026. 10. 2",
    url: "posts/paju-unjeong-jungang-city-pradium.html",
    preview: `
      <p>GTX 운정중앙역 시티프라디움은 파주 운정3지구 주상복합 3·4블록 944세대 단지이며 84㎡ 가중평균 분양가는 7.52억원, 브동산 적정가는 7.4억원으로 예상 프리미엄은 -1,160만이다. 브동산 판정은 적정이다.</p><p>청약은 11월 2~4일 접수, 당첨자는 3블록 11월 10일·4블록 11월 11일 발표, 입주는 2030년 7월 예정이다.</p>
    `
  },
  {
    id: "daegu-thesharp-dongin-centriche",
    category: "realestate",
    region: "대구",
    tag: "청약 언박싱 No.057",
    title: "대구 - 더샵 동인센트리체 | 대구시청 옆 49층 314세대, 84㎡ 8억대 분양가, 예상 프리미엄 -2.4억",
    date: "2026-10-02",
    dateLabel: "2026. 10. 2",
    url: "posts/daegu-thesharp-dongin-centriche.html",
    preview: `
      <p>대구 중구 동인동1가 더샵 동인센트리체, 포스코이앤씨 지하 4층~지상 49층 2개 동 314세대. 84㎡ 분양가 평균 약 8.36억원 기준 브동산 적정가는 5.93억원으로 예상 프리미엄은 -2.4억이다. 브동산 판정은 고평가다.</p><p>청약은 10월 12일 특별공급, 13일 1순위이며 전매제한 6개월·거주의무 없음이다.</p>
    `
  },
  {
    id: "gyeonghuigung-efit",
    category: "realestate",
    region: "서울",
    tag: "청약 언박싱 No.056",
    title: "서울 - 경희궁 에피트 | 종로 교남동 사대문 안 일반분양 134세대, 84㎡ 평균 분양가 24.78억, 예상 프리미엄 -3.06억",
    date: "2026-11-16",
    dateLabel: "2026. 11. 16",
    url: "posts/gyeonghuigung-efit.html",
    preview: `
      <p>서울 종로구 교남동 경희궁 에피트, 도시정비형 재개발 228세대 중 일반분양 134세대. 84㎡ 분양가 가중평균 24.78억원 대비 브동산 적정가는 21.71억원으로 예상 프리미엄은 -3.06억이다. 브동산 판정은 고평가다.</p><p>2026년 11월 13일 입주자모집공고, 특별공급 11월 25일·1순위 11월 26일, 입주는 2030년 8월 예정이며 투기과열지구·재당첨제한 10년·전매제한 최대 3년이다.</p>
    `
  },
  { id: "banpo-dh-classtre", category: "realestate", region: "서울", tag: "청약 언박싱 No.055", title: "서울 - 디에이치 반포124 | 분양가 재심의 12월 4일, 평당 9천만~1억이면 84㎡ 30.6억~34억, 브동산 적정가 57.3억", date: "2026-11-26", dateLabel: "2026. 11. 26", url: "posts/banpo-dh-classtre.html", preview: `<p>서초구 분양가심의위원회가 11월 18일 결정을 보류해 디에이치 반포124(5,007세대, 일반분양 1,801세대) 분양가는 12월 4일 재심의한다. 3.3㎡당 9,000만~1억원이면 84㎡는 약 30.6억~34억원이다.</p><p>반포래미안트리니원·래미안원베일리 KB 시세로 다시 계산한 브동산 적정가는 57.28억원, 시나리오별 예상 프리미엄은 +23.28억~+26.68억(저평가)이다.</p>` },
  {
    id: "acmer-dongtan",
    category: "realestate",
    region: "경기",
    tag: "청약 언박싱 No.054",
    title: "경기 - 아크메르 동탄 | 동탄1신도시 49층 1,808세대, 84㎡ 17억대 분양가, 예상 프리미엄 +2.9억",
    date: "2026-10-02",
    dateLabel: "2026. 10. 2",
    url: "posts/acmer-dongtan.html",
    preview: `
      <p>경기 화성 동탄1신도시 아크메르 동탄, 포스코이앤씨 시공 최고 49층 1,808세대. 전용 84㎡ 분양가는 층별 16.51억~17.17억원, 세대수 가중평균 약 16.85억원이고 입주는 2032년 1월 예정이다. 브동산 적정가는 19.7억원으로 예상 프리미엄은 +2.9억이다. 브동산 판정은 저평가다.</p><p>청약은 특별공급 0.37대 1, 1순위 두 블록 합산 1.02대 1에 그쳤고 95블록 84㎡C만 1순위에서 마감됐다.</p>
    `
  },
  {
    id: "ulsan-jungsan-diachae",
    category: "realestate",
    region: "울산",
    tag: "청약 언박싱 No.053",
    title: "울산 - 중산디아채 | LH 분양전환 잔여세대 선착순 8호, 2억원대 국평 예상 프리미엄 +8,160만",
    date: "2026-10-02",
    dateLabel: "2026. 10. 2",
    url: "posts/ulsan-jungsan-diachae.html",
    preview: `
      <p>울산 북구 중산동 중산디아채, LH 분양전환 잔여세대 선착순 8호(전용 84㎡ 2억 100만~2억 2,450만원, 12월 23일까지). 브동산 적정가는 2.95억원으로 예상 프리미엄은 +8,160만이다.</p><p>다만 같은 단지 시세(2.06~2.26억원)와 분양가가 비슷해 모형 결과는 구축 감가 미반영분을 감안해 해석해야 한다.</p>
    `
  },
  {
    id: "incheon-gajeong2-b2-lh",
    category: "realestate",
    region: "인천",
    tag: "청약 언박싱 No.052",
    title: "인천 - 인천가정2 B2블록 공공분양 | 마지막 공공분양 잔여세대 252세대, 예상 프리미엄 -2,730만",
    date: "2026-10-02",
    dateLabel: "2026. 10. 2",
    url: "posts/incheon-gajeong2-b2-lh.html",
    preview: `
      <p>인천 서구 인천가정2지구 마지막 공공분양, B2블록 잔여세대 252세대. 84㎡ 분양가 중앙값 6.05억원 기준 브동산 적정가는 5.78억원으로 예상 프리미엄은 -2,730만이다.</p><p>접수는 10월 6~7일이며 전매제한 3년·거주의무 3년이 붙는다.</p>
    `
  },
  {
    id: "thesharp-bundang-centro",
    category: "realestate",
    region: "경기",
    tag: "청약 언박싱 No.051",
    title: "경기 - 더샵 분당센트로 | 오리역 리모델링 647세대, 임의공급 5차까지 이어진 20억 국평, 예상 프리미엄 +6.3억",
    date: "2026-10-01",
    dateLabel: "2026. 10. 1",
    url: "posts/thesharp-bundang-centro.html",
    preview: `
      <p>경기 성남 구미동 더샵 분당센트로, 무지개마을4단지 리모델링 647세대(일반분양 84세대). 1차 1순위 평균 51.3대 1이었으나 고분양가 탓에 계약 포기가 이어져 임의공급이 5차까지 진행됐다.</p><p>5차 공급가 84N 20.72억원 기준 브동산 적정가는 27.05억원, 예상 프리미엄은 +6.3억이다. 브동산 판정은 저평가다. 다만 비교단지 연식 보정 상한의 영향이 커 해석에 유의가 필요하다.</p>
    `
  },
  {
    id: "incheon-gyeyang-a17-lh",
    category: "realestate",
    region: "인천",
    tag: "청약 언박싱 No.050",
    title: "인천 - 인천계양 A17블록 신혼희망타운 | 3기 신도시 전용 55㎡ 단일면적 309세대, 예상 프리미엄 -520만",
    date: "2026-10-01",
    dateLabel: "2026. 10. 1",
    url: "posts/incheon-gyeyang-a17-lh.html",
    preview: `
      <p>인천 계양구 3기 신도시 인천계양 A17블록, LH 신혼희망타운(공공분양) 309세대. 전용 55㎡ 평균 분양가 5.04억원 기준 브동산 적정가는 4.99억원으로 예상 프리미엄은 -520만이다. 브동산 판정은 적정이다.</p><p>본청약 신규 신청자 물량은 176세대이며 접수는 10월 26~27일이다. 수익공유형 모기지 의무가입과 전매제한 3년 조건을 함께 봐야 한다.</p>
    `
  },
  {
    id: "drefine-artia-noryangjin2",
    category: "realestate",
    region: "서울",
    tag: "청약 언박싱 No.046",
    title: "서울 - 드파인 아르티아 | 노량진뉴타운2구역 초고층 404세대, 예상 프리미엄 -1.59억",
    date: "2026-09-30",
    dateLabel: "2026. 9. 30",
    url: "posts/drefine-artia-noryangjin2.html",
    preview: `
      <p>서울 동작구 노량진2구역, SK에코플랜트의 한강 이남 첫 단독 시공 단지 드파인 아르티아 404세대. 7호선 장승배기역 바로 앞 초역세권이다. 84㎡ 분양가 26.24억원(무순위 공고 범위 중간값) 기준 브동산 적정가는 24.65억원으로 예상 프리미엄은 -1.59억이다. 브동산 판정은 고평가다.</p><p>1순위 평균 16.5대 1로 마감됐으나 8월 무순위 청약으로 15가구가 다시 나왔다.</p>
    `
  },
  {
    id: "jangwi-prugio-markone",
    category: "realestate",
    region: "서울",
    tag: "청약 언박싱 No.047",
    title: "서울 - 장위 푸르지오 마크원 | 6호선 돌곶이역 초품아 1,931세대, 예상 프리미엄 -1,960만",
    date: "2026-09-30",
    dateLabel: "2026. 9. 30",
    url: "posts/jangwi-prugio-markone.html",
    preview: `
      <p>서울 성북구 장위뉴타운10구역, 6호선 돌곶이역 도보 5분권의 장위 푸르지오 마크원 1,931세대(일반분양 1,032세대). 84㎡ 평균 분양가 17.11억원 기준 브동산 적정가는 16.92억원으로 예상 프리미엄은 -1,960만이다. 브동산 판정은 적정이다.</p><p>1순위 평균 9.55대 1로 마감됐으나 강화된 대출 규제로 미계약 39가구가 무순위로 나왔다. 단기 차익보다 실거주 관점에서 접근할 단지다.</p>
    `
  },
  {
    id: "guri-lottecastle-signature",
    category: "realestate",
    region: "경기",
    tag: "청약 언박싱 No.048",
    title: "경기 - 구리역 롯데캐슬 시그니처 | 인창C구역 1,180세대 불법행위 재공급 1가구, 예상 프리미엄 +4.85억",
    date: "2026-09-30",
    dateLabel: "2026. 9. 30",
    url: "posts/guri-lottecastle-signature.html",
    preview: `
      <p>경기 구리시 인창C구역, 1,180세대 대단지 구리역 롯데캐슬 시그니처에서 나온 전용 82㎡B 1가구 불법행위 재공급. 공급가 8.77억원 기준 브동산 적정가는 13.62억원으로 예상 프리미엄은 +4.85억이다. 브동산 판정은 저평가다.</p><p>구리시 거주 무주택 세대주만 신청할 수 있고 추첨 1가구라는 특수성이 있어, 참고 사례로 봐야 한다.</p>
    `
  },
  {
    id: "incheon-gyeyang-a6-lh",
    category: "realestate",
    region: "인천",
    tag: "청약 언박싱 No.049",
    title: "인천 - 인천계양 A6블록 | 3기 신도시 LH 공공분양 663세대, 예상 프리미엄 -4,210만",
    date: "2026-09-30",
    dateLabel: "2026. 9. 30",
    url: "posts/incheon-gyeyang-a6-lh.html",
    preview: `
      <p>인천 계양구 박촌동 3기 신도시 인천계양 A6블록, LH 공공분양 663세대. 84㎡ 평균 분양가 7.10억원 기준 브동산 적정가는 6.68억원으로 예상 프리미엄은 -4,210만이다. 브동산 판정은 고평가다.</p><p>공급의 약 80%가 59㎡(529세대)이고 84㎡는 42세대뿐이다. 이번 본청약 일반공급은 38세대이며 접수는 9월 30일~10월 2일이다.</p>
    `
  },
  {
    id: "chungjeongno-station-xi-rene",
    category: "realestate",
    region: "서울",
    tag: "청약 언박싱 No.045",
    title: "서울 - 충정로역자이르네 | 2·5호선 충정로역 직통연결 299세대, 예상 프리미엄 +5,880만",
    date: "2026-09-29",
    dateLabel: "2026. 9. 29",
    url: "posts/chungjeongno-station-xi-rene.html",
    preview: `
      <p>서울 중구 중림동, 2·5호선 충정로역과 직통 연결되는 자이S&D의 충정로역자이르네 299세대. 84㎡ 가중평균 분양가(23.47억원) 기준 브동산 적정가는 24.06억원으로, 예상 프리미엄은 +5,880만이다. 브동산 판정은 적정이다. 일반공급 1순위 평균 44.5대 1로 흥행했다.</p>
    `
  },
  {
    id: "gangbyeon-station-central-ipark",
    category: "realestate",
    region: "서울",
    tag: "청약 언박싱 No.044",
    title: "서울 - 강변역 센트럴 아이파크 | 한양연립 모아타운 재건축 68세대, 예상 프리미엄 +5.76억",
    date: "2026-09-29",
    dateLabel: "2026. 9. 29",
    url: "posts/gangbyeon-station-central-ipark.html",
    preview: `
      <p>서울 광진구 구의동, 한양연립 등을 모아타운 방식으로 재건축하는 HDC현대산업개발의 강변역 센트럴 아이파크 68세대. 84㎡ 기준 브동산 적정가는 18.46억원, 실제 분양가(12.70억원) 대비 예상 프리미엄은 +5.76억이다. 브동산 판정은 저평가다. 특별공급 263대 1, 일반공급 1순위 평균 494대 1로 100% 완판됐다.</p>
    `
  },
  {
    id: "gwacheon-prugio-labienoo",
    category: "realestate",
    region: "경기",
    tag: "청약 언박싱 No.043",
    title: "경기 - 과천 푸르지오 라비엔오 | 과천지식정보타운 지하2~35층 679세대, 예상 프리미엄 +15.71억",
    date: "2026-09-29",
    dateLabel: "2026. 9. 29",
    url: "posts/gwacheon-prugio-labienoo.html",
    preview: `
      <p>과천지식정보타운 S4블록, 2021년 12월 입주를 마친 대우건설의 과천 푸르지오 라비엔오. 2020년 원분양가(84D 7.45억원) 기준 브동산 적정가는 23.16억원으로 예상 프리미엄은 +15.71억이다. 브동산 판정은 저평가다. 최근에도 신혼부부·노부모부양 특별공급 2세대가 2020년 분양가 그대로 재공급되고 있다.</p>
    `
  },
  {
    id: "gwacheon-prugio-bellarte",
    category: "realestate",
    region: "경기",
    tag: "청약 언박싱 No.042",
    title: "경기 - 과천 푸르지오 벨라르테 | 과천지식정보타운 초품아 504세대, 예상 프리미엄 +16.95억",
    date: "2026-09-29",
    dateLabel: "2026. 9. 29",
    url: "posts/gwacheon-prugio-bellarte.html",
    preview: `
      <p>과천지식정보타운 S6블록, 2022년 10월 입주를 마친 대우건설 컨소시엄의 과천 푸르지오 벨라르테. 2020년 원분양가(84㎡ 약 6.09억원) 기준 브동산 적정가는 23.04억원으로 예상 프리미엄은 +16.95억이다. 브동산 판정은 저평가다. 최근 99㎡ B형 1세대가 2020년 분양가 그대로 "반값 로또" 무순위로 재공급됐다.</p>
    `
  },
  {
    id: "acro-riversky",
    category: "realestate",
    region: "서울",
    tag: "청약 언박싱 No.041",
    title: "서울 - 아크로 리버스카이 | 노량진뉴타운8구역 하이엔드 987세대, 예상 프리미엄 -1.94억",
    date: "2026-09-29",
    dateLabel: "2026. 9. 29",
    url: "posts/acro-riversky.html",
    preview: `
      <p>서울 동작구 노량진동, 노량진뉴타운8구역을 재개발하는 DL이앤씨의 아크로 리버스카이 987세대. 84㎡ 최고 분양가(27.96억원) 기준 브동산 적정가는 26.02억원으로 예상 프리미엄은 -1.94억이다. 브동산 판정은 고평가다. 다만 1순위 평균 19.8대 1로 전 주택형이 마감돼 모형과 시장 반응이 엇갈리는 사례다.</p>
    `
  },
  {
    id: "thesharp-cheongju-greenity",
    category: "realestate",
    region: "충북",
    tag: "청약 언박싱 No.040",
    title: "충북 - 더샵 청주그리니티 | 개신동 구룡공원 앞 1,191세대, 예상 프리미엄 +3.0억",
    date: "2026-09-29",
    dateLabel: "2026. 9. 29",
    url: "posts/thesharp-cheongju-greenity.html",
    preview: `
      <p>충북 청주시 서원구 개신동, 구룡공원을 앞마당처럼 누리는 포스코건설의 더샵 청주그리니티 1,191세대. 84㎡ 기준 브동산 적정가는 6.64억원, 실제 분양가(3.65억원) 대비 예상 프리미엄은 +2.99억이다. 브동산 판정은 저평가다. 1순위 평균 15.0대 1로 전 타입이 마감됐다.</p>
    `
  },
  {
    id: "hoecheon-central-paragon",
    category: "realestate",
    region: "경기",
    tag: "청약 언박싱 No.039",
    title: "경기 - 회천중앙역 파라곤 | 양주 회천지구 비규제지역 845세대, 예상 프리미엄 +5,060만",
    date: "2026-09-29",
    dateLabel: "2026. 9. 29",
    url: "posts/hoecheon-central-paragon.html",
    preview: `
      <p>경기 양주시 회정동, 회천지구 A10-1블록에 공급된 이지건설의 회천중앙역 파라곤 845세대. 84㎡ 기준 브동산 적정가는 5.65억원으로 실제 분양가(5.14억원) 대비 예상 프리미엄은 +5,060만이다. 브동산 판정은 저평가다. 비규제지역이지만 일부 매체는 "역대 최고가 분양"이라며 우려를 제기했다.</p>
    `
  },
  {
    id: "hillstate-songpa-thegrid",
    category: "realestate",
    region: "서울",
    tag: "청약 언박싱 No.038",
    title: "서울 - 힐스테이트 송파더그리드 | 복정역 더블역세권 주거형 오피스텔 1,393실, 예상 프리미엄 +4.2억",
    date: "2026-09-28",
    dateLabel: "2026. 9. 28",
    url: "posts/hillstate-songpa-thegrid.html",
    preview: `
      <p>서울 송파구 장지동 909번지, 8호선·수인분당선 복정역 더블역세권의 주거형 오피스텔 힐스테이트 송파더그리드. 전용 84㎡ 타입(55실)을 인근 아파트(송파파인타운8·9단지)의 84㎡와 같은 크기로 놓고 비교한 브동산 적정가는 18.41억원, 실제 분양가(14.18억원)보다 높아 예상 프리미엄은 +4.2억으로 나타났다. 브동산 판정은 저평가다. 다만 오피스텔은 아파트와 취득세·대출 규제 체계가 달라 이 신호를 단순하게 해석하기는 어렵다.</p>
    `
  },
  {
    id: "samcheon-hanulche-ravielle",
    category: "realestate",
    region: "전북",
    tag: "청약 언박싱 No.037",
    title: "전북 - 삼천 하늘채 라비엘 | 삼천주공3단지 재건축 602세대, 예상 프리미엄 +7,172만",
    date: "2026-09-28",
    dateLabel: "2026. 9. 28",
    url: "posts/samcheon-hanulche-ravielle.html",
    preview: `
      <p>전북 전주시 완산구 삼천동1가, 삼천주공3단지를 재건축하는 코오롱글로벌 '하늘채' 602세대. 84㎡ 타입이 없어 59㎡ 기준으로 인근 전주태평아이파크·힐스테이트어울림효자와 비교한 브동산 적정가는 4.40억원, 실제 분양가(3.69억원)보다 높아 예상 프리미엄은 +7,172만으로 나타났다. 브동산 판정은 저평가다. 이번 조사 대상 중 드물게 뚜렷한 저평가 신호가 나온 단지다.</p>
    `
  },
  {
    id: "sungui-station-norway-forest-the-sky",
    category: "realestate",
    region: "인천",
    tag: "청약 언박싱 No.036",
    title: "인천 - 숭의역 노르웨이숲 더 스카이 | 숭의역 도보 1분 지역주택조합 아파트 324세대, 예상 프리미엄 -1.1억",
    date: "2026-09-28",
    dateLabel: "2026. 9. 28",
    url: "posts/sungui-station-norway-forest-the-sky.html",
    preview: `
      <p>인천 미추홀구 숭의동, 수인분당선 숭의역 도보 1분을 내세우는 지역주택조합 아파트+오피스텔 복합단지. 84㎡ 기준 브동산 적정가는 5.74억원, 실제 분양가(6.84억원)보다 낮아 예상 프리미엄은 -1.1억으로 나타났다. 브동산 판정은 고평가다. 무엇보다 이 단지는 지역주택조합 사업이라 사업 지연·분담금 변동 리스크를 별도로 감안해야 한다.</p>
    `
  },
  {
    id: "hcmc-meat-and-meet-buffet",
    category: "vietnam",
    hidden: true,
    tag: "베트남 호치민 이야기 No.3",
    title: "호치민 고기부페 미트앤미트 — 두 아들과 다녀온 가성비 숯불 부페",
    date: "2026-09-30",
    dateLabel: "2026. 9. 30",
    url: "posts/hcmc-meat-and-meet-buffet.html",
    preview: `
      <p>1인 249,000동에 숯불 고기와 부페를 마음껏 즐길 수 있는 투티엠 티소몰 안 한국식 고기부페 미트앤미트. 깔끔한 매장에 치킨·라면·아이스크림까지 아이들이 좋아할 메뉴가 많고, 아이 요금도 키에 따라 무료·50%라 2살·6살 두 아들과 가기 좋은 가성비 외식 장소로 정리했다.</p>
    `
  },
  {
    id: "hcmc-lime-photodermatitis",
    category: "vietnam",
    hidden: true,
    tag: "베트남 호치민 이야기 No.2",
    title: "쌀국수 먹을 때 라임 짜고 손 안 씻으면 생기는 일 — 베트남 여행객이 꼭 기억해야 할 라임 색소침착",
    date: "2026-09-29",
    dateLabel: "2026. 9. 29",
    url: "posts/hcmc-lime-photodermatitis.html",
    preview: `
      <p>쌀국수에 라임을 짜 넣고 손을 안 씻은 채 햇빛을 쐬었더니 손등에 갈색 얼룩이 생겼다. 라임즙과 햇빛이 만나 생기는 식물광선피부염("라임 색소침착")으로, 베트남 어디서나 여행객이 기억해둘 원인과 예방법을 정리했다.</p>
    `
  },
  {
    id: "hcmc-taodien-thuthiem-commute",
    category: "vietnam",
    hidden: true,
    tag: "베트남 호치민 이야기 No.1",
    title: "타오디엔에서 투티엠까지 — 메트로로 가본 주재원 출근길",
    date: "2026-09-28",
    dateLabel: "2026. 9. 28",
    url: "posts/hcmc-taodien-thuthiem-commute.html",
    preview: `
      <p>브동산에 카테고리를 하나 새로 만들었어요. "베트남 호치민 이야기". 부동산이랑 브랜드 얘기만 하던 곳에, 저희 가족이 호치민에서 지내며 겪는 소소한 이야기들도 이제 하나씩 풀어보려고 해요. 첫 편은 신랑의 타오디엔 집에서 투티엠 사무실까지, 메트로 출근길 사진 따라가기예요.</p>
    `
  },
  {
    id: "hoban-summit-cheomdan3",
    category: "realestate",
    region: "광주",
    tag: "청약 언박싱 No.034",
    title: "광주 - 호반써밋 첨단3지구 A7BL | 광주·전남 두 지자체에 걸친 마지막 공공택지 805가구, 예상 프리미엄 -2,541만",
    date: "2026-09-28",
    dateLabel: "2026. 9. 28",
    url: "posts/hoban-summit-cheomdan3.html",
    preview: `
      <p>호반건설이 광주연구개발특구 첨단3지구에 공급하는 호반써밋 첨단3지구는 A7블록(전용 84㎡, 356세대)과 A8블록(전용 117~135㎡, 449세대)을 합쳐 총 805세대 규모다. 같은 사업이면서도 A7블록은 광주광역시 북구, A8블록은 전남 장성군에 걸쳐 있다는 점이 특징이다. 브동산이 세대수가 많은 84㎡ 타입을 기준으로 인근 첨단2지구 중흥S클래스·첨단자이2차 두 단지의 가격을 보정해 산출한 적정가는 5.12억원으로, 실제 분양가(5.37억원)보다 약 5% 낮았다.</p>
    `
  },
  {
    id: "gimhae-sinmun-central-ipark",
    category: "realestate",
    region: "경남",
    tag: "청약 언박싱 No.033",
    title: "경남 - 김해 신문 센트럴 아이파크 | 장유신문지구 마침표 찍는 1,379세대 리버뷰 대단지, 예상 프리미엄 +3,100만",
    date: "2026-09-28",
    dateLabel: "2026. 9. 28",
    url: "posts/gimhae-sinmun-central-ipark.html",
    preview: `
      <p>경상남도 김해시 신문동, 장유신문지구 A34-1블록에 HDC현대산업개발이 짓는 김해 신문 센트럴 아이파크는 지하 2층~지상 최고 25층, 13개 동, 전용 84~128㎡ 총 1,379세대 규모의 대단지다. 2026년 7월 정당계약 이후에도 865세대가 남아 8월 무순위 청약을 추가 진행했고 현재도 선착순 계약이 이어지고 있다. 브동산이 같은 신문동 생활권의 더샵신문그리니티·장유자이더파크 두 단지의 84㎡ 가격을 보정해 산출한 적정가는 5.21억원으로, 실제 분양가(4.90억원)보다 약 6% 낮았다.</p>
    `
  },
  {
    id: "eopseong-prugio-lakecity-2danji",
    category: "realestate",
    region: "충남",
    tag: "청약 언박싱 No.032",
    title: "충남 - 업성 푸르지오 레이크시티 2단지 | 성성호수 곁 대우건설 랜드마크 448세대, 예상 프리미엄 +500만",
    date: "2026-09-28",
    dateLabel: "2026. 9. 28",
    url: "posts/eopseong-prugio-lakecity-2danji.html",
    preview: `
      <p>충남 천안시 서북구 업성동, 성성호수공원을 남향으로 두른 업성 푸르지오 레이크시티 2단지(대우건설·448세대)를 브동산 모형으로 분석했다. 같은 성성동 생활권의 '푸르지오' 완공 단지 두 곳(천안푸르지오레이크사이드·천안레이크타운3차푸르지오)과 비교한 결과 적정가는 5.63억, 실제 분양가는 5.58억으로 거의 일치하는 수준(브동산 판정 적정, 차이 약 1%)이 나왔지만, 실제 청약은 특별공급 0.03대 1·1·2순위 평균 0.17대 1로 전 타입이 대거 미달돼 모형 신호와 정반대의 냉정한 결과를 보였다.</p>
    `
  },
  {
    id: "pentahills-w-1danji",
    category: "realestate",
    region: "경북",
    tag: "청약 언박싱 No.031",
    title: "경북 - 펜타힐즈 더블유 1단지 | 경산 중산지구 첫 초고층 랜드마크 1,712세대, 예상 프리미엄 -1.5억",
    date: "2026-09-27",
    dateLabel: "2026. 9. 27",
    url: "posts/pentahills-w-1danji.html",
    preview: `
      <p>경북 경산시 중산동, 아이에스동서 하이엔드 브랜드 'W'가 처음 적용된 최고 59층 랜드마크 펜타힐즈 더블유 1단지(1,712세대)를 브동산 모형으로 분석했다. 같은 펜타힐즈 지구의 브랜드 만점 기존 단지 두 곳(펜타힐즈 푸르지오·힐스테이트 펜타힐즈)과 비교한 결과 적정가는 5.22억, 실제 분양가는 6.75억으로 약 23% 고평가 신호가 나왔지만, 실제 청약에서는 전용 84㎡B 타입이 18배 넘는 경쟁률로 마감되는 등 모형 신호와 반대되는 흥행을 기록했다.</p>
    `
  },
  {
    id: "hoban-summit-pungmu-3",
    category: "realestate",
    region: "경기",
    tag: "청약 언박싱 No.030",
    title: "경기 - 호반써밋 풍무Ⅲ | 풍무역 도보 5분 '호반써밋' 브랜드타운 완성 660세대, 예상 프리미엄 +1,100만",
    date: "2026-09-27",
    dateLabel: "2026. 9. 27",
    url: "posts/hoban-summit-pungmu-3.html",
    preview: `
      <p>경기도 김포시 사우동 458번지 일원, 김포풍무역세권 도시개발사업 B4블록에 호반건설이 짓는 호반써밋 풍무Ⅲ는 지하 2층~지상 29층, 8개동, 전용 59㎡·84㎡로만 구성된 총 660세대 규모의 단지다. 김포골드라인 풍무역을 도보 5분 거리에 둔 초역세권 입지로, 앞서 공급된 B5블록 호반써밋 풍무(1차)·C5블록 호반써밋 풍무Ⅱ(2차)에 이어 이 지구에 총 2,577세대 규모의 '호반써밋' 브랜드타운을 완성하는 마지막 단지다. 브동산 모형상 적정가는 7.47억원으로 실제 분양가(7.36억원)와 거의 같아, 약 1.5% 수준의 근소한 저평가 신호로 나타났다.</p>
    `
  },
  {
    id: "chuncheon-riverview-ipark",
    category: "realestate",
    region: "강원",
    tag: "청약 언박싱 No.029",
    title: "강원 - 춘천 리버뷰 아이파크 | 동면권역 15년 만의 아이파크 브랜드타운 262세대, 예상 프리미엄 -2,445만",
    date: "2026-09-27",
    dateLabel: "2026. 9. 27",
    url: "posts/chuncheon-riverview-ipark.html",
    preview: `
      <p>강원특별자치도 춘천시 동면 장학리 883번지 일원에 HDC현대산업개발이 짓는 춘천 리버뷰 아이파크는 지하 2층~지상 최고 27층, 2개 동, 전용 59㎡·84㎡ 총 262세대 규모의 단지다. 동면권역에 아이파크 브랜드가 공급되는 것은 2012년 춘천장학아이파크 이후 약 15년 만이다. 브동산이 인접한 춘천장학아이파크·삼천동 춘천파크자이 두 단지의 84㎡ 가격을 보정해 산출한 적정가는 5.37억원으로, 실제 분양가(5.61억원)보다 약 5% 낮았다.</p>
    `
  },
  {
    id: "thesharp-tricente",
    category: "realestate",
    region: "부산",
    tag: "청약 언박싱 No.027",
    title: "부산 - 더샵 트리센트 | 지게골역 곁 대연·문현 더블생활권 803세대, 예상 프리미엄 +9천만",
    date: "2026-09-27",
    dateLabel: "2026. 9. 27",
    url: "posts/thesharp-tricente.html",
    preview: `
      <p>부산광역시 남구 문현동 334번지 일원, 문현동 재개발정비사업으로 조성되는 더샵 트리센트는 포스코이앤씨가 짓는 지하 4층~지상 35층, 6개동, 전용 59~84㎡ 총 803세대 규모의 단지다. 2026년 8월 1순위 청약에서 평균 18.29대 1의 경쟁률로 전 타입이 마감됐다. 브동산이 같은 남구 대연동의 대연롯데캐슬레전드·대연자이 두 단지의 84㎡ 가격을 보정해 산출한 적정가는 9.21억원으로, 실제 분양가(8.32억원)보다 약 11% 낮았다.</p>
    `
  },
  {
    id: "hangang-prugio-riverfront",
    category: "realestate",
    region: "경기",
    tag: "청약 언박싱 No.026",
    title: "경기 - 한강 푸르지오 리버프론트 | 김포 고촌 한강변 최고 38층 2,432세대, 예상 프리미엄 +5천만",
    date: "2026-09-27",
    dateLabel: "2026. 9. 27",
    url: "posts/hangang-prugio-riverfront.html",
    preview: `
      <p>경기 김포시 고촌읍 향산리에 대우건설이 짓는 한강 푸르지오 리버프론트는 지하 4층~지상 최고 38층, 12개 동, 전용 84~180㎡ 아파트 2,432세대에 주거형 오피스텔 250실을 더해 총 2,682세대 규모로 조성된다. 대부분 세대가 한강을 향한 영구 조망을 확보한다는 점이 최대 강점으로 꼽힌다. 브동산이 같은 고촌읍의 힐스테이트리버시티1단지·고촌센트럴자이 두 단지의 84㎡ 가격을 보정해 산출한 적정가는 7.61억원으로, 실제 분양가(7.09억원)보다 약 7% 낮았다.</p>
    `
  },
  {
    id: "yongin-dongil-hivill-parkvalley",
    category: "realestate",
    region: "경기",
    tag: "청약 언박싱 No.023",
    title: "경기 - 용인반도체클러스터 동일하이빌 파크밸리 | SK하이닉스 곁 산단 첫 아파트 589세대, 예상 프리미엄 +6천만",
    date: "2026-09-25",
    dateLabel: "2026. 9. 25",
    url: "posts/yongin-dongil-hivill-parkvalley.html",
    preview: `
      <p>경기 용인시 처인구 원삼면, 용인반도체클러스터 일반산업단지(D1-1블록)에 동일토건이 짓는 동일하이빌 파크밸리는 이 산업단지 안에 공급되는 첫 공동주택입니다. 전체 1,250세대 중 1단지 589세대가 먼저 분양됐고, SK하이닉스 600조원 투자·2027년 1기 팹 가동이 핵심 호재입니다.</p>
      <p>브동산이 같은 처인구의 힐스테이트용인둔전역·용인드마크데시앙 두 단지의 84㎡ 가격을 보정해 산출한 적정가는 5.72억원으로, 실제 분양가(5.13억원)보다 약 11% 높았습니다(저평가 신호). 다만 SITE와 비교단지의 입지 점수 격차가 극심해 평점보정을 최대치로 제한해 계산했다는 한계가 있습니다.</p>
    `
  },
  {
    id: "doosan-weve-the-zenith-bucheon",
    category: "realestate",
    region: "경기",
    tag: "청약 언박싱 No.022",
    title: "경기 - 두산위브더제니스 부천 | 소사역 더블역세권 최고 49층 2,008가구, 예상 프리미엄 +4.6억",
    date: "2026-09-25",
    dateLabel: "2026. 9. 25",
    url: "posts/doosan-weve-the-zenith-bucheon.html",
    preview: `
      <p>경기 부천시 소사구 소사본동, 소사본1-1구역 재개발로 짓는 두산위브더제니스 부천은 두산건설과 쌍용건설이 함께 시공하는 최고 49층, 총 2,008세대 규모의 랜드마크 주상복합입니다. 1호선과 서해선이 만나는 소사역 더블역세권이 강점입니다.</p>
      <p>브동산이 같은 소사본동의 힐스테이트소사역·부천소사역푸르지오 두 단지의 84㎡ 가격을 입지·브랜드·연식 차이만큼 보정해 산출한 적정가는 10.10억원으로, 실제 분양가(84A/B 최저가 기준 5.50억원)보다 매우 크게 낮았습니다. 다만 정당계약 후 229세대가 무순위로 다시 나왔다는 점은 함께 봐야 할 리스크입니다.</p>
    `
  },
  {
    id: "jeil-punggyeongchae-cheomdan3-a6bl",
    category: "realestate",
    region: "광주",
    tag: "청약 언박싱 No.021",
    title: "광주 - 제일풍경채 첨단3지구 A6BL | 반도체·AI산업단지 곁 638세대, 예상 프리미엄 -8,200만",
    date: "2026-09-25",
    dateLabel: "2026. 9. 25",
    url: "posts/jeil-punggyeongchae-cheomdan3-a6bl.html",
    preview: `
      <p>광주 북구 월출동, 광주연구개발특구 첨단3지구의 사실상 마지막 민간분양인 제일풍경채 첨단3지구 A6블록은 제일건설이 시공하는 638세대 규모의 단지입니다. 반도체·AI 국가산업단지가 인근에 조성되고 있어 견본주택에 사흘간 1만 8,000명이 몰렸습니다.</p>
      <p>브동산이 같은 북구 첨단2지구의 중흥S클래스·첨단자이2차 두 단지의 84㎡ 가격을 입지·브랜드·연식 차이만큼 보정해 산출한 적정가는 4.07억원으로, 실제 분양가(4.89억원)보다 약 20% 높았습니다(고평가 신호). 정당계약 후 638세대 중 187세대가 무순위로 다시 공급됐다는 점도 함께 봐야 합니다.</p>
    `
  },
  {
    id: "forena-hillstate-jinju",
    category: "realestate",
    region: "경남",
    tag: "청약 언박싱 No.020",
    title: "경남 - 포레나힐스테이트 진주 | 이현동 21년 만의 재건축 1,032세대, 예상 프리미엄 +3천만",
    date: "2026-09-25",
    dateLabel: "2026. 9. 25",
    url: "posts/forena-hillstate-jinju.html",
    preview: `
      <p>경남 진주시 이현동, 이현1-5구역을 재건축하는 포레나힐스테이트 진주는 한화 건설부문과 현대건설이 함께 짓는 1,032세대 규모의 단지입니다. 진주 첫 대형 건설사 컨소시엄이자, 이현동에는 21년 만에 공급되는 신규 분양입니다.</p>
      <p>브동산이 같은 남강 이북 생활권인 초전동의 더샵 진주피에르테·힐스테이트 초전 두 단지의 84㎡ 가격을 입지·브랜드·연식 차이만큼 보정해 산출한 적정가는 6.03억원으로, 실제 분양가(84A 최고가 5.77억원)보다 약 5% 낮았습니다. 실제 1순위 청약은 평균 21.2대 1을 기록했지만, 모형상 가격 메리트는 크지 않아 흥행은 희소성·브랜드 영향이 큰 것으로 풀이됩니다.</p>
    `
  },
  {
    id: "brownstone-wolgok-central",
    category: "realestate",
    region: "서울",
    tag: "청약 언박싱 No.019",
    title: "서울 - 브라운스톤 월곡 센트럴 | 트리플역세권 품은 소규모재건축 145세대, 예상 프리미엄 +4.7억",
    date: "2026-09-25",
    dateLabel: "2026. 9. 25",
    url: "posts/brownstone-wolgok-central.html",
    preview: `
      <p>서울 성북구 하월곡동, 동신아파트를 소규모재건축한 브라운스톤 월곡 센트럴은 이수건설이 시공하는 145세대 규모의 단지입니다. 6호선 월곡역이 단지 바로 앞, 4호선 미아사거리역도 도보권인 트리플역세권이 강점입니다.</p>
      <p>브동산이 같은 성북구 장위동의 꿈의숲 아이파크·래미안 장위 포레카운티 두 브랜드 단지의 59㎡ 가격을 입지·브랜드·연식 차이만큼 보정해 산출한 적정가는 13.60억원으로, 실제 분양가(8.91억원)보다 약 53% 낮았습니다. 실제 1순위 청약도 62대 1의 높은 경쟁률을 기록해, 모형과 시장 반응이 같은 방향을 가리켰습니다.</p>
    `
  },
  {
    id: "changwon-hanshin-thehue",
    category: "realestate",
    region: "경남",
    tag: "청약 언박싱 No.017",
    title: "경남 - 창원 한신더휴 메가센텀 | 마산 20년 만의 2,016세대 재개발 랜드마크, 예상 프리미엄 +7천만",
    date: "2026-09-25",
    dateLabel: "2026. 9. 25",
    url: "posts/changwon-hanshin-thehue.html",
    preview: `
      <p>경남 창원시 마산회원구 회원동, 회원2구역 주택재개발정비사업으로 공급되는 '창원 한신더휴 메가센텀'은 지하 3층~지상 최고 27층, 21개 동, 총 2,016세대(일반분양 1,139세대) 규모다. 한신공영의 '한신더휴' 브랜드가 적용됐으며, 마산회원구에 20년 만에 들어서는 2,000세대급 대단지라는 점이 가장 큰 특징이다.</p>
      <p>같은 마산회원구에서 이미 입주를 마친 창원롯데캐슬센텀골드·창원메트로시티석전 두 단지의 전용 84㎡ 가격을 입지·브랜드·연식 차이만큼 보정해 브동산 모형으로 산출한 적정가는 6.59억원, 실제 분양가(84㎡ 가중평균) 5.93억원 대비 약 11%(+7천만원) 저평가 신호다. 다만 정당계약 이후 일반분양의 약 38%(430세대)가 무순위로 남아 다시 공급됐다는 점은 함께 봐야 한다.</p>
    `
  },
  {
    id: "cityociel-9danji",
    category: "realestate",
    region: "인천",
    tag: "청약 언박싱 No.016",
    title: "인천 - 시티오씨엘 9단지 오션파크뷰 | 용현학익 미니신도시 마지막 퍼즐 1,949세대, 예상 프리미엄 +2천만",
    date: "2026-09-25",
    dateLabel: "2026. 9. 25",
    url: "posts/cityociel-9danji.html",
    preview: `
      <p>인천 미추홀구 학익동, DCRE가 폐석회 공장 부지를 개발해 온 '용현·학익 1블록' 도시개발사업(시티오씨엘)의 사실상 마지막 분양 단지다. 1단지부터 8단지까지 이어진 1군 컨소시엄(HDC현대산업개발·현대건설·포스코이앤씨) 미니신도시의 마지막 퍼즐답게 총 1,949세대 규모로 지어진다.</p>
      <p>브동산은 같은 개발지구 안에서 이미 입주를 마친 두 개의 자매 단지 — 1단지와 3단지 — 의 전용 84㎡ 가격을 입지·연식 차이만큼 보정해 적정가를 산출했다. 결과는 약 3% 저평가(+2천만원) 신호지만, 2026년 9월 1순위 청약이 대규모 미달로 마감된 만큼 가격 수용성 리스크도 함께 봐야 한다.</p>
    `
  },
  {
    id: "grandlac-eileen-ddeul",
    category: "realestate",
    region: "울산",
    tag: "청약 언박싱 No.015",
    title: "울산 - 그랑라크 에일린의 뜰 | 선암호수공원 품은 남구 최대 재개발 1,521세대, 예상 프리미엄 +9천만",
    date: "2026-09-24",
    dateLabel: "2026. 9. 24",
    url: "posts/grandlac-eileen-ddeul.html",
    preview: `
      <p>울산 남구 야음1동 일대, 남구비14구역 주택재개발정비사업으로 조성되는 1,521세대 대단지다. 전용 39~102㎡ 8개 타입 중 가장 물량이 많은 전용 84㎡(709세대)를 기준으로 브동산이 적정가를 산출했다.</p>
      <p>브동산 모형상 적정가는 8.14억원으로, 실제 분양가 평균(7.26억원) 대비 예상 프리미엄은 +9천만원이다. 브동산 판정은 저평가다. 다만 울산에 지하철이 없어 교통 입지가 제한적이고, 인접 B-04구역에 래미안 브랜드의 1,441세대 대단지가 뒤이어 예정돼 있다는 점은 유의할 변수다.</p>
    `
  },
  {
    id: "yeoju-station-thesharp-thefirst",
    category: "realestate",
    region: "경기",
    tag: "청약 언박싱 No.014",
    title: "경기 - 더샵 여주역더퍼스트 | 여주 첫 더샵, 84㎡ 단일평형 696세대, 예상 프리미엄 -1,373만",
    date: "2026-09-24",
    dateLabel: "2026. 9. 24",
    url: "posts/yeoju-station-thesharp-thefirst.html",
    preview: `
      <p>경기도 여주시 홍문동 홍문2지구에 들어서는 696세대 규모의 단지로, 포스코이앤씨의 '더샵' 브랜드가 여주·이천 권역에 처음 공급된다. 전 세대가 전용 84㎡ 단일면적(84A·84B·84C)으로만 구성되며, 이름과 달리 경강선 여주역과는 직선거리 약 1㎞ 떨어져 있다는 점이 눈여겨볼 지점이다.</p>
      <p>브동산은 같은 여주시의 완공 단지(여주아이파크)와 인근 준공예정 단지(여주역자이헤리티지)의 84㎡ 가격을 입지·브랜드·연식 차이만큼 보정해 적정가 약 4.90억원을 산출했다. 실제 분양가 평균(약 5.04억원) 대비 약 3% 고평가 신호로, 사실상 오차범위 안쪽이다.</p>
    `
  },
  {
    id: "cheonan-ipark-city-4danji",
    category: "realestate",
    region: "충남",
    tag: "청약 언박싱 No.013",
    title: "충남 - 천안 아이파크시티 4단지 | 성성호수공원 곁 부성역(예정) 250m 818세대, 예상 프리미엄 -734만",
    date: "2026-09-24",
    dateLabel: "2026. 9. 24",
    url: "posts/cheonan-ipark-city-4danji.html",
    preview: `
      <p>충남 천안시 서북구 부대동, 성성호수공원을 곁에 둔 '천안 아이파크시티' 브랜드타운의 마지막 퍼즐인 3·4단지 중 4단지다. 818세대(일반분양 777세대) 규모로 HDC현대산업개발의 '아이파크'가 시공을 맡았고, 부성역(수도권전철 1호선 연장, 예정)에서 약 250m 거리라는 입지가 강점이다.</p>
      <p>브동산이 같은 서북구 성성동의 완공된 두 단지(천안푸르지오레이크사이드·천안레이크타운3차푸르지오)의 84㎡ 가격을 보정해 산출한 적정가는 5.69억원, 실제 분양가 평균은 5.76억원으로 예상 프리미엄은 -734만에 그친다. 브동산 판정은 적정이다. 다만 실제 1순위 청약은 평균 경쟁률 0.17:1로 전 타입이 미달됐다.</p>
    `
  },
  {
    id: "godeok-hillstate-elist-a65bl",
    category: "realestate",
    region: "경기",
    tag: "청약 언박싱 No.012",
    title: "경기 - 힐스테이트 고덕엘리스트 A65BL | 평택 고덕국제신도시 분상제 84㎡ 단일평형 837세대, 예상 프리미엄 +1.7억",
    date: "2026-09-24",
    dateLabel: "2026. 9. 24",
    url: "posts/godeok-hillstate-elist-a65bl.html",
    preview: `
      <p>평택 고덕국제신도시 A65블록에 들어서는 837세대 규모의 공공분양 단지다. 분양가상한제가 적용되고 전 세대가 전용 84㎡ 단일평형으로만 구성된 것이 특징이며, 브동산은 같은 고덕동 안에서 이미 준공된 두 단지의 가격을 보정해 적정가를 직접 산출해봤다.</p>
      <p>브동산 모형상 적정가는 약 7.16억원으로, 실제 분양가 평균(5.50억원)보다 약 1.7억원, 30% 가량 저평가된 것으로 나타났다. 다만 두 비교단지(2019년 준공 포레스트자이·2024년 준공 힐스테이트 고덕센트럴)의 가격 격차가 이례적으로 커 이 저평가 신호는 참고용으로 보는 게 안전하다.</p>
    `
  },
  {
    id: "munsuro-vista-the-park",
    category: "realestate",
    region: "울산",
    tag: "청약 언박싱 No.010",
    title: "울산 - 문수로 비스타 더파크 | 삼호산 조망 숲세권 신축 700세대, 예상 프리미엄 -1,909만",
    date: "2026-09-24",
    dateLabel: "2026. 9. 24",
    url: "posts/munsuro-vista-the-park.html",
    preview: `
      <p>문수로 비스타 더파크는 울산 남구 무거삼호지구 11블록에 동원개발이 짓는 700세대 신축 아파트다. 9월 22~23일 청약을 마치고 당첨자 발표를 기다리는 이 단지의 전용 84㎡ 분양가(평균 8.07억)를, 같은 남구 안 비교단지 2곳의 시세와 견줘 보면 브동산 적정가는 7.88억 — 예상 프리미엄은 -1,909만으로, 고평가도 저평가도 아닌 오차범위 안쪽이다.</p>
      <p>삼호산 조망을 살린 전 세대 유리난간과 삼성물산 에버스케이프 조경이 강점이지만, 시공사는 중견 등급(동원개발)이고 같은 무거동 생활권에 비슷한 시기 입주하는 경쟁 단지가 약 2,096세대나 몰려 있다는 점은 실거주 목적이 아니라면 감안해야 할 리스크다.</p>
    `
  },
  {
    id: "jinju-panmun-lakesummit-wellga",
    category: "realestate",
    region: "경남",
    tag: "청약 언박싱 No.009",
    title: "경남 - 진주 판문지구 레이크써밋 웰가 | 진양호를 품은 690세대, 예상 프리미엄 +1.1억",
    date: "2026-09-24",
    dateLabel: "2026. 9. 24",
    url: "posts/jinju-panmun-lakesummit-wellga.html",
    preview: `
      <p>진양호를 남쪽으로 낀 진주 판문지구, 흥한주택종합건설의 690세대 '레이크써밋 웰가'. 브동산 적정가(84㎡) 6.4억원 · 실제 분양가 평균 5.3억원 — 예상 프리미엄 +1.1억 신호가 나왔지만, 비교단지 간 편차가 커 해석에는 유의가 필요합니다. 브동산 판정은 저평가입니다.</p>
      <p>특별공급은 9월 28일부터 시작되며, 세대당 1.88대의 넉넉한 주차와 27층 스카이라운지의 진양호 조망이 특징입니다. 다만 진주 전역이 공통으로 안고 있는 철도·지하철 접근성의 한계도 함께 짚어봤습니다.</p>
    `
  },
  {
    id: "ssangyong-the-platinum-centum",
    category: "realestate",
    region: "부산",
    tag: "청약 언박싱 No.008",
    title: "부산 - 쌍용 더 플래티넘 센텀 | 지역주택조합 490세대, 예상 프리미엄 -4.1억",
    date: "2026-09-23",
    dateLabel: "2026. 9. 23",
    url: "posts/ssangyong-the-platinum-centum.html",
    preview: `
      <p>부산 수영구 망미동, 지역주택조합 방식으로 짓는 490세대 쌍용건설 '더 플래티넘' 브랜드. 브동산 적정가(84㎡) 8.46억원 · 실제 분양가 평균 12.6억원 — 예상 프리미엄 -4.1억(약 49%)이라는 이례적으로 큰 폭의 고평가 신호가 나왔습니다.</p>
      <p>망미초등학교 바로 앞 초품아 입지와 센텀 생활권 인프라는 강점이지만, 공식 홍보와 달리 망미역까지 약 790m로 역세권이라 보기엔 애매하고 배산역은 도보권 밖입니다. 특별공급은 9월 28일부터 시작됩니다.</p>
    `
  },
  {
    id: "marketing-is-brand-management",
    category: "brand",
    tag: "브랜드 언박싱 No.002",
    title: "마케팅은 브랜드 관리다 — 세스 고딘의 40년 마케팅론을 관통하는 결론 하나",
    date: "2026-09-23",
    dateLabel: "2026. 9. 23",
    url: "posts/marketing-is-brand-management.html",
    preview: `
      <p>마케팅과 브랜딩은 정말 다른 일일까. 세스 고딘의 책 네 권을 20년 순서대로 읽으며 확인해 봤다. 단어는 책마다 달랐는데, 결과는 의외로 단순했다.</p>
    `
  },
  {
    id: "gwangmyeong-city-pradium-eduheim",
    category: "realestate",
    region: "경기",
    tag: "청약 언박싱 No.007",
    title: "경기 - 광명 시티프라디움 에듀하임 | 구름산지구 A6블록, 예상 프리미엄 -930만",
    date: "2026-09-23",
    dateLabel: "2026. 9. 23",
    url: "posts/gwangmyeong-city-pradium-eduheim.html",
    preview: `
      <p>광명 구름산지구 A6블록에 들어서는 시티건설의 426세대, 광명 시티프라디움 에듀하임. 브동산 적정가(84㎡) 11.21억원 · 실제 분양가 평균 11.3억원 — 예상 프리미엄 -930만으로 사실상 무피 수준입니다. 브동산 판정은 적정입니다.</p>
      <p>특별공급은 9월 29일부터 시작되며, "서울 옆세권" 마케팅과 달리 실제로는 도보권 지하철역이 없는 도로교통 중심 입지라는 점이 눈에 띕니다.</p>
    `
  },
  {
    id: "hwaseo-lakepark-honorsville",
    category: "realestate",
    region: "경기",
    tag: "청약 언박싱 No.005",
    title: "경기 - 화서역 호수공원 아너스빌 | 수원시 유일 비규제지역, 예상 프리미엄 +1200만",
    date: "2026-09-13",
    dateLabel: "2026. 9. 13",
    url: "posts/hwaseo-lakepark-honorsville.html",
    preview: `
      <p>서호공원·여기산공원을 마주한 수원시 유일 비규제지역 청약, 화서역 호수공원 아너스빌. 브동산 적정가(84㎡) 8.62억원 · 실제 분양가 평균(추정) 8.5억원 — 예상 프리미엄 +0.12억 신호가 나왔지만, 해석에는 유의가 필요합니다. 브동산 판정은 적정입니다.</p>
      <p>9월 22~23일 청약을 앞두고 있으며, 탑동 이노베이션밸리·수원 R&D사이언스파크 등 권선구 개발 호재와 함께 대출·전매 규제에서 자유로운 비규제지역이라는 점이 특징입니다.</p>
    `
  },
  {
    id: "mokdong-yunseulxi",
    category: "realestate",
    region: "서울",
    tag: "청약 언박싱 No.004",
    title: "서울 - 목동 윤슬자이 | 오목교역 초역세권 하이엔드 오피스텔, 예상 프리미엄 +4.8억",
    date: "2026-09-13",
    dateLabel: "2026. 9. 13",
    url: "posts/mokdong-yunseulxi.html",
    preview: `
      <p>오목교역(5호선) 도보권, 등기상 오피스텔이지만 전용 114~203㎡ 중대형 위주라 사실상 아파트에 가까운 목동 윤슬자이. 브동산 적정가(114㎡≈84㎡ 환산) 34.37억원 · 실제 분양가 평균(가중평균) 29.6억원 — 예상 프리미엄 +4.8억 신호가 나왔지만, 해석에는 유의가 필요합니다. 브동산 판정은 저평가입니다.</p>
      <p>9월 3일 모집공고를 시작으로 이미 당첨자 발표까지 끝나 9월 13~14일 정당계약이 진행 중이며, 조선호텔앤리조트가 위탁 운영하는 웰니스 클럽과 47층 스카이 커뮤니티가 특징입니다.</p>
    `
  },
  {
    id: "brand-is-not-the-hero",
    category: "brand",
    tag: "브랜드 언박싱 No.001",
    title: "브랜드가 사라져야 광고가 산다 — 나이키부터 아파트 광고까지, 좋은 광고 12편의 공통점",
    date: "2026-09-13",
    dateLabel: "2026. 9. 13",
    url: "posts/brand-is-not-the-hero.html",
    preview: `
      <p>나이키 광고에서 기억나는 건 신발이 아니라 길을 달리던 소년이다. 오래 남는 광고는 왜 제품 얘기를 안 할까. 유명 광고 5편과 주거 광고 7편을 “이 광고의 주인공은 누구인가”라는 질문 하나로 다시 봤다.</p>
    `
  },
  {
    id: "jeongja-thesharp-bundanghighest",
    category: "realestate",
    region: "경기",
    tag: "청약 언박싱 No.003",
    title: "경기 - 더샵 분당하이스트 | 정자역 리모델링 대장주, 예상 프리미엄 +9천만",
    date: "2026-09-12",
    dateLabel: "2026. 9. 12",
    url: "posts/jeongja-thesharp-bundanghighest.html",
    preview: `
      <p>정자역(신분당선·수인분당선) 도보 약 500m, 리모델링으로 143세대를 새로 공급하는 더샵 분당하이스트. 브동산 적정가(84㎡) 27.36억원 · 실제 분양가 평균(추정) 26.5억원 — 예상 프리미엄 +9천만으로 격차는 크지 않습니다. 브동산 판정은 저평가입니다.</p>
      <p>9월 22~23일 청약을 앞두고 있으며, 분당·수지권은 향후 3년간 신규 입주물량이 사실상 이 단지와 더샵분당티에르원뿐인 공급 절벽 구간입니다.</p>
    `
  },
  {
    id: "sangdong-lottecastle-signature",
    category: "realestate",
    region: "경기",
    tag: "청약 언박싱 No.002",
    title: "경기 - 상동역 롯데캐슬 시그니처 | 7호선 초역세권 대단지, 예상 프리미엄 -2,976만",
    date: "2026-08-27",
    dateLabel: "2026. 8. 27",
    url: "posts/sangdong-lottecastle-signature.html",
    preview: `
      <p>공식 분양 정보만으로는 "비싸다/싸다"를 판단하기 어렵습니다. 브동산은 같은 84㎡ 타입 기준으로 인근 준공 단지의 KB시세를 입지·브랜드·연식 차이만큼 보정해 이 단지의 적정가를 직접 산출합니다.</p>
      <p>브동산 적정가(84㎡) 14.90억원 · 실제 분양가 평균 15.2억원 — 예상 프리미엄 -2,980만으로 나타났습니다. 브동산 판정은 적정입니다.</p>
      <p>청약 성적은 일반공급 평균 1.68대 1. 국민평형(84㎡) 6개 타입 중 일부는 미달권까지 발생했는데, 그 이유는 본문에서 자세히 다룹니다.</p>
    `
  },
  {
    id: "geomam-prugio-pravenue",
    category: "realestate",
    region: "인천",
    tag: "청약 언박싱 No.001",
    title: "인천 - 검암역 푸르지오 프라베뉴 | 더블역세권 공공분양, 예상 프리미엄 -1,554만",
    date: "2026-08-30",
    dateLabel: "2026. 8. 30",
    url: "posts/geomam-prugio-pravenue.html",
    preview: `
      <p>공식 분양 정보만으로는 "비싸다/싸다"를 판단하기 어렵습니다. 브동산은 같은 84㎡ 타입 기준으로 인근 준공 단지의 시세를 입지·브랜드·연식 차이만큼 보정해 이 단지의 적정가를 직접 산출합니다.</p>
      <p>인천 서구 검암동 공공주택지구, 441세대 규모의 민간참여 공공분양(분양가상한제 적용). 브동산 적정가(84㎡) 5.99억원 · 실제 분양가 평균 6.15억원 — 예상 프리미엄 -1,550만입니다. 브동산 판정은 고평가입니다.</p>
    `
  }
];
