export default {
  async fetch(request) {
    const url = new URL(request.url);
    const id = url.searchParams.get("id");
    const search = url.searchParams.get("search");

    try {
      // 🔍 SEARCH
      if (search) {
        const res = await fetch(
          `https://v2.sg.media-imdb.com/suggestion/${search[0]}/${search}.json`
        );
        const data = await res.json();

        return json({
          query: search,
          results: data.d?.map(x => ({
            id: x.id,
            title: x.l,
            year: x.y,
            type: x.q,
            poster: x.i?.imageUrl
          })) || []
        });
      }

      // 🎬 MOVIE DETAILS
      if (id) {
        const res = await fetch(`https://www.imdb.com/title/${id}/`);
        const html = await res.text();

        // safer parsing
        const get = (regex) => html.match(regex)?.[1] || null;

        return json({
          id,
          title: get(/<title>(.*?)<\/title>/),
          year: get(/"datePublished":"(\d{4})"/),
          rating: get(/"ratingValue":\s*"([^"]+)"/),
          votes: get(/"ratingCount":\s*"([^"]+)"/),
          poster: get(/"image":"([^"]+)"/),
          description: get(/"description":"([^"]+)"/)
        });
      }

      return json({ error: "Use ?id= or ?search=" });

    } catch (e) {
      return json({ error: e.message });
    }
  }
};

function json(data) {
  return new Response(JSON.stringify(data, null, 2), {
    headers: { "content-type": "application/json" }
  });
}
