# Backend Portfolio

Static portfolio for a senior PHP and Laravel backend developer. The pages are the case studies, the shipping workflow, and the contact paths. English is the source. Arabic, French, Dutch, and Japanese are applied in the browser.

## Pages

| Path | What it is |
| --- | --- |
| `/` | Home, five case studies, and contact |
| `/work/` | All ten case studies |
| `/work/<slug>/` | One case study |
| `/how-i-ship/` | The spec-driven workflow |
| `/about/` | Background and experience |
| `/cv/` | Resume preview and PDF |

## Project layout

`build.py` is the source for the HTML. Run it after copy changes. CSS and JavaScript are not generated.

| Path | Role |
| --- | --- |
| `build.py` | Writes the HTML pages and the sitemap |
| `css/site.css` | Layout, theme, and responsive rules |
| `js/site.js` | Language, theme, section rail, and chat |
| `js/ar.js`, `js/langs.js` | Arabic, French, Dutch, and Japanese |
| `api/chat.js` | Serverless chat route used by Vercel |
| `scripts/preview.cjs` | Local server for the site and `/api/chat` |
| `cv/` | Resume page and PDF |

## Local preview

```bash
python3 build.py
node scripts/preview.cjs
```

Open http://127.0.0.1:8777/.

The chat route reads `GEMINI_API_KEY` from the environment. Put that in a local `.env` file. `.env` is gitignored and must stay out of the repository.

## Deploy

Pushes to `main` deploy through the linked Vercel project. The same `GEMINI_API_KEY` variable is set on Vercel, not in this repo. There is no separate build command: the HTML committed here is what production serves, so run `python3 build.py` before pushing copy changes.
