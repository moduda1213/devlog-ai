import json
from datetime import date as date_type
from uuid import UUID

from redis.asyncio import Redis
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.models import Journal, User, Repository
from app.schemas.journal import JournalCreate, JournalUpdate, JournalResponse, JournalStatusResponse
from app.services.gemini_service import GeminiService
from app.services.github_service import fetch_commits, GithubNoCommitsError

from loguru import logger

class JournalService:
    def __init__(self, db: AsyncSession, redis: Redis = None):
        self.db = db
        self.redis = redis
        self.gemini_service = GeminiService()
    
    async def check_daily_status(
        self,
        user: User,
        date: date_type
    ) -> JournalStatusResponse:
        """오늘 일지 생성 상태 확인"""
        # 1. 기존 일지 존재 여부 확인
        stmt = select(Journal).where(
            Journal.user_id == user.id,
            Journal.repository_id == user.selected_repo_id,
            Journal.date == date
        )
        result = await self.db.execute(stmt)
        has_journal = result.scalar_one_or_none() is not None

        # 2. 커밋 존재 여부 확인
        has_commits = False
        if user.selected_repo_id:
            # Repository 정보 조회
            repo_stmt = select(Repository).where(Repository.id == user.selected_repo_id)
            repo_result = await self.db.execute(repo_stmt)
            repo = repo_result.scalar_one_or_none()

            if repo:
                try:
                    # 커밋 조회 시도 (에러 발생 시 커밋 없음으로 처리)
                    await fetch_commits(
                        repo_name=repo.repo_name,
                        target_date=date,
                        access_token=user.decrypted_access_token
                    )
                    has_commits = True
                except GithubNoCommitsError:
                    has_commits = False
                except Exception as e:
                    logger.warning(f"커밋 확인 중 에러: {e}")
                    has_commits = False

        return JournalStatusResponse(
            date=date,
            has_journal=has_journal,
            has_commits=has_commits,
            can_generate=has_commits # (선택사항: and not has_journal 조건을 넣을 수도 있음)
        )
        
    async def create_daily_journal(
        self,
        user: User,
        date: date_type,
        overwrite: bool = True
    ) -> Journal:
        """
        1. 저장소 정보 확인
        2. GitHub 커밋 수집
        3. Gemini AI 분석
        4. DB Upsert (트랜잭션)
        """
        logger.info("✅ [JournalService] 깃허브 커밋 일지 생성 함수 진입!!")
        
        # 1. 선택된 저장소 확인 (Eager Loading 필요)
        if not user.selected_repo_id:
             raise ValueError("No repository selected")
         
        # User 객체에 repositories가 로드되지 않았을 수 있으므로 DB에서 조회
        stmt = select(Repository).where(Repository.id == user.selected_repo_id)
        try:
            result = await self.db.execute(stmt)
            repo = result.scalar_one_or_none()
            
            if not repo:
                raise ValueError("Repository not found")
            
            # 2. 커밋 수집
            commits = await fetch_commits(
                repo_name=repo.repo_name,
                target_date=date,
                access_token=user.decrypted_access_token
            )
            
            # 3. AI 분석
            ai_data = await self.gemini_service.generate_journal(commits, date)
            
            # 통계 추출 (GitHub 커밋 데이터에서 계산)
            stats = self._calculate_stats(commits)
            logger.info(f"통계 추출: {stats}")
            journal_data = JournalCreate(
                user_id=user.id,
                repository_id=repo.id,
                date=date,
                raw_commits=commits,  # 디버깅용 저장
                **ai_data,            # summary, main_tasks, learned_things
                **stats               # commit_count, files_changed 등
            )
            
            # 4. DB 저장 (Upsert)
            # upsert 로직 수행 (add, update 등)
            journal = await self._upsert_journal(journal_data, overwrite)
            
            # ✅ 핵심: 모든 작업이 성공적으로 끝나면 여기서 커밋
            await self.db.commit()
            
            # 커밋 후 객체 리프레시 (DB에서 최신 데이터 로드)
            await self.db.refresh(journal)
            return journal
        
        except Exception as e:
            # 에러 발생 시 롤백하여 데이터 정합성 유지
            await self.db.rollback()
            raise e
    
    def _calculate_stats(self, commits: list[dict]) -> dict:
        """커밋 리스트에서 통계 정보 추출 (Optimized Structure 대응)"""
        files_changed = 0
        lines_added = 0
        lines_deleted = 0
        
        for commit in commits:
            files = commit.get("files", [])
            files_changed += len(files)
            for f in files:
                lines_added += f.get("additions", 0)
                lines_deleted += f.get("deletions", 0)
                
        return {
            "commit_count": len(commits),
            "files_changed": files_changed,
            "lines_added": lines_added,
            "lines_deleted": lines_deleted,
        }
        
    async def _upsert_journal(self, data: JournalCreate, overwrite: bool) -> Journal:
        logger.info("[JournalService] 일지 생성 및 덮어씌기 commit함수 진입")
        
        # 기존 일지 조회
        stmt = select(Journal).where(
            Journal.user_id == data.user_id,
            Journal.repository_id == data.repository_id,
            Journal.date == data.date
        )
        try:
            result = await self.db.execute(stmt)
            existing = result.scalar_one_or_none()
            
            if existing:
                if not overwrite:
                    raise ValueError("Journal already exists")
                
                # 업데이트
                for key, value in data.model_dump().items():
                    setattr(existing, key, value)
                    
                return existing
                
            # 신규 생성
            new_journal = Journal(**data.model_dump())
            self.db.add(new_journal)
            return new_journal
        
        except Exception as e:
            await self.db.rollback()
            raise e
    
    async def get_journals(
        self,
        user_id: UUID,
        repository_id: UUID,
        page: int = 1,
        size: int = 10,
        start_date: date_type | None = None,
        end_date: date_type | None = None,
    ) -> tuple[list[Journal], int]:
        try:
            """일지 목록 조회 (페이지네이션)"""
            conditions = [Journal.user_id == user_id]
            # 날짜 필터링
            if start_date:
                conditions.append(Journal.date >= start_date)
            if end_date:
                conditions.append(Journal.date <= end_date)
                
            if repository_id:
                conditions.append(Journal.repository_id == repository_id)    
            
            count_stmt = select(func.count()).select_from(Journal).where(*conditions)
            total = (await self.db.execute(count_stmt)).scalar() or 0
            
            stmt = (
                select(Journal)
                .options(joinedload(Journal.repository)) # N+1방지
                .where(*conditions)
                .order_by(Journal.date.desc())
                .offset((page-1) * size)
                .limit(size)
            )
            result = await self.db.execute(stmt)
            items = result.scalars().all()
            
            return items, total
        
        except Exception as e:
            await self.db.rollback()
            raise e
        
    async def get_journal_detail(self, user_id: UUID, journal_id: UUID) -> dict | Journal | None:
        """
        일지 상세 조회 (Redis Caching 적용)
        - Cache Hit: dict 반환
        - Cache Miss: Journal(ORM) 반환 (Router가 처리 가능)
        """
        cache_key = f"journal:{user_id}:{journal_id}"
        
        # 1. Redis 캐시 확인(Hit)
        if self.redis:
            try:
                cached_data = await self.redis.get(cache_key)
                if cached_data:
                    logger.info(f"⚡Cache Hit: {cache_key}")
                    return json.loads(cached_data) # dict 반환
            except Exception as e:
                logger.warning(f"Redis get error: {e}")
        
        # 2. DB 조회 (Miss)
        stmt = select(Journal).where(
            Journal.id == journal_id,
            Journal.user_id == user_id
        )
        result = await self.db.execute(stmt)
        journal = result.scalar_one_or_none()
        
        # 3. Redis 저장 (Set)
        if journal and self.redis:
            try:
                # pydantic 모델로 변환하여 JSON 직렬화
                # (ORM객체 -> Pydantic -> JSON)
                journal_data = JournalResponse.model_validate(journal).model_dump_json()
                
                await self.redis.setex(
                    cache_key,
                    86400, # TTL : 24H
                    journal_data
                )
                logger.info(f"💾 Cache Set: {cache_key}")
            except Exception as e:
                logger.warning(f"Redis set error: {e}")
        
        return journal
    
    async def _get_journal_orm(self, user_id: UUID, journal_id: UUID) -> Journal | None:
        """
        수정/삭제용 ORM 객체 직접 조회용 헬퍼메서드 (캐시 미사용)
        ㄴ 수정/삭제는 데이터 정합성이 중요하고 ORM 객체가 필요
        """
        stmt = select(Journal).where(
            Journal.id == journal_id,
            Journal.user_id == user_id
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def update_journal(
        self,
        user_id: UUID,
        journal_id: UUID,
        data: JournalUpdate
    ) -> Journal:
        try:
            """일지 수정"""
            journal = await self._get_journal_orm(user_id, journal_id)
            if not journal:
                raise ValueError("journal not found")
            
            update_date = data.model_dump(exclude_unset=True)
            for key, value in update_date.items():
                setattr(journal, key, value)
            
        
            self.db.add(journal)
            await self.db.commit()
            await self.db.refresh(journal)
            
            if self.redis:
                await self.redis.delete(f"journal:{user_id}:{journal_id}")
                logger.info("❌ Cache Invalidate")
            return journal
        
        except Exception as e:
            await self.db.rollback()
            raise e
        
    async def delete_journal(self, user_id: UUID, journal_id: UUID) -> None:
        """일지 삭제"""
        try:
            journal = await self._get_journal_orm(user_id, journal_id)
            
            if not journal:
                raise ValueError("Journal not found")
        
            await self.db.delete(journal)
            await self.db.commit()
            
            if self.redis:
                await self.redis.delete(f"journal:{user_id}:{journal_id}")
                logger.info("❌ Cache Invalidate")
                
        except Exception as e:
            await self.db.rollback()
            raise e