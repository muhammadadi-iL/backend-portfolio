# Muhammad Adil — Portfolio

Public portfolio and private admin for **Muhammad Adil**, a senior backend developer in Karachi, open to remote roles.

The public site is the work: case studies, how he ships, background, resume, and ways to reach him. The admin dashboard is a signed-in panel for visits, locations, and saved chats. It is not part of the public navigation and is blocked from crawlers.

| | |
| --- | --- |
| Live site | https://muhammad-adil-portfolio.vercel.app |
| Alternate alias | https://adil-portfolio-sigma.vercel.app |
| Admin | `/admin/` (password required, noindex) |
| Resume | [/cv/](https://muhammad-adil-portfolio.vercel.app/cv/) |

Stack on the projects: PHP, Laravel, payments, wallets, order lifecycles, and the architecture behind marketplaces, booking systems, and SaaS platforms.

---

## Contact

| | |
| --- | --- |
| Email | [adilm0616@gmail.com](mailto:adilm0616@gmail.com) |
| Phone / WhatsApp | [+92 318 0253146](https://api.whatsapp.com/send/?phone=923180253146&text=Hello%20Muhammad%2C%20I%20saw%20your%20portfolio%20and%20wanted%20to%20reach%20you.&type=phone_number&app_absent=0) |
| GitHub | https://github.com/muhammadadi-iL |
| LinkedIn | https://www.linkedin.com/in/muhammad-adil-khan-7274a1243 |

WhatsApp opens with: *Hello Muhammad, I saw your portfolio and wanted to reach you.*

---

## Public site

### Pages

| Path | Purpose |
| --- | --- |
| `/` | Hero, terminal card, facts, five lead case studies, shorter work, how he ships, contact |
| `/work/` | All case studies, shorter write-ups, earlier work in one line each |
| `/work/<slug>/` | One case study: problem, role, decisions, outcome |
| `/how-i-ship/` | Spec-driven workflow used with coding agents |
| `/about/` | Background, how he works, experience, education, skills |
| `/privacy/` | How visits, cookies, and chats are handled |
| `/cv/` | Resume in the browser and PDF download |
| `/javascript-required/` | Fallback when JavaScript is off |

### Case studies

| | Study | Path |
| --- | --- | --- |
| 01 | VALORA — the agents draft, a person approves | `/work/valora/` |
| 02 | Food Link — a database for every merchant | `/work/food-link/` |
| 03 | Msane — one cart, many factories | `/work/msane/` |
| 04 | Waraq Oman — the order follows the payment | `/work/waraq-oman/` |
| 05 | Alejaar — units, tenants and rent in one system | `/work/alejaar/` |
| 06 | Billing Portal — a monthly charge for each service | `/work/billing-portal/` |
| 07 | The Avatar Coach — a session the system can recall | `/work/avatar-coach/` |
| 08 | Christian Business Finders — search by category and place | `/work/christian-business-finders/` |
| 09 | ASH Shop — Arabic perfumes, in Arabic and English | `/work/ash-shop/` |
| 10 | Christian Ashram — retreats, stories, and a way to give | `/work/christian-ashram/` |

Home lists the first five. `/work/` lists all ten.

### Languages

English is the source in `build.py`. Visitors pick a language in the header; the choice is stored in the browser and applied before paint.

| Code | Language |
| --- | --- |
| EN | English (source) |
| AR | Arabic (RTL) |
| FR | French |
| NL | Dutch |
| JA | Japanese |

Product names, tech names, email, and phone stay as written. The hero terminal stays LTR in every language.

### On-site chat

The chat panel asks about the work, the stack, or how to reach Muhammad.

- Visitor leaves a name (and optional phone/email), then messages.
- After the first successful send, contact fields hide; bubbles show the visitor name and **Muhammad Adil**.
- `POST /api/chat` sends recent turns plus contact. Answers stay within facts published on the site. Missing facts are not invented; WhatsApp is offered instead.
- Replies use `GEMINI_API_KEY` on the server when available; otherwise short local answers for the same public facts.
- Each exchange is saved (visitor line and reply together) for the admin Chats view. Chat rows do not store IP addresses.

### Visits and privacy

With consent, the site records visits (path, approximate location from IP, device). Cookie choices and the privacy policy are on `/privacy/`. A once-a-day reCAPTCHA gate runs when keys are configured (disabled on localhost).

---

## Admin dashboard

Path: **`/admin/`** — English only, `noindex`, disallowed in `robots.txt`.

Sign-in uses `ADMIN_PASSWORD`. A successful login sets an **HttpOnly** session cookie (not the password itself). The session lasts thirty days and refreshes while the dashboard is used. **Sign out** clears it.

### Tabs

| Tab | What it shows |
| --- | --- |
| Overview | Counts and charts for visits, IPs, locations, chats, pages, contacts |
| Activity | Merged visit and chat activity, newest first, paginated |
| Visits | Visit log with detail |
| IP addresses | Grouped by IP |
| Locations | Grouped by place |
| Chats | Threads with contact fields and a scrollable conversation |

The UI follows a dark dashboard look (black surfaces, gray borders, monochrome mark). Public violet branding is unchanged.

### Data

| Store | Cap | Notes |
| --- | --- | --- |
| Visits | Latest 500 | Private blob when `BLOB_READ_WRITE_TOKEN` is set; otherwise local `data/` |
| Chats | Latest 500 | Same store; visitor and model lines written in one append |

`GET /api/admin` needs the session cookie. `GET /api/visit` and `GET /api/chats` are localhost-only in preview; they are not public production endpoints.

---

## Repository layout

`build.py` is the source for public page copy. It writes HTML and `sitemap.xml`. CSS, JavaScript, `api/`, and `admin/` are hand-maintained.

| Path | Role |
| --- | --- |
| `build.py` | Page copy, case studies, HTML generator |
| `index.html`, `about/`, `work/`, `how-i-ship/`, `privacy/` | Generated (or privacy) HTML — commit after rebuild when generated |
| `css/site.css` | Public theme, layout, chat, motion |
| `css/admin.css` | Admin dashboard only |
| `js/site.js` | Language, theme, rail, chat, visits, captcha helpers |
| `js/admin.js` | Admin dashboard controller |
| `js/ar.js`, `js/langs.js` | Translations |
| `api/chat.js` | Chat assistant + save path |
| `api/chats.js` | Chat log helpers / localhost read |
| `api/visit.js` | Visit logging |
| `api/admin.js` | Sign-in, session, dashboard data |
| `api/captcha.js` | reCAPTCHA availability |
| `api/store.js` | Private blob / local file store |
| `admin/` | Dashboard HTML and mark |
| `scripts/preview.cjs` | Local server for static files and `/api/*` |
| `scripts/print-cv.mjs` | Rebuilds the resume PDF |
| `cv/` | Resume page and PDF (hand-maintained) |
| `assets/` | Portrait, cursor, images |
| `favicon.svg` | Public favicon (also used as site mark) |
| `sitemap.xml`, `robots.txt` | SEO and crawl rules |

Kept out of git and deploys:

| Path | Why |
| --- | --- |
| `.env`, `.env.*` | Secrets |
| `.vercel/` | Local Vercel link |
| `data/visits.jsonl`, `data/chats.jsonl` | Local inbox copies |
| `.idea/` | Editor settings |

---

## Local development

Needs Python 3 and Node.js.

```bash
python3 build.py
node scripts/preview.cjs
```

Open http://127.0.0.1:8777/ — listens on `127.0.0.1:8777` unless `PORT` is set.

Optional root `.env` (never commit):

```bash
GEMINI_API_KEY=
ADMIN_PASSWORD=
BLOB_READ_WRITE_TOKEN=
RECAPTCHA_SITE_KEY=
RECAPTCHA_SECRET_KEY=
```

- Without `GEMINI_API_KEY`, chat still works with local public-fact answers.
- Without blob token, visits and chats write under `data/` (gitignored).
- Preview loads `.env` into the process and blocks dotfile URLs, so `/.env` is not served.
- After changing any `api/*.js` file, restart the preview process so Node picks up the new module.

Resume PDF (macOS + Chrome):

```bash
node scripts/print-cv.mjs
```

---

## Editing the public site

1. Change copy in `build.py`.
2. Run `python3 build.py`.
3. Commit the generator and the regenerated HTML together.

Edit `css/site.css`, `js/site.js`, and the language files directly — no rebuild required.

If a visible English sentence changes, update `js/ar.js` and the FR/NL/JA maps in `js/langs.js` so translations stay aligned.

Do not hand-edit generated HTML as the source of truth. Do not invent employers, dates, counts, or project details that are not already on the site.

---

## Deploy

The Vercel project serves the committed static files. There is no separate build command on Vercel for the HTML.

```bash
python3 build.py   # when copy changed
git add …
git commit
git push origin main
```

Set secrets on the Vercel project (Production / Preview as needed): `GEMINI_API_KEY`, `ADMIN_PASSWORD`, `BLOB_READ_WRITE_TOKEN`, and reCAPTCHA keys when the gate should run live. Never put secrets in client code, commits, or pull requests.

---

## Guardrails

- Do not commit `.env` or inbox data files.
- Do not expose `ADMIN_PASSWORD`, blob tokens, or API keys in the README, HTML, or client JS.
- Do not treat `/admin/` as a public page; keep it noindex and out of the main nav.
- Prefer facts already published on the site over new claims in chat or copy.
