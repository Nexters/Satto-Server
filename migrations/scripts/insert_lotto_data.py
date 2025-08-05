#!/usr/bin/env python3
"""
로또 데이터를 동행복권 API에서 가져와서 데이터베이스에 저장하는 스크립트
"""

import asyncio
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

# .env 파일 로드
from dotenv import load_dotenv
load_dotenv()

from src.config.database import Mysql
from src.config.config import db_config
from src.lotto.entities.models import LottoDraws, LottoStatistics


class LottoDataImporter:
    def __init__(self):
        self.db = Mysql(db_config)
        self.base_url = "https://dhlottery.co.kr/common.do"
        
    async def fetch_lotto_data(self, client: httpx.AsyncClient, drw_no: int) -> Optional[Dict[str, Any]]:
        """특정 회차의 로또 데이터를 가져옵니다."""
        params = {
            "method": "getLottoNumber",
            "drwNo": drw_no
        }
        
        try:
            response = await client.get(self.base_url, params=params)
            if response.status_code == 200:
                data = response.json()
                if data.get("returnValue") == "success":
                    return data
                else:
                    print(f"회차 {drw_no}: API 응답 오류 - {data}")
                    return None
            else:
                print(f"회차 {drw_no}: HTTP 오류 - {response.status_code}")
                return None
        except Exception as e:
            print(f"회차 {drw_no}: 요청 오류 - {e}")
            return None
    
    def parse_lotto_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """API 응답 데이터를 데이터베이스 모델에 맞게 파싱합니다."""
        return {
            "round": data["drwNo"],
            "draw_date": datetime.strptime(data["drwNoDate"], "%Y-%m-%d").date(),
            "num1": data["drwtNo1"],
            "num2": data["drwtNo2"],
            "num3": data["drwtNo3"],
            "num4": data["drwtNo4"],
            "num5": data["drwtNo5"],
            "num6": data["drwtNo6"],
            "bonus_num": data["bnusNo"],
            "first_prize_amount": data["firstAccumamnt"],
            "total_winners": data["firstPrzwnerCo"]
        }
    
    async def save_lotto_draw(self, db_session: AsyncSession, lotto_data: Dict[str, Any]) -> bool:
        """로또 추첨 데이터를 데이터베이스에 저장합니다."""
        try:
            # 이미 존재하는지 확인
            existing = await db_session.execute(
                select(LottoDraws).where(LottoDraws.round == lotto_data["round"])
            )
            if existing.scalar_one_or_none():
                print(f"회차 {lotto_data['round']}: 이미 존재함")
                return False
            
            # 새로운 로또 추첨 데이터 생성
            lotto_draw = LottoDraws(**lotto_data)
            db_session.add(lotto_draw)
            await db_session.commit()
            print(f"회차 {lotto_data['round']}: 저장 완료")
            return True
        except Exception as e:
            await db_session.rollback()
            print(f"회차 {lotto_data['round']}: 저장 오류 - {e}")
            return False
    
    async def update_statistics(self, db_session: AsyncSession, lotto_data: Dict[str, Any]) -> None:
        """로또 통계 데이터를 업데이트합니다."""
        try:
            # 메인 번호들 (1-6번)
            main_numbers = [
                lotto_data["num1"], lotto_data["num2"], lotto_data["num3"],
                lotto_data["num4"], lotto_data["num5"], lotto_data["num6"]
            ]
            bonus_number = lotto_data["bonus_num"]
            
            # 각 번호에 대한 통계 업데이트
            for num in range(1, 46):
                # 기존 통계 조회
                stat = await db_session.execute(
                    select(LottoStatistics).where(LottoStatistics.num == num)
                )
                stat = stat.scalar_one_or_none()
                
                if not stat:
                    # 새로운 통계 생성
                    stat = LottoStatistics(
                        num=num,
                        main_count=0,
                        bonus_count=0,
                        total_count=0
                    )
                    db_session.add(stat)
                
                # 카운트 업데이트
                if num in main_numbers:
                    stat.main_count += 1
                    stat.total_count += 1
                elif num == bonus_number:
                    stat.bonus_count += 1
                    stat.total_count += 1
                
                # 마지막 출현 정보 업데이트
                if num in main_numbers or num == bonus_number:
                    stat.last_round = lotto_data["round"]
                    stat.last_date = lotto_data["draw_date"]
            
            await db_session.commit()
            print(f"회차 {lotto_data['round']}: 통계 업데이트 완료")
            
        except Exception as e:
            await db_session.rollback()
            print(f"회차 {lotto_data['round']}: 통계 업데이트 오류 - {e}")
    
    async def import_lotto_data(self, start_drw_no: int = 1, end_drw_no: int = 1183):
        """지정된 범위의 로또 데이터를 가져와서 저장합니다."""
        print(f"로또 데이터 가져오기 시작: 회차 {start_drw_no} ~ {end_drw_no}")
        
        async with httpx.AsyncClient() as client:
            async with self.db.session() as db_session:
                success_count = 0
                error_count = 0
                
                for drw_no in range(start_drw_no, end_drw_no + 1):
                    print(f"처리 중: 회차 {drw_no}")
                    
                    # API에서 데이터 가져오기
                    api_data = await self.fetch_lotto_data(client, drw_no)
                    if not api_data:
                        error_count += 1
                        continue
                    
                    # 데이터 파싱
                    lotto_data = self.parse_lotto_data(api_data)
                    
                    # 데이터베이스에 저장
                    if await self.save_lotto_draw(db_session, lotto_data):
                        # 통계 업데이트
                        await self.update_statistics(db_session, lotto_data)
                        success_count += 1
                    else:
                        error_count += 1
                    
                    # API 호출 간격 조절 (서버 부하 방지)
                    await asyncio.sleep(0.1)
                
                print(f"\n가져오기 완료:")
                print(f"성공: {success_count}개")
                print(f"실패: {error_count}개")
    
    async def close(self):
        """데이터베이스 연결을 종료합니다."""
        await self.db.close()


async def main():
    """메인 함수"""
    importer = LottoDataImporter()
    
    try:
        # 전체 회차 데이터 가져오기 (1~1183)
        await importer.import_lotto_data(1, 1183)
        
        # 또는 특정 범위만 가져오기
        # await importer.import_lotto_data(1100, 1183)
        
    except KeyboardInterrupt:
        print("\n사용자에 의해 중단되었습니다.")
    except Exception as e:
        print(f"오류 발생: {e}")
    finally:
        await importer.close()


if __name__ == "__main__":
    asyncio.run(main()) 