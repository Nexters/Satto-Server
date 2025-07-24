from pathlib import Path
from typing import Any, Dict

import yaml


class HCXUtils:
    @staticmethod
    def load_yaml_prompts(yaml_filename: str) -> Dict[str, Any]:
        """YAML 파일에서 프롬프트 로드"""
        yaml_path = Path(__file__).parents[2] / 'hcx_client' / 'prompts' / yaml_filename
        with open(yaml_path, 'r', encoding='utf-8') as file:
            prompts = yaml.safe_load(file)
        return prompts

    @staticmethod
    def get_prompt_pair(yaml_filename: str, prompt_key: str) -> tuple[str, str]:
        """특정 프롬프트 키의 system/user 프롬프트 반환"""
        prompts = HCXUtils.load_yaml_prompts(yaml_filename)
        prompt_section = prompts.get(prompt_key, {})
        system_prompt = prompt_section.get('system_prompt', '')
        user_prompt = prompt_section.get('user_prompt', '')
        return system_prompt, user_prompt
