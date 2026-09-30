import os
import time
import urllib.parse
import requests

DATA4_KEY = os.environ.get("DATA4LIBRARY_AUTH_KEY", "").strip()
PORTAL_KEY = os.environ.get("PUBLIC_DATA_API_KEY", "").strip()


def fetch_all_libraries():
    """전국 도서관 전체 데이터를 페이지네이션으로 전수 수집"""
    api_key = DATA4_KEY or PORTAL_KEY
    all_libraries = []

    # 1. 도서관 정보나루 (data4library.kr) 전수 수집 시도
    if DATA4_KEY:
        print("[도서관 정보나루] 전국 전수 데이터 수집 시작...")
        page_no = 1
        page_size = 500  # 한 번에 최대한 많이 호출

        while True:
            url = "http://data4library.kr/api/libSrch"
            params = {
                "authKey": DATA4_KEY,
                "pageNo": str(page_no),
                "pageSize": str(page_size),
                "format": "json",
            }
            try:
                res = requests.get(url, params=params, timeout=15)
                if res.status_code == 200:
                    data = res.json()
                    libs = data.get("response", {}).get("libs", [])
                    if not libs:
                        break  # 더 이상 데이터가 없으면 루프 종료

                    for item in libs:
                        lib = item.get("lib", {})
                        all_libraries.append({
                            "name": lib.get("libName", "-"),
                            "address": lib.get("address", "-"),
                            "tel": lib.get("tel", "-"),
                            "closed": lib.get("closed", "정보 없음"),
                            "homepage": lib.get("homepage", ""),
                        })

                    print(
                        f"정보나루 {page_no}페이지 수집 완료 (누적: {len(all_libraries)}개)"
                    )

                    # 마지막 페이지 도달 확인
                    total_count = data.get("response", {}).get("resultNum", 0)
                    if len(all_libraries) >= total_count or len(libs) < page_size:
                        break

                    page_no += 1
                    time.sleep(0.2)  # API 서버 보호를 위한 미세 딜레이
                else:
                    print(f"정보나루 응답 실패: {res.status_code}")
                    break
            except Exception as e:
                print(f"정보나루 통신 중 오류: {e}")
                break

        if all_libraries:
            return all_libraries

    # 2. 공공데이터포털(data.go.kr) 전수 수집 시도 (정보나루 실패 시 보조)
    if PORTAL_KEY:
        print("[공공데이터포털] 전국 전수 데이터 수집 시작...")
        decoded_key = urllib.parse.unquote(PORTAL_KEY)
        page_no = 1
        num_of_rows = 500

        while True:
            url = "http://api.data.go.kr/openapi/tn_pubr_public_lbrry_api"
            params = {
                "serviceKey": decoded_key,
                "pageNo": str(page_no),
                "numOfRows": str(num_of_rows),
                "type": "json",
            }
            try:
                res = requests.get(url, params=params, timeout=15)
                if res.status_code == 200:
                    body = (
                        res.json()
                        .get("response", {})
                        .get("body", {})
                    )
                    items = body.get("items", [])
                    if not items:
                        break

                    for it in items:
                        all_libraries.append({
                            "name": it.get("lbrryNm", "-"),
                            "address": it.get(
                                "rdnmadr", it.get("lnmadr", "-")
                            ),
                            "tel": it.get("phoneNumber", "-"),
                            "closed": it.get("rstde", "정보 없음"),
                            "homepage": it.get("homepageUrl", ""),
                        })

                    print(
                        f"공공데이터 {page_no}페이지 수집 완료 (누적: {len(all_libraries)}개)"
                    )
                    total_count = int(body.get("totalCount", 0))
                    if (
                        len(all_libraries) >= total_count
                        or len(items) < num_of_rows
                    ):
                        break

                    page_no += 1
                    time.sleep(0.2)
                else:
                    break
            except Exception as e:
                print(f"공공데이터 통신 오류: {e}")
                break

    return all_libraries


