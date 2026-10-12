from pathlib import Path

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "output"


def save_digest(text: str) -> Path:
    OUTPUT_DIR.mkdir(exist_ok=True)
    output_file = OUTPUT_DIR / "latest_digest.txt"
    output_file.write_text(text, encoding="utf-8")
    return output_file
