import json
import google.generativeai as genai
from tenacity import retry, stop_after_attempt, wait_exponential
from app.core.config import settings

from loguru import logger

JOURNAL_SCHEMA = {
    "type": "object",
    "properties": {
        "summary": {"type": "string"},
        "main_tasks": {"type": "array", "items": {"type": "string"}},
        "learned_things": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["summary", "main_tasks", "learned_things"],
}

class GeminiService:
    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(
            model_name=settings.GEMINI_MODEL,
            generation_config={
                "temperature": settings.GEMINI_TEMPERATURE,
                "max_output_tokens": settings.GEMINI_MAX_TOKENS,
                "response_mime_type": "application/json",
                "response_schema": JOURNAL_SCHEMA,
            }
        )
    
    @retry(
        stop=stop_after_attempt(3), # 최대 3회 재시도
        wait = wait_exponential(multiplier=1, min=1, max=4) # 1초 -> 2초 -> 4초
    )
    async def generate_journal(self, commits: list[dict], date: str = "Today") -> dict:
        """
        커밋 데이터를 분석하여 개발 일지를 생성
        """
        logger.info(f"커밋 데이터 분석 및 개발 일지 생성 진입: {len(commits)} | Date:{date}")
        
        if not commits:
            return {
                "summary": "작업 내역이 없습니다.",
                "main_tasks": [],
                "learned_things": [],
            }
        
        # 커밋 수 및 메타데이터 추출
        commit_count = len(commits)
        
        # 브랜치 정보는 GitHub API 커밋 응답에 직접적으로 포함되지 않을 수 있음 
        # (필요하다면 상위 호출에서 전달받아야 함. 일단 제거하거나 'main'으로 고정)
        prompt = self._build_prompt(commits, date, commit_count)
        response = await self.model.generate_content_async(prompt)
        
        try:
            return json.loads(response.text)
        
        except json.JSONDecodeError:
            # 재시도 트리커를 위해 에러 발생
            raise ValueError("❌GEMINI reponse를 json으로 파싱하는데 실패")
        
    def _build_prompt(self, commits: list[dict], date: str, commit_count: int) -> str:
        # 커밋 메시지들을 문자열로 변환
        commits_text = json.dumps(commits, ensure_ascii=False, indent=2)
        return f"""
        # Role
        Senior Backend Architect & Tech Writer

        # Context
        다음은 {date}의 Git 커밋 로그입니다.
        - 총 커밋 수: {commit_count}개

        [Commits Data]
        {commits_text}

        # Task
        위 커밋 데이터를 분석하여 개발 일지를 작성하세요.
        커밋 메시지, 변경된 파일명, diff 내용을 종합적으로 고려하여 작성합니다.

        # Output Format (JSON)
        {{
        "summary": "3문장으로 작성 (경어체)",
        "main_tasks": ["기술적 성과 1 (구체적 수치/효과 포함)", "..."],
        "learned_things": ["코드 변화에서 도출된 인사이트", "..."]
        }}

        # Constraints
        - summary: 정확히 3문장 (작업 흐름 → 주요 성과 → 기술적 의의 순서 권장)
        - main_tasks: 중요도 순 정렬, 최대 5개, trivial 커밋 제외
        - learned_things: 반드시 커밋 내용 기반, 최소 1개 이상
        - 기술 용어는 한글(영문) 형태로 병기
        - 수치가 있다면 반드시 포함
        - JSON 형식을 엄격히 준수
        
        # Examples
        ## Good Example:
        {{
        "summary": "Redis 캐싱 전략을 도입하여 API 응답 속도를 개선했습니다. 사용자 인증 로직을 JWT 기반으로 전환하여 보안을 강화했습니다. 테스트 커버리지를 65%에서 82%로 향상시켰습니다.",
        "main_tasks": [
            "Redis LFU 캐싱 전략 도입으로 주요 API 응답시간 40% 단축 (평균 200ms → 120ms)"
        ],
        "learned_things": [
            "Redis의 LFU와 LRU 정책 차이: 장기 접속 패턴에서는 LFU가 히트율이 12% 더 높음을 확인"
        ]
        }}

        ## Bad Example:
        {{
        "summary": "오늘 열심히 개발했습니다.",
        "main_tasks": ["코드 수정"],
        "learned_things": ["많은 것을 배웠습니다"]
        }}
        """

        