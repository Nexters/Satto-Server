"""
동행복권 로또 판매점 정보 수집 스크립트

1. 시도별 구/군 정보 가져오기
2. 시도/구군별 판매점 정보 가져오기 (모든 페이지)
3. 결과를 JSON 파일로 저장
"""

import json
import random
import time
from datetime import datetime
from pathlib import Path
from urllib.parse import quote

import httpx

# 17개 시도 목록
SIDO_LIST = [
    "서울",
    "경기",
    "부산",
    "대구",
    "인천",
    "대전",
    "울산",
    "강원",
    "충청북도",
    "충청남도",
    "광주",
    "전라북도",
    "전라남도",
    "경상북도",
    "경상남도",
    "제주",
    "세종",
]

# 시도 이름 매핑 (전체 이름 -> API 조회용 약어)
# API 호출 시 약어를 사용해야 하는 시도
SIDO_NAME_MAP = {
    "충청북도": "충북",
    "충청남도": "충남",
    "전라북도": "전북",
    "전라남도": "전남",
    "경상북도": "경북",
    "경상남도": "경남",
}

# API URLs
GUGUN_API_URL = "https://dhlottery.co.kr/store.do?method=searchGUGUN"
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

# API 호출 딜레이 설정 (초) - 랜덤 범위
DELAY_MIN = 2.0  # 최소 딜레이
DELAY_MAX = 4.0  # 최대 딜레이
DELAY_ON_ERROR = 10.0  # 에러 시 대기 시간
MAX_RETRIES = 3  # 최대 재시도 횟수


def get_sido_api_name(sido: str) -> str:
    """시도 이름을 API 호출용 이름으로 변환"""
    return SIDO_NAME_MAP.get(sido, sido)


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
    """
    응답을 적절한 인코딩으로 디코딩합니다.
    동행복권 API는 EUC-KR 또는 UTF-8을 사용합니다.
    """
    # 먼저 UTF-8 시도
    try:
        return response.content.decode("utf-8")
    except UnicodeDecodeError:
        pass

    # EUC-KR 시도
    try:
        return response.content.decode("euc-kr")
    except UnicodeDecodeError:
        pass

    # CP949 시도 (확장 EUC-KR)
    try:
        return response.content.decode("cp949")
    except UnicodeDecodeError:
        pass

    # 최후의 수단: errors='replace'
    return response.content.decode("utf-8", errors="replace")


def log_progress(current: int, total: int, prefix: str = "") -> str:
    """진행률 문자열 생성"""
    percentage = (current / total * 100) if total > 0 else 0
    return f"{prefix}[{current}/{total}] ({percentage:.1f}%)"


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


def fetch_gugun_list(
    client: httpx.Client, sido: str, sido_idx: int, total_sido: int
) -> list[str]:
    """
    시도에 해당하는 구/군 목록을 가져옵니다.
    """
    # API 호출용 시도 이름 (약어 사용)
    sido_api = get_sido_api_name(sido)
    data = f"SIDO={quote(sido_api)}"
    progress = log_progress(sido_idx, total_sido)

    log(f"  {progress} [{sido}] 구/군 조회 중...", end=" ")

    response = fetch_with_retry(client, GUGUN_API_URL, data)

    if not response:
        log("✗ 실패")
        return []

    try:
        text = decode_response(response)
        gugun_list = json.loads(text)
        gugun_list = [
            g for g in gugun_list if g and isinstance(g, str) and g.strip()
        ]
        log(f"✓ {len(gugun_list)}개 발견")
        return gugun_list
    except Exception as e:
        log(f"✗ 파싱 실패: {e}")
        return []


def fetch_sellers_page(
    client: httpx.Client, sido: str, gugun: str, page: int = 1
) -> dict:
    """
    특정 시도/구군의 판매점 정보를 페이지 단위로 가져옵니다.
    """
    # API 호출용 시도 이름 (약어 사용)
    sido_api = get_sido_api_name(sido)
    data = f"searchType=1&nowPage={page}&sltSIDO={quote(sido_api)}&sltGUGUN={quote(gugun)}&rtlrSttus=001"

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
    gugun: str,
    gugun_idx: int,
    total_gugun: int,
    accumulated_stores: int,
) -> list[dict]:
    """
    특정 시도/구군의 모든 판매점 정보를 가져옵니다.
    """
    all_sellers = []
    progress = log_progress(gugun_idx, total_gugun)

    log(f"    {progress} [{sido}/{gugun}] 조회 중...", end=" ")
    first_page_data = fetch_sellers_page(client, sido, gugun, 1)

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

        random_delay(1.0, 2.0)  # 페이지 간 랜덤 딜레이

        page_data = fetch_sellers_page(client, sido, gugun, page)
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


def save_progress(
    output_dir: Path, all_data: dict, prefix: str = "progress"
) -> None:
    """진행 상황을 중간 저장"""
    progress_path = output_dir / f"{prefix}_latest.json"
    with open(progress_path, "w", encoding="utf-8") as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)


