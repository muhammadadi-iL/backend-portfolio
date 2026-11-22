const fs = require("fs");
const path = require("path");

const CAP = 500;
const PATHS = {
  visits: "inbox/visits.jsonl",
  chats: "inbox/chats.jsonl",
};
const FILES = {
  visits: [path.join(__dirname, "..", "data", "visits.jsonl"), path.join("/tmp", "adil-visits.jsonl")],
  chats: [path.join(__dirname, "..", "data", "chats.jsonl"), path.join("/tmp", "adil-chats.jsonl")],
};

let chain = Promise.resolve();

function token() {
  return String(process.env.BLOB_READ_WRITE_TOKEN || "").trim();
}

function storeId() {
  const part = token().split("_")[3] || "";
  return part.startsWith("store_") ? part.slice("store_".length) : part;
}

function blobUrl(pathname) {
  const id = storeId();
  if (!id) throw new Error("blob store id missing");
  return `https://${id}.private.blob.vercel-storage.com/${pathname}`;
}

function headers(extra) {
  return Object.assign(
    {
      authorization: `Bearer ${token()}`,
      "x-api-version": "13",
      "x-vercel-blob-store-id": storeId(),
    },
    extra || {}
  );
}

function parseRows(text) {
  return String(text || "")
    .split("\n")
    .filter(Boolean)
    .slice(-CAP)
    .map((line) => {
      try {
        return JSON.parse(line);
      } catch (error) {
        return null;
      }
    })
    .filter(Boolean);
}

function readFileRows(kind) {
  for (const file of FILES[kind]) {
    try {
      if (!fs.existsSync(file)) continue;
      return parseRows(fs.readFileSync(file, "utf8"));
    } catch (error) {
      continue;
    }
  }
  return [];
}

function writeFileRows(kind, rows) {
  const body = rows.map((row) => JSON.stringify(row)).join("\n") + (rows.length ? "\n" : "");
  for (const file of FILES[kind]) {
    try {
      fs.mkdirSync(path.dirname(file), { recursive: true });
      fs.writeFileSync(file, body);
      return;
    } catch (error) {
      continue;
    }
  }
  throw new Error("file store failed");
}

async function request(url, options) {
  let last;
  for (let attempt = 0; attempt < 3; attempt += 1) {
    try {
      return await fetch(url, options);
    } catch (error) {
      last = error;
      await new Promise((resolve) => setTimeout(resolve, 300 * (attempt + 1)));
    }
  }
  console.error("blob fetch failed", last && last.cause && last.cause.code);
  throw last;
}

async function readBlob(pathname) {
  const url = blobUrl(pathname);
  const meta = await request(`https://vercel.com/api/blob?url=${encodeURIComponent(url)}`, {
    headers: headers(),
  });
  if (meta.status === 404) return { rows: [], etag: "" };
  if (!meta.ok) {
    console.error("blob read", meta.status);
    throw new Error("blob read failed");
  }
  const info = await meta.json();
  const fresh = new URL(info.url || url);
  fresh.searchParams.set("v", info.etag || String(Date.now()));
  const body = await request(fresh.toString(), {
    headers: headers(),
    cache: "no-store",
  });
  if (body.status === 404) return { rows: [], etag: info.etag || "" };
  if (!body.ok) throw new Error("blob read failed");
  return { rows: parseRows(await body.text()), etag: info.etag || "" };
}

async function writeBlob(pathname, rows, etag) {
  const body = rows.map((row) => JSON.stringify(row)).join("\n") + "\n";
  const extra = {
    "x-content-type": "text/plain",
    "x-vercel-blob-access": "private",
    "x-add-random-suffix": "0",
    "x-allow-overwrite": "1",
    "x-cache-control-max-age": "60",
  };
  if (etag) extra["x-if-match"] = etag;
  const response = await request(`https://vercel.com/api/blob/?pathname=${encodeURIComponent(pathname)}`, {
    method: "PUT",
    headers: headers(extra),
    body,
  });
  if (response.status === 412 || response.status === 409) return "conflict";
  if (!response.ok) {
    console.error("blob write", response.status);
    throw new Error("blob write failed");
  }
  return "ok";
}

async function readRows(kind) {
  if (!PATHS[kind]) throw new Error("unknown store");
  if (!token()) return readFileRows(kind);
  return (await readBlob(PATHS[kind])).rows;
}

async function appendRowNow(kind, record) {
  if (!PATHS[kind]) throw new Error("unknown store");
  if (!token()) {
    writeFileRows(kind, readFileRows(kind).concat([record]).slice(-CAP));
    return;
  }
  for (let attempt = 0; attempt < 3; attempt += 1) {
    const current = await readBlob(PATHS[kind]);
    const wrote = await writeBlob(PATHS[kind], current.rows.concat([record]).slice(-CAP), current.etag);
    if (wrote === "ok") return;
  }
  throw new Error("blob write conflict");
}

function appendRow(kind, record) {
  const run = chain.then(() => appendRowNow(kind, record));
  chain = run.catch(() => {});
  return run;
}

module.exports = { readRows, appendRow };
