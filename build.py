#!/usr/bin/env python3
"""Generate the static portfolio pages."""

from pathlib import Path

ROOT = Path(__file__).resolve().parent

CASES = [
    {
        "num": "01",
        "slug": "valora",
        "domain": "Home care operations",
        "list_domain": "Home care operations · 2026",
        "title": "VALORA — the agents draft, a person approves",
        "summary": "Home care software where clients, visits, billing and payroll share one record, and AI agents prepare the paperwork for someone to approve.",
        "tags": ["Laravel 12", "MySQL", "Alpine.js", "Claude"],
        "stack": ["Laravel 12", "PHP 8.2", "MySQL", "Alpine.js", "Tailwind CSS", "Vite", "Sanctum", "Laravel Reverb", "Claude", "Pest"],
        "meta": [
            ("Role", "Backend developer"),
            ("Year", "2026"),
            ("Live", '<a href="https://www.valoracares.com/" rel="noopener" target="_blank">valoracares.com</a>'),
        ],
        "body": """
<h2 id="the-problem">The problem</h2>
<p>A home care agency loses the week to the same paperwork: an authorization that expires, a claim that waits, a payroll batch typed in by hand, and a visit whose clock-out was never recorded. Clients, caregivers, billing and payroll have to share one record, or the same fact gets entered twice and the two copies drift.</p>
<h2 id="my-role">My role</h2>
<p>I built the backend of VALORA, the operating system for that office. It covers clients and caregivers, authorizations, EVV visits, billing and claims, payroll, the inbox and eFax, and the AI agents that draft the work. The caregiver app uses the same API.</p>
<h2 id="key-decisions">Key decisions</h2>
<h3>A bad visit does not become a bill or a paycheck</h3>
<p>A completed visit whose clock span blows past the duration cap is marked needs review. It is not billable, and payable hours keep the clean visits and leave the flagged ones out. A visit that was clocked in and never clocked out cannot be billed or paid until the clock-out is fixed.</p>
<h3>The monthly bill follows a verified check-in</h3>
<p>A client is billed for a month when three things are true: the month's compliance check-in is verified and not reversed, services were delivered, and an authorization covers the month. Hours come from that verified form. Clock-in and clock-out are only a fallback when the form has no delivered hours, so an EVV gap does not block the bill.</p>
<h3>Agents prepare. A person approves.</h3>
<p>Each agent has an autonomy mode. Where the mode is approval-required, the draft waits in a queue: an authorization renewal, an invoice batch, a payroll batch. Payroll batches that are still pending stay pending until someone approves them. The action is recorded with who made it.</p>
<h3>Portal logins stay in a vault</h3>
<p>State portals and payroll providers need credentials. Those secrets sit in a vault. An agent can receive one only for a key it is allowed to use, and the log records the grant without the password or the key.</p>
<h3>One client for Claude</h3>
<p>Document recognition, an ID scan and a case summary all go through one HTTP client for the Claude API. The model can be overridden per call, and tests replace the HTTP response instead of calling the live API.</p>
<h2 id="outcome">Outcome</h2>
<ul>
<li>The office, the caregiver API, billing, payroll and the agents run as one Laravel application, live at valoracares.com.</li>
<li>A visit with bad time data stays out of the bill and out of the paycheck.</li>
<li>Pest covers the visit gate, billing eligibility, payroll, the approval queue and the mobile API. Playwright covers the screens.</li>
</ul>
""",
    },
    {
        "num": "02",
        "slug": "food-link",
        "domain": "Multi-tenant ordering",
        "list_domain": "Multi-tenant ordering · 2026",
        "title": "Food Link — a database for every merchant",
        "summary": "A multi-tenant ordering platform for restaurants and stores, where creating a new merchant cannot be done in a single transaction.",
        "tags": ['Laravel 13', 'MySQL', 'stancl/tenancy', 'PHPUnit'],
        "stack": ['Laravel 13', 'PHP 8.3', 'MySQL', 'stancl/tenancy', 'laravel-modules', 'Sanctum', 'PHPUnit'],
        "meta": [
            ('Role', 'Sole backend developer'),
            ('Year', '2026'),
            ('Duration', '7 weeks'),
            ('Workflow', 'Spec-first, AI-assisted implementation'),
        ],
        "body": """
<h2 id="the-problem">The problem</h2>
<p>Food Link sells online ordering to restaurants and stores as a subscription. Each merchant gets a storefront, staff accounts, a catalogue and customers with wallets. The requirement that shaped everything else: one merchant's data must be kept apart from every other merchant's.</p>
<h2 id="my-role">My role</h2>
<p>I was the only backend developer, from the empty repository onwards. This case study covers the platform core I built: tenancy and provisioning, subscriptions, the admin and merchant dashboards' APIs, store settings, catalogue, customers and wallets, support tickets, the audit log and exports. The customer storefront and ordering were the next phase.</p>
<h2 id="architecture">Architecture</h2>
<p>A modular monolith with 18 modules. One central database holds the platform itself (merchants, packages, subscriptions). Every merchant has a database of their own.</p>
<p>Every endpoint follows the same path: route, form request, DTO, service, repository, resource.</p>
<p>Modules do not import each other. They talk through contracts that live in a Core module, and each contract has a null implementation, so a module can be switched off without breaking the rest. I wrote the main decisions down as 24 architecture decision records.</p>
<h2 id="key-decisions">Key decisions</h2>
<h3>A database per merchant, not a tenant_id column</h3>
<p>I chose this for two reasons:</p>
<ul>
<li><strong>Isolation.</strong> A forgotten where clause cannot leak another merchant's customers, because those rows are not in the database the request is connected to.</li>
<li><strong>A clean way out.</strong> A merchant who outgrows the platform can leave with their own domain, their own data and a licensed copy of the code. With a database each, that is one database to hand over, with no rows to untangle from shared tables.</li>
</ul>
<h3>One place decides what a merchant may do</h3>
<p>A subscription puts a merchant in one of four states: blocked, in setup, full access or read-only. A single service works that out and middleware enforces it. If the state cannot be resolved, writes are refused.</p>
<h3>Rules enforced by tests, not by convention</h3>
<p>107 architecture tests fail the build when a module reaches into another module, or when a merchant's model is used on the central connection.</p>
<h3>Money as exact decimals</h3>
<p>Prices are calculated to four decimal places and rounded at one point only. The customer wallet is an append-only ledger: every movement locks the wallet row and records the balance before and after.</p>
<h2 id="creating-a-merchant">The hard part: creating a merchant</h2>
<p>Signing up a merchant means writing to the central database and creating a new database. In MySQL, <span class="mono">CREATE DATABASE</span> commits implicitly, so it cannot sit inside a transaction and be rolled back with the rest. If a later step fails, a half-created merchant is left behind.</p>
<p>I built provisioning as a sequence of steps where each step knows how to undo itself.</p>
<ol class="steps">
<li>
<span class="n">01</span>
<div>
<strong>Create the merchant and domain records</strong>
<p>Central database, inside one transaction.</p>
</div>
</li>
<li>
<span class="n">02</span>
<div>
<strong>Create the merchant database</strong>
<p>Outside any transaction, because the statement commits by itself.</p>
<p>If it fails: remove the central records.</p>
</div>
</li>
<li>
<span class="n">03</span>
<div>
<strong>Grant the database user and set the character set</strong>
<p>If it fails: drop the database, then remove the records.</p>
</div>
</li>
<li>
<span class="n">04</span>
<div>
<strong>Run migrations and create the owner account</strong>
<p>Inside the new database.</p>
<p>If it fails: drop the database, then remove the records.</p>
</div>
</li>
<li>
<span class="n">05</span>
<div>
<strong>Mark the merchant as ready</strong>
</div>
</li>
</ol>
<p>Each step after the first has a compensating action that runs if a later step fails.</p>
<p>There was a hosting constraint too. The company's servers run cPanel, where an application cannot simply create databases with a privileged MySQL user. I wrote a database manager that goes through cPanel's own API to create the database, grant the user and set the character set. cPanel can report a failure while still exiting successfully, so the manager reads the response body and does not trust the exit code.</p>
<h2 id="outcome">Outcome</h2>
<ul>
<li>The platform core was delivered in about seven weeks: 18 modules and roughly 250 API routes.</li>
<li>About 2,900 test methods cover it, including tenant isolation, read-only mode, provisioning and the cPanel failure paths.</li>
<li>The architecture is documented in 24 decision records, so the reasoning travels with the code.</li>
</ul>
<h2 id="next">What I would do next</h2>
<ul>
<li>Run the suite against MySQL in CI. Tests currently use SQLite in memory, which does not exercise row locking the way production does.</li>
<li>Add static analysis and a pipeline that runs the tests on every merge request.</li>
<li>Add a test for the full rollback of provisioning, alongside the existing tests for each step.</li>
</ul>
""",
    },
    {
        "num": "03",
        "slug": "msane",
        "domain": "B2B manufacturing marketplace",
        "list_domain": "B2B manufacturing · 2026",
        "title": "Msane — one cart, many factories",
        "summary": "A marketplace where a single checkout becomes several orders, and the parts must add up to the total exactly.",
        "tags": ['Laravel 11', 'MySQL', 'Sanctum', 'PHPUnit'],
        "stack": ['Laravel 11', 'PHP 8.2', 'MySQL', 'Sanctum', 'Socket.IO', 'FCM', 'PHPUnit'],
        "meta": [
            ('Role', 'Sole backend developer'),
            ('Year', '2026'),
            ('Duration', '7.5 weeks'),
            ('Workflow', 'Spec-first, AI-assisted implementation'),
        ],
        "body": """
<h2 id="the-problem">The problem</h2>
<p>Msane connects buyers with factories, wholesalers and designers. A buyer fills one cart with products from several providers and pays once. Behind that single payment:</p>
<ul>
<li>each provider needs an order of their own,</li>
<li>each order needs its share of the coupon, the fees and the VAT,</li>
<li>stock must go down safely when two buyers check out together.</li>
</ul>
<p>On top of the catalogue, custom and design orders are negotiated in chat with quotes, samples and installments, and factory representatives pick up orders on behalf of a factory.</p>
<h2 id="my-role">My role</h2>
<p>I was the only backend developer and wrote almost all of the project: authentication and onboarding, products, cart and checkout, the order lifecycles, returns and refunds, ratings, wallets, settlements and reports.</p>
<h2 id="architecture">Architecture</h2>
<p>Every request follows the same path: controller, form request, DTO, service, repository, resource. Services return a result; they do not throw for business outcomes.</p>
<p>There are 48 repository interfaces. Their methods are named after what the business asks for, such as the pending orders a representative has not been assigned yet. They are not generic create, read, update and delete.</p>
<h2 id="key-decisions">Key decisions</h2>
<h3>Splitting the cart without losing a halala</h3>
<p>Checkout turns the cart into one order per provider. A coupon and a fixed fee apply to the whole cart, so each order gets a proportional share.</p>
<ol class="steps">
<li>
<span class="n">01</span>
<div>
<strong>Group the cart lines by provider</strong>
</div>
</li>
<li>
<span class="n">02</span>
<div>
<strong>Lock the product rows in ascending id order</strong>
<p>Two checkouts with overlapping products take locks in the same order, so they cannot deadlock.</p>
</div>
</li>
<li>
<span class="n">03</span>
<div>
<strong>Reserve the stock</strong>
</div>
</li>
<li>
<span class="n">04</span>
<div>
<strong>Share the coupon and the fixed fee between the orders</strong>
<p>Proportionally, in the smallest currency unit.</p>
</div>
</li>
<li>
<span class="n">05</span>
<div>
<strong>Correct the rounding drift</strong>
<p>Rounding each share can leave the sum off by one unit. The difference is assigned so the shares match the total exactly.</p>
</div>
</li>
<li>
<span class="n">06</span>
<div>
<strong>Create one order per provider with its financial breakdown</strong>
<p>The breakdown is stored as a snapshot, so later price or VAT changes do not rewrite history.</p>
</div>
</li>
</ol>
<p>The parts always sum to the amount the buyer paid.</p>
<h3>A wallet that can hold money</h3>
<p>The wallet I started from could only add and subtract. I rebuilt it as a ledger with row locks and three more operations: reserve, release and withdraw from the reserved amount. A settlement can hold a balance while it is being reviewed. Batch withdrawals take one lock and write one ledger row per order.</p>
<h3>Deadlines that cancel themselves</h3>
<p>An accepted offer must be paid within a time limit, and other steps have limits too. Each deadline is a delayed job that carries the timestamp it was created for. When it runs, it compares that timestamp with the order. If the order has moved on, the job exits. Nothing has to find and delete queued jobs.</p>
<h3>First to accept wins</h3>
<p>Several factory representatives can see the same open order. Acceptance takes a row lock, so only one of them gets it.</p>
<h2 id="outcome">Outcome</h2>
<ul>
<li>Delivered in about seven and a half weeks as the only backend developer.</li>
<li>25 feature test files with about 195 test methods, including three suites that walk a whole lifecycle from start to finish: a representative's order, a return request and a design order.</li>
<li>Each feature is documented with its API description.</li>
</ul>
<h2 id="left">What was left</h2>
<p>Card payment was designed behind a strategy interface, with wallet payment working end to end. Connecting the live gateway was the next step when I moved on. I would also break up the two largest order services, which grew past a thousand lines each.</p>
""",
    },
    {
        "num": "04",
        "slug": "waraq-oman",
        "domain": "E-commerce payments",
        "title": "Waraq Oman — the order follows the payment",
        "summary": "An online store where Amwal Pay has to mark an order paid or failed, and the customer has to hear about it.",
        "tags": ["Laravel", "JavaScript", "jQuery", "Amwal Pay"],
        "role": "Backend developer",
        "live": "https://waraq-oman.com",
        "live_label": "waraq-oman.com",
        "body": """
<h2 id="the-problem">The problem</h2>
<p>Waraq Oman sells online. A customer pays through Amwal Pay, and the order has to change when that payment succeeds or fails. Staff need one place to see the order beside the transaction, and the customer needs to be told what happened.</p>
<h2 id="what-i-built">What I built</h2>
<p>I integrated Amwal Pay so a webhook updates the order status on success and on failure. The same result sends email and WhatsApp notifications. An admin dashboard lists orders and transactions. The storefront is Laravel, with JavaScript and jQuery on the pages that take the payment.</p>
<h2 id="outcome">Outcome</h2>
<ul>
<li>Order status follows the gateway result instead of a manual edit.</li>
<li>The customer is notified when a payment succeeds and when it fails.</li>
<li>Staff review orders and transactions from one dashboard.</li>
</ul>
""",
    },
    {
        "num": "05",
        "slug": "alejaar",
        "domain": "Property operations",
        "title": "Alejaar — units, tenants and rent in one system",
        "summary": "A Laravel 11 application for buildings: who is in which unit, what rent is due, and which maintenance request is open.",
        "tags": ["Laravel 11", "MySQL", "RBAC"],
        "role": "Backend developer",
        "live": "https://sys.alejaar.com",
        "live_label": "sys.alejaar.com",
        "body": """
<h2 id="the-problem">The problem</h2>
<p>A building operation splits across lists: units, the tenants in them, rent that is due, payments that arrived, and maintenance requests that are still open. People in different roles should not all see the same screens.</p>
<h2 id="what-i-built">What I built</h2>
<p>Alejaar is a Laravel 11 system for units, tenants, rent collection, payments and maintenance requests. Access is role-based, so each person sees the work they are allowed to do. Reporting reads those records as they change, instead of waiting on a separate export.</p>
<h2 id="outcome">Outcome</h2>
<ul>
<li>Units, tenants, rent and maintenance live in one system.</li>
<li>Each role has its own access.</li>
<li>Rent and maintenance can be reported from the same records the team already updates.</li>
</ul>
""",
    },
    {
        "num": "06",
        "slug": "billing-portal",
        "domain": "Client billing",
        "title": "Billing Portal — a monthly charge for each service",
        "summary": "An internal portal that creates Stripe payments and keeps a client's monthly bill lined up with the services they are on.",
        "tags": ["Stripe", "Payments", "Billing"],
        "role": "Backend developer",
        "live": "https://billing.nolimitsocial99.com",
        "live_label": "billing.nolimitsocial99.com",
        "body": """
<h2 id="the-problem">The problem</h2>
<p>The team charges clients through Stripe, and the monthly amount depends on the services that client is on. Creating those payments by hand is how a month gets missed, or billed for a service that is no longer active.</p>
<h2 id="what-i-built">What I built</h2>
<p>A billing portal on the Stripe APIs. It creates the payments and manages the monthly bill from the services on the account, so the charge and the services stay on the same record.</p>
<h2 id="outcome">Outcome</h2>
<ul>
<li>Payments are created through Stripe from the portal, not as a one-off charge outside it.</li>
<li>The monthly bill follows the services the client is on.</li>
</ul>
""",
    },
    {
        "num": "07",
        "slug": "avatar-coach",
        "domain": "AI coaching",
        "title": "The Avatar Coach — a session the system can recall",
        "summary": "A coaching product on Laravel. Retrieval brings back earlier context, and the product logs the conversation, the goals and a feedback report.",
        "tags": ["Laravel", "RAG", "MySQL"],
        "role": "Backend developer",
        "live": "https://theavatarcoach.com",
        "live_label": "theavatarcoach.com",
        "body": """
<h2 id="the-problem">The problem</h2>
<p>A coaching conversation is only useful if the next session can use what was said before. The product also has to keep the log, the goals the person set, and a feedback report when the session is done.</p>
<h2 id="what-i-built">What I built</h2>
<p>The Avatar Coach is a Laravel application. Retrieval-augmented generation pulls earlier context into the conversation. The app logs what was said, tracks goals, and produces feedback reports from that record.</p>
<h2 id="outcome">Outcome</h2>
<ul>
<li>A later session can draw on what was already said.</li>
<li>Goals and the conversation log stay with the account.</li>
<li>Feedback is a report, not a thread someone has to reread.</li>
</ul>
""",
    },
    {
        "num": "08",
        "slug": "christian-business-finders",
        "domain": "Directory",
        "title": "Christian Business Finders — search by category and place",
        "summary": "A directory with search and filters, listing management for the business, and a moderation queue for the admin.",
        "tags": ["Laravel", "MySQL", "Search"],
        "role": "Backend developer",
        "live": "https://christianbusinessfinders.com",
        "live_label": "christianbusinessfinders.com",
        "body": """
<h2 id="the-problem">The problem</h2>
<p>A directory only works if a visitor can narrow it by what a business does and where it is, and if a new listing can be held back until someone has checked it.</p>
<h2 id="what-i-built">What I built</h2>
<p>Christian Business Finders is a Laravel directory. Visitors search and filter by category and location. A business registers, then manages its own listing. An admin dashboard is the moderation queue for what stays public.</p>
<h2 id="outcome">Outcome</h2>
<ul>
<li>Visitors search by category and by place.</li>
<li>Owners update their own listing.</li>
<li>Listings can be reviewed before they stay public.</li>
</ul>
""",
    },
    {
        "num": "09",
        "slug": "ash-shop",
        "domain": "Perfume retail",
        "title": "ASH Shop — Arabic perfumes, in Arabic and English",
        "summary": "An Oman storefront for perfume sets: search, a cart, a wishlist, and checkout by card or cash on delivery.",
        "tags": ["PHP", "JavaScript", "Payments"],
        "role": "Backend developer",
        "live": "https://ash-shop.nuewma.com/",
        "live_label": "ash-shop.nuewma.com",
        "body": """
<h2 id="the-problem">The problem</h2>
<p>ASH Shop sells Arabic perfume in Muscat. Shoppers need the catalogue in Arabic and in English, a way to search it, and a cart that can check out by card or when the parcel arrives.</p>
<h2 id="what-i-built">What I built</h2>
<p>A PHP storefront with product search, a wishlist, and a cart. Checkout takes Visa, Mastercard, or cash on delivery. Customers can open their orders, and the shop publishes its shipping and return rules. WhatsApp sits on the page for support. I built it at Thiqatech.</p>
<h2 id="outcome">Outcome</h2>
<ul>
<li>The catalogue, cart, and checkout run in Arabic and English.</li>
<li>A customer can pay by card or on delivery.</li>
<li>Orders, shipping, and returns live in the same shop.</li>
</ul>
""",
    },
    {
        "num": "10",
        "slug": "christian-ashram",
        "domain": "Ministry website",
        "title": "Christian Ashram — retreats, stories, and a way to give",
        "summary": "The public site for United Christian Ashrams: events, blogs, podcasts, resources, and donations.",
        "tags": ["WordPress", "PHP", "Elementor", "jQuery"],
        "role": "Developer",
        "live": "https://christianashram.org/",
        "live_label": "christianashram.org",
        "body": """
<h2 id="the-problem">The problem</h2>
<p>United Christian Ashrams holds retreats in many places. People need one site to understand the ministry, find an event, read and listen, and give.</p>
<h2 id="what-i-built">What I built</h2>
<p>A WordPress site on the Neeon theme, laid out with Elementor. It carries the blog, podcasts, newsletters, and stories, plus books and resources. Forms run on Fluent Forms, with jQuery and Bootstrap on the theme. Visitors can join the email list, contact the office, and open the donation page.</p>
<h2 id="outcome">Outcome</h2>
<ul>
<li>Retreat information, news, and teaching live on one site.</li>
<li>A reader can move from a story or a podcast to a form or a gift.</li>
<li>The office in Ruston, Louisiana has a public contact path.</li>
</ul>
""",
    },
]


