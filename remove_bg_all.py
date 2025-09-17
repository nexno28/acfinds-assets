# remove_bg_all.py
import sys
import time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

from rembg import remove, new_session
from PIL import Image

# --- Einstellungen ---
INPUT_ROOT = Path("assets/products")          # Quell-Root (RELATIV zum Script)
OUTPUT_ROOT = Path("assets/products_no_bg")   # Ziel-Root (RELATIV zum Script)
MAX_WORKERS = 4                               # Parallelität
VALID_EXTS = {".png", ".jpg", ".jpeg", ".webp"}
RETRY_READS = 3                               # bei WinError 32 o. ä. erneut versuchen
RETRY_SLEEP = 0.5

# Session einmal erstellen -> verhindert x-faches Model-Download
SESSION = new_session("u2net")  # default, sehr gut für Produkte

def ensure_dir(p: Path):
    p.mkdir(parents=True, exist_ok=True)

def find_images(root: Path):
    for p in root.rglob("*"):
        if p.is_file() and p.suffix.lower() in VALID_EXTS:
            yield p

def output_path_for(src_file: Path, in_root_abs: Path, out_root_abs: Path) -> Path:
    # sichere Relativierung: beide absolut & gleicher Anchor
    rel = src_file.relative_to(in_root_abs)
    out = out_root_abs / rel
    return out.with_suffix(".png")

def load_image_with_retries(src_file: Path) -> Image.Image:
    last_err = None
    for _ in range(RETRY_READS):
        try:
            im = Image.open(src_file)
            # Datei entkoppeln (Pillow hält sonst den Filehandle)
            return im.convert("RGBA").copy()
        except Exception as e:
            last_err = e
            time.sleep(RETRY_SLEEP)
    raise last_err

def process_image(src_file: Path, in_root_abs: Path, out_root_abs: Path) -> tuple[Path, bool, str]:
    try:
        out_path = output_path_for(src_file, in_root_abs, out_root_abs)

        # Skip wenn bereits vorhanden (idempotent, schnellere Re-Runs)
        if out_path.exists():
            return (src_file, True, f"skip (exists) -> {out_path}")

        ensure_dir(out_path.parent)

        im_rgba = load_image_with_retries(src_file)
        out_rgba = remove(im_rgba, session=SESSION)  # eine Session für alle Threads

        # PNG mit Transparenz speichern
        out_rgba.save(out_path, format="PNG", optimize=True)
        return (src_file, True, f"OK -> {out_path}")
    except Exception as e:
        return (src_file, False, f"ERROR: {e}")

def main():
    in_root_abs = Path(INPUT_ROOT).resolve()
    out_root_abs = Path(OUTPUT_ROOT).resolve()

    print("------------------------------------------------------------")
    print(f"INPUT : {in_root_abs}")
    print(f"OUTPUT: {out_root_abs}")
    print("------------------------------------------------------------")

    if not in_root_abs.exists():
        print("❌ Eingabeordner nicht gefunden.")
        sys.exit(1)

    files = list(find_images(in_root_abs))
    print(f"Gefundene Dateien: {len(files)}")
    if not files:
        print("Keine passenden Bilder gefunden.")
        return

    ok_count = 0
    err_count = 0

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as ex:
        futures = {ex.submit(process_image, f, in_root_abs, out_root_abs): f for f in files}
        for fut in as_completed(futures):
            src, ok, msg = fut.result()
            if ok:
                ok_count += 1
                print(f"✅ {src}: {msg}")
            else:
                err_count += 1
                print(f"❌ {src}: {msg}")

    print("------------------------------------------------------------")
    print(f"Fertig. Erfolgreich: {ok_count}, Fehler: {err_count}")

if __name__ == "__main__":
    main()
