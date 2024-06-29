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

            // Populate team1 select
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
        const selectedGroup = teamsData.find(item => item.team === selectedTeam).group;
        const teamsInSameGroup = teamsData.filter(item => item.group === selectedGroup && item.team !== selectedTeam);

        team2Select.innerHTML = ''; 

        teamsInSameGroup.forEach(teamData => {
            const option2 = document.createElement('option');
            option2.value = teamData.team;
            option2.textContent = teamData.team;
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