def tags(items):
    return "<ul class=\"tags\">" + "".join(f"<li>{item}</li>" for item in items) + "</ul>"


def case_row(case):
    domain = case.get("list_domain", case["domain"])
    return f"""<li>
<a href="/work/{case['slug']}/">
<span class="num mono" aria-hidden="true">{case['num']}</span>
<span class="main">
<span class="domain">{domain}</span>
<span class="title">{case['title']}</span>
<span class="summary">{case['summary']}</span>
{tags(case['tags'])}
</span>
<span class="arrow" aria-hidden="true">→</span>
</a>
</li>"""


HEAD_SCRIPT = """<script>
(function () {
  function cookie(name) {
    var parts = document.cookie ? document.cookie.split("; ") : [];
    for (var i = 0; i < parts.length; i++) {
      var pair = parts[i].split("=");
      if (pair[0] === name) return decodeURIComponent(pair.slice(1).join("="));
    }
    return "";
  }
  try {
    if (cookie("adil-consent")) document.documentElement.classList.add("cookies-set");
    var theme = localStorage.getItem("theme");
    var lang = localStorage.getItem("lang");
    if (cookie("adil-consent") === "all") {
      if (cookie("adil-theme") === "light" || cookie("adil-theme") === "dark") theme = cookie("adil-theme");
      if (cookie("adil-lang")) lang = cookie("adil-lang");
    }
    document.documentElement.dataset.theme = theme === "light" ? "light" : "dark";
    if (lang && lang !== "en") {
      document.documentElement.lang = lang;
      document.documentElement.dir = lang === "ar" ? "rtl" : "ltr";
      document.documentElement.dataset.lang = lang;
      setTimeout(function () { document.documentElement.classList.add("i18n-ready"); }, 2500);
    }
  } catch (e) {
    document.documentElement.dataset.theme = "dark";
  }
})();
</script>"""