def main():
    """메인 실행 함수"""
    start_time = datetime.now()

    log("=" * 70)
    log("🎰 동행복권 로또 판매점 정보 수집 시작")
    log(f"⏰ 시작 시간: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    log(f"⏱️  API 호출 딜레이: {DELAY_MIN}~{DELAY_MAX}초 (랜덤)")
    log(f"🔄 재시도: 최대 {MAX_RETRIES}회, 에러 시 {DELAY_ON_ERROR}초 대기")
    log("=" * 70)

    # 출력 디렉토리 생성
    script_dir = Path(__file__).parent
    output_dir = script_dir / "output"
    output_dir.mkdir(exist_ok=True)

    # 결과 저장 변수
    all_data = {
        "collected_at": start_time.isoformat(),
        "sido_gugun_map": {},
        "stores": [],
        "summary": {
            "total_sido": len(SIDO_LIST),
            "total_gugun": 0,
            "total_stores": 0,
        },
    }

    total_gugun_count = 0
    total_sido = len(SIDO_LIST)

    # httpx Client 생성
    with httpx.Client(headers=HEADERS, timeout=15.0) as client:
        # 1. 각 시도별 구/군 정보 수집
        log("\n" + "=" * 70)
        log("📍 [STEP 1] 시도별 구/군 정보 수집")
        log("=" * 70)

        for idx, sido in enumerate(SIDO_LIST, 1):
            gugun_list = fetch_gugun_list(client, sido, idx, total_sido)
            all_data["sido_gugun_map"][sido] = gugun_list
            total_gugun_count += len(gugun_list)

            if idx < total_sido:
                random_delay()

        all_data["summary"]["total_gugun"] = total_gugun_count

        log("\n" + "-" * 70)
        log(f"✅ [STEP 1 완료] 총 {total_gugun_count}개 구/군 발견")
        log("-" * 70)

        # 중간 저장
        save_progress(output_dir, all_data, "gugun")
        log("💾 구/군 정보 중간 저장 완료")

        # 2. 각 시도/구군별 판매점 정보 수집
        log("\n" + "=" * 70)
        log("🏪 [STEP 2] 판매점 정보 수집")
        log(
            f"📊 총 {total_gugun_count}개 구/군에서 판매점 정보를 수집합니다..."
        )
        log("=" * 70)

        gugun_processed = 0
        save_interval = 10  # 10개 구/군마다 중간 저장

        for sido_idx, sido in enumerate(SIDO_LIST, 1):
            gugun_list = all_data["sido_gugun_map"].get(sido, [])

            if not gugun_list:
                log(f"\n▶ [{sido_idx}/{total_sido}] {sido}: 구/군 없음, 스킵")
                continue

            log(
                f"\n▶ [{sido_idx}/{total_sido}] {sido} ({len(gugun_list)}개 구/군)"
            )
            log("-" * 50)

            for gugun_idx, gugun in enumerate(gugun_list, 1):
                gugun_processed += 1

                sellers = fetch_all_sellers(
                    client,
                    sido,
                    gugun,
                    gugun_processed,
                    total_gugun_count,
                    len(all_data["stores"]),
                )

                # 시도/구군 정보 추가
                for seller in sellers:
                    seller["SIDO"] = sido
                    seller["GUGUN"] = gugun

                all_data["stores"].extend(sellers)

                # 중간 저장 (10개마다)
                if gugun_processed % save_interval == 0:
                    all_data["summary"]["total_stores"] = len(
                        all_data["stores"]
                    )
                    save_progress(output_dir, all_data, "stores")
                    log(
                        f"    💾 중간 저장 완료 ({gugun_processed}/{total_gugun_count})"
                    )

                # 랜덤 딜레이
                if gugun_idx < len(gugun_list):
                    random_delay()

            # 시도 간 추가 딜레이
            if sido_idx < total_sido:
                log("\n  ⏳ 다음 시도로 이동 전 대기 중...")
                random_delay(3.0, 5.0)

    all_data["summary"]["total_stores"] = len(all_data["stores"])

    end_time = datetime.now()
    elapsed = end_time - start_time

    # 3. 결과 저장
    log("\n" + "=" * 70)
    log("💾 [STEP 3] 결과 저장")
    log("=" * 70)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # 전체 데이터 저장
    full_output_path = output_dir / f"lotto_stores_full_{timestamp}.json"
    with open(full_output_path, "w", encoding="utf-8") as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)
    log(f"  ✓ 전체 데이터: {full_output_path}")

    # 판매점 리스트만 별도 저장
    stores_output_path = output_dir / f"lotto_stores_{timestamp}.json"
    with open(stores_output_path, "w", encoding="utf-8") as f:
        json.dump(all_data["stores"], f, ensure_ascii=False, indent=2)
    log(f"  ✓ 판매점 리스트: {stores_output_path}")

    # 시도-구군 매핑 저장
    mapping_output_path = output_dir / f"sido_gugun_map_{timestamp}.json"
    with open(mapping_output_path, "w", encoding="utf-8") as f:
        json.dump(all_data["sido_gugun_map"], f, ensure_ascii=False, indent=2)
    log(f"  ✓ 시도-구군 매핑: {mapping_output_path}")

    # 최신 파일로도 저장 (덮어쓰기)
    latest_full_path = output_dir / "lotto_stores_full_latest.json"
    with open(latest_full_path, "w", encoding="utf-8") as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)

    latest_stores_path = output_dir / "lotto_stores_latest.json"
    with open(latest_stores_path, "w", encoding="utf-8") as f:
        json.dump(all_data["stores"], f, ensure_ascii=False, indent=2)
    log("  ✓ 최신 파일 업데이트 완료")

    # 요약 출력
    log("\n" + "=" * 70)
    log("🎉 수집 완료!")
    log("=" * 70)
    log(f"  ⏰ 시작 시간: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    log(f"  ⏰ 종료 시간: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    log(f"  ⏱️  소요 시간: {elapsed}")
    log("-" * 70)
    log(f"  📍 총 시도: {all_data['summary']['total_sido']}개")
    log(f"  📍 총 구/군: {all_data['summary']['total_gugun']}개")
    log(f"  🏪 총 판매점: {all_data['summary']['total_stores']}개")
    log("=" * 70)


if __name__ == "__main__":
    main()
