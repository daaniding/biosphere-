// Serverless proxy voor Overpass (OpenStreetMap-bankjes).
// De browser roept /api/benches?s=..&w=..&n=..&e=.. aan op ONS eigen domein,
// zodat er geen CORS-problemen of geblokkeerde verbindingen in de browser zijn.
// Deze functie haalt de bankjes server-side op bij Overpass en geeft nette JSON terug.

const OVERPASS_ENDPOINTS = [
  "https://overpass-api.de/api/interpreter",
  "https://overpass.kumi.systems/api/interpreter",
  "https://overpass.private.coffee/api/interpreter",
  "https://maps.mail.ru/osm/tools/overpass/api/interpreter"
];

function num(v) {
  const n = parseFloat(v);
  return Number.isFinite(n) ? n : null;
}

module.exports = async (req, res) => {
  const q = req.query || {};
  const s = num(q.s), w = num(q.w), n = num(q.n), e = num(q.e);

  if (s === null || w === null || n === null || e === null) {
    res.status(400).json({ error: "bad_bbox", detail: "Geef s, w, n, e als getallen." });
    return;
  }
  // Voorkom te grote gebieden (Overpass timeout / misbruik).
  if (Math.abs(n - s) > 0.5 || Math.abs(e - w) > 0.5) {
    res.status(400).json({ error: "bbox_too_large", detail: "Zoom wat verder in." });
    return;
  }

  const query =
    `[out:json][timeout:25];node["amenity"="bench"](${s},${w},${n},${e});out;`;

  let lastErr = null;
  for (const url of OVERPASS_ENDPOINTS) {
    try {
      const controller = new AbortController();
      const timer = setTimeout(() => controller.abort(), 25000);
      const r = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: "data=" + encodeURIComponent(query),
        signal: controller.signal
      });
      clearTimeout(timer);
      if (!r.ok) throw new Error("HTTP " + r.status + " van " + url);
      const data = await r.json();
      const elements = Array.isArray(data.elements) ? data.elements : [];
      // Alleen wat de app nodig heeft doorsturen.
      const benches = elements
        .filter(el => typeof el.lat === "number" && typeof el.lon === "number")
        .map(el => ({ id: el.id, lat: el.lat, lon: el.lon, name: (el.tags && el.tags.name) || "" }));
      res.setHeader("Cache-Control", "public, max-age=60, s-maxage=300");
      res.status(200).json({ ok: true, count: benches.length, benches });
      return;
    } catch (err) {
      lastErr = err;
      // probeer de volgende server
    }
  }

  res.status(502).json({ error: "overpass_unreachable", detail: String(lastErr) });
};