TOGGLE = """<button class="theme-toggle" type="button" aria-label="Switch between light and dark" data-theme-toggle>
<svg class="sun" viewBox="0 0 24 24" width="18" height="18" aria-hidden="true"><circle cx="12" cy="12" r="4" fill="none" stroke="currentColor" stroke-width="1.8"></circle><path d="M12 2v2.5M12 19.5V22M2 12h2.5M19.5 12H22M4.9 4.9l1.8 1.8M17.3 17.3l1.8 1.8M4.9 19.1l1.8-1.8M17.3 6.7l1.8-1.8" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"></path></svg>
<svg class="moon" viewBox="0 0 24 24" width="18" height="18" aria-hidden="true"><path d="M20 14.5A8 8 0 0 1 9.5 4a8 8 0 1 0 10.5 10.5z" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"></path></svg>
</button>"""

DIALOG = """<dialog id="cv-preview" class="cv-dialog" aria-labelledby="cv-preview-title">
<div class="bar">
<h2 id="cv-preview-title">Resume</h2>
<a class="btn btn-primary" href="/cv/Muhammad-Adil-Resume.pdf" download>Download PDF</a>
<button type="button" class="close" data-cv-close aria-label="Close"><svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true"><path d="M6 6l12 12M18 6L6 18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"></path></svg></button>
</div>
<iframe class="frame" src="/cv/" title="Muhammad Adil Resume"></iframe>
</dialog>"""

FOOTER = """<footer id="contact" class="contact" data-rail="Contact">
<div class="wrap">
<div class="grid">
<div class="intro">
<p class="eyebrow">Contact</p>
<h2>Get in touch</h2>
<p class="muted">Open to senior backend roles. Email is the fastest way to reach me.</p>
<div class="btn-row">
<a class="btn btn-primary" href="https://api.whatsapp.com/send/?phone=923180253146&amp;text=Hello%20Muhammad%2C%20I%20saw%20your%20portfolio%20and%20wanted%20to%20reach%20you.&amp;type=phone_number&amp;app_absent=0" rel="noopener" target="_blank">Message on WhatsApp</a>
<a class="btn" href="/cv/Muhammad-Adil-Resume.pdf" download>Download Resume (PDF)</a>
<button type="button" class="btn" data-cv-preview>Preview Resume</button>
</div>
</div>
<dl class="details">
<div><dt>Email</dt><dd><a href="mailto:adilm0616@gmail.com">adilm0616@gmail.com</a></dd></div>
<div><dt>Phone</dt><dd><a href="tel:+923180253146">+92 318 0253146</a></dd></div>
<div><dt>WhatsApp</dt><dd><a href="https://api.whatsapp.com/send/?phone=923180253146&amp;text=Hello%20Muhammad%2C%20I%20saw%20your%20portfolio%20and%20wanted%20to%20reach%20you.&amp;type=phone_number&amp;app_absent=0" rel="noopener" target="_blank">Message on WhatsApp</a></dd></div>
<div><dt>Elsewhere</dt><dd class="links"><a class="icon-link" href="https://github.com/muhammadadi-iL" rel="me noopener" target="_blank" aria-label="GitHub"><svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true"><path fill="currentColor" d="M12 2C6.5 2 2 6.6 2 12.2c0 4.5 2.9 8.3 6.9 9.6.5.1.7-.2.7-.5v-1.7c-2.8.6-3.4-1.2-3.4-1.2-.4-1.1-1.1-1.4-1.1-1.4-.9-.6.1-.6.1-.6 1 .1 1.5 1 1.5 1 .9 1.6 2.4 1.1 3 .9.1-.7.4-1.1.6-1.4-2.2-.3-4.6-1.1-4.6-5.1 0-1.1.4-2 1-2.7-.1-.3-.4-1.3.1-2.7 0 0 .8-.3 2.8 1a9.4 9.4 0 0 1 5 0c2-1.3 2.8-1 2.8-1 .5 1.4.2 2.4.1 2.7.7.7 1 1.6 1 2.7 0 4-2.4 4.8-4.6 5.1.4.3.7.9.7 1.9v2.8c0 .3.2.6.7.5 4-1.3 6.9-5.1 6.9-9.6C22 6.6 17.5 2 12 2z"/></svg></a><a class="icon-link" href="https://www.linkedin.com/in/muhammad-adil-khan-7274a1243" rel="me noopener" target="_blank" aria-label="LinkedIn"><svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true"><path fill="currentColor" d="M5.7 8.7H2.9V21h2.8V8.7zM4.3 3C3.3 3 2.5 3.8 2.5 4.8S3.3 6.6 4.3 6.6 6.1 5.8 6.1 4.8 5.3 3 4.3 3zM21.1 21h-2.8v-6.4c0-1.8-.8-2.4-1.8-2.4s-1.9.8-1.9 2.5V21H11.8V8.7h2.7v1.7c.5-.9 1.6-1.9 3.3-1.9 2.2 0 3.3 1.4 3.3 4.2V21z"/></svg></a></dd></div>
</dl>
</div>
<p class="fine">© 2026 Muhammad Adil · Karachi, Pakistan · Open to remote</p>
</div>
</footer>
<div class="cookie-bar" id="cookie-bar" role="dialog" aria-labelledby="cookie-title">
<p class="cookie-kicker" id="cookie-title">Privacy preferences</p>
<p class="cookie-copy">This site counts visits so I can see which pages people read: your IP address, approximate location (from that address), device and the pages you open. With your permission, it also remembers your browser between visits, and the chat can note how you found the site.</p>
<button type="button" class="cookie-btn" data-cookie="all">Accept all</button>
<button type="button" class="cookie-btn" data-cookie="necessary">Necessary only</button>
<button type="button" class="cookie-manage" data-cookie-manage>Manage preferences</button>
</div>
<div class="cookie-modal" id="cookie-modal" hidden>
<div class="cookie-modal-card" role="dialog" aria-modal="true" aria-labelledby="cookie-modal-title">
<button type="button" class="cookie-close" data-cookie-close aria-label="Close"><svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true"><path d="M6 6l12 12M18 6L6 18" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"></path></svg></button>
<p class="cookie-kicker" id="cookie-modal-title">Privacy preferences</p>
<p class="cookie-copy">This site counts visits so I can see which pages people read: your IP address, approximate location (from that address), device and the pages you open. With your permission, it also remembers your browser between visits, and the chat can note how you found the site.</p>
<div class="cookie-option">
<div class="cookie-option-head"><h3>Necessary</h3><span class="cookie-always">Always on</span></div>
<p>Your theme, your language, this chat session, and the visit count described above. The site needs them, so they are always on.</p>
</div>
<div class="cookie-option">
<div class="cookie-option-head"><h3>Remember me between visits</h3><button type="button" class="cookie-switch" id="cookie-remember" role="switch" aria-checked="false" aria-label="Remember me between visits"></button></div>
<p>A random ID stored in your browser, so a return visit is recognised, and your region, referring site, landing page and device attached to your chat messages. Off unless you turn it on.</p>
</div>
<p class="cookie-note">No advertising cookies and no third-party analytics.</p>
<p class="cookie-note">Your location is never read unless you allow it in your browser's own permission prompt.</p>
<p><a class="cookie-policy" href="/privacy/">Privacy Policy</a></p>
<div class="cookie-modal-actions">
<button type="button" class="cookie-btn cookie-btn-fill" data-cookie="save">Save preferences</button>
<button type="button" class="cookie-btn" data-cookie="all">Accept all</button>
<button type="button" class="cookie-btn" data-cookie="necessary">Necessary only</button>
</div>
</div>
</div>"""

MARK = """<span class="mark" aria-hidden="true"><img src="/favicon.svg?v=3" alt="" width="46" height="46"></span>"""
WA_ICON = """<svg class="wa-icon" viewBox="0 0 24 24" width="18" height="18" aria-hidden="true"><circle cx="12" cy="12" r="12" fill="#25D366"/><path fill="#fff" d="M17.47 14.73c-.25.7-1.45 1.34-2 1.42-.52.08-1.16.12-1.87-.12-.43-.14-.98-.32-1.68-.63-2.96-1.28-4.89-4.27-5.04-4.47-.15-.2-1.2-1.59-1.2-3.03s.76-2.15 1.03-2.45c.25-.28.66-.41 1.05-.41.13 0 .25 0 .36.01.32.01.48-.02.72.55.25.62.86 2.13.93 2.28.07.16.12.35.02.56-.1.21-.15.34-.29.52-.14.18-.31.4-.44.53-.14.14-.29.3-.12.57.16.28.72 1.2 1.56 1.94 1.07.95 1.97 1.25 2.27 1.39.28.13.44.11.61-.07.16-.19.7-.81.89-1.09.18-.28.37-.23.62-.14.25.09 1.59.75 1.86.89.27.13.45.2.52.32.07.11.07.66-.18 1.36z"/></svg>"""
CLOSE_ICON = """<svg class="close-icon" viewBox="0 0 24 24" width="16" height="16" aria-hidden="true"><path fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" d="M6.5 6.5l11 11M17.5 6.5l-11 11"/></svg>"""

