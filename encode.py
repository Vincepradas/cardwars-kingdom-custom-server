import json
import gzip
import base64
from io import BytesIO
from pathlib import Path

from app import app, db, Player


USERNAME = "10b6f2a5-58e7-4707-94f9-626a65a76f14"
JSON_FILE = Path("data.json")


def encode_game(username: str, game: dict) -> bytes:
    # Compact JSON (MUST match server format)
    json_data = json.dumps(game, separators=(",", ":"), ensure_ascii=False)

    # GZIP compress
    buffer = BytesIO()
    with gzip.GzipFile(fileobj=buffer, mode="wb") as gz:
        gz.write(json_data.encode("utf-8"))

    # Base64 encode
    encoded = base64.b64encode(buffer.getvalue()).decode("utf-8")

    # Wrap in expected format
    final = f"username={username}&data={encoded}"

    return final.encode("utf-8")


def update_from_file():
    if not JSON_FILE.exists():
        print("❌ game_data.json not found.")
        return

    # Load JSON file
    with JSON_FILE.open("r", encoding="utf-8") as f:
        game_data = json.load(f)

    encoded_save = encode_game(USERNAME, game_data)

    with app.app_context():
        player = Player.query.filter_by(username=USERNAME).first()

        if not player:
            print("❌ Player not found in DB.")
            return

        player.game = encoded_save
        db.session.commit()

        print("✅ Save updated successfully from JSON file.")


if __name__ == "__main__":
    update_from_file()