// Backend URL - Change this if your backend is on different port
const BACKEND_URL = "http://localhost:8000";

// DOM Elements
const userInput = document.getElementById('userInput');
const checkBtn = document.getElementById('checkBtn');
const loading = document.getElementById('loading');
const resultDiv = document.getElementById('result');
const connectionStatus = document.getElementById('connectionStatus');
const difficultySelect = document.getElementById('difficulty');

// Initialize the app
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 English Tutor Frontend Started');
    console.log('Backend URL:', BACKEND_URL);
    
    // Test backend connection on startup
    testBackendConnection();
    
    // Add Enter key support for textarea
    userInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter' && e.ctrlKey) {
            checkGrammar();
        }
    });
});

// Test backend connection
async function testBackendConnection() {
    try {
        const response = await fetch(`${BACKEND_URL}/health`);
        if (response.ok) {
            connectionStatus.className = 'status-connected';
            connectionStatus.textContent = '✅ Connected to AI Backend';
        } else {
            throw new Error('Backend not responding properly');
        }
    } catch (error) {
        connectionStatus.className = 'status-error';
        connectionStatus.textContent = '❌ Backend Connection Failed';
        console.error('Connection test failed:', error);
    }
}

// Main grammar checking function
async function checkGrammar() {
    const text = userInput.value.trim();
    
    if (!text) {
        showError('Please enter some text to check!');
        return;
    }
    
    if (text.length < 2) {
        showError('Please enter a longer sentence!');
        return;
    }
    
    // Show loading state
    setLoading(true);
    hideResult();
    
    try {
        console.log('Sending request to backend...');
        
        const response = await fetch(`${BACKEND_URL}/correct`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                text: text,
                difficulty: difficultySelect.value
            })
        });
        
        if (!response.ok) {
            throw new Error(`Server error: ${response.status}`);
        }
        
        const data = await response.json();
        console.log('Received response:', data);
        
        displayResult(data);
        
    } catch (error) {
        console.error('Error:', error);
        showError(`
            Could not connect to the grammar service. 
            
            Make sure:
            • Your backend server is running
            • The URL is correct: ${BACKEND_URL}
            • You have internet connection
            
            Error details: ${error.message}
        `);
    } finally {
        setLoading(false);
    }
}

// Display results
function displayResult(data) {
    const statusClass = data.status.toLowerCase();
    const statusEmoji = getStatusEmoji(data.status);
    
    let correctedHtml = '';
    if (data.status === 'corrected') {
        correctedHtml = `
            <div class="result-item">
                <strong>Corrected:</strong> 
                <span style="color: #28a745; font-weight: 500;">${data.corrected_text}</span>
            </div>
        `;
    }
    
    let suggestionsHtml = '';
    if (data.suggestions && data.suggestions.length > 0) {
        suggestionsHtml = `
            <div class="suggestions">
                <h4>💡 Vocabulary Suggestions</h4>
                ${data.suggestions.map(suggestion => 
                    `<div style="margin: 5px 0; padding: 8px; background: white; border-radius: 5px;">
                        ${suggestion}
                    </div>`
                ).join('')}
            </div>
        `;
    }
    
    resultDiv.innerHTML = `
        <div class="result ${statusClass}">
            <h3>
                ${statusEmoji} 
                ${data.status.toUpperCase()} 
                <span style="font-size: 14px; color: #666; margin-left: auto;">
                    ${(data.confidence * 100).toFixed(0)}% confidence
                </span>
            </h3>
            
            <div class="result-item">
                <strong>Your input:</strong> ${data.original_text}
            </div>
            
            ${correctedHtml}
            
            <div class="result-item">
                <strong>Explanation:</strong> ${data.explanation}
            </div>
            
            ${suggestionsHtml}
            
            <div style="margin-top: 15px; padding-top: 15px; border-top: 1px solid #eee;">
                <small style="color: #666;">
                    Difficulty: ${data.difficulty_used} • Powered by AI Grammar Correction
                </small>
            </div>
        </div>
    `;
    
    resultDiv.style.display = 'block';
    
    // Smooth scroll to results
    resultDiv.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

// Helper functions
function getStatusEmoji(status) {
    switch(status.toLowerCase()) {
        case 'correct': return '✅';
        case 'corrected': return '🔧';
        case 'unsure': return '❓';
        default: return '📝';
    }
}

function setLoading(isLoading) {
    if (isLoading) {
        checkBtn.disabled = true;
        loading.style.display = 'block';
        checkBtn.querySelector('.btn-text').style.display = 'none';
        checkBtn.querySelector('.btn-loading').style.display = 'inline';
    } else {
        checkBtn.disabled = false;
        loading.style.display = 'none';
        checkBtn.querySelector('.btn-text').style.display = 'inline';
        checkBtn.querySelector('.btn-loading').style.display = 'none';
    }
}

function hideResult() {
    resultDiv.style.display = 'none';
}

function showError(message) {
    resultDiv.innerHTML = `
        <div class="result unsure">
            <h3>❌ Error</h3>
            <div class="result-item">
                ${message.split('\n').map(line => `<p>${line}</p>`).join('')}
            </div>
        </div>
    `;
    resultDiv.style.display = 'block';
}

// Example button functionality
function fillExample(text) {
    userInput.value = text;
    userInput.focus();
}

// Add some keyboard shortcuts
document.addEventListener('keydown', function(e) {
    // Ctrl + Enter to check grammar
    if (e.ctrlKey && e.key === 'Enter') {
        checkGrammar();
    }
    
    // Escape to clear input
    if (e.key === 'Escape') {
        userInput.value = '';
        hideResult();
    }
});