CHAT = f"""<div class="chat">
<section class="chat-panel" id="chat-panel" hidden>
<header class="chat-head">
{MARK}
<div>
<p class="chat-name">Muhammad Adil</p>
<p class="status"><span class="pulse" aria-hidden="true"></span> Open to remote</p>
<p class="chat-time">Local time in Karachi, Pakistan: <time data-no-i18n datetime="">00:00</time></p>
</div>
<a class="chat-wa" href="https://api.whatsapp.com/send/?phone=923180253146&amp;text=Hello%20Muhammad%2C%20I%20saw%20your%20portfolio%20and%20wanted%20to%20reach%20you.&amp;type=phone_number&amp;app_absent=0" rel="noopener" target="_blank" aria-label="WhatsApp">{WA_ICON}</a>
<button type="button" class="chat-close" data-chat-close aria-label="Close">{CLOSE_ICON}</button>
</header>
<p class="chat-note">An assistant answers from this site. Muhammad reads the saved chat and WhatsApp.</p>
<div class="chat-log" aria-live="polite"></div>
<form class="chat-form">
<div class="chat-fields">
<label for="chat-name">Name</label>
<input id="chat-name" type="text" autocomplete="name" maxlength="80">
<div class="chat-fields-row">
<div>
<label for="chat-phone">Phone</label>
<input id="chat-phone" type="tel" autocomplete="tel" maxlength="40" inputmode="tel">
</div>
<div>
<label for="chat-email">Email</label>
<input id="chat-email" type="text" autocomplete="email" maxlength="120" inputmode="email">
</div>
</div>
</div>
<p class="chat-error" id="chat-error" hidden></p>
<label for="chat-message">Your message</label>
<textarea id="chat-message" rows="2"></textarea>
<div class="chat-actions">
<button class="chat-send" type="submit">Send</button>
<a class="chat-handoff" href="https://api.whatsapp.com/send/?phone=923180253146&amp;text=Hello%20Muhammad%2C%20I%20saw%20your%20portfolio%20and%20wanted%20to%20reach%20you.&amp;type=phone_number&amp;app_absent=0" rel="noopener" target="_blank">{WA_ICON}<span>WhatsApp</span></a>
</div>
</form>
</section>
<button class="chat-toggle" type="button" aria-expanded="false" aria-controls="chat-panel" aria-label="Open chat"><svg viewBox="0 0 32 32" width="28" height="28" aria-hidden="true"><path fill="currentColor" d="M7 6.2h15.6a3.4 3.4 0 0 1 3.4 3.4v8.4a3.4 3.4 0 0 1-3.4 3.4h-7.6L9 26.6a1.1 1.1 0 0 1-1.8-.9v-4.3H7a3.4 3.4 0 0 1-3.4-3.4V9.6A3.4 3.4 0 0 1 7 6.2Z"/><circle cx="11.2" cy="14.3" r="1.45" fill="#5b35f0"/><circle cx="16" cy="14.3" r="1.45" fill="#5b35f0"/><circle cx="20.8" cy="14.3" r="1.45" fill="#5b35f0"/></svg></button>
</div>
<nav class="rail" aria-label="Sections"></nav>"""


def nav(current):
    items = [
        ("/work/", "Work", "work"),
        ("/how-i-ship/", "Process", "process"),
        ("/about/", "About", "about"),
    ]
    parts = []
    for href, label, key in items:
        current_attr = ' aria-current="page"' if key == current else ""
        parts.append(f'<a href="{href}"{current_attr}>{label}</a>')
    parts.append('<a class="contact-link" href="#contact">Contact</a>')
    return "".join(parts)


def page(path, title, description, body, current=None, tone=None):
    body_attr = f' class="{tone}"' if tone else ""
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{title}</title>
<meta name="description" content="{description}">
<meta name="theme-color" content="#0c1024">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{description}">
<meta property="og:type" content="website">
<link rel="icon" href="/favicon.svg?v=3" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans+Arabic:wght@400;500;600&family=IBM+Plex+Sans:wght@400;500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/css/site.css">
{HEAD_SCRIPT}
<noscript><meta http-equiv="refresh" content="0;url=/javascript-required/"></noscript>
</head>
<body{body_attr}>
<div class="captcha-gate" id="captcha-gate" hidden>
<div class="captcha-card" role="dialog" aria-modal="true" aria-labelledby="captcha-title">
{MARK}
<p class="eyebrow">Quick check</p>
<h2 id="captcha-title">Confirm you are a person</h2>
<p>This runs once a day in this browser. It stays off while you move between pages.</p>
<div id="captcha-widget"></div>
<p class="captcha-error" hidden>That check did not pass. Try again.</p>
</div>
</div>
<div class="aurora" aria-hidden="true"></div>
<a class="skip" href="#main">Skip to content</a>
<div class="read-bar" aria-hidden="true"></div>
<header class="site-header">
<div class="wrap bar">
<a class="brand" href="/">{MARK}<span class="brand-copy"><span class="brand-name">Muhammad Adil</span><span class="brand-role">Senior Backend Developer</span></span></a>
<nav aria-label="Main">{nav(current)}</nav>
<div class="tools"><div class="lang" data-no-i18n><button class="lang-toggle" type="button" data-lang-toggle aria-expanded="false" aria-controls="lang-menu" aria-label="Language"><svg viewBox="0 0 24 24" width="16" height="16" aria-hidden="true"><circle cx="12" cy="12" r="8" fill="none" stroke="currentColor" stroke-width="1.6"/><path d="M4 12h16M12 4c2.2 2.4 3.3 5.1 3.3 8s-1.1 5.6-3.3 8c-2.2-2.4-3.3-5.1-3.3-8s1.1-5.6 3.3-8z" fill="none" stroke="currentColor" stroke-width="1.6"/></svg><span data-lang-code>EN</span></button><div class="lang-menu" id="lang-menu" hidden><button type="button" data-lang="en" class="is-current">English<span>EN</span></button><button type="button" data-lang="ar">العربية<span>AR</span></button><button type="button" data-lang="fr">Français<span>FR</span></button><button type="button" data-lang="nl">Nederlands<span>NL</span></button><button type="button" data-lang="ja">日本語<span>JA</span></button></div></div>{TOGGLE}</div>
</div>
</header>
<main id="main">
{body}
</main>
{FOOTER}
{CHAT}
{DIALOG}
<script src="/js/ar.js"></script>
<script src="/js/langs.js"></script>
<script src="/js/site.js"></script>
</body>
</html>
"""
    dest = ROOT / path
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(html)
    print(path)


def case_list(cases=None):
    items = CASES if cases is None else cases
    return '<ol class="case-list">' + "".join(case_row(case) for case in items) + "</ol>"


def home():
    body = f"""
<section class="hero" id="home" data-rail="Home">
<div class="hero-dots" aria-hidden="true"></div>
<div class="wrap">
<div class="who">
<img class="avatar" src="/assets/avatar.jpg" alt="Muhammad Adil" width="340" height="340">
<div>
<p class="eyebrow">Senior Backend Developer</p>
<p class="status"><span class="pulse" aria-hidden="true"></span> Open to remote</p>
</div>
</div>
<div class="hero-grid">
<div class="hero-copy">
<h1>Backends where money, state and concurrency have to be right.</h1>
<p class="lead">I'm Muhammad Adil. I've worked with PHP and Laravel for more than five years, over four of them professionally, building the server side of marketplaces, booking systems and SaaS platforms: payment flows, wallets, order lifecycles and the architecture that keeps them maintainable.</p>
</div>
<div class="actions">
<a class="btn btn-primary" href="#cases">Read the case studies <span class="arrow" aria-hidden="true">→</span></a>
<a class="btn" href="/cv/Muhammad-Adil-Resume.pdf" download>Download Resume</a>
<button type="button" class="btn" data-cv-preview>Preview Resume</button>
</div>
<aside class="term" data-no-i18n aria-label="Profile">
<header>
<span class="term-dots" aria-hidden="true"><i></i><i></i><i></i></span>
<span class="term-title">muhammad-adil — zsh</span>
<span class="term-live"><span class="pulse" aria-hidden="true"></span> Online</span>
</header>
<pre><span class="prompt">$</span> whoami   <span>muhammad-adil</span>
<span class="prompt">$</span> role     <span>senior-backend-developer</span>
<span class="prompt">$</span> focus    <span>php / laravel / react / vue</span>
<span class="prompt">$</span> backend  <span>rest-apis / firebase / postgres</span>
<span class="prompt">$</span> cloud    <span>google-cloud / google-oauth</span>
<span class="prompt">$</span> ai       <span>openai / embeddings / gpt</span>
<span class="prompt">$</span> workflow <span>spec-driven feature packs</span>
<span class="prompt">$</span> deployment <span>vercel / aws / hostinger / vps / node</span>
<span class="prompt">$</span> delivered <span>50+ projects</span>
<span class="prompt">$</span> status   <span>open-to-opportunities</span>
<span class="prompt">$</span> email    <span>adilm0616@gmail.com</span>
<span class="prompt">$</span> <i class="term-caret" aria-hidden="true"></i></pre>
</aside>
</div>
<dl class="hero-facts">
<div><dt>Experience</dt><dd>5+ years</dd></div>
<div><dt>Delivered</dt><dd>50+ projects</dd></div>
<div><dt>Focus</dt><dd>PHP / Laravel / React / Vue</dd></div>
<div><dt>Based in</dt><dd>Karachi, Pakistan</dd></div>
</dl>
<a class="scroll-cue" href="#cases">Scroll<span aria-hidden="true"></span></a>
</div>
</section>
<section class="section" id="cases" data-rail="Cases">
<div class="wrap">
<div class="section-head">
<h2>Case studies</h2>
<p>Five projects, each told as a problem, the decisions I made and what came out of them.</p>
</div>
{case_list(CASES[:5])}
</div>
</section>
<section class="section" id="more" data-rail="Work">
<div class="wrap">
<div class="section-head">
<h2>More work</h2>
<p>Four projects, with the longer notes on the work page.</p>
</div>
<div class="cards">
<article class="card">
<header>
<p class="domain">Multi-vendor local delivery · 2024–2025</p>
<h3><a href="/work/#thunder">Thunder</a></h3>
<p class="role muted">Backend developer in a small team</p>
</header>
<p>A delivery marketplace with customer, store and driver apps, and an order that moves through 13 states. The distinctive piece is ordering an item the store has not priced yet.</p>
<p class="highlight-line"><span class="label">What stood out:</span> Negotiating a price inside the chat.</p>
<ul class="tags"><li>Laravel 9</li><li>MySQL</li><li>Socket.IO</li><li>FCM</li></ul>
</article>
<article class="card">
<header>
<p class="domain">Academic research services · 2025–2026</p>
<h3><a href="/work/#mosaed-elbhos">Mosaed Elbhos</a></h3>
<p class="role muted">Lead backend developer</p>
</header>
<p>A live platform connecting researchers with consultants, technicians and institutions. About thirteen request workflows and a course platform share one order lifecycle.</p>
<p class="highlight-line"><span class="label">What stood out:</span> Many order types, one lifecycle.</p>
<ul class="tags"><li>Laravel 11</li><li>MySQL</li><li>MyFatoorah</li><li>FCM</li></ul>
</article>
<article class="card">
<header>
<p class="domain">Virtual leadership learning</p>
<h3><a href="/work/#experience-accelerator">The Experience Accelerator</a></h3>
<p class="role muted">Backend developer</p>
</header>
<p>A learning platform for leadership practice. It covers behaviour assessment, progress over time, role-based access and feedback workflows.</p>
<p class="highlight-line"><span class="label">What stood out:</span> Assessment, progress and feedback share one account.</p>
{tags(["Laravel", "MySQL", "RBAC"])}
</article>
<article class="card">
<header>
<p class="domain">E-commerce data · Techigator · 2023–2024</p>
<h3><a href="/work/#data-aggregation">Data aggregation</a></h3>
<p class="role muted">Backend developer</p>
</header>
<p>Crawlers collect product pages, an ETL pipeline loads MySQL, and Pusher and Firebase carry live updates and sign-in. Proxy rotation keeps a blocked address from stopping the run.</p>
<p class="highlight-line"><span class="label">What stood out:</span> The crawl still lands as rows someone can query.</p>
{tags(["Laravel", "Scrapy", "Goutte", "MySQL", "Pusher", "Firebase"])}
</article>
</div>
<p class="more"><a href="/work/">All projects <span class="arrow" aria-hidden="true">→</span></a></p>
</div>
</section>
<section class="section" id="ship" data-rail="Process">
<div class="wrap about-block">
<div class="section-head">
<h2>How I ship</h2>
<p>I built a workflow that turns a Figma file and a business analysis into small feature packs, then has AI agents implement each one under fixed architecture rules. I review every change and own the decisions.</p>
</div>
<p class="more"><a href="/how-i-ship/">See the workflow <span class="arrow" aria-hidden="true">→</span></a></p>
</div>
</section>
<section class="section" id="about" data-rail="About">
<div class="wrap about-block">
<div class="section-head">
<h2>About</h2>
<p>Sole backend developer on most of what you see here, and a former backend team head who led up to 4 developers: reviewing code, mentoring developers and owning delivery.</p>
</div>
<p class="more"><a href="/about/">More about how I work <span class="arrow" aria-hidden="true">→</span></a></p>
</div>
</section>
"""
    page(
        "index.html",
        "Muhammad Adil — Senior Backend Developer",
        "Senior backend developer (PHP and Laravel). Payment flows, wallets, order lifecycles and the architecture behind marketplaces, booking systems and SaaS platforms.",
        body,
    )


def work():
    body = f"""
