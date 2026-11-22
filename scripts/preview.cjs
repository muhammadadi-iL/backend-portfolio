const http = require("http");
const fs = require("fs");
const path = require("path");

const root = path.resolve(__dirname, "..");
const envFile = path.join(root, ".env");
if (fs.existsSync(envFile)) {
  for (const line of fs.readFileSync(envFile, "utf8").split("\n")) {
    const trimmed = line.trim();
    if (!trimmed || trimmed.startsWith("#")) continue;
    const eq = trimmed.indexOf("=");
    if (eq === -1) continue;
    const name = trimmed.slice(0, eq);
    if (!process.env[name]) process.env[name] = trimmed.slice(eq + 1);
  }
}

const handlers = {
  "/api/chat": require("../api/chat.js"),
  "/api/captcha": require("../api/captcha.js"),
  "/api/visit": require("../api/visit.js"),
  "/api/chats": require("../api/chats.js"),
  "/api/admin": require("../api/admin.js"),
};
const types = {
  ".html": "text/html; charset=utf-8",
  ".css": "text/css; charset=utf-8",
  ".js": "text/javascript; charset=utf-8",
  ".svg": "image/svg+xml",
  ".png": "image/png",
  ".jpg": "image/jpeg",
  ".pdf": "application/pdf",
  ".xml": "application/xml",
  ".ico": "image/x-icon",
};

function sendFile(res, file) {
  fs.readFile(file, (error, data) => {
    if (error) {
      res.statusCode = 404;
      res.end("Not found");
      return;
    }
    res.setHeader("Content-Type", types[path.extname(file)] || "application/octet-stream");
    res.end(data);
  });
}

const server = http.createServer((req, res) => {
  const url = new URL(req.url, "http://127.0.0.1");
  if (handlers[url.pathname]) {
    const handler = handlers[url.pathname];
    const chunks = [];
    let size = 0;
    req.on("data", (chunk) => {
      size += chunk.length;
      if (size > 8000) {
        res.statusCode = 413;
        res.end(JSON.stringify({ error: "too large" }));
        req.destroy();
        return;
      }
      chunks.push(chunk);
    });
    req.on("end", () => {
      if (res.writableEnded) return;
      try {
        req.body = chunks.length ? JSON.parse(Buffer.concat(chunks).toString("utf8")) : {};
      } catch (error) {
        res.statusCode = 400;
        res.setHeader("Content-Type", "application/json");
        res.end(JSON.stringify({ error: "bad json" }));
        return;
      }
      Promise.resolve(handler(req, res)).catch((error) => {
        console.error(error && error.message, error && error.cause && error.cause.code);
        if (!res.writableEnded) {
          res.statusCode = 500;
          res.setHeader("Content-Type", "application/json");
          res.end(JSON.stringify({ error: "unavailable" }));
        }
      });
    });
    return;
  }

  let pathname = decodeURIComponent(url.pathname);
  if (pathname.split("/").some((part) => part.startsWith("."))) {
    res.statusCode = 404;
    res.end("Not found");
    return;
  }
  if (pathname.endsWith("/")) pathname += "index.html";
  const file = path.normalize(path.join(root, pathname));
  if (!file.startsWith(root)) {
    res.statusCode = 403;
    res.end("Forbidden");
    return;
  }
  sendFile(res, file);
});

const port = Number(process.env.PORT || 8777);
server.listen(port, "127.0.0.1", () => {
  console.log(`preview http://127.0.0.1:${port}/`);
});
