#!/usr/bin/env python3
"""Met à jour la galerie des cartes postales.

Usage : python3 scripts/maj-galerie.py

1. Déposer les images (jpg, png, webp) dans le sous-dossier de leur voie :
   galerie/cartes/voie-1/, galerie/cartes/voie-2/, galerie/cartes/voie-3/
   (une image posée directement dans galerie/cartes/ s'affiche sans voie)
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
    # (dossier, voie) : d'abord les trois voies, puis les images sans voie
    sources = [(DOSSIER / f"voie-{v}", v) for v in (1, 2, 3)] + [(DOSSIER, None)]
    for dossier, voie in sources:
        dossier.mkdir(exist_ok=True)
        images = sorted((p for p in dossier.iterdir() if p.suffix.lower() in EXTENSIONS), key=cle_tri)
        for chemin in images:
            relatif = chemin.relative_to(DOSSIER)
            mini = MINI / relatif.with_suffix(".webp")
            mini.parent.mkdir(parents=True, exist_ok=True)
            with Image.open(chemin) as im:
                im = ImageOps.exif_transpose(im)
                largeur, hauteur = im.size
                if not mini.exists() or mini.stat().st_mtime < chemin.stat().st_mtime:
                    copie = im.convert("RGB")
                    copie.thumbnail((TAILLE_MINI, TAILLE_MINI))
                    copie.save(mini, "WEBP", quality=82)
            cartes.append({
                "src": f"cartes/{relatif.as_posix()}",
                "mini": f"cartes/mini/{mini.relative_to(MINI).as_posix()}",
                "w": largeur,
                "h": hauteur,
                "voie": voie,
            })

    # Supprime les miniatures orphelines
    gardees = {MINI / Path(c["mini"]).relative_to("cartes/mini") for c in cartes}
    for m in MINI.rglob("*.webp"):
        if m not in gardees:
            m.unlink()

    SORTIE.write_text(
        "// Fichier généré par scripts/maj-galerie.py : ne pas modifier à la main.\n"
        "window.CARTES = " + json.dumps(cartes, ensure_ascii=False, indent=1) + ";\n",
        encoding="utf-8",
    )
    print(f"{len(cartes)} carte(s) dans la galerie.")


if __name__ == "__main__":
    main()
