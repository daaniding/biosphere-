# 🪑 Bankjesjacht

Een mobiele web-app om samen met een vriend(in) bankjes in de buurt af te vinken.
Zit je op een nieuw bankje? Maak een foto, geef een rating (sterren) en vink 'm af —
zo maak je samen de hele kaart vol.

## Wat kan het

- 🗺️ **Kaart** met OpenStreetMap.
- 🔎 **Bestaande bankjes laden** uit OpenStreetMap (`Laad bankjes hier`) — die staan er vaak al in.
- ＋ **Zelf een bankje toevoegen** op je huidige GPS-locatie.
- 📷 **Foto** maken + ⭐ **rating** (1–5 sterren) + notitie per bankje.
- ✅ **Afvinken**, met wie het afvinkte.
- 🎯 **Filters**: alles / nog te doen / afgevinkt / van mij.
- 📊 **Teller** bovenin: hoeveel van hoeveel afgevinkt.
- 🤝 **Samen delen** via Firebase (optioneel) óf lokaal op je eigen telefoon.

## Draaien (lokaal testen)

```bash
cd web
./start.sh
# open daarna http://localhost:8765/bankjes/ in je browser
```

Op je telefoon werkt de camera en GPS het beste als je de site via **https** opent
(bijv. gehost op GitHub Pages). Op `localhost` werkt het ook.

## Samen één kaart (Firebase aanzetten — gratis, ~5 min)

Zonder Firebase werkt alles, maar staat je data alleen op je eigen telefoon.
Wil je dat jij én je vriend dezelfde bankjes zien:

1. Ga naar <https://console.firebase.google.com> en maak een project.
2. Voeg een **Web-app** toe (het `</>`-icoon) en kopieer het `firebaseConfig`-object.
3. Ga naar **Build → Firestore Database → Create database** (start in *testmodus*).
4. Open de app → ⚙️ (rechtsboven) → plak de config, kies een **team-code**
   (bijv. `daan-en-max`) en klik **Opslaan**.
5. Je vriend doet hetzelfde met **dezelfde config + dezelfde team-code**.

Klaar — jullie zien nu samen dezelfde bankjes. 🎉

### Firestore-regels (belangrijk)

Testmodus laat na ~30 dagen niets meer toe. Voor een simpel privé-projectje voor
twee vrienden kun je in **Firestore → Rules** dit zetten (iedereen met jullie
team-code kan lezen/schrijven — prima voor bankjes):

```
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /teams/{team}/benches/{bench} {
      allow read, write: if true;
    }
  }
}
```

> Let op: dit is bewust open (geen login). Voor bankjes-data is dat geen probleem,
> maar zet er geen privé-info in.

## Hosten zodat je vriend het ook op zijn telefoon heeft

De makkelijkste gratis manier is **GitHub Pages**: zet de repo online, activeer
Pages, en deel de link `…/web/bankjes/`. Foto's en delen werken dan overal.

## Techniek

- Pure HTML/CSS/JS, geen build-stap.
- [Leaflet](https://leafletjs.com) (lokaal meegeleverd in `vendor/leaflet/`) voor de kaart.
- OpenStreetMap-tiles + Overpass API voor bestaande bankjes.
- Firebase Firestore voor het delen (dynamisch geladen, alleen als je 't instelt).
- Foto's worden gecomprimeerd (max ~900px, JPEG) zodat ze klein genoeg zijn om
  gratis via Firestore te delen — geen aparte foto-opslag nodig.
