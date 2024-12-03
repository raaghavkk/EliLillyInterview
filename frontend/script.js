document.addEventListener('DOMContentLoaded', () => {
    fetchData();
});

function fetchData() {
    fetch('http://localhost:8000/medicines')
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            displayData(data);
        })
        .catch(error => {
            showError(`Error fetching data: ${error.message}`);
            console.error('Error:', error);
        });
}

function displayData(data) {
    const container = document.getElementById('data-container');
    container.innerHTML = '';

    if (!Array.isArray(data)) {
        showError('Invalid data format received');
        return;
    }

    data.forEach(item => {
        const div = document.createElement('div');
        div.className = 'medicine-item';
        
        // Validate and sanitize data
        const name = item.name?.trim() || 'Unknown Medicine';
        const price = item.price !== null ? `$${item.price}` : 'Price not available';
        const description = item.description?.trim() || 'No description available';

        div.innerHTML = `
            <h3>${sanitizeHTML(name)}</h3>
            <p>Price: ${sanitizeHTML(price)}</p>
            <p>Description: ${sanitizeHTML(description)}</p>
        `;
        container.appendChild(div);
    });
}

function showError(message) {
    const container = document.getElementById('data-container');
    container.innerHTML = `
        <div class="error-message">
            ${message}
        </div>
    `;
}

function sanitizeHTML(str) {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}