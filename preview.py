# preview.py
import asyncio
from fetch_professor import fetch_professor

async def main():
    docs = await fetch_professor("1935348")
    for d in docs[:5]:
        print(d)

asyncio.run(main())