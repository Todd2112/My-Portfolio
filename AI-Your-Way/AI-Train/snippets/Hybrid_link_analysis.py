# Demonstrates: Hybrid LLM + keyword fallback for link relevance analysis.
# 8B reasoner handles multi-hop reasoning about goal relevance.
# Keyword scoring activates automatically if LLM parsing fails.
# Part of ai-train.py. Not standalone.

def analyze_relevant_links(html_content: str, source_url: str,
                            goal: str, llm) -> list:
    """
    Two-path link relevance analysis: LLM primary, keyword fallback.

    Path 1 — LLM reasoning (8B model):
        Sends up to 15 candidate links with context snippets to the reasoner.
        Returns JSON array of selected IDs with relevance reasons.
        Invoked before text cleaning so raw HTML link context is preserved.

    Path 2 — Keyword fallback (no LLM):
        Activates if LLM returns unparseable JSON or raises any exception.
        Scores links by goal keyword overlap, threshold: 20/100 minimum score.
        Labeled "medium" confidence vs LLM's "high" so callers can distinguish.

    Design decision: analyze links BEFORE sanitizing HTML because
    link context (<p>, <li>, <td> parent elements) is stripped during cleaning.
    """
    soup = BeautifulSoup(html_content, PARSER)
    candidates = []
    seen_urls = set()
    base_domain = urlparse(source_url).netloc
    goal_keywords = set(word.lower() for word in re.findall(r'\b\w{3,}\b', goal))

    for link in soup.find_all('a', href=True):
        full_url = urljoin(source_url, link['href'])
        if full_url in seen_urls or urlparse(full_url).netloc != base_domain:
            continue
        seen_urls.add(full_url)

        text = link.get_text(" ", strip=True)
        parent = link.find_parent(['p', 'li', 'div', 'td', 'section'])
        context = parent.get_text(" ", strip=True)[:150] if parent else ""
        combined = (text + " " + context).lower()

        keyword_score = min(100,
            (sum(1 for kw in goal_keywords if kw in combined) / len(goal_keywords)) * 100
        ) if goal_keywords else 0

        candidates.append({"id": len(candidates), "url": full_url,
                           "text": text, "context": context,
                           "keyword_score": keyword_score})

    recommendations = []

    # Path 1: LLM reasoning
    try:
        prompt = (
            f"User Goal: '{goal}'\n"
            f"Identify top 3-5 most relevant links:\n"
        )
        for item in candidates[:15]:
            prompt += f"ID {item['id']}: '{item['text']}' (Context: {item['context'][:80]})\n"
        prompt += "\nOutput ONLY JSON: [{\"id\": 0, \"reason\": \"explanation\"}]"

        response = llm.generate(prompt, REASONER_SYSTEM, max_tokens=256, temperature=0.1)
        match = re.search(r'\[.*\]', response, re.DOTALL)

        if match:
            for sel in json.loads(match.group(0)):
                original = next((c for c in candidates[:15] if c['id'] == sel.get('id')), None)
                if original:
                    recommendations.append({
                        "url": original['url'],
                        "link_text": original['text'],
                        "relevance_reason": sel.get('reason', ''),
                        "method": "llm",
                        "confidence": "high",
                        "action": "ingest_recommended"
                    })

    except (json.JSONDecodeError, Exception):
        pass  # fall through to keyword fallback

    # Path 2: Keyword fallback (activates if LLM path produced nothing)
    if not recommendations:
        for item in sorted(candidates, key=lambda x: x['keyword_score'], reverse=True)[:5]:
            if item['keyword_score'] >= KEYWORD_FALLBACK_THRESHOLD:
                recommendations.append({
                    "url": item['url'],
                    "link_text": item['text'],
                    "relevance_reason": f"Keyword match score: {item['keyword_score']:.0f}/100",
                    "method": "keyword_fallback",
                    "confidence": "medium",
                    "action": "ingest_recommended"
                })

    return recommendations