<section class="page-head" data-rail="Work">
<div class="wrap">
<h1>Work</h1>
<p class="lead">Case studies first, then shorter write-ups, then earlier work in a line each.</p>
</div>
</section>
<section class="section" id="cases">
<div class="wrap">
<div class="section-head">
<h2>Case studies</h2>
</div>
{case_list()}
</div>
</section>
<section class="section">
<div class="wrap">
<div class="section-head">
<h2>In brief</h2>
</div>
<div class="cards">
<article class="card" id="thunder">
<header>
<p class="domain">Multi-vendor local delivery · 2024–2025</p>
<h3>Thunder</h3>
<p class="role muted">Backend developer in a small team</p>
</header>
<p>A delivery marketplace for supermarkets, pharmacies and produce shops with three apps (customer, store and driver) and an order that moves through 13 states. I set up the service layer and its generator, built the driver side of the order lifecycle, and built its most distinctive feature: ordering something that has no price yet.</p>
<div class="highlight">
<p class="label">What stood out</p>
<h4>Negotiating a price inside the chat</h4>
<ul>
<li>A customer asks for an item the store has not priced. The request opens a private chat room with the store instead of an order.</li>
<li>The store answers with an invoice sent as a typed chat message. Its status changes in place as the customer accepts or declines.</li>
<li>On payment the invoice is converted into a normal order, with VAT and the store and driver commissions split, so everything after that reuses the standard lifecycle.</li>
<li>Each state change has its own request class that checks who is asking and what the previous state was.</li>
</ul>
</div>
<ul class="tags"><li>Laravel 9</li><li>MySQL</li><li>Socket.IO</li><li>FCM</li></ul>
</article>
<article class="card" id="mosaed-elbhos">
<header>
<p class="domain">Academic research services marketplace · 2025–2026</p>
<h3>Mosaed Elbhos</h3>
<p class="role muted">Lead backend developer</p>
</header>
<p>A live platform that connects researchers with consultants, technicians and institutions. It covers about thirteen request workflows (consultations, research, partial services, ethical approval, publishing, conferences and grants) plus a course platform, across five kinds of account.</p>
<div class="highlight">
<p class="label">What stood out</p>
<h4>Many order types, one lifecycle</h4>
<ul>
<li>One order service drives every paid order type, so an offer, an acceptance or a payment behaves the same way whatever is being ordered.</li>
<li>Two commercial paths share that lifecycle: individuals pay half up front and the rest on delivery, while users sponsored by an institution skip the offer and payment steps.</li>
<li>Course videos upload in resumable chunks, and a lock guarantees the file is assembled exactly once.</li>
<li>The settlements and payment modules written here were later moved into the company starter kit and reused on other projects.</li>
</ul>
</div>
<ul class="tags"><li>Laravel 11</li><li>MySQL</li><li>MyFatoorah</li><li>FCM</li></ul>
</article>
<article class="card" id="experience-accelerator">
<header>
<p class="domain">Virtual leadership learning</p>
<h3>The Experience Accelerator</h3>
<p class="role muted">Backend developer · <a href="https://theexperienceaccelerator.com" rel="noopener" target="_blank">theexperienceaccelerator.com</a></p>
</header>
<p>A learning platform for leadership practice. It covers behaviour assessment, progress over time, role-based access and feedback workflows.</p>
<div class="highlight">
<p class="label">What stood out</p>
<h4>Assessment, progress and feedback share one account</h4>
<ul>
<li>Behaviour assessment, progress and feedback are parts of the same product, not three exports.</li>
<li>Role-based access decides who can see a learner's record and who can leave feedback.</li>
</ul>
</div>
{tags(["Laravel", "MySQL", "RBAC"])}
</article>
<article class="card" id="data-aggregation">
<header>
<p class="domain">E-commerce data · Techigator · 2023–2024</p>
<h3>Data aggregation</h3>
<p class="role muted">Backend developer</p>
</header>
<p>An e-commerce data platform. Crawlers collect pages, an ETL pipeline loads MySQL, and Pusher and Firebase carry live updates and sign-in.</p>
<div class="highlight">
<p class="label">What stood out</p>
<h4>The crawl still lands as rows someone can query</h4>
<ul>
<li>Scrapy and Goutte extract the pages. The pipeline transforms them and loads MySQL.</li>
<li>Proxy rotation keeps a blocked address from ending the run.</li>
<li>Pusher and Firebase cover live updates and sign-in on the product side.</li>
</ul>
</div>
{tags(["Laravel", "Scrapy", "Goutte", "MySQL", "Pusher", "Firebase"])}
</article>
</div>
</div>
</section>
<section class="section">
<div class="wrap">
<div class="section-head">
<h2>Other projects</h2>
<p>Earlier and smaller work.</p>
</div>
<ul class="line-list">
<li>
<div class="row">
<span>
<span class="name">Dras</span>
<span class="desc">Education app: one-to-one video lessons, school and nursery enrolment, and a bookstore.</span>
</span>
<span class="meta">Laravel 9 · 2023–2024</span>
</div>
</li>
<li>
<div class="row">
<span>
<span class="name">Sam</span>
<span class="desc">Healthcare booking across centres, branches and doctors, at the clinic or as a home visit.</span>
</span>
<span class="meta">Laravel 9 · 2024</span>
</div>
</li>
<li>
<div class="row">
<span>
<span class="name">Slasel</span>
<span class="desc">Membership platform with consultations, seminars, training courses and a digital store.</span>
</span>
<span class="meta">Laravel 9 · 2024–2025</span>
</div>
</li>
<li>
<div class="row">
<span>
<span class="name">Edu Hub</span>
<span class="desc">Course marketplace for training centres, with commissions and provider settlements.</span>
</span>
<span class="meta">Laravel 11 · 2025</span>
</div>
</li>
<li>
<div class="row">
<span>
<span class="name">Haddaf</span>
<span class="desc">Pick-up football: stadium owners publish games and players book a seat, with or without a guest.</span>
</span>
<span class="meta">Laravel 11 · 2025–2026</span>
</div>
</li>
<li>
<div class="row">
<span>
<span class="name">Wezna</span>
<span class="desc">Fitness and nutrition app: training programmes, meal logging and daily reward points.</span>
</span>
<span class="meta">Laravel 11 · 2026</span>
</div>
</li>
<li>
<div class="row">
<span>
<span class="name">ShopBase</span>
<span class="desc">White-label e-commerce backend deployed once per shop, with checkout and loyalty points.</span>
</span>
<span class="meta">Laravel 12 · 2026</span>
</div>
</li>
<li>
<div class="row">
<span>
<span class="name">B-I</span>
<span class="desc">Investment brokerage platform where the admin mediates every deal between investor and advertiser.</span>
</span>
<span class="meta">Laravel 12 · 2026</span>
</div>
</li>
<li>
<div class="row">
<span>
<span class="name">Saudia Ticket</span>
<span class="desc">Event-ticket resale marketplace with admin approval, online payment and seller settlements.</span>
</span>
<span class="meta">Laravel 10 · 2024–2025</span>
</div>
</li>
<li>
<div class="row">
<span>
<span class="name">Restaurants</span>
<span class="desc">Multi-vendor restaurant ordering with customer and courier apps and live order tracking.</span>
</span>
<span class="meta">Laravel 8 · 2022–2023</span>
</div>
</li>
<li>
<div class="row">
<span>
<span class="name">Fat2Fit</span>
<span class="desc">Nutrition clinic system. Took over an existing codebase and added memberships, finance and per-client plans.</span>
</span>
<span class="meta">Laravel 9 · 2023</span>
</div>
</li>
<li>
<div class="row">
<span>
<span class="name">Jufrah</span>
<span class="desc">Classifieds marketplace in seven countries. Production support: cross-country time display, and Al Rajhi Bank and Fawry payment fixes.</span>
</span>
<span class="meta">Laravel · 2022–2023</span>
</div>
</li>
<li>
<a class="row" href="https://film-in-saudi.netlify.app" rel="noopener" target="_blank">
<span>
<span class="name">Film In Saudi</span>
<span class="desc">A film-crew listing. People find available crew, hire them, or follow a job already in progress.</span>
</span>
<span class="meta">React</span>
</a>
</li>
<li>
<a class="row" href="https://unique-advertisers.netlify.app" rel="noopener" target="_blank">
<span>
<span class="name">Unique Advertisers</span>
<span class="desc">An informational site. Visitors compare packages and leave a lead.</span>
</span>
<span class="meta">React</span>
</a>
</li>
<li>
<div class="row">
<span>
<span class="name">Recruitment software</span>
<span class="desc">A hiring product with Laravel on the server and React on the client.</span>
</span>
<span class="meta">Laravel · React</span>
</div>
</li>
</ul>
</div>
</section>
"""
    page(
        "work/index.html",
        "Work — Muhammad Adil",
        "Case studies and other backend work by Muhammad Adil: multi-tenant ordering, marketplace checkout, payments, billing and earlier products.",
        body,
        "work",
        "page-work",
    )


def case_facts(case):
    if "meta" in case:
        rows = "\n".join(
            f"<div><dt>{label}</dt><dd>{value}</dd></div>" for label, value in case["meta"]
        )
    else:
        rows = (
            f"<div><dt>Role</dt><dd>{case['role']}</dd></div>\n"
            f"<div><dt>Live</dt><dd><a href=\"{case['live']}\" rel=\"noopener\" target=\"_blank\">{case['live_label']}</a></dd></div>"
        )
    stack = case.get("stack", case["tags"])
    return f"""
