const crypto = require("crypto");
const store = require("./store");
const chats = require("./chats");

const fails = new Map();

function clean(value, max) {
  return String(value || "").replace(/[\r\n\t]+/g, " ").trim().slice(0, max);
}

function clientIp(req) {
  const forwarded = String((req.headers && req.headers["x-forwarded-for"]) || "").split(",")[0].trim();
  if (forwarded) return forwarded;
  return (req.socket && req.socket.remoteAddress) || "";
}

function localHost(req) {
  const host = String((req.headers && req.headers.host) || "")
    .split(":")[0]
    .replace(/^\[|\]$/g, "")
    .toLowerCase();
  return host === "localhost" || host === "127.0.0.1" || host === "::1";
}

function password() {
  return String(process.env.ADMIN_PASSWORD || "");
}

function sessionValue() {
  return crypto.createHmac("sha256", password()).update("adil-admin-v1").digest("hex");
}

function cookies(req) {
  const out = {};
  String((req.headers && req.headers.cookie) || "")
    .split(";")
    .forEach((part) => {
      const index = part.indexOf("=");
      if (index === -1) return;
      out[part.slice(0, index).trim()] = part.slice(index + 1).trim();
    });
  return out;
}

function authed(req) {
  if (!password()) return false;
  const given = cookies(req)["adil-admin"] || "";
  const expected = sessionValue();
  const left = Buffer.from(given);
  const right = Buffer.from(expected);
  if (left.length !== right.length) return false;
  return crypto.timingSafeEqual(left, right);
}

function passwordOk(given) {
  const expected = password();
  if (!expected || !given) return false;
  const left = crypto.createHash("sha256").update(String(given)).digest();
  const right = crypto.createHash("sha256").update(expected).digest();
  return crypto.timingSafeEqual(left, right);
}

function tooMany(ip) {
  const row = fails.get(ip);
  if (!row) return false;
  if (Date.now() - row.at > 15 * 60 * 1000) {
    fails.delete(ip);
    return false;
  }
  return row.n >= 8;
}

function markFail(ip) {
  const row = fails.get(ip);
  if (!row || Date.now() - row.at > 15 * 60 * 1000) {
    fails.set(ip, { n: 1, at: Date.now() });
    return;
  }
  row.n += 1;
  row.at = Date.now();
}

const SESSION_AGE = 60 * 60 * 24 * 30;

function setCookie(res, req, value, maxAge) {
  const parts = [`adil-admin=${value}`, "HttpOnly", "Path=/", "SameSite=Lax", `Max-Age=${maxAge}`];
  if (!localHost(req)) parts.push("Secure");
  res.setHeader("Set-Cookie", parts.join("; "));
}

function send(res, status, body) {
  res.statusCode = status;
  res.setHeader("Content-Type", "application/json");
  res.setHeader("Cache-Control", "no-store");
  res.end(JSON.stringify(body));
}

module.exports = async function handler(req, res) {
  if (!password()) {
    send(res, 404, { error: "not found" });
    return;
  }
  if (req.method === "GET") {
    if (!authed(req)) {
      send(res, 401, { error: "sign in" });
      return;
    }
    setCookie(res, req, sessionValue(), SESSION_AGE);
    const visits = await store.readRows("visits");
    const threads = await chats.threads();
    send(res, 200, { visits: visits.slice().reverse(), chats: threads.slice().reverse() });
    return;
  }
  if (req.method !== "POST") {
    res.setHeader("Allow", "GET, POST");
    send(res, 405, { error: "GET or POST" });
    return;
  }
  const body = req.body && typeof req.body === "object" ? req.body : {};
  if (body.logout) {
    setCookie(res, req, "", 0);
    send(res, 200, { ok: true });
    return;
  }
  const ip = clean(clientIp(req), 80) || "unknown";
  if (tooMany(ip)) {
    send(res, 429, { error: "too many tries" });
    return;
  }
  const given = clean(body.password, 200);
  if (!passwordOk(given)) {
    markFail(ip);
    send(res, 401, { error: "wrong password" });
    return;
  }
  fails.delete(ip);
  setCookie(res, req, sessionValue(), SESSION_AGE);
  send(res, 200, { ok: true });
};
