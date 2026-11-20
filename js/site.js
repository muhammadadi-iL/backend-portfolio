(function () {
  var root = document.documentElement;
  var dictionaries = {
    ar: window.AR || {},
    fr: window.FR || {},
    nl: window.NL || {},
    ja: window.JA || {}
  };
  var langMeta = {
    en: { code: "EN", dir: "ltr" },
    ar: { code: "AR", dir: "rtl" },
    fr: { code: "FR", dir: "ltr" },
    nl: { code: "NL", dir: "ltr" },
    ja: { code: "JA", dir: "ltr" }
  };

  function currentTheme() {
    return root.dataset.theme === "light" ? "light" : "dark";
  }

  document.querySelectorAll("[data-theme-toggle]").forEach(function (button) {
    button.addEventListener("click", function () {
      var next = currentTheme() === "dark" ? "light" : "dark";
      root.dataset.theme = next;
      try {
        localStorage.setItem("theme", next);
      } catch (e) {}
    });
  });

  function norm(value) {
    return value.replace(/\s+/g, " ").trim();
  }

  function t(text) {
    var dict = dictionaries[root.dataset.lang] || {};
    var key = norm(text);
    return dict[key] || text;
  }

  function applyLang(lang) {
    if (!langMeta[lang]) lang = "en";
    var meta = langMeta[lang];
    var dict = dictionaries[lang] || {};
    root.lang = lang;
    root.dir = meta.dir;
    if (lang === "en") delete root.dataset.lang;
    else root.dataset.lang = lang;

    var walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
    var node;
    while ((node = walker.nextNode())) {
      var parent = node.parentElement;
      if (!parent || parent.closest("script, style, [data-no-i18n]")) continue;
      if (node.__en == null) node.__en = node.nodeValue;
      var original = node.__en;
      var key = norm(original);
      if (!key) continue;
      var lead = original.match(/^\s*/)[0];
      var tail = original.match(/\s*$/)[0];
      node.nodeValue = dict[key] ? lead + dict[key] + tail : original;
    }

    document.querySelectorAll("[alt], [aria-label], [title]").forEach(function (el) {
      if (el.closest("[data-no-i18n]")) return;
      ["alt", "aria-label", "title"].forEach(function (attr) {
        if (!el.hasAttribute(attr)) return;
        if (!el._i18n) el._i18n = {};
        if (el._i18n[attr] == null) el._i18n[attr] = el.getAttribute(attr);
        var key = norm(el._i18n[attr]);
        el.setAttribute(attr, dict[key] || el._i18n[attr]);
      });
    });

    if (!root.dataset.enTitle) root.dataset.enTitle = document.title;
    var titleKey = norm(root.dataset.enTitle);
    document.title = dict[titleKey] || root.dataset.enTitle;

    document.querySelectorAll("[data-lang-code]").forEach(function (el) {
      el.textContent = meta.code;
    });
    document.querySelectorAll("[data-lang]").forEach(function (button) {
      button.classList.toggle("is-current", button.getAttribute("data-lang") === lang);
    });

    root.classList.add("i18n-ready");
  }

  document.querySelectorAll(".lang").forEach(function (box) {
    var toggle = box.querySelector("[data-lang-toggle]");
    var menu = box.querySelector(".lang-menu");
    var frame = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    var shape = document.createElementNS("http://www.w3.org/2000/svg", "polygon");
    frame.setAttribute("class", "lang-frame");
    frame.setAttribute("aria-hidden", "true");
    frame.appendChild(shape);
    if (menu) menu.insertBefore(frame, menu.firstChild);
    function drawLangFrame() {
      if (!menu) return;
      var width = menu.clientWidth;
      var height = menu.clientHeight;
      if (!width || !height) return;
      var topCut = 12;
      var bottomCut = 18;
      var rtl = document.documentElement.dir === "rtl";
      var points = rtl
        ? [[topCut, 0], [width, 0], [width, height - bottomCut], [width - bottomCut, height], [0, height], [0, topCut]]
        : [[0, 0], [width - topCut, 0], [width, topCut], [width, height], [bottomCut, height], [0, height - bottomCut]];
      frame.setAttribute("viewBox", "0 0 " + width + " " + height);
      shape.setAttribute("points", points.map(function (point) { return point.join(","); }).join(" "));
    }
    function setMenu(open) {
      if (!menu || !toggle) return;
      menu.hidden = !open;
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
      if (open) requestAnimationFrame(drawLangFrame);
    }
    if (toggle) {
      toggle.addEventListener("click", function () {
        setMenu(menu.hidden);
      });
    }
    box.querySelectorAll("[data-lang]").forEach(function (button) {
      button.addEventListener("click", function () {
        var next = button.getAttribute("data-lang");
        try { localStorage.setItem("lang", next); } catch (e) {}
        applyLang(next);
        setMenu(false);
      });
    });
    document.addEventListener("click", function (event) {
      if (!box.contains(event.target)) setMenu(false);
    });
    document.addEventListener("keydown", function (event) {
      if (event.key === "Escape") setMenu(false);
    });
  });

  if (root.dataset.lang && langMeta[root.dataset.lang]) applyLang(root.dataset.lang);
  else root.classList.add("i18n-ready");

  var bar = document.querySelector(".read-bar");
  if (bar) {
    var ticking = false;
    function paintBar() {
      var height = document.documentElement.scrollHeight - window.innerHeight;
      var ratio = height > 0 ? window.scrollY / height : 0;
      bar.style.transform = "scaleX(" + Math.min(1, Math.max(0, ratio)) + ")";
      ticking = false;
    }
    window.addEventListener("scroll", function () {
      if (ticking) return;
      ticking = true;
      requestAnimationFrame(paintBar);
    }, { passive: true });
    paintBar();
  }

  var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  var rail = document.querySelector(".rail");
  var spots = Array.prototype.slice.call(document.querySelectorAll("[data-rail]"));
  if (rail && spots.length > 1) {
    var frame = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    frame.setAttribute("class", "rail-frame");
    frame.setAttribute("aria-hidden", "true");
    var shape = document.createElementNS("http://www.w3.org/2000/svg", "polygon");
    frame.appendChild(shape);
    rail.appendChild(frame);
    var track = document.createElement("span");
    track.className = "rail-track";
    track.setAttribute("aria-hidden", "true");
    rail.appendChild(track);
    spots.forEach(function (el, index) {
      if (!el.id) el.id = "section-" + index;
      var link = document.createElement("a");
      link.href = "#" + el.id;
      var label = document.createElement("span");
      label.textContent = el.getAttribute("data-rail");
      var mark = document.createElement("i");
      mark.setAttribute("aria-hidden", "true");
      link.appendChild(label);
      link.appendChild(mark);
      rail.appendChild(link);
    });
    var links = rail.querySelectorAll("a");
    function markRail() {
      var doc = document.documentElement;
      var atEnd = window.scrollY + window.innerHeight >= doc.scrollHeight - 2;
      var line = window.scrollY + window.innerHeight * 0.34;
      var current = atEnd ? spots.length - 1 : 0;
      if (!atEnd) {
        spots.forEach(function (el, index) {
          var top = el.getBoundingClientRect().top + window.scrollY;
          if (top <= line) current = index;
        });
      }
      links.forEach(function (link, index) {
        if (index === current) link.classList.add("is-current");
        else link.classList.remove("is-current");
      });
      var span = links.length > 1 ? (current / (links.length - 1)) * 100 : 0;
      rail.style.setProperty("--rail-progress", span + "%");
    }
    function drawFrame() {
      var width = rail.clientWidth;
      var height = rail.clientHeight;
      if (!width || !height) return;
      var topCut = 14;
      var bottomCut = 28;
      var rtl = document.documentElement.dir === "rtl";
      var points = rtl
        ? [[topCut, 0], [width, 0], [width, height - bottomCut], [width - bottomCut, height], [0, height], [0, topCut]]
        : [[0, 0], [width - topCut, 0], [width, topCut], [width, height], [bottomCut, height], [0, height - bottomCut]];
      frame.setAttribute("viewBox", "0 0 " + width + " " + height);
      shape.setAttribute("points", points.map(function (point) { return point.join(","); }).join(" "));
    }
    if ("ResizeObserver" in window) new ResizeObserver(drawFrame).observe(rail);
    rail.addEventListener("mouseenter", drawFrame);
    drawFrame();
    window.addEventListener("scroll", markRail, { passive: true });
    markRail();
  } else if (rail) {
    rail.hidden = true;
  }

  var chat = document.querySelector(".chat");
  if (chat) {
    var panel = chat.querySelector(".chat-panel");
    var toggle = chat.querySelector(".chat-toggle");
    var clock = chat.querySelector("time");
    function showClock() {
      if (!clock) return;
      var value = new Intl.DateTimeFormat("en-GB", {
        hour: "2-digit",
        minute: "2-digit",
        hour12: false,
        timeZone: "Asia/Karachi"
      }).format(new Date());
      clock.textContent = value;
      clock.dateTime = value;
    }
    showClock();
    setInterval(showClock, 30000);
    function setChat(open) {
      if (!panel || !toggle) return;
      panel.hidden = !open;
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
      if (open && log && !greeted) {
        greeted = true;
        addLine(t("Ask about Muhammad's work, his stack, or how to reach him."), "from-bot");
      }
      if (open && field) field.focus();
    }
    toggle.addEventListener("click", function () {
      setChat(panel.hidden);
    });
    chat.querySelectorAll("[data-chat-close]").forEach(function (button) {
      button.addEventListener("click", function () { setChat(false); });
    });
    document.addEventListener("keydown", function (event) {
      if (event.key === "Escape") setChat(false);
    });
    var log = chat.querySelector(".chat-log");
    var form = chat.querySelector(".chat-form");
    var field = chat.querySelector("#chat-message");
    var handoff = chat.querySelector(".chat-handoff");
    var greeted = false;
    function addLine(text, kind) {
      var line = document.createElement("p");
      line.className = kind;
      line.textContent = text;
      log.appendChild(line);
      log.scrollTop = log.scrollHeight;
    }
    function answer(raw) {
      var q = raw.toLowerCase();
      function has(words) {
        return words.some(function (word) { return q.indexOf(word) !== -1; });
      }
      if (has(["hello", "hi", "hey", "salam", "assalam"])) return "Hello. Ask about Muhammad's work, his stack, or how to reach him.";
      if (has(["email", "e-mail", "gmail"])) return "Email him at adilm0616@gmail.com.";
      if (has(["whatsapp", "phone", "number", "call"])) return "WhatsApp and phone: +92 318 0253146.";
      if (has(["where", "karachi", "location", "remote", "hire", "available", "role"])) return "He is in Karachi and open to remote senior backend roles.";
      if (has(["resume", "cv"])) return "Use Download Resume or Preview Resume on this site.";
      if (has(["language", "urdu", "english", "french", "arabic", "dutch", "japanese"])) return "English and Urdu. Urdu is native. This site also reads in Arabic, French, Dutch and Japanese.";
      if (has(["valora"])) return "VALORA is home-care software. Clients, visits, billing and payroll share one record. Agents draft the paperwork and a person approves it.";
      if (has(["food link", "foodlink"])) return "Food Link is multi-tenant ordering. A new merchant gets its own database, and that step cannot be one transaction.";
      if (has(["msane"])) return "Msane is a B2B marketplace. One checkout becomes several factory orders, and the parts have to add up to the total.";
      if (has(["waraq"])) return "Waraq Oman is an online store. Amwal Pay marks an order paid or failed, and the customer hears about it.";
      if (has(["alejaar"])) return "Alejaar keeps buildings, units, tenants, rent and open maintenance requests in one Laravel application.";
      if (has(["figma", "workflow", "feature pack", "how i ship", "how he ship"])) return "He cuts a Figma file and a business analysis into small feature packs. An agent implements each one under rules that stay fixed. He reviews every change.";
      if (has(["skill", "stack", "laravel", "php", "mysql"])) return "PHP, Laravel and MySQL, plus REST APIs, payments, queues and tests. More than five years with them, over four of those professionally.";
      if (has(["project", "case", "built", "portfolio"])) return "The homepage case studies are VALORA, Food Link, Msane, Waraq Oman and Alejaar. The work page has the rest.";
      if (has(["thiqatech", "techigator", "olive", "company", "job history"])) return "Senior backend developer at Thiqatech, remote with a team in Muscat. Before that, Techigator and Olive Digital. Star of the Quarter at Techigator in 2024.";
      if (has(["who", "about", "experience", "team", "years"])) return "Muhammad Adil is a senior backend developer. On recent projects he was the only backend developer. Before that he led a backend team of up to 4.";
      return "That is not written on this site, so I will not guess. Send it on WhatsApp and Muhammad will read it.";
    }
    var turns = [];
    var busy = false;
    if (form) {
      form.addEventListener("submit", function (event) {
        event.preventDefault();
        var text = field.value.trim();
        if (!text || busy) return;
        if (!greeted) greeted = true;
        addLine(text, "from-user");
        field.value = "";
        if (handoff) handoff.href = "https://api.whatsapp.com/send/?phone=923180253146&text=" + encodeURIComponent(text) + "&type=phone_number&app_absent=0";
        turns.push({ role: "user", text: text });
        if (turns.length > 8) turns = turns.slice(-8);
        busy = true;
        var pending = document.createElement("p");
        pending.className = "from-bot";
        pending.textContent = "…";
        log.appendChild(pending);
        log.scrollTop = log.scrollHeight;
        fetch("/api/chat", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ messages: turns, lang: root.dataset.lang || "en" })
        }).then(function (response) {
          if (!response.ok) throw new Error("unavailable");
          return response.json();
        }).then(function (data) {
          if (!data || !data.reply) throw new Error("empty");
          pending.textContent = data.reply;
          turns.push({ role: "model", text: data.reply });
        }).catch(function () {
          var fallback = t(answer(text));
          pending.textContent = fallback;
          turns.push({ role: "model", text: fallback });
        }).then(function () {
          busy = false;
          log.scrollTop = log.scrollHeight;
        });
      });
    }
  }

  if (root.dataset.lang) applyLang(root.dataset.lang);

  if (!reduce && "IntersectionObserver" in window) {
    var nodes = document.querySelectorAll(".case-list > li, .card, .principles article, .page-head, .job, .section-head");
    nodes.forEach(function (node, index) {
      node.classList.add("reveal");
      node.style.animationDelay = (index % 5) * 45 + "ms";
    });
    var seen = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        entry.target.classList.add("is-in");
        seen.unobserve(entry.target);
      });
    }, { threshold: 0.14, rootMargin: "0px 0px -6% 0px" });
    nodes.forEach(function (node) { seen.observe(node); });
  }

  var dialog = document.querySelector("#cv-preview");
  if (!dialog) return;

  document.addEventListener("click", function (event) {
    var target = event.target;
    if (!(target instanceof Element)) return;
    if (target.closest("[data-cv-preview]")) {
      dialog.showModal();
    } else if (target === dialog || target.closest("[data-cv-close]")) {
      dialog.close();
    }
  });
})();
