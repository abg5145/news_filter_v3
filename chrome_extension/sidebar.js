// Set this to your App Runner URL in production, or localhost for local testing
const BACKEND_URL = 'https://YOUR_APP_RUNNER_URL';

function $(id) { return document.getElementById(id); }

function show(id) { $(id).classList.remove('hidden'); }
function hide(id) { $(id).classList.add('hidden'); }

function escapeHtml(text) {
  const d = document.createElement('div');
  d.textContent = String(text || '');
  return d.innerHTML;
}

$('analyzeBtn').addEventListener('click', runAnalysis);
$('retryBtn').addEventListener('click', reset);
$('resetBtn').addEventListener('click', reset);

function reset() {
  hide('resultsSection');
  hide('errorState');
  hide('loadingState');
  show('idleState');
}

async function runAnalysis() {
  // Extract text from the active tab via content script
  let articleText = '';
  try {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    const results = await chrome.scripting.executeScript({
      target: { tabId: tab.id },
      files: ['content.js']
    });
    articleText = results?.[0]?.result?.trim() || '';
  } catch (e) {
    showError('Could not read the page. Make sure you are on a news article.');
    return;
  }

  if (!articleText || articleText.length < 100) {
    showError('Not enough article text found on this page. Try a different article.');
    return;
  }

  showLoading();

  try {
    const response = await fetch(`${BACKEND_URL}/analyze`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ article_text: articleText })
    });

    const data = await response.json();

    if (data.success) {
      showResults(data);
    } else {
      showError(data.error || 'Analysis failed. Please try again.');
    }
  } catch (e) {
    showError('Could not reach the server. Check your connection.');
  }
}

function showLoading() {
  hide('idleState');
  hide('errorState');
  hide('resultsSection');
  show('loadingState');
}

function showError(msg) {
  hide('idleState');
  hide('loadingState');
  hide('resultsSection');
  $('errorMessage').textContent = msg;
  show('errorState');
}

function showResults(data) {
  hide('loadingState');
  hide('errorState');
  hide('idleState');

  renderArticles(data.section_1.similar_articles);
  renderAnalysis(data.section_2);
  renderAIScore(data.section_3);

  show('resultsSection');
}

function renderArticles(articles) {
  const container = $('similarArticles');
  container.innerHTML = '';

  articles.forEach(article => {
    const tile = document.createElement('div');
    tile.className = 'article-tile';

    const img = article.image_url
      ? `<img src="${escapeHtml(article.image_url)}" alt="" onerror="this.style.display='none'">`
      : `<div class="img-placeholder"><i class="fas fa-newspaper"></i></div>`;

    tile.innerHTML = `
      ${img}
      <h3>${escapeHtml(article.headline)}</h3>
      <p class="source"><i class="fas fa-building"></i> ${escapeHtml(article.source)}</p>
      <p class="summary">${escapeHtml(article.summary)}</p>
      ${article.url ? `<a href="${escapeHtml(article.url)}" target="_blank"><i class="fas fa-external-link-alt"></i> Read More</a>` : ''}
    `;
    container.appendChild(tile);
  });
}

function renderAnalysis(analysis) {
  // Key Facts
  const factsEl = $('keyFacts');
  factsEl.innerHTML = '';
  if (analysis.key_facts?.length) {
    analysis.key_facts.forEach(f => {
      factsEl.innerHTML += `
        <div class="card card-green">
          <p><strong>${escapeHtml(f.fact)}</strong></p>
          <p>${escapeHtml(f.verification)}</p>
          <span class="label label-green">Confidence: ${escapeHtml(f.confidence)}</span>
        </div>`;
    });
  } else {
    factsEl.innerHTML = '<p style="color:#6b7280;font-size:12px">No key facts identified.</p>';
  }

  // Opinions
  const opinionsEl = $('opinions');
  opinionsEl.innerHTML = '';
  if (analysis.opinions?.length) {
    analysis.opinions.forEach(o => {
      opinionsEl.innerHTML += `
        <div class="card card-yellow">
          <p><em>"${escapeHtml(o.statement)}"</em></p>
          <p>${escapeHtml(o.context)}</p>
          <span class="label label-yellow">${escapeHtml(o.bias_indication)}</span>
        </div>`;
    });
  } else {
    opinionsEl.innerHTML = '<p style="color:#6b7280;font-size:12px">No opinions identified.</p>';
  }

  // Biases
  const biasesEl = $('biases');
  biasesEl.innerHTML = '';
  if (analysis.biases?.length) {
    analysis.biases.forEach(b => {
      biasesEl.innerHTML += `
        <div class="card card-red">
          <p><strong>${escapeHtml(b.type.replace(/_/g, ' ').toUpperCase())}</strong></p>
          <p>${escapeHtml(b.description)}</p>
          <p style="color:#6b7280;margin-top:4px">${escapeHtml(b.impact)}</p>
        </div>`;
    });
  } else {
    biasesEl.innerHTML = '<p style="color:#6b7280;font-size:12px">No biases identified.</p>';
  }

  // Overall Assessment
  $('overallAssessment').innerHTML = `<p>${escapeHtml(analysis.overall_assessment)}</p>`;
}

function renderAIScore(aiData) {
  const score = aiData.genai_score || 0;
  const scoreEl = $('aiScore');
  const bar = $('aiScoreBar');

  scoreEl.textContent = score;
  bar.style.width = `${score}%`;

  let color;
  if (score < 30) color = '#16a34a';
  else if (score < 70) color = '#ca8a04';
  else color = '#dc2626';

  bar.style.background = color;
  scoreEl.style.color = color;

  let html = `<h4>Reasoning:</h4><p>${escapeHtml(aiData.genai_reasoning)}</p>`;
  if (aiData.genai_telltales?.length) {
    html += `<h4>AI Indicators:</h4><ul>`;
    aiData.genai_telltales.forEach(t => { html += `<li>${escapeHtml(t)}</li>`; });
    html += '</ul>';
  }
  $('aiReasoning').innerHTML = html;
}
