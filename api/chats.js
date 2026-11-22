const store = require("./store");

function clean(value, max) {
  return String(value || "").replace(/[\r\n\t]+/g, " ").trim().slice(0, max);
}

function emailOf(value) {
  const email = clean(value, 120).toLowerCase();
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email) ? email : "";
}

function phoneOf(value) {
  const phone = clean(value, 40).replace(/[^0-9+\-().\s]/g, "");
  const digits = phone.replace(/\D/g, "");
  return digits.length >= 6 && digits.length <= 15 ? phone : "";
}

function localHost(req) {
  const host = String((req.headers && req.headers.host) || "")
    .split(":")[0]
    .replace(/^\[|\]$/g, "")
    .toLowerCase();
  return host === "localhost" || host === "127.0.0.1" || host === "::1";
}

async function threads() {
  const order = [];
  const map = new Map();
  (await store.readRows("chats")).forEach((row) => {
    const id = clean(row.sessionId, 80) || "unknown";
    if (!map.has(id)) {
      map.set(id, {
        sessionId: id,
        name: "",
        phone: "",
        email: "",
        path: "",
        region: "",
        visitorId: "",
        referrer: "",
        landing: "",
        device: "",
        messages: [],
      });
      order.push(id);
    }
    const thread = map.get(id);
    ["name", "phone", "email", "path", "region", "visitorId", "referrer", "landing", "device"].forEach((field) => {
      if (row[field]) thread[field] = row[field];
    });
    thread.messages.push({ at: row.at, role: row.role, text: row.text });
  });
  return order.map((id) => map.get(id));
}

async function append(row) {
  const text = clean(row.text, 1200);
  if (!text) return;
  const context = row.context && typeof row.context === "object" ? row.context : {};
  const contact = row.contact && typeof row.contact === "object" ? row.contact : {};
  try {
    await store.appendRow("chats", {
    at: new Date().toISOString(),
    sessionId: clean(row.sessionId, 80),
    path: clean(row.path, 180),
    name: clean(contact.name, 80),
    phone: phoneOf(contact.phone),
    email: emailOf(contact.email),
    region: clean(context.region, 180),
    visitorId: clean(context.visitorId, 80),
    referrer: clean(context.referrer, 180),
    landing: clean(context.landing, 180),
    device: clean(context.device, 80),
    role: row.role === "model" ? "model" : "user",
    text: text,
    });
  } catch (error) {
    console.error("chat store failed");
  }
}

async function handler(req, res) {
  res.setHeader("Content-Type", "application/json");
  if (req.method !== "GET" || !localHost(req)) {
    res.statusCode = 404;
    res.end(JSON.stringify({ error: "not found" }));
    return;
  }
  res.statusCode = 200;
  res.end(JSON.stringify({ chats: await threads() }));
}

module.exports = handler;
module.exports.append = append;
module.exports.threads = threads;
