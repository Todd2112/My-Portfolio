# Business Suite: End-to-End Content & Marketing Automation

A collection of integrated AI tools for content creation, SEO optimization, and social media management—all running locally without cloud dependencies.

## Components

### CopyIQ: AI-Assisted Content Generation
**Location:** `copyiq/`

Intelligent content generation with factual overlap scoring to prevent hallucination and maintain consistency with source material.

**Key Features:**
- Template-based content generation
- Factual overlap validation
- Multi-format export (Markdown, HTML, plain text)
- Local LLM integration (no API costs)

**Use Cases:** Blog posts, product descriptions, marketing copy, documentation

---

### SEO Agent: Keyword & Competitor Analysis
**Location:** `seo-agent/`

Local keyword extraction, competitor scraping, and SEO scoring pipelines without sending data to third-party SEO tools.

**Key Features:**
- Keyword extraction and density analysis
- Competitor content scraping
- On-page SEO scoring
- Backlink analysis (local)
- SERP position tracking

**Use Cases:** Content optimization, competitor research, keyword strategy

---

### LLMO: LLM-First Content Optimization
**Location:** `llmo/`

Content optimization specifically designed for LLM retrieval and search engines, focusing on semantic relevance over keyword stuffing.

**Key Features:**
- Semantic density analysis
- Content structure optimization
- Entity extraction and linking
- Readability scoring
- LLM-friendly formatting

**Use Cases:** Knowledge base optimization, internal search, AI-first SEO

---

### SMO: Social Media Optimization Agent
**Location:** `smo/`

Platform-specific post formatting, hashtag generation, and engagement prediction—all processed locally.

**Key Features:**
- Hashtag generation (trending + relevant)
- Platform-specific formatting (Twitter, LinkedIn, Instagram)
- Engagement prediction models
- Content calendar automation
- Multi-platform scheduling prep

**Use Cases:** Social media management, brand monitoring, content distribution

---

## Integrated Workflow
```
Input: Raw content idea
    ↓
[CopyIQ] → Generate initial content
    ↓
[LLMO] → Optimize for semantic search
    ↓
[SEO Agent] → Analyze keywords & competitors
    ↓
[SMO] → Format for social platforms
    ↓
Output: Multi-channel ready content
```

## Technology Stack

- **Backend:** Python 3.8+, FastAPI/Flask
- **LLM Integration:** Ollama (local models)
- **NLP:** spaCy, NLTK, sentence-transformers
- **Scraping:** BeautifulSoup, Selenium (for dynamic sites)
- **UI:** Streamlit (for demos), Tkinter (for desktop)
- **Storage:** SQLite (local), JSONL (for logs)

## Why Local Processing Matters

**Cloud SEO Tools (SEMrush, Ahrefs):**
- Cost: $99–399/month
- Data uploaded to third parties
- Rate limits and usage caps
- Subscription dependency

**Business Suite (Local):**
- Cost: $0/month after setup
- Complete data privacy
- No rate limits
- Customizable for specific industries

**Break-even:** 1–2 months vs cloud alternatives

---

## Setup & Usage

Each component has its own README with setup instructions:

- [CopyIQ Setup →](copyiq/README.md)
- [SEO Agent Setup →](seo-agent/README.md)
- [LLMO Setup →](llmo/README.md)
- [SMO Setup →](smo/README.md)

## Commercial Availability

The Business Suite is available for licensing with custom integration support.

**Ideal For:**
- Marketing agencies (multi-client content production)
- E-commerce businesses (product description automation)
- Media companies (content optimization pipelines)
- Enterprises (internal content management)

**Contact:** [your-email@example.com]

---

## Status

**Current Version:** Proof-of-concept  
**License:** Proprietary  
**Last Updated:** January 2025
```

5. Commit with message: `Create Business Suite consolidated README`

---

**Step 2:** Move CopyIQ files

1. Navigate to: `https://github.com/Todd2112/My-Portfolio/tree/master/CopyIq`
2. Click on the first file (e.g., `app.py`)
3. Click the **pencil icon** (Edit)
4. Change the filename path at top from:
```
   CopyIq/app.py
```
   to:
```
   Business-Suite/copyiq/app.py
```
5. Commit: `Move CopyIQ to Business Suite`
6. Repeat for all files in `CopyIq/` folder

**Alternative (faster):** Create placeholder files

1. Click **"Add file"** → **"Create new file"**
2. Filename: `Business-Suite/copyiq/README.md`
3. Content: `# CopyIQ - Moved from legacy folder. See parent README for details.`
4. Commit: `Add CopyIQ to Business Suite`

---

**Step 3:** Repeat for other components

Create placeholder files for each:
```
Business-Suite/
├── README.md (master file, created above)
├── copyiq/
│   └── README.md (or move actual files)
├── seo-agent/
│   └── README.md
├── llmo/
│   └── README.md
└── smo/
    └── README.md
