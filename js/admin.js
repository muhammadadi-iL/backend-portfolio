(function () {
  const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  if (!reduce) document.documentElement.classList.add("motion");
  const gate = document.getElementById("gate");
  const app = document.getElementById("app");
  const login = document.getElementById("login");
  const board = document.getElementById("board");
  const unavailable = document.getElementById("unavailable");
  const error = document.getElementById("login-error");
  const refresh = document.getElementById("refresh");
  const signout = document.getElementById("signout");
  const lead = document.getElementById("inbox-lead");
  const viewRoot = document.getElementById("dash-view");
  const search = document.getElementById("dash-search");
  const count = document.getElementById("dash-count");
  const clearSearch = document.getElementById("dash-clear");
  const pageTitle = document.getElementById("dash-title");

  let data = { visits: [], chats: [] };
  let view = "overview";
  let selected = "";
  let riseIndex = 0;
  let page = 1;
  const pageSize = 20;

  function rise(node) {
    node.classList.add("rise");
    node.style.setProperty("--d", Math.min(riseIndex, 10) * 55 + "ms");
    riseIndex += 1;
    return node;
  }

  function blank(value) {
    const text = String(value || "").trim();
    return text || "—";
  }

  function when(value) {
    if (!value) return "—";
    const date = new Date(value);
    if (Number.isNaN(date.getTime())) return String(value);
    return date.toLocaleString(undefined, { month: "short", day: "numeric", hour: "numeric", minute: "2-digit" });
  }

  function ago(value) {
    const date = new Date(value);
    if (!value || Number.isNaN(date.getTime())) return "";
    const minutes = Math.round((Date.now() - date.getTime()) / 60000);
    if (minutes < 1) return "just now";
    if (minutes < 60) return minutes + "m ago";
    const hours = Math.round(minutes / 60);
    if (hours < 24) return hours + "h ago";
    const days = Math.round(hours / 24);
    if (days < 14) return days + "d ago";
    return when(value);
  }

  function pageWindow(rows) {
    const pages = Math.max(1, Math.ceil(rows.length / pageSize));
    if (page > pages) page = pages;
    if (page < 1) page = 1;
    const start = (page - 1) * pageSize;
    return { rows: rows.slice(start, start + pageSize), start: start, total: rows.length, pages: pages };
  }

  function pager(total) {
    if (total <= pageSize) return null;
    const pages = Math.max(1, Math.ceil(total / pageSize));
    const start = (page - 1) * pageSize;
    const end = Math.min(total, start + pageSize);
    const bar = el("nav", "pager");
    bar.setAttribute("aria-label", "Pages");
    const label = el("p", "", (start + 1) + "–" + end + " of " + total);
    const prev = el("button", "btn", "Previous");
    const next = el("button", "btn", "Next");
    prev.type = "button";
    next.type = "button";
    prev.disabled = page <= 1;
    next.disabled = page >= pages;
    prev.addEventListener("click", () => {
      page -= 1;
      selected = "";
      render();
      window.scrollTo(0, 0);
    });
    next.addEventListener("click", () => {
      page += 1;
      selected = "";
      render();
      window.scrollTo(0, 0);
    });
    bar.append(prev, label, next);
    return bar;
  }

  function deviceLabel(value) {
    return String(value || "").replace(/,/g, " ").replace(/\s+/g, " ").trim();
  }

  function tally(amount, one, many) {
    return amount + " " + (amount === 1 ? one : many);
  }

  function placeParts(row) {
    if (row.city || row.area || row.country) {
      return { city: row.city || "", area: row.area || "", country: row.country || "" };
    }
    const bits = String(row.region || "").split(",").map((part) => part.trim()).filter(Boolean);
    if (bits.length >= 3) return { city: bits[0], area: bits.slice(1, -1).join(", "), country: bits[bits.length - 1] };
    if (bits.length === 2) return { city: bits[0], area: "", country: bits[1] };
    if (bits.length === 1) return { city: "", area: "", country: bits[0] };
    return { city: "", area: "", country: "" };
  }

  function placeLabel(row) {
    const parts = placeParts(row);
    return [parts.city, parts.area, parts.country].filter(Boolean).join(", ");
  }

  function haystack(values) {
    return values.join(" ").toLowerCase();
  }

  function matches(values) {
    const needle = search.value.trim().toLowerCase();
    if (!needle) return true;
    return haystack(values).includes(needle);
  }

  function el(tag, className, text) {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (text !== undefined) node.textContent = text;
    return node;
  }

  function facts(pairs) {
    const list = el("dl", "facts");
    pairs.forEach((pair) => {
      const item = el("div");
      item.append(el("dt", "", pair[0]), el("dd", "", blank(pair[1])));
      list.appendChild(item);
    });
    return list;
  }

  function table(headers, rows, narrow) {
    const wrap = rise(el("div", "table-wrap"));
    const grid = el("table", narrow ? "table-narrow" : "");
    const head = document.createElement("thead");
    const headRow = document.createElement("tr");
    headers.forEach((label) => headRow.appendChild(el("th", "", label)));
    head.appendChild(headRow);
    const body = document.createElement("tbody");
    rows.forEach((row) => {
      const line = document.createElement("tr");
      if (row.key) {
        line.className = "pick" + (row.key === selected ? " is-on" : "");
        line.tabIndex = 0;
        line.setAttribute("role", "button");
        line.setAttribute("aria-label", row.cells.map((cell) => cell.text).join(", "));
        const open = () => {
          selected = selected === row.key ? "" : row.key;
          render();
        };
        line.addEventListener("click", open);
        line.addEventListener("keydown", (event) => {
          if (event.key === "Enter" || event.key === " ") {
            event.preventDefault();
            open();
          }
        });
      }
      row.cells.forEach((cell, index) => {
        const item = el("td", index === 0 || cell.mono ? "mono" : "", cell.text);
        line.appendChild(item);
      });
      body.appendChild(line);
    });
    grid.append(head, body);
    wrap.appendChild(grid);
    return wrap;
  }

  function empty(text) {
    return el("p", "empty", text);
  }

  function ipGroups() {
    const map = new Map();
    data.visits.forEach((row) => {
      const ip = row.ip || "Unknown";
      if (!map.has(ip)) map.set(ip, []);
      map.get(ip).push(row);
    });
    return Array.from(map, ([ip, rows]) => ({
      ip: ip,
      rows: rows.slice().sort((a, b) => String(a.at || "").localeCompare(String(b.at || ""))),
    }));
  }

  function locationGroups() {
    const map = new Map();
    data.visits.forEach((row) => {
      const label = placeLabel(row) || "Unknown";
      if (!map.has(label)) map.set(label, []);
      map.get(label).push(row);
    });
    return Array.from(map, ([label, rows]) => ({
      label: label,
      rows: rows.slice().sort((a, b) => String(a.at || "").localeCompare(String(b.at || ""))),
    }));
  }

  function unique(rows, field) {
    return new Set(rows.map((row) => row[field]).filter(Boolean)).size;
  }

  function chatsForVisits(rows) {
    const sessions = new Set(rows.map((row) => row.sessionId).filter(Boolean));
    const visitors = new Set(rows.map((row) => row.visitorId).filter(Boolean));
    return data.chats.filter((thread) => {
      return (thread.sessionId && thread.sessionId !== "unknown" && sessions.has(thread.sessionId)) || (thread.visitorId && visitors.has(thread.visitorId));
    });
  }

  function visitsForChat(thread) {
    return data.visits.filter((row) => {
      const sameSession = thread.sessionId && thread.sessionId !== "unknown" && row.sessionId === thread.sessionId;
      const sameVisitor = thread.visitorId && row.visitorId === thread.visitorId;
      return sameSession || sameVisitor;
    });
  }

  function seriesByDay(rows, timeOf) {
    const map = new Map();
    rows.slice().sort((a, b) => String(timeOf(a) || "").localeCompare(String(timeOf(b) || ""))).forEach((row) => {
      const date = new Date(timeOf(row));
      if (Number.isNaN(date.getTime())) return;
      const key = date.toLocaleDateString(undefined, { month: "short", day: "numeric" });
      map.set(key, (map.get(key) || 0) + 1);
    });
    return Array.from(map);
  }

  function deviceCounts(rows) {
    const map = new Map();
    rows.forEach((row) => {
      const label = deviceLabel(row.device) || "Unknown";
      map.set(label, (map.get(label) || 0) + 1);
    });
    return Array.from(map).sort((a, b) => b[1] - a[1]).slice(0, 6);
  }

  function svg(tag, attrs) {
    const node = document.createElementNS("http://www.w3.org/2000/svg", tag);
    Object.keys(attrs).forEach((key) => node.setAttribute(key, attrs[key]));
    return node;
  }

  function columnChart(title, pairs) {
    const card = rise(el("section", "dash-card chart-card"));
    card.appendChild(el("h2", "dash-title", title));
    if (!pairs.length) {
      card.appendChild(empty("Nothing recorded yet."));
      return card;
    }
    const shown = pairs.slice(-10);
    const max = Math.max.apply(null, shown.map((pair) => pair[1]).concat(1));
    const width = 360;
    const height = 176;
    const plot = 128;
    const gap = 10;
    const barW = Math.max(10, (width - gap * (shown.length + 1)) / shown.length);
    const board = svg("svg", { viewBox: "0 0 " + width + " " + height, class: "chart", role: "img" });
    board.setAttribute("aria-label", title);
    shown.forEach((pair, index) => {
      const barH = Math.max(6, (pair[1] / max) * (plot - 28));
      const x = gap + index * (barW + gap);
      const y = plot - barH;
      const rect = svg("rect", { x: x, y: y, width: barW, height: barH, rx: "5", class: "chart-col" });
      rect.style.animationDelay = index * 45 + "ms";
      const tip = svg("title", {});
      tip.textContent = pair[0] + ": " + pair[1];
      rect.appendChild(tip);
      const value = svg("text", { x: x + barW / 2, y: Math.max(14, y - 8), "text-anchor": "middle", class: "chart-value" });
      value.textContent = String(pair[1]);
      const label = svg("text", { x: x + barW / 2, y: plot + 18, "text-anchor": "middle" });
      label.textContent = pair[0];
      board.append(rect, value);
      if (barW >= 32) board.appendChild(label);
    });
    card.appendChild(board);
    return card;
  }

  function donutChart(title, pairs) {
    const card = rise(el("section", "dash-card chart-card"));
    card.appendChild(el("h2", "dash-title", title));
    if (!pairs.length) {
      card.appendChild(empty("Nothing recorded yet."));
      return card;
    }
    const total = pairs.reduce((sum, pair) => sum + pair[1], 0) || 1;
    const tones = ["#ededed", "#666666", "#a1a1a1", "#333333", "#888888", "#444444"];
    const radius = 46;
    const circ = 2 * Math.PI * radius;
    const board = svg("svg", { viewBox: "0 0 180 140", class: "chart donut", role: "img" });
    board.setAttribute("aria-label", title);
    let cursor = 0;
    pairs.forEach((pair, index) => {
      const length = (pair[1] / total) * circ;
      const seg = svg("circle", {
        cx: "62",
        cy: "70",
        r: String(radius),
        fill: "none",
        "stroke-width": "16",
        stroke: tones[index % tones.length],
        "stroke-dasharray": length + " " + (circ - length),
        "stroke-dashoffset": String(-cursor),
        class: "donut-seg",
        transform: "rotate(-90 62 70)",
      });
      seg.style.animationDelay = index * 70 + "ms";
      const tip = svg("title", {});
      tip.textContent = pair[0] + ": " + pair[1];
      seg.appendChild(tip);
      board.appendChild(seg);
      cursor += length;
    });
    const totalText = svg("text", { x: "62", y: "74", "text-anchor": "middle", class: "donut-total" });
    totalText.textContent = String(total);
    board.appendChild(totalText);
    const legend = el("ul", "legend");
    pairs.forEach((pair, index) => {
      const item = el("li");
      const swatch = el("i");
      swatch.style.background = tones[index % tones.length];
      item.append(swatch, document.createTextNode(pair[0] + " · " + pair[1]));
      legend.appendChild(item);
    });
    card.append(board, legend);
    return card;
  }

  function rankList(title, pairs) {
    const card = rise(el("section", "dash-card"));
    card.appendChild(el("h2", "dash-title", title));
    if (!pairs.length) {
      card.appendChild(empty("Nothing recorded yet."));
      return card;
    }
    const max = pairs[0][1] || 1;
    pairs.forEach((pair) => {
      const row = el("div", "rank");
      const top = el("div", "rank-top");
      top.append(el("span", "", pair[0]), el("b", "", String(pair[1])));
      const bar = el("div", "meter");
      const fill = document.createElement("i");
      fill.style.width = Math.max(8, Math.round((pair[1] / max) * 100)) + "%";
      bar.appendChild(fill);
      row.append(top, bar);
      card.appendChild(row);
    });
    return card;
  }

  function detailCard(title, pairs, extra) {
    const card = rise(el("article", "dash-card detail"));
    const head = el("div", "detail-head");
    head.appendChild(el("h2", "dash-title", title));
    const close = el("button", "btn", "Close");
    close.type = "button";
    close.addEventListener("click", () => {
      selected = "";
      render();
    });
    head.appendChild(close);
    card.append(head, facts(pairs));
    if (extra) card.appendChild(extra);
    return card;
  }

  function transcript(messages, visitorName) {
    const wrap = el("div", "thread-wrap");
    const visitor = String(visitorName || "").trim() || "Visitor";
    const fromVisitor = messages.filter((message) => message.role !== "model").length;
    const fromMuhammad = messages.length - fromVisitor;
    wrap.appendChild(el("h3", "", "Conversation"));
    wrap.appendChild(el("p", "thread-count", fromVisitor + " from " + visitor + " · " + fromMuhammad + " from Muhammad"));
    if (!messages.length) {
      wrap.appendChild(empty("No messages saved."));
      return wrap;
    }
    const thread = el("div", "thread");
    messages.forEach((message) => {
      const mine = message.role === "model";
      const block = el("div", "bubble " + (mine ? "reply" : "visitor"));
      const time = el("time", "", when(message.at));
      if (message.at) time.dateTime = message.at;
      block.append(el("span", "who", mine ? "Muhammad" : visitor), el("p", "", message.text || ""), time);
      thread.appendChild(block);
    });
    wrap.appendChild(thread);
    requestAnimationFrame(function () {
      requestAnimationFrame(function () {
        thread.scrollTop = thread.scrollHeight;
      });
    });
    return wrap;
  }

  function visitRows(rows) {
    return rows.filter((row) => matches([row.path, row.ip, placeLabel(row), row.device, row.referrer, row.landing, row.sessionId, row.visitorId, row.city, row.area, row.country])).map((row, index) => ({
      key: "visit:" + (row.at || "") + ":" + (row.ip || "") + ":" + (row.path || "") + ":" + index,
      row: row,
      cells: [
        { text: when(row.at), mono: true },
        { text: blank(row.path), mono: true },
        { text: blank(row.ip), mono: true },
        { text: blank(placeLabel(row)) },
        { text: blank(deviceLabel(row.device)) },
        { text: blank(row.referrer || "direct") },
      ],
    }));
  }

  function paintVisitDetail(records) {
    const hit = records.find((item) => item.key === selected);
    if (!hit) return null;
    const row = hit.row;
    const parts = placeParts(row);
    const related = chatsForVisits([row]);
    const extra = el("div");
    extra.appendChild(el("h3", "", "Chats from this session"));
    if (!related.length) extra.appendChild(empty("No saved chat shares this session."));
    related.forEach((thread) => {
      extra.appendChild(el("p", "", [thread.name || "No name", thread.phone, thread.email].filter(Boolean).join(" · ") + " · " + (thread.messages || []).length + " messages"));
    });
    return detailCard(row.path || "/", [
      ["Time", when(row.at)],
      ["Page", row.path],
      ["IP address", row.ip],
      ["City", parts.city],
      ["Region", parts.area],
      ["Country", parts.country],
      ["Location", placeLabel(row)],
      ["Device", deviceLabel(row.device)],
      ["Session", row.sessionId],
      ["Visitor ID", row.visitorId],
      ["Referrer", row.referrer || "direct"],
      ["Landing page", row.landing],
    ], extra);
  }

  function paintOverview(root) {
    const pages = new Map();
    const places = new Map();
    const visits = data.visits.filter((row) => matches([row.path, row.ip, placeLabel(row), row.device, row.referrer, row.landing, row.sessionId, row.visitorId]));
    visits.forEach((row) => {
      const page = row.path || "/";
      pages.set(page, (pages.get(page) || 0) + 1);
      const place = placeLabel(row) || "Unknown";
      places.set(place, (places.get(place) || 0) + 1);
    });
    const top = (map) => Array.from(map, (pair) => pair).sort((a, b) => b[1] - a[1]).slice(0, 6);
    root.append(el("p", "dash-note", "Open a row for the full record. The cards above jump to that list."));
    const charts = el("div", "split");
    charts.append(columnChart("Visits by day", seriesByDay(visits, (row) => row.at)), donutChart("Devices", deviceCounts(visits)));
    root.appendChild(charts);
    const split = el("div", "split");
    split.append(rankList("Pages", top(pages)), rankList("Locations", top(places)));
    root.appendChild(split);
    const heading = el("h2", "dash-title", "Latest visits");
    const latest = visitRows(visits).slice(0, 6);
    const detail = paintVisitDetail(latest);
    if (detail) root.appendChild(detail);
    root.appendChild(heading);
    root.appendChild(latest.length ? table(["Time", "Page", "IP address", "Location", "Device"], latest.map((item) => ({
      key: item.key,
      row: item.row,
      cells: item.cells.slice(0, 5),
    })), true) : empty("No visits yet."));
    const needle = search.value.trim();
    count.textContent = needle
      ? tally(visits.length, "matching visit", "matching visits")
      : tally(data.visits.length, "visit", "visits") + " · " + tally(data.chats.length, "chat", "chats");
  }

  function paintVisits(root) {
    root.append(el("h2", "dash-title", "Visits"), el("p", "dash-note", "Every counted page view, newest first. Open a row for the full record."));
    const rows = visitRows(data.visits);
    const shown = pageWindow(rows);
    root.appendChild(columnChart("Visits by day", seriesByDay(rows.map((item) => item.row), (row) => row.at)));
    const detail = paintVisitDetail(rows);
    if (detail) root.appendChild(detail);
    root.appendChild(shown.rows.length ? table(["Time", "Page", "IP address", "Location", "Device", "Referrer"], shown.rows) : empty("No visits match."));
    const bar = pager(rows.length);
    if (bar) root.appendChild(bar);
    count.textContent = tally(rows.length, "visit", "visits");
  }

  function activityItems() {
    const items = [];
    data.visits.forEach((row, index) => {
      items.push({
        key: "visit:" + (row.at || "") + ":" + (row.ip || "") + ":" + (row.path || "") + ":" + index,
        at: row.at,
        kind: "Visit",
        title: row.path || "/",
        meta: [row.ip, placeLabel(row), deviceLabel(row.device)].filter(Boolean).join(" · "),
        search: [row.path, row.ip, placeLabel(row), row.device, row.referrer, row.landing, row.sessionId, row.visitorId],
        visit: row,
      });
    });
    data.chats.forEach((thread) => {
      const messages = thread.messages || [];
      const last = messages[messages.length - 1];
      const spoken = messages.filter((message) => message.role !== "model");
      const previewSource = spoken.length ? spoken[spoken.length - 1] : last;
      const preview = String((previewSource && previewSource.text) || "").replace(/\s+/g, " ").trim();
      items.push({
        key: "chat:" + (thread.sessionId || thread.name || ""),
        at: (last && last.at) || "",
        kind: "Chat",
        title: thread.name || thread.email || thread.phone || "Visitor",
        meta: preview.length > 96 ? preview.slice(0, 93) + "…" : preview,
        search: [thread.name, thread.phone, thread.email, thread.region, thread.path, preview, thread.sessionId, thread.visitorId],
        thread: thread,
      });
    });
    return items.filter((item) => matches(item.search)).sort((a, b) => String(b.at).localeCompare(String(a.at)));
  }

  function paintActivity(root) {
    root.append(el("h2", "dash-title", "Activity"), el("p", "dash-note", "Visits and chats in one list, newest first. The page stays put while you refresh. Open a row for the full record."));
    const items = activityItems();
    const shown = pageWindow(items);
    const hit = items.find((item) => item.key === selected);
    if (hit && hit.visit) {
      const records = items.filter((item) => item.visit).map((item) => ({ key: item.key, row: item.visit }));
      const detail = paintVisitDetail(records);
      if (detail) root.appendChild(detail);
    } else if (hit && hit.thread) {
      const thread = hit.thread;
      const visits = visitsForChat(thread);
      const first = (thread.messages || [])[0];
      const last = (thread.messages || [])[(thread.messages || []).length - 1];
      const extra = el("div");
      extra.appendChild(transcript(thread.messages || [], thread.name));
      extra.appendChild(el("h3", "", "Visits from this person"));
      if (!visits.length) extra.appendChild(empty("No visit shares this session or visitor ID."));
      else {
        extra.appendChild(table(["Time", "IP address", "Page", "Location"], visits.slice().reverse().map((row) => ({
          cells: [{ text: when(row.at), mono: true }, { text: blank(row.ip), mono: true }, { text: blank(row.path), mono: true }, { text: blank(placeLabel(row)) }],
        })), true));
      }
      root.appendChild(detailCard(thread.name || "Visitor", [
        ["Name", thread.name],
        ["Phone", thread.phone],
        ["Email", thread.email],
        ["Location", thread.region || (visits[0] && placeLabel(visits[0]))],
        ["Page", thread.path],
        ["Device", deviceLabel(thread.device)],
        ["Session", thread.sessionId],
        ["Started", when(first && first.at)],
        ["Last message", when(last && last.at)],
      ], extra));
    }
    if (!shown.rows.length) {
      root.appendChild(empty("No activity matches."));
    } else {
      const list = el("ul", "log");
      shown.rows.forEach((item) => {
        const line = el("li");
        const button = el("button");
        button.type = "button";
        if (item.key === selected) button.classList.add("is-on");
        const time = el("time", "", when(item.at));
        time.dateTime = item.at || "";
        const copy = el("span", "log-copy");
        copy.append(el("span", "log-title", item.title), el("span", "log-meta", item.meta || "—"));
        button.append(time, el("span", "log-kind", item.kind), copy, el("span", "log-ago", ago(item.at)));
        button.addEventListener("click", () => {
          selected = selected === item.key ? "" : item.key;
          render();
        });
        line.appendChild(button);
        list.appendChild(line);
      });
      root.appendChild(list);
    }
    const bar = pager(items.length);
    if (bar) root.appendChild(bar);
    count.textContent = tally(items.length, "event", "events");
  }

  function paintIps(root) {
    root.append(el("h2", "dash-title", "IP addresses"), el("p", "dash-note", "Each address is the one the host saw on the request. Open a row for every page, location and any chat from that session."));
    const groups = ipGroups().map((group) => {
      const last = group.rows[group.rows.length - 1];
      const places = Array.from(new Set(group.rows.map(placeLabel).filter(Boolean)));
      const devices = Array.from(new Set(group.rows.map((row) => deviceLabel(row.device)).filter(Boolean)));
      return {
        key: "ip:" + group.ip,
        group: group,
        places: places,
        devices: devices,
        last: last,
        cells: [
          { text: group.ip, mono: true },
          { text: String(group.rows.length) },
          { text: blank(places.join("; ")) },
          { text: when(last && last.at) },
          { text: blank(devices.join(", ")) },
          { text: String(unique(group.rows, "path")) },
        ],
      };
    }).filter((item) => matches([item.group.ip, item.places.join(" "), item.devices.join(" "), item.group.rows.map((row) => row.path).join(" ")]));
    groups.sort((a, b) => String(b.last && b.last.at).localeCompare(String(a.last && a.last.at)));
    root.appendChild(rankList("Top addresses", groups.slice(0, 6).map((item) => [item.group.ip, item.group.rows.length])));
    const hit = groups.find((item) => item.key === selected);
    if (hit) {
      const pages = Array.from(new Set(hit.group.rows.map((row) => row.path).filter(Boolean)));
      const related = chatsForVisits(hit.group.rows);
      const extra = el("div");
      extra.appendChild(el("h3", "", "Chats tied to this address"));
      if (!related.length) extra.appendChild(empty("No saved chat shares a session with this address."));
      related.forEach((thread) => extra.appendChild(el("p", "", [thread.name || "No name", thread.email, thread.phone].filter(Boolean).join(" · "))));
      extra.appendChild(el("h3", "", "Pages from this address"));
      const pageRows = hit.group.rows.slice().reverse().map((row) => ({
        cells: [{ text: when(row.at), mono: true }, { text: blank(row.path), mono: true }, { text: blank(placeLabel(row)) }, { text: blank(deviceLabel(row.device)) }],
      }));
      extra.appendChild(table(["Time", "Page", "Location", "Device"], pageRows, true));
      root.appendChild(detailCard(hit.group.ip, [
        ["IP address", hit.group.ip],
        ["Visits", String(hit.group.rows.length)],
        ["First seen", when(hit.group.rows[0] && hit.group.rows[0].at)],
        ["Last seen", when(hit.last && hit.last.at)],
        ["Locations", hit.places.join("; ")],
        ["Devices", hit.devices.join(", ")],
        ["Pages", pages.join(", ")],
        ["Sessions", String(unique(hit.group.rows, "sessionId"))],
        ["Visitor IDs", String(unique(hit.group.rows, "visitorId"))],
      ], extra));
    }
    const shownIps = pageWindow(groups);
    root.appendChild(shownIps.rows.length ? table(["IP address", "Visits", "Locations", "Last seen", "Devices", "Pages"], shownIps.rows) : empty("No IP addresses match."));
    const ipBar = pager(groups.length);
    if (ipBar) root.appendChild(ipBar);
    count.textContent = tally(groups.length, "address", "addresses");
  }

  function paintLocations(root) {
    root.append(el("h2", "dash-title", "Locations"), el("p", "dash-note", "Approximate place from the IP address: city, region and country when the host supplies them. GPS is never read."));
    const groups = locationGroups().map((group) => {
      const sample = group.rows[group.rows.length - 1] || group.rows[0];
      const parts = placeParts(sample || {});
      const ips = Array.from(new Set(group.rows.map((row) => row.ip).filter(Boolean)));
      return {
        key: "place:" + group.label,
        group: group,
        parts: parts,
        ips: ips,
        cells: [
          { text: group.label },
          { text: String(group.rows.length) },
          { text: String(ips.length) },
          { text: when(sample && sample.at) },
          { text: blank(parts.country) },
        ],
      };
    }).filter((item) => matches([item.group.label, item.parts.city, item.parts.area, item.parts.country, item.ips.join(" ")]));
    groups.sort((a, b) => b.group.rows.length - a.group.rows.length);
    root.appendChild(rankList("Places", groups.slice(0, 6).map((item) => [item.group.label, item.group.rows.length])));
    const hit = groups.find((item) => item.key === selected);
    if (hit) {
      const pageRows = hit.group.rows.slice().reverse().map((row) => ({
        cells: [{ text: when(row.at), mono: true }, { text: blank(row.ip), mono: true }, { text: blank(row.path), mono: true }, { text: blank(deviceLabel(row.device)) }],
      }));
      const extra = el("div");
      extra.appendChild(el("h3", "", "Visits from this place"));
      extra.appendChild(table(["Time", "IP address", "Page", "Device"], pageRows, true));
      root.appendChild(detailCard(hit.group.label, [
        ["Location", hit.group.label],
        ["City", hit.parts.city],
        ["Region", hit.parts.area],
        ["Country", hit.parts.country],
        ["Visits", String(hit.group.rows.length)],
        ["IP addresses", String(hit.ips.length)],
        ["Devices", Array.from(new Set(hit.group.rows.map((row) => deviceLabel(row.device)).filter(Boolean))).join(", ")],
        ["Pages", Array.from(new Set(hit.group.rows.map((row) => row.path).filter(Boolean))).join(", ")],
      ], extra));
    }
    const shownPlaces = pageWindow(groups);
    root.appendChild(shownPlaces.rows.length ? table(["Location", "Visits", "IP addresses", "Last seen", "Country"], shownPlaces.rows, true) : empty("No locations match."));
    const placeBar = pager(groups.length);
    if (placeBar) root.appendChild(placeBar);
    count.textContent = tally(groups.length, "location", "locations");
  }

  function paintChats(root) {
    root.append(el("h2", "dash-title", "Chats"), el("p", "dash-note", "Name, phone, email and the full conversation. The assistant reply is saved here. Name, phone and email are not sent to the model."));
    const threads = data.chats.map((thread) => {
      const last = (thread.messages || [])[(thread.messages || []).length - 1];
      const visits = visitsForChat(thread);
      return {
        key: "chat:" + (thread.sessionId || thread.name || ""),
        thread: thread,
        visits: visits,
        cells: [
          { text: blank(thread.name) },
          { text: blank(thread.phone), mono: true },
          { text: blank(thread.email) },
          { text: blank(thread.region || (visits[0] && placeLabel(visits[0]))) },
          { text: String((thread.messages || []).length) },
          { text: when(last && last.at) },
        ],
      };
    }).filter((item) => matches([
      item.thread.name, item.thread.phone, item.thread.email, item.thread.region, item.thread.path,
      item.thread.device, item.thread.referrer, item.thread.landing, item.thread.sessionId, item.thread.visitorId,
      (item.thread.messages || []).map((message) => message.text).join(" "),
    ]));
    root.appendChild(columnChart("Messages by day", seriesByDay(threads.flatMap((item) => item.thread.messages || []), (row) => row.at)));
    const hit = threads.find((item) => item.key === selected);
    if (hit) {
      const thread = hit.thread;
      const first = (thread.messages || [])[0];
      const last = (thread.messages || [])[(thread.messages || []).length - 1];
      const extra = el("div");
      extra.appendChild(transcript(thread.messages || [], thread.name));
      extra.appendChild(el("h3", "", "Visits from this person"));
      if (!hit.visits.length) extra.appendChild(empty("No visit shares this session or visitor ID."));
      else {
        extra.appendChild(table(["Time", "IP address", "Page", "Location"], hit.visits.slice().reverse().map((row) => ({
          cells: [{ text: when(row.at), mono: true }, { text: blank(row.ip), mono: true }, { text: blank(row.path), mono: true }, { text: blank(placeLabel(row)) }],
        })), true));
      }
      root.appendChild(detailCard(thread.name || "No name", [
        ["Name", thread.name],
        ["Phone", thread.phone],
        ["Email", thread.email],
        ["Location", thread.region || (hit.visits[0] && placeLabel(hit.visits[0]))],
        ["Page", thread.path],
        ["Landing page", thread.landing],
        ["Referrer", thread.referrer],
        ["Device", deviceLabel(thread.device)],
        ["Session", thread.sessionId],
        ["Visitor ID", thread.visitorId],
        ["Started", when(first && first.at)],
        ["Last message", when(last && last.at)],
      ], extra));
    }
    const shownThreads = pageWindow(threads);
    root.appendChild(shownThreads.rows.length ? table(["Name", "Phone", "Email", "Location", "Messages", "Last message"], shownThreads.rows, true) : empty("No chats match."));
    const chatBar = pager(threads.length);
    if (chatBar) root.appendChild(chatBar);
    count.textContent = tally(threads.length, "chat", "chats");
  }

  function render() {
    document.querySelectorAll(".dash-nav button").forEach((button) => {
      const on = button.dataset.view === view;
      button.classList.toggle("is-on", on);
      if (on) button.setAttribute("aria-current", "page");
      else button.removeAttribute("aria-current");
    });
    viewRoot.replaceChildren();
    count.textContent = "";
    if (view === "overview") paintOverview(viewRoot);
    else if (view === "activity") paintActivity(viewRoot);
    else if (view === "visits") paintVisits(viewRoot);
    else if (view === "ips") paintIps(viewRoot);
    else if (view === "locations") paintLocations(viewRoot);
    else paintChats(viewRoot);
    const names = { overview: "Overview", activity: "Activity", visits: "Visits", ips: "IP addresses", locations: "Locations", chats: "Chats" };
    if (pageTitle) pageTitle.textContent = names[view] || "Overview";
    const prompts = {
      overview: "Search page, IP, location, device",
      activity: "Search a page, IP, name, or message",
      visits: "Search page, IP, location, device",
      ips: "Search an IP address or page",
      locations: "Search a city, region, or country",
      chats: "Search a name, email, phone, or message",
    };
    search.placeholder = prompts[view] || prompts.overview;
    lead.textContent = "The latest 500 visits and 500 chat lines. Older ones are dropped.";
  }

  function stats() {
    const knownPlaces = locationGroups().filter((group) => group.label !== "Unknown").length;
    const named = data.chats.filter((thread) => thread.name || thread.phone || thread.email).length;
    const cards = [
      ["overview", data.visits.length, "Visits"],
      ["ips", ipGroups().length, "IP addresses"],
      ["locations", knownPlaces || locationGroups().length, "Locations"],
      ["chats", data.chats.length, "Chats"],
      ["visits", unique(data.visits, "path"), "Pages"],
      ["chats", named, "Contacts"],
    ];
    const row = el("div", "stats");
    cards.forEach((card) => {
      const button = el("button", "stat" + (view === card[0] && card[2] !== "Pages" && card[2] !== "Contacts" ? " is-on" : ""));
      button.type = "button";
      button.append(el("b", "", String(card[1])), el("span", "", card[2]));
      button.addEventListener("click", () => {
        view = card[0];
        selected = "";
        page = 1;
        render();
        window.scrollTo(0, 0);
      });
      row.appendChild(button);
    });
    return row;
  }

  const baseRender = render;
  render = function () {
    riseIndex = 0;
    baseRender();
    riseIndex = 0;
    if (viewRoot.firstChild) viewRoot.insertBefore(stats(), viewRoot.firstChild);
    if (selected) {
      const open = viewRoot.querySelector(".detail");
      if (open) open.scrollIntoView({ block: "nearest" });
    }
  };

  function show(mode) {
    gate.hidden = mode === "board";
    app.hidden = mode !== "board";
    login.hidden = mode !== "login";
    board.hidden = mode !== "board";
    unavailable.hidden = mode !== "unavailable";
    refresh.hidden = mode !== "board";
    signout.hidden = mode !== "board";
    if (mode === "login") document.getElementById("password").focus();
  }

  async function load() {
    const busy = !refresh.hidden;
    if (busy) {
      refresh.disabled = true;
      refresh.classList.add("is-busy");
      refresh.setAttribute("aria-label", "Refreshing");
    }
    let response;
    try {
      response = await fetch("/api/admin", { cache: "no-store", credentials: "same-origin" });
    } catch (failure) {
      response = null;
    } finally {
      if (busy) {
        refresh.disabled = false;
        refresh.classList.remove("is-busy");
        refresh.setAttribute("aria-label", "Refresh");
      }
    }
    if (!response) {
      error.textContent = "The dashboard could not be loaded.";
      show("login");
      return;
    }
    if (response.status === 404) {
      show("unavailable");
      return;
    }
    if (response.status === 401) {
      show("login");
      return;
    }
    if (!response.ok) {
      error.textContent = "The dashboard could not be loaded.";
      show("login");
      return;
    }
    data = await response.json();
    data.visits = data.visits || [];
    data.chats = data.chats || [];
    render();
    show("board");
  }

  document.querySelectorAll(".dash-nav button").forEach((button) => {
    button.addEventListener("click", () => {
      view = button.dataset.view;
      selected = "";
      page = 1;
      render();
      window.scrollTo(0, 0);
    });
  });
  function syncClear() {
    clearSearch.hidden = !search.value.trim();
  }
  search.addEventListener("input", () => {
    selected = "";
    page = 1;
    syncClear();
    render();
  });
  clearSearch.addEventListener("click", () => {
    search.value = "";
    selected = "";
    page = 1;
    syncClear();
    search.focus();
    render();
  });

  function setPasswordVisible(visible) {
    const field = document.getElementById("password");
    const toggle = document.getElementById("toggle-password");
    if (!field || !toggle) return;
    field.type = visible ? "text" : "password";
    toggle.setAttribute("aria-pressed", visible ? "true" : "false");
    toggle.setAttribute("aria-label", visible ? "Hide password" : "Show password");
    toggle.querySelectorAll("svg").forEach((icon) => {
      const on = icon.classList.contains(visible ? "icon-hide" : "icon-show");
      if (on) icon.removeAttribute("hidden");
      else icon.setAttribute("hidden", "");
    });
  }

  function concealPassword() {
    const field = document.getElementById("password");
    if (field) field.value = "";
    setPasswordVisible(false);
  }

  document.getElementById("toggle-password").addEventListener("click", () => {
    const field = document.getElementById("password");
    setPasswordVisible(field.type === "password");
    field.focus();
  });

  login.addEventListener("submit", async (event) => {
    event.preventDefault();
    error.textContent = "";
    const response = await fetch("/api/admin", {
      method: "POST",
      credentials: "same-origin",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ password: document.getElementById("password").value }),
    });
    if (response.status === 429) {
      error.textContent = "Too many tries. Wait a few minutes.";
      return;
    }
    if (!response.ok) {
      error.textContent = "That password is wrong.";
      return;
    }
    concealPassword();
    await load();
  });

  refresh.addEventListener("click", load);
  signout.addEventListener("click", async () => {
    await fetch("/api/admin", {
      method: "POST",
      credentials: "same-origin",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ logout: true }),
    });
    data = { visits: [], chats: [] };
    selected = "";
    search.value = "";
    page = 1;
    view = "overview";
    viewRoot.replaceChildren();
    lead.textContent = "Visits, IP addresses, locations and saved chats.";
    concealPassword();
    show("login");
  });

  load();
})();
