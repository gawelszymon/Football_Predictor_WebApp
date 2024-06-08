document.addEventListener('DOMContentLoaded', function() {
    const teams = [
        "Niemcy", "Albania", "Austria", "Belgia", "Chorwacja", "Czechy", 
        "Dania", "Anglia", "Francja", "Gruzja", "Węgry", "Włochy", "Holandia", 
        "Polska", "Portugalia", "Rumunia", "Szkocja", "Serbia", "Słowacja", "Słowenia", 
        "Hiszpania", "Szwajcaria", "Turcja", "Ukraina"
    ];

    const team1Select = document.getElementById('team1');
    const team2Select = document.getElementById('team2');

    teams.forEach(team => {
        const option1 = document.createElement('option');
        option1.value = team;
        option1.textContent = team;
        team1Select.appendChild(option1);

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
