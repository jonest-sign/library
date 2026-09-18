import os
import urllib.parse
import requests

# 환경변수에서 키 가져오기
DATA4_KEY = os.environ.get("DATA4LIBRARY_AUTH_KEY", "").strip()
PORTAL_KEY = os.environ.get("PUBLIC_DATA_API_KEY", "").strip()


def fetch_library_data():
    # 1. 공공데이터포털 (data.go.kr) 시도
    api_key = PORTAL_KEY or DATA4_KEY
    if api_key:
        print("[1] 공공데이터포털 API 호출 시도...")
        decoded_key = urllib.parse.unquote(api_key)
        url = "http://api.data.go.kr/openapi/tn_pubr_public_lbrry_api"
        params = {
            "serviceKey": decoded_key,
            "pageNo": "1",
            "numOfRows": "50",
            "type": "json",
        }
        try:
            res = requests.get(url, params=params, timeout=15)
            print(f"공공데이터 상태코드: {res.status_code}")
            if res.status_code == 200:
                data = res.json()
                items = (
                    data.get("response", {})
                    .get("body", {})
                    .get("items", [])
                )
                if items:
                    print(f"공공데이터포털에서 {len(items)}개 수집 성공!")
                    result = []
                    for it in items:
                        result.append({
                            "name": it.get("lbrryNm", "-"),
                            "address": it.get(
                                "rdnmadr", it.get("lnmadr", "-")
                            ),
                            "tel": it.get("phoneNumber", "-"),
                            "closed": it.get("rstde", "정보 없음"),
                            "homepage": it.get("homepageUrl", ""),
                        })
                    return result
            print(f"공공데이터포털 응답 내용: {res.text[:200]}")
        except Exception as e:
            print(f"공공데이터포털 요청 중 예외: {e}")

    # 2. 도서관 정보나루 (data4library.kr) 시도
    naru_key = DATA4_KEY or PORTAL_KEY
    if naru_key:
        print("[2] 도서관 정보나루 API 호출 시도...")
        url = "http://data4library.kr/api/libSrch"
        params = {
            "authKey": naru_key,
            "pageNo": "1",
            "pageSize": "50",
            "format": "json",
        }
        try:
            res = requests.get(url, params=params, timeout=15)
            print(f"정보나루 상태코드: {res.status_code}")
            if res.status_code == 200:
                data = res.json()
                libs = data.get("response", {}).get("libs", [])
                if libs:
                    print(f"도서관 정보나루에서 {len(libs)}개 수집 성공!")
                    result = []
                    for item in libs:
                        lib = item.get("lib", {})
                        result.append({
                            "name": lib.get("libName", "-"),
                            "address": lib.get("address", "-"),
                            "tel": lib.get("tel", "-"),
                            "closed": lib.get("closed", "정보 없음"),
                            "homepage": lib.get("homepage", ""),
                        })
                    return result
            print(f"도서관 정보나루 응답 내용: {res.text[:200]}")
        except Exception as e:
            print(f"정보나루 요청 중 예외: {e}")

    return []


def generate_html(libs):
    rows = ""
    for lib in libs:
        hp = lib["homepage"]
        link = (
            f'<a href="{hp}" target="_blank" rel="noopener" style="display:inline-block;padding:4px 8px;background:#228be6;color:#fff;text-decoration:none;border-radius:4px;font-size:12px;">바로가기</a>'
            if hp
            else "-"
        )
        rows += f"""
        <tr>
            <td style="padding:10px;border:1px solid #dee2e6;font-weight:bold;">{lib['name']}</td>
            <td style="padding:10px;border:1px solid #dee2e6;">{lib['address']}</td>
            <td style="padding:10px;border:1px solid #dee2e6;">{lib['tel']}</td>
            <td style="padding:10px;border:1px solid #dee2e6;"><span style="background:#ffe3e3;color:#c92a2a;padding:2px 6px;border-radius:4px;font-size:12px;">{lib['closed']}</span></td>
            <td style="padding:10px;border:1px solid #dee2e6;text-align:center;">{link}</td>
        </tr>
        """

    if not rows:
        rows = '<tr><td colspan="5" style="text-align:center;padding:30px;color:#888;">도서관 데이터를 불러오지 못했습니다. API 키 및 요청을 확인하세요.</td></tr>'

    return f"""
    <div style="width:100%;overflow-x:auto;font-family:-apple-system,BlinkMacSystemFont,sans-serif;margin:20px 0;">
        <table style="width:100%;border-collapse:collapse;min-width:650px;font-size:14px;">
            <thead>
                <tr style="background:#f1f3f5;color:#333;">
                    <th style="padding:12px 10px;border:1px solid #dee2e6;text-align:left;">도서관명</th>
                    <th style="padding:12px 10px;border:1px solid #dee2e6;text-align:left;">주소</th>
                    <th style="padding:12px 10px;border:1px solid #dee2e6;text-align:left;">전화번호</th>
                    <th style="padding:12px 10px;border:1px solid #dee2e6;text-align:left;">정기 휴관일</th>
                    <th style="padding:12px 10px;border:1px solid #dee2e6;text-align:center;">홈페이지</th>
                </tr>
            </thead>
            <tbody>
                {rows}
            </tbody>
        </table>
    </div>
    """


if __name__ == "__main__":
    libs = fetch_library_data()
    print(f"최종 처리 건수: {len(libs)}개")
    html_output = generate_html(libs)
    with open("library_list.html", "w", encoding="utf-8") as f:
        f.write(html_output)
    print("library_list.html 저장 완료")
