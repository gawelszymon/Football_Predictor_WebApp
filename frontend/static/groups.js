document.addEventListener('DOMContentLoaded', function() {
    const groupsContainer = document.getElementById('groups-container');
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

            const groups = {};

            data.forEach(item => {
                if (!groups[item.group]) {
                    groups[item.group] = [];
                }
                groups[item.group].push({ team: item.team, points: item.points });
            });

            for (const group in groups) {
                groups[group].sort((a, b) => b.points - a.points);
            }

            for (const group in groups) {
                const groupDiv = document.createElement('div');
                groupDiv.classList.add('group');
                const groupTitle = document.createElement('h2');
                groupTitle.textContent = group;
                groupDiv.appendChild(groupTitle);

                const table = document.createElement('table');
                table.classList.add('group-table');

                const thead = document.createElement('thead');
                thead.innerHTML = `
                    <tr>
                        <th>Team</th>
                        <th>Points</th>
                    </tr>
                `;
                table.appendChild(thead);

                const tbody = document.createElement('tbody');
                groups[group].forEach(item => {
                    const row = document.createElement('tr');
                    row.innerHTML = `
                        <td><img src="/static/flags/${item.team.toLowerCase().replace(/\s/g, '')}.png" alt="${item.team}" class="flag-icon"> ${item.team}</td>
                        <td>${item.points}</td>
                    `;
                    tbody.appendChild(row);
                });

                table.appendChild(tbody);
                groupDiv.appendChild(table);
                groupsContainer.appendChild(groupDiv);
            }
        })
        .catch(error => {
            console.error('Error fetching data:', error);
            document.getElementById('result').textContent = 'Wystąpił błąd podczas ładowania danych o grupach.';
        });
});