<aside class="facts" aria-label="{case['title']}">
<dl>
{rows}
<div><dt>Stack</dt><dd>{tags(stack)}</dd></div>
</dl>
</aside>
"""


def cases():
    for case in CASES:
        facts = case_facts(case)
        body = f"""
<header class="case-head">
<div class="wrap">
<a class="back" href="/work/"><span class="arrow" aria-hidden="true">←</span>All work</a>
<p class="eyebrow">Case study · {case['domain']}</p>
<h1>{case['title']}</h1>
<p class="lead">{case['summary']}</p>
</div>
</header>
<div class="wrap layout">
{facts}
<div class="prose">{case['body']}</div>
</div>
"""
        page(
            f"work/{case['slug']}/index.html",
            f"{case['title'].split('—')[0].strip()} — Muhammad Adil",
            case["summary"],
            body,
            "work",
        )


def ship():
    body = """
<section class="page-head ship" data-rail="Process">
<div class="wrap ship-wrap">
<p class="ship-kicker">Process</p>
<h1>How I ship — a spec-driven workflow for AI coding agents</h1>
<p class="lead">I built a workflow that cuts a Figma file and a business analysis into small feature packs, then has an AI agent implement each one under architecture rules it cannot renegotiate. I use it on my own projects and taught it to other developers.</p>

<h2>Why I built it</h2>
<p>Ask an AI agent to build the orders module and you get code that looks plausible and matches neither the design nor the business rules. Every session also invents its own architecture, so the tenth feature does not look like the first.</p>
<p>The model is rarely the problem. The input is. A whole Figma file and a long analysis document are too big and too vague to implement from, for an agent or for a person.</p>
<p>So the workflow does two things. It cuts the project into pieces small enough to leave no room for guessing, and it gives the agent rules that stay the same from the first feature to the last.</p>

<h2>Stage 1: from design and analysis to feature packs</h2>
<ol class="spec-card">
<li><span class="spec-n">01</span><div><strong>Pull the Figma file as JSON</strong><span>A script calls the Figma API and saves the raw file.</span></div></li>
<li><span class="spec-n">02</span><div><strong>Reduce it to a spec</strong><span>A second script keeps what a backend needs to know (screens, fields, flows) and drops the drawing data.</span></div></li>
<li><span class="spec-n">03</span><div><strong>Split by actor</strong><span>Customer, provider, representative, admin. The Figma spec and the business analysis are both split, so each actor has its own screens file and its own business file.</span></div></li>
<li><span class="spec-n">04</span><div><strong>Split each actor into features</strong><span>Three separate agent runs with one job each: scan and index, extract the fragments, build the packs.</span></div></li>
<li class="is-done"><span class="spec-n">05</span><div><strong>A feature pack per feature</strong><span>Screens, business rules and an execution prompt, in one numbered folder.</span></div></li>
<li class="spec-note">The output is one folder per feature, ready to be implemented without the rest of the project in view.</li>
</ol>
<p>A feature pack holds three files:</p>
<ul class="ship-points">
<li><strong>The screens of this feature</strong>, as a fragment of the Figma spec.</li>
<li><strong>The business rules of this feature</strong>, as a fragment of the analysis.</li>
<li><strong>An execution prompt</strong>: what to build, which features it depends on, and where each requirement comes from.</li>
</ul>
<p>Two rules are written into every pack. When the design and the business analysis disagree, the business analysis wins. And the agent may not invent a business rule that is not in the pack. Every field and rule carries a tag saying whether it came from the analysis or from the design.</p>

<h2>Stage 2: implementing a feature</h2>
<p>The project itself carries the rules. I call the main file the constitution. It is about 1,500 lines and fixes the things that should never vary between features: layering, naming, the shape of DTOs and requests, the response envelope, translations, API documentation, query performance and seed data.</p>
<p>One decision is taken once per project and then locked: whether the code uses a repository layer or a leaner path from service to model. The agent asks on the first feature, records the answer and never asks again.</p>
<p>To build a feature I name its folder and say “execute”.</p>
<ol class="spec-card">
<li><span class="spec-n">01</span><div><strong>Read the pack and the constitution, then open a branch</strong></div></li>
<li><span class="spec-n">02</span><div><strong>Build in a fixed order</strong><span>Migrations, enums, DTOs, repositories, services, requests, resources, controllers, routes.</span></div></li>
<li><span class="spec-n">03</span><div><strong>Sync the API collection after every endpoint</strong><span>The work does not continue until the request exists in the shared collection.</span></div></li>
<li><span class="spec-n">04</span><div><strong>Admin screens, translations, feature tests, API documentation</strong></div></li>
<li><span class="spec-n">05</span><div><strong>Run the quality gate</strong><span>A checklist of about 25 items. Every unchecked box is fixed before the feature counts as complete.</span></div></li>
<li class="is-done"><span class="spec-n">06</span><div><strong>Commit, push and open a merge request</strong><span>The pack then moves to a finished folder, so the list of open features is always the list of remaining work.</span></div></li>
</ol>
<p>The same order for every feature, on every project.</p>
<p>The same folder name with the word “review” starts a different mode. The agent compares existing code with the pack and the constitution, refactors what breaks the rules and generates whatever is missing. That makes the workflow usable on a project that is already half built.</p>

<h2>What I added on the latest project</h2>
<p>On Al-Kout I kept the feature packs and changed how the work is driven.</p>
<ul class="ship-points">
<li><strong>Delivery cycles.</strong> Features are grouped into cycles. Each cycle starts with a planning agent that writes a plan: the shared entities, the state machine, the order of pull requests, an acceptance scenario and a list of questions for me. I answer all the questions in one go, before any code is written.</li>
<li><strong>Separate agents for planning, implementing and reviewing.</strong> No agent reviews its own work.</li>
<li><strong>Triage before code.</strong> A pack that describes a navigation shell or another screen-only feature is classified as a frontend reference, and no backend code is written for it.</li>
<li><strong>One register for deferred work.</strong> Every agreed deferral has an identifier, a reason and a description of what remains. The agent may not record an approval I did not give.</li>
<li><strong>Skills.</strong> Thirteen small, reusable procedures such as generating a DTO, creating a repository or reviewing an endpoint.</li>
</ul>

<h2>Where I stay in the loop</h2>
<p>Two rules matter more than the rest:</p>
<ul class="ship-points">
<li>A question the plan does not cover stops the work. The agent asks. It does not assume.</li>
<li>Nothing is merged without my explicit decision.</li>
</ul>
<p>Beyond those, the division is simple. I choose the architecture and write the rules. I answer the business questions. I review each pull request and run the full test suite myself. The agent does the typing, in an order that does not change.</p>

<h2>What it has produced</h2>
<ul class="ship-points">
<li>Msane, the first full project built this way: a B2B marketplace delivered in about seven and a half weeks with one backend developer.</li>
<li>Al-Kout: 123 feature packs across three kinds of user, delivered in eight cycles over four weeks, with about 1,800 test methods.</li>
<li>I taught the workflow to other developers, who went on to use it on their own projects.</li>
</ul>

<h2>What it does not solve</h2>
<p>Speed moves the bottleneck. Review becomes the slow step, and it has to stay careful. External integrations such as payment gateways and SMS providers still wait on accounts, credentials and testing against the real service. And code that is correct in a test suite still needs to be verified against a real database under concurrent load.</p>
</div>
</section>
"""
    page(
        "how-i-ship/index.html",
        "How I ship — Muhammad Adil",
        "How Muhammad Adil ships: Figma and a business analysis cut into feature packs, then implemented by an agent under architecture rules it cannot renegotiate.",
        body,
        "process",
        "page-process",
    )


def about():
    body = """
