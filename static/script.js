/**
 * Emoji Semantic Search - JavaScript
 * Provides search functionality and UI interactions
 */

// DOM Element References
const searchInput = document.getElementById('search-query');
const searchButton = document.getElementById('search-button');
const resultsContainer = document.getElementById('results-container');
const statusMessage = document.getElementById('status-message');

/**
 * Displays a status message (loading, error, or clears it).
 * @param {string} message - The message text.
 * @param {'loading' | 'error' | 'clear'} type - The type of message for styling.
 */
function showStatus(message, type = 'loading') {
    statusMessage.textContent = message;
    statusMessage.className = 'status'; // Reset classes first
    if (type === 'loading') {
        statusMessage.classList.add('loading');
    } else if (type === 'error') {
        statusMessage.classList.add('error');
    }
}

/**
 * Clears the results container and status messages, and hides the container.
 */
function clearResultsAndStatus() {
    resultsContainer.innerHTML = ''; // Clear previous results
    resultsContainer.style.display = 'none';
    showStatus('', 'clear'); // Clear status message
}

/**
 * Copies the emoji to clipboard and shows a temporary feedback message.
 * @param {string} emoji - The emoji character to copy.
 * @param {HTMLElement} element - The element that was clicked.
 */
function copyEmojiToClipboard(emoji, element) {
    navigator.clipboard.writeText(emoji)
        .then(() => {
            // Create and show feedback element
            const feedback = document.createElement('span');
            feedback.textContent = 'Copied!';
            feedback.classList.add('copy-feedback');
            
            // Position the feedback near the emoji
            element.appendChild(feedback);
            
            // Remove the feedback message after 1 second to match CSS animation
            setTimeout(() => {
                feedback.remove();
            }, 1000);
        })
        .catch(err => {
            console.error('Failed to copy: ', err);
            showStatus('Failed to copy emoji', 'error');
        });
}

/**
 * Creates and appends an emoji result item to the container.
 * @param {object} result - An object containing { emoji: string, score: number }.
 */
function displayResult(result) {
    const itemDiv = document.createElement('div');
    itemDiv.classList.add('emoji-item');

    const emojiSpan = document.createElement('span');
    emojiSpan.classList.add('emoji-char');
    emojiSpan.textContent = result.emoji;

    // Add tooltip and cursor style to indicate it's clickable
    emojiSpan.title = 'Click to copy';
    emojiSpan.style.cursor = 'pointer';

    // Add click handler to copy emoji
    emojiSpan.addEventListener('click', function() {
        copyEmojiToClipboard(result.emoji, this);
    });

    const scoreSpan = document.createElement('span');
    scoreSpan.classList.add('emoji-score');
    scoreSpan.textContent = `Score: ${result.score.toFixed(2)}`;

    itemDiv.appendChild(emojiSpan);
    itemDiv.appendChild(scoreSpan);
    resultsContainer.appendChild(itemDiv);
}

/**
 * Performs the search by calling the backend API.
 */
async function performSearch() {
    const query = searchInput.value.trim();

    if (!query) {
        clearResultsAndStatus();
        showStatus('Please enter a search term.', 'error');
        return;
    }

    clearResultsAndStatus();
    showStatus('Searching for emojis...', 'loading');

    try {
        const apiUrl = `/search?q=${encodeURIComponent(query)}`;
        const response = await fetch(apiUrl);

        if (!response.ok) {
            let errorMsg = `Error: ${response.status} ${response.statusText}`;
            try {
                const errorData = await response.json();
                if (errorData.detail) {
                    errorMsg += ` - ${errorData.detail}`;
                }
            } catch (e) { /* Ignore JSON parsing errors */ }
            throw new Error(errorMsg);
        }

        const data = await response.json();

        if (data.results && data.results.length > 0) {
            showStatus('', 'clear'); // Clear 'Searching...' message
            resultsContainer.style.display = 'grid';
            data.results.forEach(result => {
                displayResult(result);
            });
        } else {
            showStatus('No relevant emojis found for your query.', 'clear');
        }

    } catch (error) {
        console.error("Search failed:", error);
        showStatus(`Search failed: ${error.message}`, 'error');
    }
}

// Event Listeners
searchButton.addEventListener('click', performSearch);
searchInput.addEventListener('keypress', function(event) {
    if (event.key === 'Enter') {
        event.preventDefault();
        performSearch();
    }
});

// Initial Setup
resultsContainer.style.display = 'none';
showStatus('', 'clear');