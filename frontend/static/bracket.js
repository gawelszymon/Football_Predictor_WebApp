document.addEventListener("DOMContentLoaded", function () {
    const teamBrackets = {
        roundOf16: [

        ],
        quarterFinals: [

        ],
        semiFinals: [

        ],
        final: [
            
        ]
    };

    const resultBrackets = {
        roundOf16: [1, 3, 5, 7, 9, 11, 13, 15],
        quarterFinals: [1, 3, 5, 7],
        semiFinals: [1, 3],
        final: [1]
    };

    function addMatches(roundId, teams, results) {
        const roundDiv = document.getElementById(roundId);
        teams.forEach((match, index) => {
            const matchDiv = document.createElement('div');
            matchDiv.className = 'match';
            matchDiv.innerHTML = `
                <div>${match[0]} ${results[index] === 0 ? '' : ''}</div>
                <div>${match[1]} ${results[index] === 1 ? '' : ''}</div>
            `;
            roundDiv.appendChild(matchDiv);
        });
    }

    fetch('static/final_teamBrackets.json')
        .then(response => response.json())
        .then(data => {

            console.log(data);
            // Zaktualizuj dane w teamBrackets.final na podstawie danych z JSON
            teamBrackets.final = [
                [data.team_name_15 + '<br><br>', data.team_name_16]
            ];

            addMatches('final', teamBrackets.final, resultBrackets.final);
        })
        .catch(error => console.error('Error loading team names:', error));


    fetch('/static/one_eight_teamBrackets.json')
        .then(response => response.json())
        .then(data => {

            console.log(data);

            teamBrackets.roundOf16 = [
                [data.team_name_1 + '<br><br>', data.team_name_2],
                [data.team_name_5 + '<br><br>', data.team_name_6],
                [data.team_name_9 + '', data.team_name_10],
                [data.team_name_13 + '<br><br>', data.team_name_14],
                [data.team_name_17 + '<br><br>', data.team_name_18],
                [data.team_name_21 + '<br><br>', data.team_name_22],
                [data.team_name_25 + '<br><br>', data.team_name_26],
                [data.team_name_29 + '<br><br>', data.team_name_30]
            ]

            addMatches('round-of-16', teamBrackets.roundOf16, resultBrackets.roundOf16);
        })
        .catch(error => console.error('Error loading team names:', error));

    fetch('static/one_four_teamBrackets.json')
        .then(response => response.json())
        .then(data => {

            console.log(data);

            teamBrackets.quarterFinals = [
                [data.team_name_3 + '<br><br>', data.team_name_4],
                [data.team_name_11 + '<br><br>', data.team_name_12],
                [data.team_name_19 + '<br><br>', data.team_name_20],
                [data.team_name_27 + '<br><br>', data.team_name_28]
            ];

            addMatches('quarter-finals', teamBrackets.quarterFinals, resultBrackets.quarterFinals);
        })
        .catch(error => console.error('Error loading team names:', error));

    fetch('static/one_two_teamBrackets.json')
        .then(response => response.json())
        .then(data => {

            console.log(data);

            teamBrackets.semiFinals = [
                [data.team_name_7 + '<br><br>', data.team_name_8],
                [data.team_name_23 + '<br><br>', data.team_name_24]
            ];

            addMatches('semi-finals', teamBrackets.semiFinals, resultBrackets.semiFinals);
        })
        .catch(error => console.error('Error loading team names:', error));
        
});