<section class="page-head" data-rail="About">
<div class="wrap about-intro">
<img class="about-photo" src="/assets/adil-desk.jpg" alt="Muhammad Adil" width="800" height="800">
<div class="about-copy">
<p class="eyebrow">About</p>
<h1>Muhammad Adil</h1>
<p class="lead">I am a senior backend developer with more than five years of experience with PHP, Laravel and MySQL, over four of them spent professionally building production web applications, REST APIs and multi-role platforms.</p>
<p class="lead">I have worked across e-commerce, healthcare, pharmacy delivery, e-learning, sports booking and service marketplaces. On most recent projects I was the only backend developer, from the empty repository to delivery. Before that I led a backend team of up to 4 developers: reviewing code, mentoring developers and owning delivery across 8 production platforms.</p>
<div class="actions">
<a class="btn btn-primary" href="/cv/Muhammad-Adil-Resume.pdf" download>Download Resume</a>
<button type="button" class="btn" data-cv-preview>Preview Resume</button>
</div>
</div>
</div>
</section>
<section class="section">
<div class="wrap">
<div class="section-head">
<h2>How I work</h2>
</div>
<div class="principles">
<article>
<p class="num">01</p>
<h3>Specification first</h3>
<p>Before writing code I write down the use cases, the state transitions and the money rules, and I record why. The next developer should know the reason, not only the change.</p>
</article>
<article>
<p class="num">02</p>
<h3>Tests for the expensive failures</h3>
<p>I test the paths that cost money when they break: a payment confirmed twice, a charge that fails, two people taking the last slot.</p>
</article>
<article>
<p class="num">03</p>
<h3>A contract someone else can call</h3>
<p>REST endpoints are documented in Postman or Swagger. Role checks, queues and cache sit behind that contract so the next change does not grow a second, private way to update the same row.</p>
</article>
<article>
<p class="num">04</p>
<h3>Review before it ships</h3>
<p>I review the change, including work I did not start. Git and CI carry it to production after that review. On VALORA, an agent can draft the paperwork, and a person still approves it.</p>
</article>
</div>
<p class="more"><a href="/how-i-ship/">See the workflow <span class="arrow" aria-hidden="true">→</span></a></p>
</div>
</section>
<section class="section">
<div class="wrap">
<div class="section-head">
<h2>Experience</h2>
</div>
<div class="timeline">
<article class="job">
<p class="when">09/2024 – Present</p>
<div>
<h3>Senior Backend Developer</h3>
<p class="where"><a class="ext" href="https://www.linkedin.com/company/thiqatech/" rel="noopener" target="_blank">Thiqatech<svg class="ext-icon" viewBox="0 0 24 24" width="13" height="13" aria-hidden="true"><path d="M14 4h6v6M19 5 10 14" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/><path d="M16 14v5a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1V9a1 1 0 0 1 1-1h5" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg></a> · Muscat, Oman (Remote)</p>
<ul>
<li>Architect and build Laravel backends for business workflows that are already in production.</li>
<li>Design the API and keep the database work fast enough for those workflows.</li>
<li>Integrate third-party services, and use queues, caching, and authentication where the request should not do that work inline.</li>
<li>Plan features with a team split across Oman and Pakistan, and lead the backend tasks on the systems I own.</li>
</ul>
</div>
</article>
<article class="job">
<p class="when">09/2023 – 08/2024</p>
<div>
<h3>Backend Developer</h3>
<p class="where"><a class="ext" href="https://www.linkedin.com/company/techigator/" rel="noopener" target="_blank">Techigator<svg class="ext-icon" viewBox="0 0 24 24" width="13" height="13" aria-hidden="true"><path d="M14 4h6v6M19 5 10 14" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/><path d="M16 14v5a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1V9a1 1 0 0 1 1-1h5" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg></a> · Karachi, Pakistan</p>
<ul>
<li>Built and maintained Laravel applications with an eye on performance and security.</li>
<li>Real-time notifications with Pusher, and Firebase for live data and sign-in.</li>
<li>Crawler pipelines with Scrapy and Goutte: extract, transform, and load into MySQL.</li>
<li>Proxy rotation so a blocked address did not end the run. The extracts fed analysis and machine-learning work.</li>
<li>Star of the Quarter, 2024.</li>
</ul>
</div>
</article>
<article class="job">
<p class="when">11/2022 – 08/2023</p>
<div>
<h3>Backend Developer</h3>
<p class="where"><a class="ext" href="https://www.linkedin.com/company/olivedigital/" rel="noopener" target="_blank">Olive Digital<svg class="ext-icon" viewBox="0 0 24 24" width="13" height="13" aria-hidden="true"><path d="M14 4h6v6M19 5 10 14" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/><path d="M16 14v5a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1V9a1 1 0 0 1 1-1h5" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg></a> · Karachi, Pakistan</p>
<ul>
<li>Joined as a junior backend developer and was promoted in March 2023.</li>
<li>Stripe and PayPal on e-commerce platforms, so a customer could pay without leaving the store's flow.</li>
<li>REST APIs between the front end and the server, plus the query work that came with them.</li>
<li>Code review, and the agile loop of planning, stand-ups and retrospectives.</li>
</ul>
</div>
</article>
<article class="job">
<p class="when">01/2022 – 10/2022</p>
<div>
<h3>Frontend Developer</h3>
<p class="where"><a class="ext" href="https://www.linkedin.com/company/waapsdeveloper/" rel="noopener" target="_blank">Waaps Developer<svg class="ext-icon" viewBox="0 0 24 24" width="13" height="13" aria-hidden="true"><path d="M14 4h6v6M19 5 10 14" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/><path d="M16 14v5a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1V9a1 1 0 0 1 1-1h5" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg></a> · Karachi, Pakistan</p>
<ul>
<li>Frontend work before I moved fully onto the backend.</li>
</ul>
</div>
</article>
</div>
</div>
</section>
<section class="section">
<div class="wrap">
<div class="section-head">
<h2>Skills</h2>
</div>
<div class="skill-grid">
<div>
<h3>Backend</h3>
<ul class="tags"><li>PHP</li><li>Laravel</li><li>Livewire</li><li>REST APIs</li><li>Node.js</li><li>NestJS</li><li>Filament</li><li>Sanctum</li><li>RBAC</li><li>Authentication</li><li>Queues &amp; jobs</li><li>Events &amp; observers</li><li>Repository pattern</li><li>Clean architecture</li><li>PHPUnit</li></ul>
</div>
<div>
<h3>Databases &amp; performance</h3>
<ul class="tags"><li>MySQL</li><li>PostgreSQL</li><li>SQL</li><li>NoSQL</li><li>Redis</li><li>Database design</li><li>Indexing</li><li>Query optimisation</li><li>Caching</li><li>Scrapy</li><li>Goutte</li><li>ETL</li></ul>
</div>
<div>
<h3>Integrations</h3>
<ul class="tags"><li>Stripe</li><li>PayPal</li><li>Amwal Pay</li><li>MyFatoorah</li><li>Tap</li><li>Al Rajhi Bank</li><li>Fawry</li><li>Webhooks</li><li>Google OAuth</li><li>Google Cloud</li><li>WhatsApp QR connect</li><li>Pusher</li><li>Firebase</li><li>Firebase Cloud Messaging</li><li>SMS gateways</li><li>Socket.IO</li><li>Swagger</li></ul>
</div>
<div>
<h3>Interface</h3>
<ul class="tags"><li>JavaScript</li><li>Next.js</li><li>React</li><li>jQuery</li><li>WordPress</li><li>Elementor</li><li>HTML</li><li>CSS</li><li>SEO</li></ul>
</div>
<div>
<h3>Tools &amp; workflow</h3>
<ul class="tags"><li>Git</li><li>GitHub</li><li>GitLab</li><li>Bitbucket</li><li>GitHub Actions</li><li>Docker</li><li>Linux</li><li>macOS</li><li>Postman</li><li>OpenAPI</li><li>CI/CD</li><li>Agile</li><li>AI-assisted development (Claude Code, Cursor)</li></ul>
</div>
<div>
<h3>Leadership</h3>
<ul class="tags"><li>Code review</li><li>Mentoring</li><li>Task coordination</li><li>Technical decisions</li><li>Delivery ownership</li></ul>
</div>
</div>
</div>
</section>
<section class="section">
<div class="wrap prose">
<h2>Education</h2>
<ul>
<li>Bachelor of Science in Data Science, Virtual University of Pakistan. In progress.</li>
<li>Intermediate (DAE Electrical), Monopoly Technical College, 2022.</li>
<li>Matriculation, Pak German School, 2018.</li>
</ul>
<h2>Recognition and courses</h2>
<ul>
<li>Star of the Quarter 2024, Techigator.</li>
<li>Laravel, Udemy (Kati Frantz).</li>
<li>Node.js, Udemy.</li>
<li>Vue.js, Udemy.</li>
</ul>
<h2>Languages</h2>
<p>English, Urdu, native.</p>
</div>
</section>
"""
    page(
        "about/index.html",
        "About — Muhammad Adil",
        "Muhammad Adil is a senior Laravel backend developer in Karachi, currently at Thiqatech. Previously Techigator and Olive Digital.",
        body,
        "about",
        "page-about",
    )


def js_required():
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>JavaScript is Required — Muhammad Adil</title>
<meta name="robots" content="noindex">
<meta name="theme-color" content="#0c1024">
<link rel="icon" href="/favicon.svg?v=3" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:wght@400;500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/css/site.css">
{HEAD_SCRIPT}
<script>location.replace("/");</script>
</head>
<body>
<div class="aurora" aria-hidden="true"></div>
<main class="js-required">
<div class="js-card">
{MARK}
<div class="js-icon" aria-hidden="true"><svg viewBox="0 0 48 48" width="36" height="36"><path d="M18 16l-7 8 7 8M30 16l7 8-7 8" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/><circle cx="24" cy="24" r="18" fill="none" stroke="currentColor" stroke-width="1.6"/><path d="M12 36L36 12" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/></svg></div>
<h1>JavaScript is Required</h1>
<p>This website requires JavaScript to be enabled in your browser.</p>
<p>Please enable JavaScript and refresh the page.</p>
</div>
</main>
</body>
</html>
"""
    dest = ROOT / "javascript-required" / "index.html"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(html)
    print("javascript-required/index.html")


