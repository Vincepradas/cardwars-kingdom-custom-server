import argparse
import base64
import gzip
import json
import os
from io import BytesIO
from pathlib import Path

DEFAULT_USERNAME = "10b6f2a5-58e7-4707-94f9-626a65a76f14"
DEFAULT_JSON_FILE = Path("data.json")


def encode_game(username: str, game: dict) -> bytes:
    # Compact JSON (must match server format).
    json_data = json.dumps(game, separators=(",", ":"), ensure_ascii=False)

    buffer = BytesIO()
    with gzip.GzipFile(fileobj=buffer, mode="wb") as gz:
        gz.write(json_data.encode("utf-8"))

    encoded = base64.b64encode(buffer.getvalue()).decode("utf-8")
    final = f"username={username}&data={encoded}"
    return final.encode("utf-8")


def update_from_file(username: str, json_file: Path) -> int:
    if not json_file.exists():
        print("ERROR: source JSON file not found:", json_file)
        return 1

    with json_file.open("r", encoding="utf-8") as f:
        game_data = json.load(f)

    encoded_save = encode_game(username, game_data)

    # Import after env setup so app picks up SQLITE_PATH from --db.
    from app import app, db, Player

    print("Using DB:", app.config["SQLALCHEMY_DATABASE_URI"])

    with app.app_context():
        player = Player.query.filter_by(username=username).first()
        if not player:
            print("ERROR: Player not found in DB:", username)
            return 2

        player.game = encoded_save
        db.session.commit()

    print("OK: Save updated successfully for", username)
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Encode JSON save and write to Player.game")
    parser.add_argument("--username", default=DEFAULT_USERNAME, help="Player UUID/username to update")
    parser.add_argument("--json", dest="json_file", default=str(DEFAULT_JSON_FILE), help="Path to source JSON file")
    parser.add_argument("--db", dest="db_path", default=None, help="Absolute SQLITE_PATH override")
    args = parser.parse_args()

    if args.db_path:
        os.environ["SQLITE_PATH"] = args.db_path

    raise SystemExit(update_from_file(args.username, Path(args.json_file)))
