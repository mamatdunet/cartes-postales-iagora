// Cartes publiées depuis les outils de l'atelier :
//   voie 1 · WordArt 97 (wordart-iagora.vercel.app)
//   voie 2 · PixelGPT   (cartes-iagora.vercel.app)
// GET  /api/cartes : liste des cartes publiées (les plus récentes d'abord)
// POST /api/cartes : { image: "data:image/jpeg;base64,…", w, h, pseudo?: "Léa", voie?: 1 | 2 }
// Les images vivent dans le store Vercel Blob du projet (dossier publiees/voie-N/).
// Le prénom et les dimensions sont rangés dans le nom du fichier, pour que
// la liste se lise en un seul appel. Pour retirer une carte : onglet Storage
// du projet sur vercel.com, ou `vercel blob del <url>`.
import { list, put } from "@vercel/blob";

const ORIGINES = [
  "https://wordart-iagora.vercel.app",
  "https://cartes-iagora.vercel.app",
  "http://localhost:8080",
  "http://localhost:8765",
  "http://127.0.0.1:8765",
];
const DOSSIER = "publiees/";
const VOIES = [1, 2];
const TAILLE_MAX = 3.5 * 1024 * 1024; // octets d'image décodée (limite Vercel : 4,5 Mo par requête)
const TYPES = { "image/jpeg": "jpg", "image/png": "png", "image/webp": "webp" };

function entetes(request) {
  const origine = request.headers.get("origin");
  const h = { "Content-Type": "application/json; charset=utf-8", Vary: "Origin" };
  if (ORIGINES.includes(origine)) {
    h["Access-Control-Allow-Origin"] = origine;
    h["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS";
    h["Access-Control-Allow-Headers"] = "Content-Type";
  }
  return h;
}
const repondre = (request, corps, statut = 200, extra = {}) =>
  new Response(JSON.stringify(corps), { status: statut, headers: { ...entetes(request), ...extra } });

// Prénom : lettres, chiffres, espaces et ponctuation simple, 30 caractères au plus
function nettoyerPseudo(p) {
  return String(p || "")
    .normalize("NFC")
    .replace(/[^\p{L}\p{N} '’._-]/gu, "")
    .replace(/\s+/g, " ")
    .trim()
    .slice(0, 30);
}
const versB64 = s => Buffer.from(s, "utf8").toString("base64url");
const depuisB64 = s => { try { return Buffer.from(s, "base64url").toString("utf8"); } catch { return ""; } };

export function OPTIONS(request) {
  return new Response(null, { status: 204, headers: entetes(request) });
}

export async function GET(request) {
  const cartes = [];
  let curseur;
  do {
    const page = await list({ prefix: DOSSIER, cursor: curseur, limit: 1000 });
    for (const b of page.blobs) {
      // publiees/voie-<N>/<horodatage>-<largeur>x<hauteur>-<prénom en base64url>.<ext>
      const m = b.pathname.slice(DOSSIER.length).match(/^voie-(\d)\/(\d+)-(\d+)x(\d+)-([A-Za-z0-9_-]*)\.\w+$/);
      if (!m) continue;
      cartes.push({ src: b.url, mini: b.url, w: +m[3], h: +m[4], voie: +m[1], pseudo: depuisB64(m[5]) || null, date: +m[2] });
    }
    curseur = page.hasMore ? page.cursor : undefined;
  } while (curseur);
  cartes.sort((a, b) => b.date - a.date);
  return repondre(request, cartes, 200, { "Cache-Control": "public, s-maxage=20, stale-while-revalidate=60" });
}

export async function POST(request) {
  if (!ORIGINES.includes(request.headers.get("origin"))) return repondre(request, { erreur: "Origine refusée" }, 403);
  let donnees;
  try { donnees = await request.json(); } catch { return repondre(request, { erreur: "Requête illisible" }, 400); }
  const m = /^data:(image\/(?:jpeg|png|webp));base64,([A-Za-z0-9+/=]+)$/.exec(donnees?.image || "");
  if (!m) return repondre(request, { erreur: "Image manquante" }, 400);
  const octets = Buffer.from(m[2], "base64");
  if (!octets.length || octets.length > TAILLE_MAX) return repondre(request, { erreur: "Image trop lourde" }, 413);
  const w = Math.round(+donnees.w), h = Math.round(+donnees.h);
  if (!(w > 0 && h > 0 && w <= 6000 && h <= 6000)) return repondre(request, { erreur: "Dimensions invalides" }, 400);
  const voie = donnees.voie == null ? 1 : +donnees.voie;
  if (!VOIES.includes(voie)) return repondre(request, { erreur: "Voie inconnue" }, 400);
  const pseudo = nettoyerPseudo(donnees.pseudo);
  const nom = `${DOSSIER}voie-${voie}/${Date.now()}-${w}x${h}-${versB64(pseudo)}.${TYPES[m[1]]}`;
  const blob = await put(nom, octets, { access: "public", contentType: m[1], addRandomSuffix: false });
  return repondre(request, { ok: true, src: blob.url, voie, pseudo: pseudo || null }, 201);
}
