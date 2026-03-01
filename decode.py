import base64
import gzip
import json
import re
from io import BytesIO


def decode_game(encoded_string: str) -> dict:
    """
    Accepts:
        username=<uuid>&data=<base64_gzip_json>

    Returns:
        Python dictionary of game data
    """

    # 1️⃣ Validate format
    if "&data=" not in encoded_string:
        raise ValueError("Invalid format: missing '&data='")

    # 2️⃣ Extract base64 part
    base64_part = encoded_string.split("&data=", 1)[1].strip()

    # 3️⃣ Base64 decode
    try:
        compressed_bytes = base64.b64decode(base64_part)
    except Exception as e:
        raise ValueError("Base64 decode failed") from e

    # 4️⃣ GZIP decompress
    try:
        with gzip.GzipFile(fileobj=BytesIO(compressed_bytes)) as gz:
            json_bytes = gz.read()
    except Exception as e:
        raise ValueError("GZIP decompression failed") from e

    # 5️⃣ Decode to string
    json_string = json_bytes.decode("utf-8")

    # 6️⃣ Remove trailing commas (tolerant fix)
    json_string = re.sub(r",(\s*[}\]])", r"\1", json_string)

    # 7️⃣ Parse JSON
    try:
        game_dict = json.loads(json_string)
    except Exception as e:
        print("\n⚠️ Raw decompressed data preview:\n")
        print(json_string[:2000])
        raise ValueError("JSON parsing failed even after cleanup") from e

    return game_dict


# 🔬 Run as standalone tool
if __name__ == "__main__":
    encoded_input = input("Paste encoded save:\n").strip()

    try:
        decoded = decode_game(encoded_input)

        print("\n✅ DECODED DATA:\n")
        print(json.dumps(decoded, indent=2))

    except Exception as e:
        print("\n❌ Error:", e)