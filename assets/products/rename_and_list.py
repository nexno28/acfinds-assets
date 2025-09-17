import os

# === Schritt 1: Namen für den Produktordner abfragen ===
ordner = input("Name des Produktordners (z.B. stone_island_sweat): ").strip()
if not ordner:
    print("Ordnername darf nicht leer sein.")
    exit(1)

# === Schritt 2: Absoluter Pfad berechnen, aber für die Ausgabe nur den Ordnernamen nutzen ===
ordner_abs = os.path.abspath(ordner)
if not os.path.isdir(ordner_abs):
    print(f"Ordner '{ordner}' wurde nicht gefunden!")
    exit(1)

# === Schritt 3: Alle PNG/JPG/JPEG finden und sortieren ===
alle_bilder = [f for f in os.listdir(ordner_abs) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
alle_bilder.sort()

# === Schritt 4: Umbenennen im Produktordner (nur im Zielordner!) ===
for i, filename in enumerate(alle_bilder, 1):
    ext = os.path.splitext(filename)[1].lower()
    zielname = f"{i}{ext}"
    src = os.path.join(ordner_abs, filename)
    dst = os.path.join(ordner_abs, zielname)
    if filename != zielname:
        os.rename(src, dst)

# Nach Umbenennung die aktualisierte Liste holen
alle_bilder = [f for f in os.listdir(ordner_abs) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
alle_bilder.sort(key=lambda x: int(os.path.splitext(x)[0]))

# === Schritt 5: Fertige Bildpfade-Liste erstellen ===
result = ", ".join([f"{ordner}/{bild}" for bild in alle_bilder])
print("\nFertige Bildliste für JSON:\n")
print(result)
print("\nKopiere diesen String in deinen Admin-Tool!")

# === Optional: In Zwischenablage kopieren ===
try:
    import pyperclip
    pyperclip.copy(result)
    print("\n--> Die Bildliste wurde auch in die Zwischenablage kopiert!")
except ImportError:
    print("\nTipp: Installiere pyperclip mit 'pip install pyperclip', dann wird der Output direkt kopiert.")
