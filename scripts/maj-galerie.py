#!/usr/bin/env python3
"""Met à jour la galerie des cartes postales.

Usage : python3 scripts/maj-galerie.py

1. Déposer les images (jpg, png, webp) dans galerie/cartes/
   Préfixe facultatif pour indiquer la voie : v1-…, v2-…, v3-… (ex. v2-chat-pixel.jpg)
2. Lancer ce script : il crée les miniatures dans galerie/cartes/mini/
   et réécrit galerie/cartes.js (la liste lue par la page).

Nécessite Pillow (pip install Pillow).
"""
import json
import re
from pathlib import Path

from PIL import Image, ImageOps

RACINE = Path(__file__).resolve().parent.parent
DOSSIER = RACINE / "galerie" / "cartes"
MINI = DOSSIER / "mini"
SORTIE = RACINE / "galerie" / "cartes.js"
EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
TAILLE_MINI = 720  # px, plus grand côté


def cle_tri(chemin):
    # Tri « naturel » : carte-2 avant carte-10
    return [int(t) if t.isdigit() else t.lower() for t in re.split(r"(\d+)", chemin.name)]


def main():
    DOSSIER.mkdir(parents=True, exist_ok=True)
    MINI.mkdir(exist_ok=True)
    cartes = []
    images = sorted((p for p in DOSSIER.iterdir() if p.suffix.lower() in EXTENSIONS), key=cle_tri)
    for chemin in images:
        with Image.open(chemin) as im:
            im = ImageOps.exif_transpose(im)
            largeur, hauteur = im.size
            mini = MINI / (chemin.stem + ".webp")
            if not mini.exists() or mini.stat().st_mtime < chemin.stat().st_mtime:
                copie = im.convert("RGB")
                copie.thumbnail((TAILLE_MINI, TAILLE_MINI))
                copie.save(mini, "WEBP", quality=82)
        voie = re.match(r"v([123])[-_]", chemin.name, re.I)
        cartes.append({
            "src": f"cartes/{chemin.name}",
            "mini": f"cartes/mini/{mini.name}",
            "w": largeur,
            "h": hauteur,
            "voie": int(voie.group(1)) if voie else None,
        })

    # Supprime les miniatures orphelines
    noms = {Path(c["mini"]).name for c in cartes}
    for m in MINI.glob("*.webp"):
        if m.name not in noms:
            m.unlink()

    SORTIE.write_text(
        "// Fichier généré par scripts/maj-galerie.py : ne pas modifier à la main.\n"
        "window.CARTES = " + json.dumps(cartes, ensure_ascii=False, indent=1) + ";\n",
        encoding="utf-8",
    )
    print(f"{len(cartes)} carte(s) dans la galerie.")


if __name__ == "__main__":
    main()
