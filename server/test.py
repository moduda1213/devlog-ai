import copy
import asyncio
from app.core.database import engine
from sqlalchemy import text

state = {"user": {"tags": ["vips"]}}

a = state
b = state.copy()
c = copy.deepcopy(state)

state["user"]["tags"].append("paid")

print(a,b,c)
print(id(a["user"]["tags"][1]))
print(id(b["user"]["tags"][1]))
print(id(c["user"]["tags"][0]))


state["a"] = 3
b = state.copy()
print(a,b,c)
state["a"] = 4
print(a,b,c)

async def reset():
    async with engine.begin() as conn:
        await conn.execute(text("DROP TABLE IF EXISTS alembic_version"))
    print("✅ alembic_version table dropped.")
    
asyncio.run(reset())