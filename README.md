# Rate Right — Price Transparency for Local Services in India

Price transparency for local services. Compare real prices from mechanics, electricians, repair shops, and local service providers across Indian cities — powered by multi-layered web scraping, LLM extraction, vector search, and intelligent discovery.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | Next.js 16, React 19, Tailwind CSS 4, shadcn/ui, Radix UI |
| **Maps** | Leaflet + react-leaflet with OpenStreetMap (Carto basemaps) |
| **Backend** | FastAPI (async), Pydantic v2 |
| **Database** | MongoDB Atlas (Motor async driver) |
| **Search** | MongoDB Atlas Search (full-text, fuzzy) + Atlas Vector Search (cosine similarity) |
| **Embeddings** | OpenAI `text-embedding-3-small` (1536 dims) via LangChain |
| **LLM** | GPT-4o-mini — price extraction, email drafting, chat refinement |
| **Scraping** | httpx, BeautifulSoup4, Playwright (async Chromium) |
| **External APIs** | SerpAPI (Google Maps discovery), Linkup SDK (web price search) |
| **Payments** | Razorpay / UPI (placeholder for future integration) |
| **Email** | SMTP / IMAP (smtplib, imaplib) |
| **Infra** | Docker Compose (MongoDB 7 + FastAPI) |

## Features

### OpenStreetMap with Live Provider Pins

Results are displayed on an interactive Leaflet map backed by OpenStreetMap / Carto tiles. Each provider appears as a pin with its price label. The map auto-fits bounds to all visible results and shows a blue dot for the user's location. Mobile-first design with list view as default — map is optional.

### Multi-Tier Price Discovery

Prices are discovered through a three-level cascade optimized for the Indian market — each tier fires only if the previous one comes up empty:

1. **Google Maps scraping** — Primary discovery method via SerpAPI. Many Indian service providers don't have websites, so we prioritize Google Maps listings with contact information.

2. **Website scraping (optional)** — For providers with websites, a multi-level crawl (homepage, top 3 links, top 2 sub-links) extracts prices with a currency-aware regex (₹). URLs are scored by query-token overlap so the most relevant pages are crawled first. Context-aware matching inspects surrounding HTML containers to avoid false positives.

3. **LLM extraction** — If regex finds nothing and there's enough token overlap (>= 2), the scraped page text is sent to GPT-4o-mini which semantically matches service descriptions and returns structured prices.

Scraping happens in the background: the API returns partial results immediately and the frontend polls every 3 s while `scraping_in_progress` is true.

### Vector-Space Price Observation

Service types are embedded with OpenAI `text-embedding-3-small` into a 1536-dimensional vector space. When a user searches, both a full-text Atlas Search query **and** a cosine-similarity Atlas Vector Search query run in parallel. Results are merged and deduplicated (vector score >= 0.75, text score >= 0.10). This makes it easy to find the best price for the most similar service at the closest location — even when wording differs between providers.

### WhatsApp & Call Integration

When a user wants to inquire or book:

1. **WhatsApp inquiry** — Pre-filled message with service details, opens WhatsApp with provider's number
2. **Call now** — Direct phone call button
3. **Email inquiry (optional)** — For providers with email addresses

The system recognizes Indian bargaining culture and displays price ranges (min-max) with median prices and "cheap / fair / expensive" badges based on area comparisons.

### Email Automation for Inquiries

For providers with email addresses, the system:

1. **Discovers contact emails** by scraping the provider's homepage, `/contact`, `/about` pages (filtering out common platform domains).
2. **Drafts a personalised inquiry** using GPT-4o-mini — professional tone, asks for pricing on the specific service.
3. **Sends it via SMTP** and stores the inquiry with its `Message-ID`.
4. **Monitors the inbox via IMAP** — matches replies by `In-Reply-To` / `References` headers, extracts prices from the reply body with the LLM, and automatically creates price observations.

### Conversational Search Refinement

A chat interface (GPT-4o-mini) guides the user through one question at a time — collecting device/brand/model for repairs, make/model for vehicles, or job details for trade services — then returns a ready-to-search query.

### SerpAPI Provider Discovery

When the local database has no results, the system queries SerpAPI's Google Maps endpoint to discover businesses matching the query within the user's radius. New providers are upserted into MongoDB and embeddings are generated on the fly. Optimized for Indian cities with support for JustDial and IndiaMART integration (coming soon).

## Running It

```bash
# 1. Clone & configure
git clone <repo-url> && cd rate-right
cp backend/.env.example backend/.env   # fill in MONGO_URL, OPENAI_API_KEY, etc.

# 2. Backend
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m scripts.create_search_indexes   # one-time: Atlas Search + Vector indexes
python -m scripts.seed                    # optional: demo providers and observations
uvicorn app.main:app --reload             # http://localhost:8000

# 3. Frontend
cd ../frontend
npm install
npm run dev                               # http://localhost:3000
```

Or with Docker:

```bash
docker-compose up   # MongoDB 7 + FastAPI backend
```

### Environment Variables (backend)

| Variable | Required | Purpose |
|----------|----------|---------|
| `MONGO_URL` | Yes | MongoDB Atlas connection string |
| `MONGO_DB` | Yes | Database name (default: rateright) |
| `OPENAI_API_KEY` | Yes | Embeddings + LLM extraction |
| `SERPAPI_KEY` | No | Google Maps provider discovery |
| `LINKUP_API_KEY` | No | Linkup web price search |
| `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`, `IMAP_HOST`, `IMAP_PORT`, `FROM_EMAIL` | No | Email inquiry automation |

## Roadmap

- [ ] JustDial integration for provider discovery
- [ ] IndiaMART integration for B2B services
- [ ] Razorpay payment integration
- [ ] UPI payment links
- [ ] Multi-city support (Delhi, Mumbai, Bangalore, Hyderabad, Chennai)
- [ ] Hindi language support
- [ ] Price negotiation history tracking
- [ ] Provider verification system
- [ ] User reviews and ratings
