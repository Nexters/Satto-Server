"""
동행복권 로또 판매점 정보 추가 수집 스크립트

충청북도, 충청남도, 전라북도, 전라남도, 경상북도, 경상남도
-> 판매점 조회 시 sltSIDO에 충북, 충남, 전북, 전남, 경북, 경남으로 변환하여 조회
-> 기존 저장된 구/군 정보를 사용
"""

import json
import random
import time
from datetime import datetime
from pathlib import Path
from urllib.parse import quote

import httpx

# 시도 이름 매핑 (전체 이름 -> API 조회용 약어)
SIDO_NAME_MAP = {
    "충청북도": "충북",
    "충청남도": "충남",
    "전라북도": "전북",
    "전라남도": "전남",
    "경상북도": "경북",
    "경상남도": "경남",
}

# 조회할 시도 목록
SIDO_LIST = list(SIDO_NAME_MAP.keys())

# API URL
SELLER_API_URL = "https://dhlottery.co.kr/store.do?method=sellerInfo645Result"

# 요청 헤더
HEADERS = {
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
    "Origin": "https://dhlottery.co.kr",
    "Referer": "https://dhlottery.co.kr/store.do?method=sellerInfo645",
    "X-Requested-With": "XMLHttpRequest",
}

# API 호출 딜레이 설정 (초)
DELAY_MIN = 2.0
DELAY_MAX = 4.0
DELAY_ON_ERROR = 10.0
MAX_RETRIES = 3


def log(message: str, end: str = "\n") -> None:
    """즉시 출력되는 로그 함수"""
    print(message, end=end, flush=True)


def random_delay(
    min_sec: float = DELAY_MIN, max_sec: float = DELAY_MAX
) -> None:
    """랜덤 딜레이"""
    delay = random.uniform(min_sec, max_sec)
    time.sleep(delay)


def decode_response(response: httpx.Response) -> str:
    """응답을 적절한 인코딩으로 디코딩합니다."""
    try:
        return response.content.decode("utf-8")
    except UnicodeDecodeError:
        pass
    try:
        return response.content.decode("euc-kr")
    except UnicodeDecodeError:
        pass
    try:
        return response.content.decode("cp949")
    except UnicodeDecodeError:
        pass
    return response.content.decode("utf-8", errors="replace")


def fetch_with_retry(
    client: httpx.Client,
    url: str,
    data: str,
    max_retries: int = MAX_RETRIES,
) -> httpx.Response | None:
    """재시도 로직이 포함된 POST 요청"""
    for attempt in range(max_retries):
        try:
            response = client.post(url, content=data, timeout=15.0)
            response.raise_for_status()
            return response
        except Exception as e:
            if attempt < max_retries - 1:
                wait_time = DELAY_ON_ERROR * (attempt + 1)
                log(
                    f"\n      ⚠️ 요청 실패 (시도 {attempt + 1}/{max_retries}): {e}"
                )
                log(f"      ⏳ {wait_time}초 대기 후 재시도...")
                time.sleep(wait_time)
            else:
                log(f"\n      ❌ 최대 재시도 횟수 초과: {e}")
                return None
    return None


def fetch_sellers_page(
    client: httpx.Client, sido_short: str, gugun: str, page: int = 1
) -> dict:
    """특정 시도/구군의 판매점 정보를 페이지 단위로 가져옵니다."""
    data = f"searchType=1&nowPage={page}&sltSIDO={quote(sido_short)}&sltGUGUN={quote(gugun)}&rtlrSttus=001"

    response = fetch_with_retry(client, SELLER_API_URL, data)

    if not response:
        return {}

    try:
        text = decode_response(response)
        return json.loads(text)
    except Exception as e:
        log(f"      [페이지 {page}] 파싱 실패: {e}")
        return {}


def fetch_all_sellers(
    client: httpx.Client,
    sido: str,
    sido_short: str,
    gugun: str,
    gugun_idx: int,
    total_gugun: int,
    accumulated_stores: int,
) -> list[dict]:
    """특정 시도/구군의 모든 판매점 정보를 가져옵니다."""
    all_sellers = []

    log(
        f"    [{gugun_idx}/{total_gugun}] [{sido}/{gugun}] 조회 중 (API: {sido_short})...",
        end=" ",
    )
    first_page_data = fetch_sellers_page(client, sido_short, gugun, 1)

    if not first_page_data:
        log("✗ 데이터 없음")
        return []

    total_page = first_page_data.get("totalPage", 1)
    arr = first_page_data.get("arr", [])

    if arr:
        all_sellers.extend(arr)

    log(f"총 {total_page}페이지, 페이지 1 완료 ({len(arr)}개)")

    # 나머지 페이지 조회
    for page in range(2, total_page + 1):
        log(f"      └─ 페이지 {page}/{total_page} 조회 중...", end=" ")

        random_delay(1.0, 2.0)

        page_data = fetch_sellers_page(client, sido_short, gugun, page)
        arr = page_data.get("arr", [])

        if arr:
            all_sellers.extend(arr)
            log(f"✓ {len(arr)}개")
        else:
            log("데이터 없음")

    total_so_far = accumulated_stores + len(all_sellers)
    log(
        f"    ➜ [{sido}/{gugun}] 완료! "
        f"이 지역: {len(all_sellers)}개, 누적: {total_so_far}개"
    )

    return all_sellers


