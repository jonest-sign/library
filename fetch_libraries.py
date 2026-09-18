import os
import urllib.parse
import requests

DATA4_KEY = os.environ.get("DATA4LIBRARY_AUTH_KEY", "").strip()
PORTAL_KEY = os.environ.get("PUBLIC_DATA_API_KEY", "").strip()


def fetch_library_data():
    # 1. 도서관 정보나루 시도
    api_key = DATA4_KEY or PORTAL_KEY
    if api_key:
        print("[1] 도서관 정보나루 API 호출 시도...")
        url = "http://data4library.kr/api/libSrch"
        params = {
            "authKey": api_key,
            "pageNo": "1",
            "pageSize": "50",
            "format": "json",
        }
        try:
            res = requests.get(url, params=params, timeout=10)
            if res.status_code == 200:
                data = res.json()
                libs = data.get("response", {}).get("libs", [])
                if libs:
                    print(f"도서관 정보나루 {len(libs)}개 수집 완료")
                    return [
                        {
                            "name": it["lib"].get("libName", "-"),
                            "address": it["lib"].get("address", "-"),
                            "tel": it["lib"].get("tel", "-"),
                            "closed": it["lib"].get("closed", "정보 없음"),
                            "homepage": it["lib"].get("homepage", ""),
                        }
                        for it in libs
                    ]
            print(f"정보나루 응답: {res.text[:150]}")
        except Exception as e:
            print(f"정보나루 통신 오류: {e}")

    # 2. 공공데이터포털 시도
    portal_key = PORTAL_KEY or DATA4_KEY
    if portal_key:
        print("[2] 공공데이터포털 API 호출 시도...")
        decoded = urllib.parse.unquote(portal_key)
        url = "http://api.data.go.kr/openapi/tn_pubr_public_lbrry_api"
        params = {
            "serviceKey": decoded,
            "pageNo": "1",
            "numOfRows": "50",
            "type": "json",
        }
        try:
            res = requests.get(url, params=params, timeout=10)
            if res.status_code == 200:
                items = (
                    res.json()
                    .get("response", {})
                    .get("body", {})
                    .get("items", [])
                )
                if items:
                    print(f"공공데이터포털 {len(items)}개 수집 완료")
                    return [
                        {
                            "name": it.get("lbrryNm", "-"),
                            "address": it.get("rdnmadr", it.get("lnmadr", "-")),
                            "tel": it.get("phoneNumber", "-"),
                            "closed": it.get("rstde", "정보 없음"),
                            "homepage": it.get("homepageUrl", ""),
                        }
                        for it in items
                    ]
            print(f"공공데이터 응답: {res.text[:150]}")
        except Exception as e:
            print(f"공공데이터 통신 오류: {e}")

    # 3. API 키 활성화 대기 중 임시 기본 공공도서관 데이터셋 제공 (블로그 공백 방지)
    print("API 미활성화 상태 -> 기본 전국 대표 도서관 데이터셋 로드")
    return [
        {
            "name": "국립중앙도서관",
            "address": "서울특별시 서초구 반포대로 201",
            "tel": "02-590-0500",
            "closed": "매월 둘째·넷째 월요일, 공휴일",
            "homepage": "https://www.nl.go.kr",
        },
        {
            "name": "국회도서관",
            "address": "서울특별시 영등포구 의사당대로 1",
            "tel": "02-6788-4211",
            "closed": "매월 둘째·넷째 토요일, 일요일 제외 법정공휴일",
            "homepage": "https://www.nanet.go.kr",
        },
        {
            "name": "서울도서관",
            "address": "서울특별시 중구 세종대로 110",
            "tel": "02-2133-0300",
            "closed": "매주 월요일, 법정공휴일",
            "homepage": "https://lib.seoul.go.kr",
        },
        {
            "name": "경기도립중앙도서관",
            "address": "경기도 수원시 장안구 조원로 18",
            "tel": "031-240-4000",
            "closed": "매주 월요일, 국가공휴일",
            "homepage": "https://www.gelib.or.kr",
        },
        {
            "name": "성남시립중앙도서관",
            "address": "경기도 성남시 분당구 야탑로 98",
            "tel": "031-729-4331",
            "closed": "매주 월요일, 신정·설·추석연휴",
            "homepage": "https://snlib.go.kr/ct",
        },
        {
            "name": "용인시립수지도서관",
            "address": "경기도 용인시 수지구 문정로7번길 15",
            "tel": "031-324-4751",
            "closed": "매월 둘째·넷째 월요일, 법정공휴일",
            "homepage": "https://lib.yongin.go.kr/suji",
        },
        {
            "name": "광주시립중앙도서관",
            "address": "경기도 광주시 문화로 102",
            "tel": "031-760-5697",
            "closed": "매주 월요일, 공휴일",
            "homepage": "https://lib.gjcity.go.kr",
        },
        {
            "name": "인천광역시 미추홀도서관",
            "address": "인천광역시 남동구 인주대로776번길 53",
            "tel": "032-440-6600",
            "closed": "매주 월요일, 일요일 제외 법정공휴일",
            "homepage": "https://www.michuhollib.go.kr",
        },
        {
            "name": "부산도서관",
            "address": "부산광역시 사상구 사상로310번길 33",
            "tel": "051-310-5400",
            "closed": "매주 월요일, 법정공휴일",
            "homepage": "https://library.busan.go.kr",
        },
        {
            "name": "대구광역시립중앙도서관",
            "address": "대구광역시 중구 국채보상로 670",
            "tel": "053-231-2000",
            "closed": "매월 첫째·셋째 월요일, 법정공휴일",
            "homepage": "https://library.daegu.go.kr/jungang",
        },
        {
            "name": "대전광역시 한밭도서관",
            "address": "대전광역시 중구 서문로 107",
            "tel": "042-270-7420",
            "closed": "매주 월요일, 국가지정공휴일",
            "homepage": "https://www.daejeon.go.kr/hanbatlib",
        },
        {
            "name": "광주광역시립무등도서관",
            "address": "광주광역시 북구 면앙로 130",
            "tel": "062-613-5353",
            "closed": "매주 월요일, 일요일 제외 공휴일",
            "homepage": "https://citylib.gwangju.kr",
        },
    ]


