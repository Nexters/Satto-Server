from datetime import date, datetime, timezone, timedelta


def get_kst_date() -> date:
    """한국 표준시(KST) 기준으로 오늘 날짜를 반환합니다."""
    kst_tz = timezone(timedelta(hours=9))
    kst_now = datetime.now(kst_tz)
    return kst_now.date()