def privacy():
    body = """
<section class="page-head">
<div class="wrap">
<p class="eyebrow">Legal</p>
<h1>Privacy Policy</h1>
<p class="lead">How visit statistics, the chat, and technical server logs are handled on this portfolio.</p>
</div>
</section>
<section class="section">
<div class="wrap">
<h2 class="glance-title">Summary at a glance</h2>
<dl class="glance">
<div><dt>Last updated</dt><dd>23 November 2026</dd></div>
<div><dt>Data controller</dt><dd>Muhammad Adil</dd></div>
<div><dt>Direct inquiries</dt><dd><a href="mailto:adilm0616@gmail.com">adilm0616@gmail.com</a></dd></div>
<div><dt>Location</dt><dd>Karachi, Pakistan</dd></div>
<div><dt>Cookies</dt><dd>Choice and session always. Theme, language and a visitor ID only with your consent.</dd></div>
<div><dt>Analytics</dt><dd>First-party visit counting only. No Google Analytics and no Meta Pixel.</dd></div>
<div><dt>Visit data stored</dt><dd>IP address, approximate location, device and the pages opened. A recent log of about the last 500 views.</dd></div>
<div><dt>Stored on your device</dt><dd>Theme, language, privacy choice and this chat session. A visitor ID only if you allow it.</dd></div>
<div><dt>Chat</dt><dd>Name, an optional phone and email, and the messages are saved in a private log. Google Gemini writes the reply and does not receive the name, phone or email.</dd></div>
<div><dt>Spam protection</dt><dd>Google reCAPTCHA v2 checkbox, once a day in this browser on the hosted site.</dd></div>
<div><dt>Hosting</dt><dd>Vercel (Edge Network)</dd></div>
<div><dt>Fonts</dt><dd>IBM Plex, loaded from Google Fonts.</dd></div>
</dl>
<nav class="policy-toc" aria-label="On this page">
<p class="eyebrow">Contents</p>
<ol>
<li><a href="#overview"><span>1.</span> Overview and purpose</a></li>
<li><a href="#collected"><span>2.</span> Information collected</a></li>
<li><a href="#cookies"><span>3.</span> Cookies and tracking</a></li>
<li><a href="#use"><span>4.</span> How information is used</a></li>
<li><a href="#storage"><span>5.</span> Storage and processors</a></li>
<li><a href="#retention"><span>6.</span> Data retention</a></li>
<li><a href="#rights"><span>7.</span> Your rights</a></li>
<li><a href="#links"><span>8.</span> External links</a></li>
<li><a href="#security"><span>9.</span> Security</a></li>
<li><a href="#children"><span>10.</span> Children's privacy</a></li>
<li><a href="#changes"><span>11.</span> Changes to this policy</a></li>
<li><a href="#contact-policy"><span>12.</span> Contact</a></li>
</ol>
</nav>
<article class="prose policy">
<h2 id="overview">1. Overview and purpose</h2>
<p>This website, at <a href="https://muhammad-adil-portfolio.vercel.app/">muhammad-adil-portfolio.vercel.app</a> and <a href="https://adil-portfolio-sigma.vercel.app/">adil-portfolio-sigma.vercel.app</a>, is the portfolio of Muhammad Adil, a senior backend developer in Karachi, Pakistan.</p>
<p>I do not sell personal information, run advertising, or follow people across other websites. This policy describes the limited information the site processes when you read it, use the chat, or write to me directly.</p>
<h2 id="collected">2. Information collected</h2>
<h3>A. Email, phone and WhatsApp links</h3>
<p>There is no separate contact form for a project brief. The email, phone and WhatsApp links open your own mail app or WhatsApp. A message you send that way is received by me at adilm0616@gmail.com or on WhatsApp at +92 318 0253146. This website does not keep a copy of those direct messages. The on-site chat is different and is described next.</p>
<h3>B. Chat messages</h3>
<p>If you use the chat, it asks for your name. Phone and email are optional. The name, phone, email, the message you type, and the reply are saved in a private log so I can read the conversation. The open page also keeps the current thread until you leave it.</p>
<p>The message and up to the previous eight turns go to Google's Gemini API, which writes a short reply from what is written on this site. Your name, phone and email are not sent to Gemini. The chat does not ask for your GPS location.</p>
<p>If you chose Accept all, or turned on Remember me between visits, that request also includes a random visitor ID, the approximate region already taken from the visit, the referring site, the landing page and a coarse device label. The assistant may use those if you ask how you found the site. It is not given your IP address.</p>
<p>Replies are generated automatically. They can be wrong, and they are not a job offer or a promise from me.</p>
<h3>C. Direct messages</h3>
<p>If you email adilm0616@gmail.com, call or message +92 318 0253146, or open WhatsApp from a button on this site, that conversation lives in those tools. I read it there.</p>
<h3>D. Technical logs</h3>
<p>When your browser requests a page, the host records ordinary access data: IP address, browser and operating system from the User-Agent header, the requested URL, the referring URL, the response status, and the date and time. Those logs are Vercel's, and Vercel keeps them on its own schedule.</p>
<h3>E. Visit statistics</h3>
<p>Each page you open is counted, so I can see which pages people read. The record has:</p>
<ul>
<li>The IP address, and an approximate location taken from the hosting network when it supplies a city, region and country. Nothing is read from the device's GPS.</li>
<li>A coarse device label: phone, tablet or desktop, and Chrome, Safari, Firefox, Edge, or simply browser.</li>
<li>The page path, the time, the first page of this visit, and the referring address, or "direct".</li>
<li>A session ID that lasts until you close the browser.</li>
<li>A random visitor ID only if you accepted Remember me between visits.</li>
</ul>
<p>The page itself is told the region, when one is available. The IP address is not sent back to the browser, and the visit list is not published.</p>
<h3>F. First-visit check</h3>
<p>On the hosted site, Google reCAPTCHA v2 shows an "I'm not a robot" checkbox. Google's token lasts two minutes and can be checked once, so this site confirms it immediately. After it passes, this browser stores the time in a local flag named adil-human and keeps the check off for 24 hours, including while you move between pages. A new browser, a private window, or a cleared store shows it again. The check is skipped on a local preview. Google processes it under its own privacy policy and terms.</p>
<h2 id="cookies">3. Cookies and tracking</h2>
<p>There are no advertising cookies, no ad pixels, and no third-party analytics such as Google Analytics, Meta Pixel, Hotjar or PostHog. Visits are counted by this site, and that record stays with me.</p>
<p>Cookies this site sets:</p>
<ul>
<li><strong>adil-consent</strong>, for 180 days. Accept all or Necessary only, so the bar does not return on every page.</li>
<li><strong>adil-session</strong>, until you close the browser. A random ID for this visit.</li>
<li><strong>adil-theme</strong> and <strong>adil-lang</strong>, for 180 days, only if you choose Accept all or turn on Remember me.</li>
<li><strong>adil-id</strong>, for 180 days, only with that same choice. A random ID so a return visit is recognised.</li>
<li><strong>adil-admin</strong>, for 30 days, and only in the browser I use to sign in to the private reading page. It refreshes while that page is used. It is not set for visitors.</li>
</ul>
<p>The browser also keeps a few values that are not cookies. Theme and language are saved in local storage when you change them, so the next page can paint the same way. After the reCAPTCHA check passes, a local flag named adil-human stores the time, and the check stays off in this browser for 24 hours. For the open tab, the landing page, the referring address, the region, and the name, phone and email typed in the chat sit in session storage and are dropped when the tab closes.</p>
<p>Necessary only deletes adil-theme, adil-lang and adil-id. To choose again later, clear this site's cookies in your browser.</p>
<h2 id="use">4. How information is used</h2>
<ul>
<li>To see which pages are read, and from which sort of device and region, so I can improve the portfolio.</li>
<li>To read the chat, including the name and any phone or email you typed, and to answer from what is written on this site.</li>
<li>To run the person check once a day and keep the hosted site available.</li>
<li>To reply when you email me or message me on WhatsApp.</li>
</ul>
<p>I do not sell, rent or trade this information.</p>
<h2 id="storage">5. Storage and processors</h2>
<p>There are no user accounts. Chats and visit records are private logs of about the last 500 lines each. On the hosted site they are kept in a private Vercel Blob store. That store is not a public URL. I read the logs from a password-protected page that is not linked from the rest of the site.</p>
<ul>
<li><strong>Vercel.</strong> Hosts the site and the serverless functions, stores the private visit and chat logs, records its own access logs, and supplies the approximate location from the IP address.</li>
<li><strong>Google Gemini.</strong> Writes the chat reply from the message and, when you have allowed it, the visitor note described above.</li>
<li><strong>Google reCAPTCHA.</strong> Runs the person check once a day on the hosted site.</li>
<li><strong>Google Fonts.</strong> The pages load IBM Plex Sans, IBM Plex Mono and IBM Plex Sans Arabic from fonts.googleapis.com. That request is Google's.</li>
</ul>
<h2 id="retention">6. Data retention</h2>
<ul>
<li><strong>Visit records.</strong> About the last 500 page views. Older lines in that log are dropped as new ones are added. I do not keep a separate 13-month archive.</li>
<li><strong>Chat.</strong> About the last 500 lines, including the name, phone, email and messages. Older lines are dropped as new ones are added. Google processes the message, without the name, phone or email, under its own terms in order to write the reply.</li>
<li><strong>Cookies.</strong> 180 days, except adil-session, which ends when the browser closes.</li>
<li><strong>Email and WhatsApp.</strong> Kept in those inboxes for as long as I need them to reply, and deleted if you ask and I have no reason to keep them.</li>
<li><strong>Hosting logs.</strong> Kept by Vercel on Vercel's schedule.</li>
</ul>
<h2 id="rights">7. Your rights</h2>
<p>You can ask me what visit records or saved chats I can still see for you, ask me to correct something that is wrong, or ask me to delete a saved chat, an email, a WhatsApp message, or a visit record I still hold. Email <a href="mailto:adilm0616@gmail.com">adilm0616@gmail.com</a> with the subject "Privacy Request". I reply without a charge.</p>
<h2 id="links">8. External links</h2>
<p>The site links out to GitHub, LinkedIn, WhatsApp, and to live projects named in the case studies. Once you follow one of those links, that site's own terms and privacy policy apply. I do not control them.</p>
<h2 id="security">9. Security</h2>
<p>The hosted site is served over HTTPS. The visit endpoint does not return your IP address to the page. The visit and chat lists sit behind a password, and a request without that sign-in receives nothing. Chat and visit fields are trimmed to a short length before they are used.</p>
<p>No transmission over the internet is perfectly safe. I cannot promise that a determined attacker, or a failure at a provider named above, can never reach a message in transit.</p>
<h2 id="children">10. Children's privacy</h2>
<p>This is a professional portfolio for clients, recruiters and engineers. It is not aimed at children under 16, and I do not knowingly collect their information. If you believe a child has sent me personal information, email me and I will delete it.</p>
<h2 id="changes">11. Changes to this policy</h2>
<p>If I change what the site stores, I will update this page and the date at the top. The address stays <a href="/privacy/">/privacy/</a>.</p>
<h2 id="contact-policy">12. Contact</h2>
<p>Muhammad Adil<br>Senior Backend Developer<br>Karachi, Pakistan<br><a href="mailto:adilm0616@gmail.com">adilm0616@gmail.com</a><br><a href="https://api.whatsapp.com/send/?phone=923180253146&amp;text=Hello%20Muhammad%2C%20I%20saw%20your%20portfolio%20and%20wanted%20to%20reach%20you.&amp;type=phone_number&amp;app_absent=0">+92 318 0253146</a> on WhatsApp<br><a href="https://muhammad-adil-portfolio.vercel.app/">muhammad-adil-portfolio.vercel.app</a></p>
</article>
</div>
</section>
"""
    page(
        "privacy/index.html",
        "Privacy Policy — Muhammad Adil",
        "How Muhammad Adil's portfolio handles visit statistics, the chat, cookies and hosting logs.",
        body,
    )


def sitemap():
    urls = [
        "/",
        "/about/",
        "/how-i-ship/",
        "/privacy/",
        "/work/",
    ] + [f"/work/{case['slug']}/" for case in CASES]
    locs = "\n".join(f"  <url><loc>https://muhammad-adil-portfolio.vercel.app{url}</loc></url>" for url in urls)
    # Placeholder host is rewritten after deploy if needed. Relative sitemap is not valid,
    # so the file is written once the production host is known.
    (ROOT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"{locs}\n</urlset>\n"
    )
    print("sitemap.xml")


if __name__ == "__main__":
    home()
    work()
    cases()
    ship()
    about()
    privacy()
    js_required()
    sitemap()
