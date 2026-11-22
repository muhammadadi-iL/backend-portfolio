const store = require("./store");

function clean(value, max) {
  return String(value || "").replace(/[\r\n\t]+/g, " ").trim().slice(0, max);
}

function header(req, name) {
  const value = req.headers && req.headers[name];
  if (!value) return "";
  try {
    return decodeURIComponent(String(value));
  } catch (error) {
    return String(value);
  }
}

function clientIp(req) {
  const forwarded = String((req.headers && req.headers["x-forwarded-for"]) || "").split(",")[0].trim();
  if (forwarded) return forwarded;
  return (req.socket && req.socket.remoteAddress) || "";
}

function geo(req) {
  const city = clean(header(req, "x-vercel-ip-city"), 80);
  const area = clean(header(req, "x-vercel-ip-country-region"), 80);
  const country = clean(header(req, "x-vercel-ip-country"), 80);
  return {
    city: city,
    area: area,
    country: country,
    region: [city, area, country].filter(Boolean).join(", "),
  };
}

function localHost(req) {
  const host = String((req.headers && req.headers.host) || "")
    .split(":")[0]
    .replace(/^\[|\]$/g, "")
    .toLowerCase();
  return host === "localhost" || host === "127.0.0.1" || host === "::1";
}

async function writeLog(entry) {
  try {
    await store.appendRow("visits", entry);
  } catch (error) {
    console.error("visit store failed");
  }
}

module.exports = async function handler(req, res) {
  res.setHeader("Content-Type", "application/json");
  if (req.method === "GET") {
    if (!localHost(req)) {
      res.statusCode = 404;
      res.end(JSON.stringify({ error: "not found" }));
      return;
    }
    const visits = await store.readRows("visits");
    res.statusCode = 200;
    res.end(JSON.stringify({ visits: visits }));
    return;
  }
  if (req.method !== "POST") {
    res.statusCode = 405;
    res.setHeader("Allow", "GET, POST");
    res.end(JSON.stringify({ error: "GET or POST" }));
    return;
  }
  const body = req.body || {};
  const page = clean(body.path, 180);
  if (!page.startsWith("/") || page.startsWith("//")) {
    res.statusCode = 400;
    res.end(JSON.stringify({ error: "path required" }));
    return;
  }
  const place = geo(req);
  await writeLog({
    at: new Date().toISOString(),
    path: page,
    ip: clean(clientIp(req), 80),
    region: place.region,
    city: place.city,
    area: place.area,
    country: place.country,
    device: clean(body.device, 80),
    sessionId: clean(body.sessionId, 80),
    visitorId: clean(body.visitorId, 80),
    referrer: clean(body.referrer, 180),
    landing: clean(body.landing, 180),
  });
  res.statusCode = 200;
  res.end(JSON.stringify({ ok: true, region: place.region }));
};
