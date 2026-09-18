import json
import os
import requests

# GitHub Secrets에서 인증키 읽어오기
API_KEY = os.environ.get("DATA4LIBRARY_AUTH_KEY")


def fetch_library_data(page_no=1, page_size=100):
    """도서관 정보나루 API 호출"""
    url = "http://data4library.kr/api/libSrch"
    params = {
        "authKey": API_KEY,
        "pageNo": page_no,
        "pageSize": page_size,
        "format": "json",
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        try:
            data = response.json()
            return data.get("response", {}).get("libs", [])
        except Exception as e:
            print(f"JSON 파싱 에러: {e}")
            return []
    print(f"API 요청 실패 (코드: {response.status_code})")
    return []


def generate_html(libs):
    """티스토리용 반응형 테이블 HTML 생성"""
    html = """
    <style>
        .lib-box { width: 100%; overflow-x: auto; margin: 20px 0; font-family: -apple-system, BlinkMacSystemFont, "Malgun Gothic", sans-serif; }
        .lib-table { width: 100%; border-collapse: collapse; min-width: 600px; font-size: 14px; }
        .lib-table th { background-color: #f1f3f5; color: #333; font-weight: 600; padding: 12px 10px; border: 1px solid #dee2e6; text-align: left; }
        .lib-table td { padding: 10px; border: 1px solid #dee2e6; color: #495057; }
        .lib-table tr:hover { background-color: #f8f9fa; }
        .badge-closed { display: inline-block; padding: 2px 8px; font-size: 12px; border-radius: 4px; background: #ffe3e3; color: #c92a2a; font-weight: bold; }
        .btn-home { display: inline-block; padding: 4px 10px; font-size: 12px; background: #228be6; color: #fff !important; text-decoration: none; border-radius: 4px; }
        .btn-home:hover { background: #1c7ed6; }
    </style>
    <div class="lib-box">
        <table class="lib-table">
            <thead>
                <tr>
                    <th>도서관명</th>
                    <th>주소</th>
                    <th>전화번호</th>
                    <th>정기 휴관일</th>
                    <th>홈페이지</th>
                </tr>
            </thead>
            <tbody>
    """

    for item in libs:
        lib = item.get("lib", {})
        name = lib.get("libName", "-")
        addr = lib.get("address", "-")
        tel = lib.get("tel", "-")
        closed = lib.get("closed", "정보 없음")
        hp = lib.get("homepage", "")

        hp_btn = (
            f'<a href="{hp}" target="_blank" rel="noopener" class="btn-home">방문</a>'
            if hp
            else "-"
        )

        html += f"""
                <tr>
                    <td><strong>{name}</strong></td>
                    <td>{addr}</td>
                    <td>{tel}</td>
                    <td><span class="badge-closed">{closed}</span></td>
                    <td>{hp_btn}</td>
                </tr>
        """

    html += """
            </tbody>
        </table>
    </div>
    """
    return html


if __name__ == "__main__":
    if not API_KEY:
        print("경고: DATA4LIBRARY_AUTH_KEY가 설정되지 않았습니다.")

    # 기본 100개 데이터 조회 (필요 시 page_no 조절)
    libs = fetch_library_data(page_no=1, page_size=100)
    print(f"조회된 도서관 수: {len(libs)}개")

    # HTML 결과물 파일 생성
    result_html = generate_html(libs)
    with open("library_list.html", "w", encoding="utf-8") as f:
        f.write(result_html)

    print("성공: library_list.html 파일 생성 완료")
