# Backend Portfolio

Portfolio of Muhammad Adil, a senior backend developer. The public site is the case studies, the shipping workflow, the background, and the ways to reach him.

Live site: https://muhammad-adil-portfolio.vercel.app

The work is PHP and Laravel: payment flows, wallets, order lifecycles, and the architecture behind marketplaces, booking systems, and SaaS platforms. He is based in Karachi and open to remote senior backend roles.

## Contact

| | |
| --- | --- |
| Email | adilm0616@gmail.com |
| Phone and WhatsApp | +92 318 0253146 |
| GitHub | https://github.com/muhammadadi-iL |
| LinkedIn | https://www.linkedin.com/in/muhammad-adil-khan-7274a1243 |
| Resume | [/cv/](https://muhammad-adil-portfolio.vercel.app/cv/) |

WhatsApp opens with this line already filled in: "Hello Muhammad, I saw your portfolio and wanted to reach you."

## Pages

| Path | What a visitor gets |
| --- | --- |
| `/` | Introduction, terminal card, four facts, the first five case studies, shorter work, how he ships, and contact |
| `/work/` | All ten case studies, then shorter write-ups, then earlier work as one line each |
| `/work/<slug>/` | One case study: the problem, the role, the decisions, and the outcome |
| `/how-i-ship/` | The spec-driven workflow used with coding agents |
| `/about/` | Background, how he works, experience, education, and skills |
| `/cv/` | Resume in the browser, plus the PDF download |

The home page lists five studies. The work page lists all ten.

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

## How the repository is organised

`build.py` is the source for page copy. It writes the HTML files and `sitemap.xml`. CSS and JavaScript are not generated. The resume page and the PDF are maintained by hand.

| Path | Role |
| --- | --- |
| `build.py` | Page copy, case studies, and the HTML generator |
| `index.html`, `about/`, `work/`, `how-i-ship/` | Generated HTML. Commit these after a rebuild |
| `css/site.css` | Theme, layout, motion, and the responsive rules |
| `js/site.js` | Language switch, theme, section rail, and the chat panel |
| `js/ar.js` | Arabic for the published pages |
| `js/langs.js` | French, Dutch, and Japanese |
| `api/chat.js` | Vercel serverless route for the on-site assistant |
| `scripts/preview.cjs` | Local server. Serves the site and `POST /api/chat` |
| `scripts/print-cv.mjs` | Rebuilds `cv/Muhammad-Adil-Resume.pdf` from `cv/index.html` |
| `cv/index.html` | Resume page. Not produced by `build.py` |
| `cv/Muhammad-Adil-Resume.pdf` | One-page resume |
| `assets/` | Portrait, cursor, and other images |
| `sitemap.xml` | Generated with the HTML |

Ignored on purpose:

| Path | Why it stays out |
| --- | --- |
| `.env`, `.env.*` | Holds `GEMINI_API_KEY` |
| `.vercel/` | Local link to the Vercel project |
| `.idea/` | Editor settings |

`.vercelignore` also excludes those paths, plus `.git`, so a deploy cannot publish the key at `/.env`.

## Editing

Change copy in `build.py`, then regenerate the HTML before committing:

```bash
python3 build.py
```

`build.py` uses only the Python standard library. It rewrites:

- `index.html`
- `about/index.html`
- `how-i-ship/index.html`
- `work/index.html` and each `work/<slug>/index.html`
- `sitemap.xml`

Edit `css/site.css`, `js/site.js`, `js/ar.js`, and `js/langs.js` directly. Those files are served as they are. A CSS or JavaScript change does not need `build.py`.

Edit `cv/index.html` by hand. Rebuild the PDF only when the resume copy changes:

```bash
node scripts/print-cv.mjs
```

That script needs Google Chrome on macOS. The PDF is one custom-height page.

## Languages

English is the source written in `build.py`. The visitor picks a language from the header. The choice is saved in `localStorage` and applied before the next paint.

| Code | Language | Coverage |
| --- | --- | --- |
| EN | English | Source |
| AR | Arabic | Published pages, and the page direction becomes right to left |
| FR | French | The same visible strings as the other translations |
| NL | Dutch | The same visible strings as the other translations |
| JA | Japanese | The same visible strings as the other translations |

The header button shows the active code: EN, AR, FR, NL, or JA. The menu lists the language name and the same code.

The terminal card in the hero stays left to right in every language, including Arabic. Product names, technology names, the email address, and the phone number stay as written.

## Chat

The chat button opens a panel on the site. The greeting asks about the work, the stack, or how to reach Muhammad.

A message is sent as `POST /api/chat` with the last eight turns and the current site language. `api/chat.js` answers only from the facts published on the site. If a fact is not there, it says so and points the visitor to WhatsApp. It does not invent employers, dates, numbers, or project details.

The route reads `GEMINI_API_KEY` on the server. The key is not in the HTML, the JavaScript, or this repository. If the route is unavailable, the panel falls back to short answers for the same public facts.

Messages are kept in the browser tab only. They are not written to a database or to `localStorage`. A refresh clears the panel.

## Local preview

Python 3 and Node.js are enough for the site.

```bash
python3 build.py
node scripts/preview.cjs
```

Open http://127.0.0.1:8777/. The server listens on `127.0.0.1` and port `8777` unless `PORT` is set.

Create `.env` in the project root when you want the assistant to answer through the API:

```bash
GEMINI_API_KEY=your-key
```

`scripts/preview.cjs` loads that file into the process environment and refuses any URL whose path contains a dotfile, so `/.env` returns 404. Without the key, the chat panel still opens and uses the short public answers.

A plain Python static server cannot run `/api/chat`. Use `scripts/preview.cjs` for that.

## Deploy

The Vercel project is connected to this repository. A push to `main` deploys production.

There is no Vercel build command. The HTML committed in the repository is what production serves. After a copy change:

```bash
python3 build.py
git add index.html about how-i-ship work sitemap.xml
git commit
git push origin main
```

CSS and JavaScript can be committed without running `build.py`.

`GEMINI_API_KEY` is set on the Vercel project for Production, Preview, and Development. It is a secret there. Do not put the key in a commit, in client-side code, or in a pull request.

Production aliases:

- https://muhammad-adil-portfolio.vercel.app
- https://adil-portfolio-sigma.vercel.app

## What a change should not do

Do not commit `.env`. Do not add the Gemini key to `api/chat.js`, `js/site.js`, or any HTML file. Do not replace the generated HTML by hand. Change `build.py`, run it, and commit the result together with the source.
