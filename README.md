# Olympic Pool Leaderboard

A simple static website for tracking your office Olympic pool competition.

## How It Works

1. Each participant picks up to 7 countries
2. Points are earned based on medal counts:
   - Gold = 3 points
   - Silver = 2 points
   - Bronze = 1 point
3. The leaderboard automatically calculates and ranks everyone

## Setup

### Local Testing
Simply open `index.html` in your browser. Note: You may need to use a local server due to CORS restrictions when loading CSV files.

Quick local server options:
```bash
# Python 3
python -m http.server 8000

# Node.js (if you have npx)
npx serve
```

Then open `http://localhost:8000` in your browser.

### Deploy to GitHub Pages

1. Create a new repository on GitHub
2. Upload all files to the repository
3. Go to Settings > Pages
4. Under "Source", select "Deploy from a branch"
5. Select "main" branch and "/ (root)" folder
6. Click Save
7. Your site will be live at `https://yourusername.github.io/repository-name`

## Updating Data

### Adding/Editing Participants
Edit `data/picks.csv`:
```
Name,Country1,Country2,Country3,Country4,Country5,Country6,Country7
John,USA,Canada,Norway,Germany,Switzerland,Austria,Sweden
```

### Updating Medal Counts
Edit `data/medals.csv`:
```
Country,Gold,Silver,Bronze
Norway,5,3,2
USA,3,4,1
```

**Important:** Country names must match exactly between picks.csv and medals.csv (case-insensitive).

### On GitHub
1. Navigate to the CSV file you want to edit
2. Click the pencil icon to edit
3. Make your changes
4. Click "Commit changes"
5. The site will update within a few minutes

## Files

```
Olympic_Pool/
├── index.html          # Main page
├── style.css           # Olympics-themed styling
├── app.js              # Score calculation logic
├── data/
│   ├── picks.csv       # Participant country picks
│   └── medals.csv      # Current medal counts
└── README.md           # This file
```

## Features

- Auto-calculates scores from CSV data
- Sorts leaderboard by total points
- Shows point breakdown per country
- Mobile-friendly responsive design
- Olympics-themed styling with rings
- Auto-refreshes every 5 minutes
