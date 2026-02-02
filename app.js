// Scoring constants
const POINTS = {
    gold: 3,
    silver: 2,
    bronze: 1
};

// Parse CSV text into array of objects
function parseCSV(text) {
    const lines = text.trim().split('\n');
    const headers = lines[0].split(',').map(h => h.trim());

    return lines.slice(1).map(line => {
        const values = line.split(',').map(v => v.trim());
        const obj = {};
        headers.forEach((header, i) => {
            obj[header] = values[i] || '';
        });
        return obj;
    });
}

// Fetch and parse a CSV file
async function fetchCSV(filename) {
    const response = await fetch(`data/${filename}?t=${Date.now()}`);
    if (!response.ok) {
        throw new Error(`Failed to load ${filename}`);
    }
    const text = await response.text();
    return parseCSV(text);
}

// Calculate points for a country based on medal counts
function calculateCountryPoints(medals) {
    const gold = parseInt(medals.Gold) || 0;
    const silver = parseInt(medals.Silver) || 0;
    const bronze = parseInt(medals.Bronze) || 0;

    return (gold * POINTS.gold) + (silver * POINTS.silver) + (bronze * POINTS.bronze);
}

// Calculate scores for all participants
function calculateScores(picks, medals) {
    // Create a map of country -> points
    const countryPoints = {};
    medals.forEach(m => {
        countryPoints[m.Country.toLowerCase()] = calculateCountryPoints(m);
    });

    // Calculate each person's score
    const scores = picks.map(pick => {
        const name = pick.Name;
        const countries = [];
        let totalPoints = 0;

        // Get all country columns (Country1 through Country7)
        for (let i = 1; i <= 7; i++) {
            const country = pick[`Country${i}`];
            if (country) {
                const points = countryPoints[country.toLowerCase()] || 0;
                countries.push({ name: country, points });
                totalPoints += points;
            }
        }

        return {
            name,
            countries,
            totalPoints
        };
    });

    // Sort by total points (descending)
    scores.sort((a, b) => b.totalPoints - a.totalPoints);

    return scores;
}

// Render the leaderboard
function renderLeaderboard(scores) {
    const container = document.getElementById('leaderboard-container');

    if (scores.length === 0) {
        container.innerHTML = '<p class="error">No picks data found</p>';
        return;
    }

    let html = `
        <table class="leaderboard-table">
            <thead>
                <tr>
                    <th>Rank</th>
                    <th>Name</th>
                    <th>Points</th>
                    <th>Countries</th>
                </tr>
            </thead>
            <tbody>
    `;

    scores.forEach((score, index) => {
        const rank = index + 1;
        const rankClass = rank <= 3 ? `rank-${rank}` : '';

        const countriesHtml = score.countries
            .map(c => `<span class="country-score ${c.points > 0 ? 'has-points' : ''}">${c.name}: ${c.points}</span>`)
            .join(' ');

        html += `
            <tr>
                <td class="rank ${rankClass}">${rank}</td>
                <td>${score.name}</td>
                <td class="points">${score.totalPoints}</td>
                <td class="countries-list">${countriesHtml}</td>
            </tr>
        `;
    });

    html += '</tbody></table>';
    container.innerHTML = html;
}

// Render the medal table
function renderMedalTable(medals) {
    const container = document.getElementById('medal-container');

    if (medals.length === 0) {
        container.innerHTML = '<p class="error">No medal data found</p>';
        return;
    }

    // Sort by total medals (gold weighted highest)
    medals.sort((a, b) => {
        const aTotal = (parseInt(a.Gold) || 0) * 1000 + (parseInt(a.Silver) || 0) * 100 + (parseInt(a.Bronze) || 0);
        const bTotal = (parseInt(b.Gold) || 0) * 1000 + (parseInt(b.Silver) || 0) * 100 + (parseInt(b.Bronze) || 0);
        return bTotal - aTotal;
    });

    let html = `
        <table class="medal-table">
            <thead>
                <tr>
                    <th>Country</th>
                    <th class="gold">Gold</th>
                    <th class="silver">Silver</th>
                    <th class="bronze">Bronze</th>
                    <th>Points</th>
                </tr>
            </thead>
            <tbody>
    `;

    medals.forEach(medal => {
        const gold = parseInt(medal.Gold) || 0;
        const silver = parseInt(medal.Silver) || 0;
        const bronze = parseInt(medal.Bronze) || 0;
        const points = calculateCountryPoints(medal);

        html += `
            <tr>
                <td>${medal.Country}</td>
                <td class="gold">${gold}</td>
                <td class="silver">${silver}</td>
                <td class="bronze">${bronze}</td>
                <td class="medal-total">${points}</td>
            </tr>
        `;
    });

    html += '</tbody></table>';
    container.innerHTML = html;
}

// Update the last updated timestamp
function updateTimestamp() {
    const element = document.getElementById('last-updated');
    element.textContent = new Date().toLocaleString();
}

// Main initialization
async function init() {
    try {
        // Fetch both CSV files
        const [picks, medals] = await Promise.all([
            fetchCSV('picks.csv'),
            fetchCSV('medals.csv')
        ]);

        // Calculate and render leaderboard
        const scores = calculateScores(picks, medals);
        renderLeaderboard(scores);

        // Render medal table
        renderMedalTable(medals);

        // Update timestamp
        updateTimestamp();

    } catch (error) {
        console.error('Error loading data:', error);
        document.getElementById('leaderboard-container').innerHTML =
            `<p class="error">Error loading data: ${error.message}</p>`;
        document.getElementById('medal-container').innerHTML =
            `<p class="error">Error loading data: ${error.message}</p>`;
    }
}

// Start the app
init();

// Auto-refresh every 5 minutes
setInterval(init, 5 * 60 * 1000);
