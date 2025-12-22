#!/usr/bin/env python3
"""
로또 판매점 데이터를 JSON 파일에서 읽어서 데이터베이스에 저장하는 스크립트

Usage:
    python migrations/scripts/insert_lotto_stores.py
    python migrations/scripts/insert_lotto_stores.py --json-path /path/to/json
    python migrations/scripts/insert_lotto_stores.py --batch-size 500
"""

import argparse
import asyncio
import html
import json
import sys
from pathlib import Path
from typing import Any

from sqlalchemy import select

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# .env 파일 로드
from dotenv import load_dotenv

load_dotenv()

from src.config.database import Mysql
from src.config.config import db_config
from src.lotto_stores.domain.entities.models import LottoStore
from src.lotto.domain.entities.models import LottoDraws  # relationship 초기화용
from src.users.domain.entities.models import User  # relationship 초기화용


class LottoStoreImporter:
    def __init__(self, json_path: str | None = None, batch_size: int = 500):
        self.db = Mysql(db_config)
        self.batch_size = batch_size

        # 기본 JSON 파일 경로 설정
        if json_path:
            self.json_path = Path(json_path)
        else:
            # 가장 최신 JSON 파일 찾기
            output_dir = Path(__file__).parent / "output"
            json_files = list(
                output_dir.glob("lotto_stores_full_merged_*.json")
            )
            if not json_files:
                raise FileNotFoundError(
                    f"JSON 파일을 찾을 수 없습니다: {output_dir}"
                )
            self.json_path = max(json_files, key=lambda p: p.stat().st_mtime)

        print(f"사용할 JSON 파일: {self.json_path}")

    def load_json_data(self) -> list[dict[str, Any]]:
        """JSON 파일에서 판매점 데이터를 로드합니다."""
        with open(self.json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        stores = data.get("stores", [])
        print(f"로드된 판매점 수: {len(stores)}")
        return stores

    def _unescape(self, value: str | None) -> str | None:
        """HTML entity를 디코딩합니다."""
        if value is None:
            return None
        return html.unescape(value)

    def parse_store_data(self, raw_store: dict[str, Any]) -> dict[str, Any]:
        """JSON 데이터를 LottoStore 모델에 맞게 파싱합니다."""
        return {
            "id": str(raw_store.get("RTLRID", "")),
            "name": self._unescape(raw_store.get("FIRMNM", "")),
            "latitude": raw_store.get("LATITUDE"),
            "longitude": raw_store.get("LONGITUDE"),
            "road_address": self._unescape(raw_store.get("BPLCDORODTLADRES")),
            "lot_address": self._unescape(raw_store.get("BPLCLOCPLCDTLADRES")),
            "region1": self._unescape(raw_store.get("BPLCLOCPLC1")),
            "region2": self._unescape(raw_store.get("BPLCLOCPLC2")),
            "region3": self._unescape(raw_store.get("BPLCLOCPLC3")),
            "phone": raw_store.get("RTLRSTRTELNO"),
            "first_prize_count": 0,
            "first_prize_auto": 0,
            "first_prize_manual": 0,
            "first_prize_semi": 0,
        }

    async def check_existing_store(self, session, store_id: str) -> bool:
        """판매점이 이미 존재하는지 확인합니다."""
        result = await session.execute(
            select(LottoStore.id).where(LottoStore.id == store_id)
        )
        return result.scalar_one_or_none() is not None

    async def import_stores(self) -> None:
        """판매점 데이터를 데이터베이스에 저장합니다."""
        stores_data = self.load_json_data()

        if not stores_data:
            print("저장할 판매점 데이터가 없습니다.")
            return

        async with self.db.session() as session:
            success_count = 0
            skip_count = 0
            error_count = 0

            # 배치 단위로 처리
            for i in range(0, len(stores_data), self.batch_size):
                batch = stores_data[i : i + self.batch_size]
                batch_stores = []

                for raw_store in batch:
                    try:
                        store_data = self.parse_store_data(raw_store)

                        # 필수 필드 검증
                        if not store_data["id"] or not store_data["name"]:
                            print(f"필수 필드 누락: {raw_store}")
                            error_count += 1
                            continue

                        # 이미 존재하는지 확인
                        if await self.check_existing_store(
                            session, store_data["id"]
                        ):
                            skip_count += 1
                            continue

                        batch_stores.append(LottoStore(**store_data))

                    except Exception as e:
                        print(
                            f"파싱 오류 ({raw_store.get('RTLRID', 'unknown')}): {e}"
                        )
                        error_count += 1
                        continue

                # 배치 저장
                if batch_stores:
                    try:
                        session.add_all(batch_stores)
                        await session.commit()
                        success_count += len(batch_stores)
                        print(
                            f"진행: {i + len(batch)}/{len(stores_data)} - 배치 저장 완료 ({len(batch_stores)}개)"
                        )
                    except Exception as e:
                        await session.rollback()
                        print(f"배치 저장 오류: {e}")
                        error_count += len(batch_stores)
                else:
                    print(
                        f"진행: {i + len(batch)}/{len(stores_data)} - 새로운 데이터 없음"
                    )

            print(f"\n=== 가져오기 완료 ===")
            print(f"성공: {success_count}개")
            print(f"건너뜀 (이미 존재): {skip_count}개")
            print(f"실패: {error_count}개")

    async def close(self) -> None:
        """데이터베이스 연결을 종료합니다."""
        await self.db.close()


async def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(description="로또 판매점 데이터 가져오기")
    parser.add_argument(
        "--json-path",
        type=str,
        default=None,
        help="JSON 파일 경로 (기본값: 가장 최신 파일 자동 선택)",
    )
    parser.add_argument(
        "--batch-size", type=int, default=500, help="배치 크기 (기본값: 500)"
    )

    args = parser.parse_args()

    try:
        importer = LottoStoreImporter(
            json_path=args.json_path, batch_size=args.batch_size
        )

        await importer.import_stores()

    except FileNotFoundError as e:
        print(f"파일 오류: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n사용자에 의해 중단되었습니다.")
    except Exception as e:
        print(f"오류 발생: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
    finally:
        if "importer" in locals():
            await importer.close()


if __name__ == "__main__":
    asyncio.run(main())
