document.addEventListener('DOMContentLoaded', function() {

    const predictedResults = {
        "Germany": {"Scotland": "2-0", "Hungary": "2-0", "Denmark": "2-1", "Spain": "1-2"},
        "Hungary": {"Switzerland": "1-2", "Germany": "0-2", "Scotland": "1-1"},
        "Scotland": {"Switzerland": "1-1", "Hungary": "1-1", "Germany": "0-2"},
        "Switzerland": {"Germany": "1-2", "Hungary": "2-1", "Italy": "2-1", "England": "0-2"},
        "Spain": {"Croatia": "2-1", "Italy": "2-1", "Georgia": "2-0", "Germany": "2-1", "France": "1-1", "England": "1-1"},
        "Italy": {"Albania": "2-0", "Spain": "1-2"},
        "Croatia": {"Albania": "2-1"},
        "Albania": {"Spain": "0-2"},
        "Slovenia": {"Denmark": "1-2", "Serbia": "1-2"},
        "Serbia": {"England": "0-2", "Slovenia": "2-1"},
        "Denmark": {"England": "0-2", "Serbia": "1-1"},
        "England": {"Slovakia": "2-0", "Switzerland": "2-0", "Slovenia": "2-0", "Serbia": "2-0", "Netherlands": "2-1", "Spain": "1-1"},
        "Poland": {"Netherlands": "0-2", "Austria": "1-1", "France": "0-2"},
        "Austria": {"France": "0-2", "Poland": "1-1", "Turkey": "1-1"},
        "Netherlands": {"France": "1-1", "Austria": "2-1", "Turkey": "2-1", "England": "1-2"},
        "France": {"Poland": "2-0", "Belgium": "2-1", "Netherlands": "1-1", "Portugal": "1-1", "Spain": "1-1"},
        "Romania": {"Ukraine": "1-1"},
        "Belgium": {"Slovakia": "2-1", "Romania": "2-1"},
        "Slovakia": {"Ukraine": "1-1", "Belgium": "1-2"},
        "Ukraine": {"Belgium": "1-1"},
        "Turkey": {"Georgia": "2-1", "Portugal": "0-2"},
        "Portugal": {"Czech Republic": "2-1", "Turkey": "2-0", "Slovenia": "2-0", "France": "1-1", "Spain": "1-1"},
        "Georgia": {"Czech Republic": "1-1", "Portugal": "0-2"},
        "Czech Republic": {"Turkey": "1-1"}
    };

    const realResults = {
        "Germany": {"Scotland": "5-1", "Hungary": "2-0", "Denmark": "2-0", "Spain": "1-2"},
        "Hungary": {"Switzerland": "1-3", "Germany": "0-2", "Scotland": "1-0"},
        "Scotland": {"Switzerland": "1-1", "Hungary": "0-1", "Germany": "1-5"},
        "Switzerland": {"Germany": "1-1", "Hungary": "3-1", "Italy": "2-0", "England": "1-1"},
        "Spain": {"Croatia": "3-0", "Italy": "1-0", "Georgia": "4-1", "Germany": "2-1", "France": "2-1", "England": "2-1"},
        "Italy": {"Albania": "2-1", "Spain": "0-1"},
        "Croatia": {"Albania": "2-2"},
        "Albania": {"Spain": "0-1"},
        "Slovenia": {"Denmark": "1-1", "Serbia": "1-1"},
        "Serbia": {"England": "0-1", "Slovenia": "1-1"},
        "Denmark": {"England": "1-1", "Serbia": "0-0"},
        "England": {"Slovakia": "2-1", "Switzerland": "1-1", "Slovenia": "0-0", "Serbia": "1-0", "Netherlands": "1-2", "Spain": "1-2"},
        "Poland": {"Netherlands": "1-2", "Austria": "1-3", "France": "1-1"},
        "Austria": {"France": "0-1", "Poland": "3-1", "Turkey": "2-1"},
        "Netherlands": {"France": "0-0", "Austria": "2-3", "Turkey": "2-1", "England": "2-1"},
        "France": {"Poland": "1-1", "Belgium": "1-0", "Netherlands": "0-0", "Portugal": "0-0", "Spain": "1-2"},
        "Romania": {"Ukraine": "3-0"},
        "Belgium": {"Slovakia": "0-1", "Romania": "2-0"},
        "Slovakia": {"Ukraine": "2-1", "Belgium": "1-0"},
        "Ukraine": {"Belgium": "0-0"},
        "Turkey": {"Georgia": "3-1", "Portugal": "0-3"},
        "Portugal": {"Czech Republic": "2-1", "Turkey": "3-0", "Slovenia": "0-0", "France": "0-0", "Spain": "0-2"},
        "Georgia": {"Czech Republic": "1-1", "Portugal": "2-0"},
        "Czech Republic": {"Turkey": "2-1"}
    };

    // Load video and UEFA images with event listeners
    const videoImage = document.getElementById("video");
    videoImage.style.cursor = "pointer";  
    videoImage.addEventListener("click", function () {
        window.open("https://www.youtube.com/watch?v=R67eLGy2nGw", '_blank');
    });

    const uefaImage = document.getElementById("uefa");
    uefaImage.style.cursor = "pointer";  
    uefaImage.addEventListener("click", function () {
        window.open("https://www.uefa.com/", '_blank');
    });

    // Fetching DOM elements for teams selection
    const team1Select = document.getElementById('team1');
    const team2Select = document.getElementById('team2');

    let teamsData = [];

    // Fetch the team data for dropdowns
    fetch('http://127.0.0.1:5000/euro_groups')
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok ' + response.statusText);
            }
            return response.json();
        })
        .then(data => {
            teamsData = data;

            const uniqueTeams = [...new Set(data.map(item => item.team))];

            uniqueTeams.forEach(team => {
                const option1 = document.createElement('option');
                option1.value = team;
                option1.textContent = team;
                team1Select.appendChild(option1);
            });
        })
        .catch(error => {
            console.error('Error fetching data:', error);
            document.getElementById('result').textContent = 'Wystąpił błąd podczas ładowania danych o drużynach.';
        });

    // Update second team select options based on the first selection
    team1Select.addEventListener('change', function() {
        const selectedTeam = team1Select.value;
        team2Select.innerHTML = '';

        const remainingTeams = teamsData.filter(item => item.team !== selectedTeam).map(item => item.team);

        remainingTeams.forEach(team => {
            const option2 = document.createElement('option');
            option2.value = team;
            option2.textContent = team;
            team2Select.appendChild(option2);
        });
    });

    // Predict result on form submission
    document.getElementById('predictionForm').addEventListener('submit', function(event) {
        event.preventDefault();

        const team1 = document.getElementById('team1').value;
        const team2 = document.getElementById('team2').value;

        const predictedResult = (predictedResults[team1] && predictedResults[team1][team2]) || 
                                (predictedResults[team2] && predictedResults[team2][team1]) || 
                                'No predicted result available';
        const realResult = (realResults[team1] && realResults[team1][team2]) || 
                           (realResults[team2] && realResults[team2][team1]) || 
                           'No real result available';

        // Display the results
        if (predictedResult !== 'No predicted result available') {
            document.getElementById('result').textContent = `Predicted result: ${team1} ${predictedResult.split('-')[0].trim()} - ${team2} ${predictedResult.split('-')[1].trim()}`;
        } else {
            document.getElementById('result').textContent = 'No predicted result available';
        }

        if (realResult !== 'No real result available') {
            document.getElementById('true_result').textContent = `Real result: ${team1} ${realResult.split('-')[0].trim()} - ${team2} ${realResult.split('-')[1].trim()}`;
        } else {
            document.getElementById('true_result').textContent = 'No real result available';
        }
    });

    // Load existing entries
    function loadEntries() {
        fetch('/get_entries')
            .then(response => response.json())
            .then(data => {
                const entriesContainer = document.getElementById('entries');
                entriesContainer.innerHTML = '';

                data.forEach(entry => {
                    const entryDiv = document.createElement('div');
                    entryDiv.classList.add('entry');

                    const usernameDiv = document.createElement('div');
                    usernameDiv.classList.add('username');
                    usernameDiv.textContent = entry.username;

                    const timestampDiv = document.createElement('div');
                    timestampDiv.classList.add('timestamp');
                    timestampDiv.textContent = entry.timestamp;

                    const contentDiv = document.createElement('div');
                    contentDiv.textContent = entry.content;

                    entryDiv.appendChild(usernameDiv);
                    entryDiv.appendChild(timestampDiv);
                    entryDiv.appendChild(contentDiv);

                    entriesContainer.appendChild(entryDiv);
                });
            })
            .catch(error => {
                console.error('Error loading entries:', error);
            });
    }

    // Add a new entry
    document.getElementById('opinionForm').addEventListener('submit', function(event) {
        event.preventDefault();

        const username = document.getElementById('username').value;
        const content = document.getElementById('content').value;

        if (!username || !content) {
            alert("Please fill in both username and content fields!");
            return;
        }

        fetch('/add_entry', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username, content })
        })
        .then(response => {
            if (!response.ok) {
                return response.text().then(text => { throw new Error(text) });
            }
            return response.json();
        })
        .then(data => {
            loadEntries();  // Reload entries after adding
            document.getElementById('username').value = '';  // Clear form
            document.getElementById('content').value = '';
        })
        .catch(error => {
            console.error('Error adding entry:', error);
        });
    });

    loadEntries();  // Load entries on page load
});
