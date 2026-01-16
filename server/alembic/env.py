import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# ----------------------------------------------------------------------
# 1. App 설정 및 모델 임포트 (마이그레이션 대상)
# ----------------------------------------------------------------------
from app.core.config import settings
from app.core.database import Base

# 모든 모델을 임포트해야 Base.metadata가 테이블을 인식합니다.
from app.models.user import User
from app.models.repository import Repository
from app.models.devlog import DevLog
# ----------------------------------------------------------------------

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.

config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

def run_migrations_offline() -> None:
    """오프라인 모드: DB 연결 없이 SQL 스크립트만 생성"""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()
        
def do_run_migrations(connection: Connection) -> None:
    """동기 연결을 사용하여 마이그레이션 실행"""
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()
        
async def run_migrations_online() -> None:
    """온라인 모드: 실제 DB에 연결하여 마이그레이션 실행"""
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
        
    await connectable.dispose()
    
if context.is_offline_mode():
    run_migrations_offline()
    
else:
    asyncio.run(run_migrations_online())