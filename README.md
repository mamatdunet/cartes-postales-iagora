# Cartes Post-IA-les : atelier IAgora

Site statique de l'atelier :

- `index.html` : page d'accueil des participants (choix de la voie 1, 2 ou 3).
- `galerie/` : galerie des cartes créées à IAgora Paris le samedi 10 octobre 2026.

## Ajouter les cartes à la galerie

1. Déposer les scans ou photos des cartes (jpg, png ou webp) dans le sous-dossier de leur voie :

   ```
   galerie/cartes/voie-1/   Ordinosaure
   galerie/cartes/voie-2/   IA frugale
   galerie/cartes/voie-3/   IA Rolls-Royce
   ```

   Une image posée directement dans `galerie/cartes/` s'affiche sans voie.
2. Lancer le script (Python 3 et Pillow). Sur Mac, le plus simple est un
   environnement Python dédié, créé une seule fois :

   ```
   python3 -m venv .venv
   .venv/bin/pip install Pillow
   .venv/bin/python scripts/maj-galerie.py
   ```

   Il crée les miniatures dans `galerie/cartes/mini/` et réécrit `galerie/cartes.js`.
   Les copies identiques d'une même image (« photo (1).png ») ne sont affichées qu'une fois,
   et les fichiers qui ne sont pas des images (vidéos…) sont ignorés : le script les signale.
3. Commiter le tout (images, miniatures et `cartes.js`).

Tant que la galerie est vide, elle affiche « Les cartes arrivent bientôt ».

### Prompts

Le script lit le prompt dans la métadonnée « description » de chaque image
(texte PNG écrit par Midjourney, EXIF ImageDescription ou XMP dc:description) ;
l'identifiant « Job ID » final de Midjourney est retiré. Dans la visionneuse,
le bouton « ✎ Voir le prompt » l'affiche, avec un bouton pour le copier.
Les cartes sans description s'affichent sans ce bouton.

## Album Google Photos (images Midjourney)

Lien de l'album : constante `ALBUM_GOOGLE_PHOTOS` dans `galerie/index.html`
Tant qu'elle est vide, le bouton affiche « Album bientôt en ligne ».

## Aperçu en local

```
python3 -m http.server 8000
```

puis ouvrir http://localhost:8000
