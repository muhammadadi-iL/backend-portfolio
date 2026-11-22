const https = require("https");

function siteKey() {
  return process.env.RECAPTCHA_SITE_KEY || "";
}

function secret() {
  return process.env.RECAPTCHA_SECRET_KEY || "";
}

function verify(token) {
  const body = new URLSearchParams({
    secret: secret(),
    response: token,
  }).toString();
  return new Promise((resolve) => {
    const request = https.request(
      {
        hostname: "www.google.com",
        path: "/recaptcha/api/siteverify",
        method: "POST",
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
          "Content-Length": Buffer.byteLength(body),
        },
      },
      (response) => {
        const chunks = [];
        response.on("data", (chunk) => chunks.push(chunk));
        response.on("end", () => {
          try {
            const data = JSON.parse(Buffer.concat(chunks).toString("utf8"));
            resolve(Boolean(data && data.success));
          } catch (error) {
            resolve(false);
          }
        });
      }
    );
    request.on("error", () => resolve(false));
    request.setTimeout(8000, () => {
      request.destroy();
      resolve(false);
    });
    request.end(body);
  });
}

function localHost(req) {
  const host = String((req.headers && req.headers.host) || "")
    .split(":")[0]
    .replace(/^\[|\]$/g, "")
    .toLowerCase();
  return host === "localhost" || host === "127.0.0.1" || host === "::1";
}

module.exports = async function handler(req, res) {
  res.setHeader("Content-Type", "application/json");
  const ready = Boolean(siteKey() && secret()) && !localHost(req);
  if (req.method === "GET") {
    res.statusCode = 200;
    res.end(JSON.stringify(ready ? { enabled: true, siteKey: siteKey() } : { enabled: false }));
    return;
  }
  if (req.method !== "POST") {
    res.statusCode = 405;
    res.setHeader("Allow", "GET, POST");
    res.end(JSON.stringify({ error: "GET or POST" }));
    return;
  }
  if (!ready) {
    res.statusCode = 503;
    res.end(JSON.stringify({ error: "unavailable" }));
    return;
  }
  const token = req.body && String(req.body.token || "").trim();
  if (!token || token.length > 4000) {
    res.statusCode = 400;
    res.end(JSON.stringify({ ok: false }));
    return;
  }
  const ok = await verify(token);
  res.statusCode = ok ? 200 : 400;
  res.end(JSON.stringify({ ok: ok }));
};
