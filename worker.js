export default {
  async fetch(request) {
    const url = new URL(request.url);
    const path = url.pathname;

    try {
      // ✅ SEARCH ROUTE
      if (path === "/search") {
        const query = url.searchParams.get("query");
        if (!query) return json({ error: "Missing query" });

        const clean = query.split("(")[0].trim();

        const res = await fetch(
          `https://v2.sg.media-imdb.com/suggestion/${clean[0]}/${encodeURIComponent(clean)}.json`
        );
        const data = await res.json();

        return json({
          results: data.d?.map(x => ({
            id: x.id?.replace("tt", ""),
            title: x.l,
            year: x.y,
            type: normalizeType(x.q),
            poster: x.i?.imageUrl
          })) || []
        });
      }

      // ✅ TITLE ROUTE
      if (path.startsWith("/title/tt")) {
        const id = path.split("/")[2];

        const res = await fetch(`https://www.imdb.com/title/${id}/`);
        const html = await res.text();

        const get = (r) => html.match(r)?.[1] || null;

        return json({
          id: id.replace("tt", ""),
          title: get(/<title>(.*?)<\/title>/),
          year: get(/"datePublished":"(\d{4})"/),
          rating: get(/"ratingValue":\s*"([^"]+)"/),
          votes: get(/"ratingCount":\s*"([^"]+)"/),
          poster: get(/"image":"([^"]+)"/),
          description: get(/"description":"([^"]+)"/)
        });
      }

      // ✅ OPTIONAL: SEASON ROUTE (avoid crash)
      if (path.includes("/season/")) {
        return json({ episodes: [] });
      }

      return json({ error: "Invalid endpoint" });

    } catch (e) {
      return json({ error: e.message });
    }
  }
};

function normalizeType(q) {
  if (!q) return "movie";
  if (q.toLowerCase().includes("tv")) return "tvSeries";
  return "movie";
}

function json(data) {
  return new Response(JSON.stringify(data), {
    headers: { "content-type": "application/json" }
  });
}
