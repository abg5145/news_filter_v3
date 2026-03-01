document.addEventListener('DOMContentLoaded', function() {
    const analyzeBtn = document.getElementById('analyzeBtn');
    const articleInput = document.getElementById('articleInput');
    const loadingState = document.getElementById('loadingState');
    const resultsSection = document.getElementById('resultsSection');
    const errorSection = document.getElementById('errorSection');
    const progressSteps = document.getElementById('progressSteps');

    analyzeBtn.addEventListener('click', analyzeArticle);
    articleInput.addEventListener('keydown', function(e) {
        if (e.ctrlKey && e.key === 'Enter') {
            analyzeArticle();
        }
    });

    async function analyzeArticle() {
        const articleText = articleInput.value.trim();
        
        if (!articleText) {
            showError('Please paste some article text to analyze.');
            return;
        }

        // Show loading state
        showLoading();
        
        try {
            const response = await fetch('/analyze', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ article_text: articleText })
            });

            const data = await response.json();

            if (data.success) {
                showResults(data);
            } else {
                showError(data.error || 'Analysis failed. Please try again.');
            }
        } catch (error) {
            showError('Network error. Please check your connection and try again.');
            console.error('Error:', error);
        } finally {
            hideLoading();
        }
    }

    function showLoading() {
        analyzeBtn.disabled = true;
        analyzeBtn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Analyzing...';
        loadingState.classList.remove('hidden');
        resultsSection.classList.add('hidden');
        errorSection.classList.add('hidden');
        
        // Reset progress steps
        progressSteps.innerHTML = `
            <div class="flex items-center mb-2">
                <i class="fas fa-circle-notch fa-spin text-blue-500 mr-2"></i>
                <span>Generating search terms...</span>
            </div>
            <div class="flex items-center mb-2">
                <i class="fas fa-circle text-gray-300 mr-2"></i>
                <span>Fetching articles from multiple sources...</span>
            </div>
            <div class="flex items-center mb-2">
                <i class="fas fa-circle text-gray-300 mr-2"></i>
                <span>Selecting diverse perspectives...</span>
            </div>
            <div class="flex items-center mb-2">
                <i class="fas fa-circle text-gray-300 mr-2"></i>
                <span>Performing comprehensive analysis...</span>
            </div>
        `;
    }

    function hideLoading() {
        analyzeBtn.disabled = false;
        analyzeBtn.innerHTML = '<i class="fas fa-search mr-2"></i>Analyze Article';
        loadingState.classList.add('hidden');
    }

    function showResults(data) {
        resultsSection.classList.remove('hidden');
        errorSection.classList.add('hidden');

        // Display Section 1: Similar Articles
        displaySimilarArticles(data.section_1.similar_articles);

        // Display Section 2: Article Analysis
        displayArticleAnalysis(data.section_2);

        // Display Section 3: AI Score
        displayAIScore(data.section_3);
    }

    function displaySimilarArticles(articles) {
        const container = document.getElementById('similarArticles');
        container.innerHTML = '';

        articles.forEach(article => {
            const tile = document.createElement('div');
            tile.className = 'bg-gray-50 rounded-lg p-4 hover:shadow-lg transition-shadow duration-200';
            
            const imageHtml = article.image_url 
                ? `<img src="${article.image_url}" alt="${article.headline}" class="w-full h-32 object-cover rounded mb-3">`
                : `<div class="w-full h-32 bg-gray-200 rounded mb-3 flex items-center justify-center">
                     <i class="fas fa-newspaper text-gray-400 text-2xl"></i>
                   </div>`;

            tile.innerHTML = `
                ${imageHtml}
                <h3 class="font-semibold text-gray-800 mb-2 line-clamp-2">${escapeHtml(article.headline)}</h3>
                <p class="text-sm text-gray-600 mb-2">
                    <i class="fas fa-source mr-1"></i> ${escapeHtml(article.source)}
                </p>
                <p class="text-sm text-gray-700 line-clamp-3">${escapeHtml(article.summary)}</p>
                ${article.url ? `<a href="${article.url}" target="_blank" class="text-blue-600 hover:text-blue-800 text-sm mt-2 inline-block">
                    <i class="fas fa-external-link-alt mr-1"></i>Read More
                </a>` : ''}
            `;
            
            container.appendChild(tile);
        });
    }

    function displayArticleAnalysis(analysis) {
        // Display Key Facts
        const factsContainer = document.getElementById('keyFacts');
        factsContainer.innerHTML = '';
        
        if (analysis.key_facts && analysis.key_facts.length > 0) {
            analysis.key_facts.forEach(fact => {
                const factDiv = document.createElement('div');
                factDiv.className = 'p-3 bg-green-50 rounded-lg border-l-4 border-green-500';
                factDiv.innerHTML = `
                    <p class="font-medium text-gray-800">${escapeHtml(fact.fact)}</p>
                    <p class="text-sm text-gray-600 mt-1">${escapeHtml(fact.verification)}</p>
                    <span class="inline-block mt-2 px-2 py-1 text-xs bg-green-200 text-green-800 rounded">
                        Confidence: ${fact.confidence}
                    </span>
                `;
                factsContainer.appendChild(factDiv);
            });
        } else {
            factsContainer.innerHTML = '<p class="text-gray-500">No key facts identified.</p>';
        }

        // Display Opinions
        const opinionsContainer = document.getElementById('opinions');
        opinionsContainer.innerHTML = '';
        
        if (analysis.opinions && analysis.opinions.length > 0) {
            analysis.opinions.forEach(opinion => {
                const opinionDiv = document.createElement('div');
                opinionDiv.className = 'p-3 bg-yellow-50 rounded-lg border-l-4 border-yellow-500';
                opinionDiv.innerHTML = `
                    <p class="font-medium text-gray-800">"${escapeHtml(opinion.statement)}"</p>
                    <p class="text-sm text-gray-600 mt-1">${escapeHtml(opinion.context)}</p>
                    <span class="inline-block mt-2 px-2 py-1 text-xs bg-yellow-200 text-yellow-800 rounded">
                        ${opinion.bias_indication}
                    </span>
                `;
                opinionsContainer.appendChild(opinionDiv);
            });
        } else {
            opinionsContainer.innerHTML = '<p class="text-gray-500">No opinions identified.</p>';
        }

        // Display Biases
        const biasesContainer = document.getElementById('biases');
        biasesContainer.innerHTML = '';
        
        if (analysis.biases && analysis.biases.length > 0) {
            analysis.biases.forEach(bias => {
                const biasDiv = document.createElement('div');
                biasDiv.className = 'p-3 bg-red-50 rounded-lg border-l-4 border-red-500';
                biasDiv.innerHTML = `
                    <p class="font-medium text-gray-800">${bias.type.replace('_', ' ').toUpperCase()}</p>
                    <p class="text-sm text-gray-700 mt-1">${escapeHtml(bias.description)}</p>
                    <p class="text-sm text-gray-600 mt-2">${escapeHtml(bias.impact)}</p>
                `;
                biasesContainer.appendChild(biasDiv);
            });
        } else {
            biasesContainer.innerHTML = '<p class="text-gray-500">No biases identified.</p>';
        }

        // Display Overall Assessment
        document.getElementById('overallAssessment').innerHTML = `
            <p class="text-gray-700">${escapeHtml(analysis.overall_assessment)}</p>
        `;
    }

    function displayAIScore(aiData) {
        const score = aiData.genai_score || 0;
        const scoreElement = document.getElementById('aiScore');
        const scoreBar = document.getElementById('aiScoreBar');
        const reasoningElement = document.getElementById('aiReasoning');

        // Update score display
        scoreElement.textContent = score;
        
        // Update score bar
        scoreBar.style.width = `${score}%`;
        
        // Color code based on score
        let barColor, textColor;
        if (score < 30) {
            barColor = 'bg-green-500';
            textColor = 'text-green-600';
        } else if (score < 70) {
            barColor = 'bg-yellow-500';
            textColor = 'text-yellow-600';
        } else {
            barColor = 'bg-red-500';
            textColor = 'text-red-600';
        }
        
        scoreBar.className = `h-4 rounded-full transition-all duration-500 ${barColor}`;
        scoreElement.className = `text-3xl font-bold ${textColor}`;

        // Update reasoning
        let reasoningHtml = `
            <div class="mb-4">
                <h4 class="font-semibold text-gray-800 mb-2">Reasoning:</h4>
                <p class="text-gray-700">${escapeHtml(aiData.genai_reasoning)}</p>
            </div>
        `;

        if (aiData.genai_telltales && aiData.genai_telltales.length > 0) {
            reasoningHtml += `
                <div>
                    <h4 class="font-semibold text-gray-800 mb-2">AI Indicators Found:</h4>
                    <ul class="list-disc list-inside text-gray-700">
            `;
            aiData.genai_telltales.forEach(telltale => {
                reasoningHtml += `<li>${escapeHtml(telltale)}</li>`;
            });
            reasoningHtml += '</ul></div>';
        }

        reasoningElement.innerHTML = reasoningHtml;
    }

    function showError(message) {
        errorSection.classList.remove('hidden');
        resultsSection.classList.add('hidden');
        document.getElementById('errorMessage').textContent = message;
    }

    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
});