def main():
    """메인 실행 함수"""
    start_time = datetime.now()

    log("=" * 70)
    log("🎰 누락된 판매점 정보 추가 수집")
    log(f"⏰ 시작 시간: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    log(f"📍 대상 시도: {', '.join(SIDO_LIST)}")
    log("=" * 70)

    script_dir = Path(__file__).parent
    output_dir = script_dir / "output"

    # 기존 데이터 로드
    existing_stores_path = output_dir / "lotto_stores_full_latest.json"
    if existing_stores_path.exists():
        log(f"\n📂 기존 데이터 로드: {existing_stores_path}")
        with open(existing_stores_path, encoding="utf-8") as f:
            existing_data = json.load(f)
        log(f"   기존 판매점 수: {len(existing_data.get('stores', []))}개")
    else:
        log(
            "\n❌ 기존 데이터가 없습니다. 먼저 fetch_lotto_stores.py를 실행하세요."
        )
        return

    # 기존 구/군 정보 사용 - 별도 저장된 파일에서 로드
    gugun_map_path = output_dir / "sido_gugun_map_20251221_015234.json"
    if gugun_map_path.exists():
        log(f"\n📂 구/군 맵 로드: {gugun_map_path}")
        with open(gugun_map_path, encoding="utf-8") as f:
            sido_gugun_map = json.load(f)
    else:
        sido_gugun_map = existing_data.get("sido_gugun_map", {})

    # 대상 시도의 구/군 정보 확인
    log("\n📍 대상 시도 구/군 정보:")
    total_gugun_count = 0
    for sido in SIDO_LIST:
        gugun_list = sido_gugun_map.get(sido, [])
        log(f"  - {sido}: {len(gugun_list)}개 구/군")
        total_gugun_count += len(gugun_list)

    if total_gugun_count == 0:
        log("\n❌ 대상 시도의 구/군 정보가 없습니다.")
        return

    new_stores = []

    with httpx.Client(headers=HEADERS, timeout=15.0) as client:
        log("\n" + "=" * 70)
        log("🏪 판매점 정보 수집")
        log(
            f"📊 총 {total_gugun_count}개 구/군에서 판매점 정보를 수집합니다..."
        )
        log("=" * 70)

        gugun_processed = 0

        for sido in SIDO_LIST:
            sido_short = SIDO_NAME_MAP[sido]
            gugun_list = sido_gugun_map.get(sido, [])

            if not gugun_list:
                log(f"\n▶ {sido}: 구/군 없음, 스킵")
                continue

            log(f"\n▶ {sido} ({len(gugun_list)}개 구/군)")
            log("-" * 50)

            for gugun_idx, gugun in enumerate(gugun_list, 1):
                gugun_processed += 1

                sellers = fetch_all_sellers(
                    client,
                    sido,
                    sido_short,
                    gugun,
                    gugun_processed,
                    total_gugun_count,
                    len(new_stores),
                )

                for seller in sellers:
                    seller["SIDO"] = sido
                    seller["GUGUN"] = gugun

                new_stores.extend(sellers)

                if gugun_idx < len(gugun_list):
                    random_delay()

            random_delay(3.0, 5.0)

    # 기존 데이터와 병합
    log("\n" + "=" * 70)
    log("🔄 기존 데이터와 병합")
    log("=" * 70)

    # 기존 stores에서 해당 시도 데이터 제거 후 새 데이터 추가
    filtered_stores = [
        s
        for s in existing_data.get("stores", [])
        if s.get("SIDO") not in SIDO_LIST
    ]
    log(
        f"  기존 데이터에서 대상 시도 제외: {len(existing_data.get('stores', []))} -> {len(filtered_stores)}개"
    )

    merged_stores = filtered_stores + new_stores
    log(f"  새 데이터 추가: {len(new_stores)}개")
    log(f"  병합 후 총 판매점: {len(merged_stores)}개")

    existing_data["stores"] = merged_stores
    existing_data["summary"]["total_stores"] = len(merged_stores)
    existing_data["collected_at"] = datetime.now().isoformat()

    # 저장
    log("\n" + "=" * 70)
    log("💾 결과 저장")
    log("=" * 70)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # 새로 추가된 데이터만 별도 저장
    new_data_path = output_dir / f"lotto_stores_missing_{timestamp}.json"
    with open(new_data_path, "w", encoding="utf-8") as f:
        json.dump(new_stores, f, ensure_ascii=False, indent=2)
    log(f"  ✓ 새로 수집된 데이터: {new_data_path}")

    # 병합된 전체 데이터 저장
    merged_path = output_dir / f"lotto_stores_full_merged_{timestamp}.json"
    with open(merged_path, "w", encoding="utf-8") as f:
        json.dump(existing_data, f, ensure_ascii=False, indent=2)
    log(f"  ✓ 병합된 전체 데이터: {merged_path}")

    # latest 파일 업데이트
    latest_path = output_dir / "lotto_stores_full_latest.json"
    with open(latest_path, "w", encoding="utf-8") as f:
        json.dump(existing_data, f, ensure_ascii=False, indent=2)

    latest_stores_path = output_dir / "lotto_stores_latest.json"
    with open(latest_stores_path, "w", encoding="utf-8") as f:
        json.dump(existing_data["stores"], f, ensure_ascii=False, indent=2)
    log("  ✓ latest 파일 업데이트 완료")

    # 요약
    end_time = datetime.now()
    elapsed = end_time - start_time

    log("\n" + "=" * 70)
    log("🎉 추가 수집 완료!")
    log("=" * 70)
    log(f"  ⏱️  소요 시간: {elapsed}")
    log(f"  🆕 새로 수집: {len(new_stores)}개")
    log(f"  🏪 총 판매점: {len(merged_stores)}개")
    log("=" * 70)


if __name__ == "__main__":
    main()
