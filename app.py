import hashlib
import json
import os
import secrets
import time
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, Response
from nacl.exceptions import BadSignatureError
from nacl.signing import VerifyKey

app = FastAPI()
PUBLIC_KEY = os.environ["DISCORD_PUBLIC_KEY"]
IMAGE_PATH = Path(__file__).parent / "assets" / "diwali.png"

def verify_discord_request(request_timestamp: str, signature: str, body: bytes) -> bool:
    try:
        VerifyKey(bytes.fromhex(PUBLIC_KEY)).verify(
            request_timestamp.encode("utf-8") + body,
            bytes.fromhex(signature),
        )
        return True
    except (BadSignatureError, ValueError, TypeError):
        return False

def multipart_interaction_response(payload: dict, image_path: Path) -> Response:
    boundary = "----DiwaliWish" + secrets.token_hex(12)
    image_bytes = image_path.read_bytes()

    parts = [
        f"--{boundary}\r\n"
        'Content-Disposition: form-data; name="payload_json"\r\n'
        "Content-Type: application/json\r\n\r\n"
        + json.dumps(payload, ensure_ascii=False)
        + "\r\n",
        f"--{boundary}\r\n"
        'Content-Disposition: form-data; name="files[0]"; filename="diwali.png"\r\n'
        "Content-Type: image/png\r\n\r\n",
    ]
    body = parts[0].encode("utf-8") + parts[1].encode("utf-8") + image_bytes
    body += f"\r\n--{boundary}--\r\n".encode("utf-8")

    return Response(
        content=body,
        media_type=f"multipart/form-data; boundary={boundary}",
    )

@app.get("/")
async def health():
    return {"ok": True, "service": "Diwali Wish app"}

@app.post("/interactions")
async def interactions(request: Request):
    raw_body = await request.body()
    timestamp = request.headers.get("X-Signature-Timestamp", "")
    signature = request.headers.get("X-Signature-Ed25519", "")

    if not timestamp or not signature or not verify_discord_request(timestamp, signature, raw_body):
        return JSONResponse({"error": "Invalid request signature"}, status_code=401)

    interaction = json.loads(raw_body)

    # Discord sends PING when validating the Interactions Endpoint URL.
    if interaction.get("type") == 1:
        return JSONResponse({"type": 1})

    # This app is deliberately restricted to its own DM context.
    if interaction.get("context") != 1:
        return JSONResponse({
            "type": 4,
            "data": {
                "content": "Please use /wish in this app's DM.",
                "flags": 64,
            },
        })

    command_name = interaction.get("data", {}).get("name")
    if command_name != "wish":
        return JSONResponse({
            "type": 4,
            "data": {"content": "Unknown command.", "flags": 64},
        })

    if not IMAGE_PATH.is_file():
        return JSONResponse({
            "type": 4,
            "data": {"content": "The greeting image is missing from the app.", "flags": 64},
        })

    embed = {
        "title": "🪔 Happy Diwali!",
        "description": (
            "May the glow of every diya brighten your days, "
            "fill your home with happiness, and bring you a year "
            "full of peace, success, and beautiful moments.\n\n"
            "**Wishing you and your loved ones a joyful Festival of Lights!**"
            "Cool bot right? 😎"
        ),
        "color": 0xE6A23C,
        "image": {"url": "attachment://diwali.png"},
        "footer": {"text": "Ik this is better than typing normally lol (spent a whole day coding this)"},
    }

    payload = {
        "type": 4,
        "data": {
            "embeds": [embed],
            "attachments": [{"id": 0, "filename": "diwali.png"}],
        },
    }
    return multipart_interaction_response(payload, IMAGE_PATH)
