import json
import re


class Parser:
    @staticmethod
    def parse_four_pillar(content: str):
        # 마크다운 JSON 블록에서 JSON 추출
        json_match = re.search(r"```json\s*(\{.*?\})\s*```", content, re.DOTALL)
        if json_match:
            try:
                json_str = json_match.group(1)
                json_data = json.loads(json_str)
                return json_data
            except json.JSONDecodeError as e:
                raise ValueError(f"JSON 파싱 오류: {e}")
            except Exception as e:
                raise ValueError(f"모델 검증 오류: {e}")

        # 일반 코드 블록에서 JSON 추출 (```json이 아닌 경우)
        code_match = re.search(r"```\s*(\{.*?\})\s*```", content, re.DOTALL)
        if code_match:
            try:
                json_str = code_match.group(1)
                json_data = json.loads(json_str)
                return json_data
            except json.JSONDecodeError as e:
                raise ValueError(f"JSON 파싱 오류: {e}")
            except Exception as e:
                raise ValueError(f"모델 검증 오류: {e}")

        # JSON 블록을 찾지 못한 경우
        raise ValueError("마크다운 JSON 블록을 찾을 수 없습니다.")
