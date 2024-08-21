document.addEventListener('DOMContentLoaded', function() {
    const team1Select = document.getElementById('team1');
    const team2Select = document.getElementById('team2');
    let teamsData = [];

    fetch('http://127.0.0.1:5000/euro_groups')
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok ' + response.statusText);
            }
            return response.json();
        })
        .then(data => {
            teamsData = data;
            console.log('Fetched data:', data);

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

    team1Select.addEventListener('change', function() {
        const selectedTeam = team1Select.value;

        // Update team2Select to exclude the selectedTeam
        team2Select.innerHTML = '';

        const remainingTeams = teamsData.filter(item => item.team !== selectedTeam).map(item => item.team);

        remainingTeams.forEach(team => {
            const option2 = document.createElement('option');
            option2.value = team;
            option2.textContent = team;
            team2Select.appendChild(option2);
        });
    });

    document.getElementById('predictionForm').addEventListener('submit', function(event) {
        event.preventDefault();

        const team1 = document.getElementById('team1').value;
        const team2 = document.getElementById('team2').value;

        const url = `http://backend/predict?team1=${encodeURIComponent(team1)}&team2=${encodeURIComponent(team2)}`;

        fetch(url)
            .then(response => response.json())
            .then(data => {
                document.getElementById('result').textContent = `Przewidywany wynik: ${data.prediction}`;
            })
            .catch(error => {
                document.getElementById('result').textContent = 'Wystąpił błąd. Spróbuj ponownie później.';
                console.error('Error:', error);
            });
    });
});
