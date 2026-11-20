import { spawn } from "node:child_process";
import { writeFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import path from "node:path";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const htmlPath = path.join(root, "cv", "index.html");
const pdfPath = path.join(root, "cv", "Muhammad-Adil-Resume.pdf");
const chrome = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";
const port = 9333;
const profile = "/tmp/adil-cv-chrome";

const child = spawn(chrome, [
  "--headless=new",
  "--disable-gpu",
  "--no-first-run",
  "--no-default-browser-check",
  `--remote-debugging-port=${port}`,
  `--user-data-dir=${profile}`,
  "about:blank",
], { stdio: "ignore" });

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function ready() {
  for (let i = 0; i < 40; i++) {
    try {
      const response = await fetch(`http://127.0.0.1:${port}/json/version`);
      if (response.ok) return;
    } catch {}
    await sleep(150);
  }
  throw new Error("Chrome did not open a debugging port");
}

const pending = new Map();
let nextId = 0;

function send(socket, method, params = {}) {
  const id = ++nextId;
  return new Promise((resolve, reject) => {
    pending.set(id, { resolve, reject });
    socket.send(JSON.stringify({ id, method, params }));
  });
}

try {
  await ready();
  const fileUrl = "file://" + htmlPath;
  const created = await fetch(`http://127.0.0.1:${port}/json/new?${encodeURIComponent(fileUrl)}`, { method: "PUT" });
  if (!created.ok) throw new Error("Could not open the CV page in Chrome");
  const page = await created.json();
  const socket = new WebSocket(page.webSocketDebuggerUrl);
  socket.addEventListener("message", (event) => {
    const message = JSON.parse(event.data);
    const waiter = pending.get(message.id);
    if (!waiter) return;
    pending.delete(message.id);
    if (message.error) waiter.reject(new Error(JSON.stringify(message.error)));
    else waiter.resolve(message.result);
  });
  await new Promise((resolve, reject) => {
    socket.addEventListener("open", resolve);
    socket.addEventListener("error", () => reject(new Error("DevTools socket failed")));
  });

  await send(socket, "Page.enable");
  await send(socket, "Emulation.setDeviceMetricsOverride", {
    width: 1100,
    height: 1400,
    deviceScaleFactor: 1,
    mobile: false,
  });
  await send(socket, "Runtime.evaluate", {
    expression: "document.fonts.ready.then(() => document.querySelector('.sheet').scrollHeight)",
    awaitPromise: true,
    returnByValue: true,
  });
  const measured = await send(socket, "Runtime.evaluate", {
    expression: "document.querySelector('.sheet').getBoundingClientRect().height",
    returnByValue: true,
  });
  const pixels = measured.result.value;
  const inches = pixels / 96;
  const printed = await send(socket, "Page.printToPDF", {
    printBackground: true,
    displayHeaderFooter: false,
    preferCSSPageSize: false,
    paperWidth: 8.27,
    paperHeight: Math.ceil(inches * 100) / 100 + 0.08,
    marginTop: 0,
    marginBottom: 0,
    marginLeft: 0,
    marginRight: 0,
    scale: 1,
  });
  writeFileSync(pdfPath, Buffer.from(printed.data, "base64"));
  console.log(`wrote ${pdfPath} height_in=${inches.toFixed(2)}`);
  socket.close();
} finally {
  child.kill("SIGKILL");
}