def generate_html(libs):
    rows = ""
    for lib in libs:
        hp = lib["homepage"]
        link = (
            f'<a href="{hp}" target="_blank" rel="noopener" style="display:inline-block;padding:5px 12px;background:#1971c2;color:#ffffff!important;text-decoration:none;border-radius:4px;font-size:12px;font-weight:bold;">홈페이지</a>'
            if hp
            else "-"
        )
        rows += f"""
        <tr style="border-bottom: 1px solid #e9ecef;">
            <td style="padding: 12px 10px; font-weight: bold; color: #212529;">{lib['name']}</td>
            <td style="padding: 12px 10px; color: #495057;">{lib['address']}</td>
            <td style="padding: 12px 10px; color: #495057;">{lib['tel']}</td>
            <td style="padding: 12px 10px;"><span style="display:inline-block;padding:3px 8px;background:#ffe3e3;color:#c92a2a;border-radius:4px;font-size:12px;font-weight:600;">{lib['closed']}</span></td>
            <td style="padding: 12px 10px; text-align: center;">{link}</td>
        </tr>
        """

    return f"""
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, "Malgun Gothic", dotum, sans-serif; margin: 0; padding: 10px; background: #fff; }}
            .tbl-wrap {{ width: 100%; overflow-x: auto; box-shadow: 0 1px 3px rgba(0,0,0,0.08); border-radius: 6px; border: 1px solid #dee2e6; }}
            table {{ width: 100%; border-collapse: collapse; min-width: 650px; font-size: 14px; text-align: left; }}
            th {{ background: #f8f9fa; color: #343a40; padding: 12px 10px; font-weight: 700; border-bottom: 2px solid #dee2e6; }}
            tr:hover {{ background-color: #f1f3f5; }}
        </style>
    </head>
    <body>
        <div class="tbl-wrap">
            <table>
                <thead>
                    <tr>
                        <th style="width: 22%;">도서관명</th>
                        <th style="width: 38%;">주소</th>
                        <th style="width: 15%;">전화번호</th>
                        <th style="width: 15%;">정기 휴관일</th>
                        <th style="width: 10%; text-align:center;">바로가기</th>
                    </tr>
                </thead>
                <tbody>
                    {rows}
                </tbody>
            </table>
        </div>
    </body>
    </html>
    """


if __name__ == "__main__":
    libs = fetch_library_data()
    print(f"최종 처리 건수: {len(libs)}개")
    html_output = generate_html(libs)
    with open("library_list.html", "w", encoding="utf-8") as f:
        f.write(html_output)
    print("library_list.html 갱신 완료")
