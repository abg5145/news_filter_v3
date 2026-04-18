function extractArticleText() {
  // Try semantic article containers first, fall back to body paragraphs
  const selectors = ['article', 'main', '[role="main"]', '.article-body', '.post-content', '.entry-content'];

  for (const selector of selectors) {
    const el = document.querySelector(selector);
    if (el) {
      const text = el.innerText.trim();
      if (text.length > 200) return text;
    }
  }

  // Fall back to collecting all paragraph text
  const paragraphs = Array.from(document.querySelectorAll('p'))
    .map(p => p.innerText.trim())
    .filter(t => t.length > 40);

  return paragraphs.join('\n\n');
}

extractArticleText();