def generate_html(libs):
    """검색창 및 필터가 포함된 고기능 반응형 HTML 테이블 생성"""
    rows = ""
    for lib in libs:
        hp = lib.get("homepage", "")
        link = (
            f'<a href="{hp}" target="_blank" rel="noopener" class="btn-link">홈페이지</a>'
            if (hp and hp.startswith("http"))
            else "-"
        )
        rows += f"""
        <tr>
            <td class="col-name">{lib['name']}</td>
            <td class="col-addr">{lib['address']}</td>
            <td>{lib['tel']}</td>
            <td><span class="badge-closed">{lib['closed']}</span></td>
            <td style="text-align:center;">{link}</td>
        </tr>
        """

    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>전국 공공도서관 정보</title>
    <style>
        * {{ box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Malgun Gothic", dotum, sans-serif; margin: 0; padding: 12px; background: #fff; }}
        .header-box {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; flex-wrap: wrap; gap: 8px; }}
        .count-info {{ font-size: 14px; font-weight: bold; color: #1971c2; }}
        .search-input {{ padding: 8px 12px; border: 1px solid #ced4da; border-radius: 4px; font-size: 13px; width: 250px; outline: none; }}
        .search-input:focus {{ border-color: #1971c2; }}
        .tbl-wrap {{ width: 100%; overflow-x: auto; box-shadow: 0 1px 3px rgba(0,0,0,0.08); border-radius: 6px; border: 1px solid #dee2e6; max-height: 700px; overflow-y: auto; }}
        table {{ width: 100%; border-collapse: collapse; min-width: 650px; font-size: 13px; text-align: left; }}
        thead th {{ background: #f8f9fa; color: #343a40; padding: 12px 10px; font-weight: 700; border-bottom: 2px solid #dee2e6; position: sticky; top: 0; z-index: 2; }}
        tbody tr {{ border-bottom: 1px solid #e9ecef; }}
        tbody tr:hover {{ background-color: #f1f3f5; }}
        td {{ padding: 10px; color: #495057; }}
        .col-name {{ font-weight: bold; color: #212529; }}
        .col-addr {{ font-size: 12px; }}
        .badge-closed {{ display: inline-block; padding: 3px 6px; background: #ffe3e3; color: #c92a2a; border-radius: 4px; font-size: 11px; }}
        .btn-link {{ display: inline-block; padding: 4px 8px; background: #1971c2; color: #fff !important; text-decoration: none; border-radius: 4px; font-size: 11px; }}
    </style>
</head>
<body>
    <div class="header-box">
        <div class="count-info">전국 도서관 총 <span id="total-count">{len(libs)}</span>개 등록</div>
        <input type="text" id="searchInput" class="search-input" placeholder="도서관명 또는 지역(시/구) 검색..." onkeyup="filterLibraries()">
    </div>
    <div class="tbl-wrap">
        <table id="libTable">
            <thead>
                <tr>
                    <th style="width: 25%;">도서관명</th>
                    <th style="width: 35%;">주소</th>
                    <th style="width: 15%;">전화번호</th>
                    <th style="width: 15%;">정기 휴관일</th>
                    <th style="width: 10%; text-align:center;">홈페이지</th>
                </tr>
            </thead>
            <tbody>
                {rows}
            </tbody>
        </table>
    </div>

    <script>
        function filterLibraries() {{
            const input = document.getElementById("searchInput").value.toLowerCase();
            const table = document.getElementById("libTable");
            const tr = table.getElementsByTagName("tbody")[0].getElementsByTagName("tr");
            let visibleCount = 0;

            for (let i = 0; i < tr.length; i++) {{
                const text = tr[i].textContent.toLowerCase();
                if (text.includes(input)) {{
                    tr[i].style.display = "";
                    visibleCount++;
                }} else {{
                    tr[i].style.display = "none";
                }}
            }}
            document.getElementById("total-count").innerText = visibleCount;
        }}
    </script>
</body>
</html>
"""


if __name__ == "__main__":
    libs = fetch_all_libraries()
    print(f"최종 수집 완료 건수: {len(libs)}개")

    if not libs:
        print("수집 데이터가 없어 파일을 갱신하지 않습니다.")
    else:
        html_code = generate_html(libs)
        with open("library_list.html", "w", encoding="utf-8") as f:
            f.write(html_code)
        print("library_list.html 전수 데이터 저장 완료")
