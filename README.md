# Cartes Post-IA-les : atelier IAgora

Site statique de l'atelier :

- `index.html` : page d'accueil des participants (choix de la voie 1, 2 ou 3).
- `galerie/` : galerie des cartes créées à IAgora Paris le samedi 10 octobre 2026.

## Ajouter les cartes à la galerie

1. Déposer les scans ou photos des cartes (jpg, png ou webp) dans `galerie/cartes/`.
   Pour indiquer la voie, préfixer le nom du fichier par `v1-`, `v2-` ou `v3-`
   (ex. `v2-chat-pixel.jpg`). Sans préfixe, la carte s'affiche sans voie.
2. Lancer le script (Python 3 et Pillow : `pip install Pillow`) :

   ```
   python3 scripts/maj-galerie.py
   ```

   Il crée les miniatures dans `galerie/cartes/mini/` et réécrit `galerie/cartes.js`.
3. Commiter le tout (images, miniatures et `cartes.js`).

Tant que la galerie est vide, elle affiche « Les cartes arrivent bientôt ».

## Album Google Photos (images Midjourney)

Renseigner le lien dans `galerie/index.html`, constante `ALBUM_GOOGLE_PHOTOS`.
Tant qu'elle est vide, le bouton affiche « Album bientôt en ligne ».

## Aperçu en local

```
python3 -m http.server 8000
```

puis ouvrir http://localhost:8000
