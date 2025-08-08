# tts.py
import os
import base64
import asyncio
from typing import AsyncGenerator, Generator, Optional
from dotenv import load_dotenv
from hume import AsyncHumeClient
from hume.tts import PostedUtterance, PostedContextWithGenerationId, FormatPcm

load_dotenv()
api_key = os.getenv("HUME_API_KEY")
if not api_key:
    raise EnvironmentError("HUME_API_KEY not found in environment variables")

hume = AsyncHumeClient(api_key=api_key)
VOICE_ID = "2ca55181-9d21-43b3-9e6e-0cb24a669e6c"

async def stream_tts_pcm_bytes(texts: list[str]):
    speech = await hume.tts.synthesize_json(
        utterances=[PostedUtterance(text="init")],
        format=FormatPcm(type="pcm"),
        voice=VOICE_ID,
    )
    gen_id = speech.generations[0].generation_id

    async for snippet in hume.tts.synthesize_json_streaming(
        context=PostedContextWithGenerationId(generation_id=gen_id),
        utterances=[PostedUtterance(text=t) for t in texts],
        format=FormatPcm(type="pcm"),
        voice=VOICE_ID,
    ):
        yield base64.b64decode(snippet.audio)

def stream_tts_pcm_bytes_sync(texts: list[str]) -> Generator[bytes, None, None]:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    agen = stream_tts_pcm_bytes(texts)
    try:
        while True:
            chunk = loop.run_until_complete(agen.__anext__())
            yield chunk
    except StopAsyncIteration:
        pass
    finally:
        loop.run_until_complete(agen.aclose())
        loop.close()
