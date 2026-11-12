"""edge-tts wrapper that also works behind an HTTPS-inspecting proxy.

edge-tts opens its own websocket with aiohttp: it ignores HTTPS_PROXY and trusts only certifi.
So we pass the proxy explicitly and, when a custom CA bundle exists (TTS_CA_BUNDLE, or the
cloud sandbox's /root/.ccr/ca-bundle.crt), trust it. On a normal laptop neither is needed.
"""
import asyncio, os, ssl, sys
import edge_tts, edge_tts.communicate as C

_ca = os.environ.get("TTS_CA_BUNDLE") or ("/root/.ccr/ca-bundle.crt" if os.path.exists("/root/.ccr/ca-bundle.crt") else None)
if _ca:
    C._SSL_CTX = ssl.create_default_context(cafile=_ca)
VOICE = os.environ.get("TTS_VOICE", "vi-VN-HoaiMyNeural")   # nam: vi-VN-NamMinhNeural


async def go(text, out, voice=VOICE, rate="+8%"):
    proxy = os.environ.get("HTTPS_PROXY") or os.environ.get("https_proxy")
    await edge_tts.Communicate(text, voice, rate=rate, proxy=proxy).save(out)


if __name__ == "__main__":
    asyncio.run(go(sys.argv[1], sys.argv[2]))
