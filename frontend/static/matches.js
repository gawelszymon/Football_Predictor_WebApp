document.addEventListener('DOMContentLoaded', function () {
    const teamSelect = document.getElementById('team-select');
    
    function fetchMatches(teamId) {
        fetch(`/last_matches?team_id=${teamId}`)
            .then(response => response.json())
            .then(data => {
                const matchesContainer = document.getElementById('matches-container');
                matchesContainer.innerHTML = ''; 
                data.forEach(match => {
                    const matchDiv = document.createElement('div');
                    matchDiv.classList.add('match');

                    const matchHeader = document.createElement('h2');
                    matchHeader.innerHTML = `
                        <img src="/static/flags/${match.match.split(' - ')[0]}.png" alt="${match.match.split(' - ')[0]} flag" class="flag-icon">
                        ${match.match} 
                        <img src="/static/flags/${match.match.split(' - ')[1]}.png" alt="${match.match.split(' - ')[1]} flag" class="flag-icon">
                    `;
                    matchDiv.appendChild(matchHeader);

                    const scoreParagraph = document.createElement('p');
                    scoreParagraph.classList.add('score');
                    scoreParagraph.textContent = `Score: ${match.score}`;
                    matchDiv.appendChild(scoreParagraph);

                    const scorersHeader = document.createElement('h3');
                    scorersHeader.textContent = 'Scorers:';
                    matchDiv.appendChild(scorersHeader);

                    const scorersList = document.createElement('ul');
                    match.scorers.forEach(scorer => {
                        const scorerItem = document.createElement('li');
                        scorerItem.textContent = scorer;
                        scorersList.appendChild(scorerItem);
                    });
                    matchDiv.appendChild(scorersList);

                    const assistsHeader = document.createElement('h3');
                    assistsHeader.textContent = 'Assists:';
                    matchDiv.appendChild(assistsHeader);

                    const assistsList = document.createElement('ul');
                    match.assists.forEach(assist => {
                        const assistItem = document.createElement('li');
                        assistItem.textContent = assist;
                        assistsList.appendChild(assistItem);
                    });
                    matchDiv.appendChild(assistsList);

                    matchesContainer.appendChild(matchDiv);
                });
            })
            .catch(error => {
                console.error('Error fetching match data:', error);
            });
    }

    teamSelect.addEventListener('change', function () {
        const teamId = this.value;
        fetchMatches(teamId);
    });

    fetchMatches(teamSelect.value);
});
