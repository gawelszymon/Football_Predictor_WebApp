document.addEventListener("DOMContentLoaded", function () {
    const teamBrackets = {
        roundOf16: [],
        quarterFinals: [],
        semiFinals: [],
        final: []
    };

    const resultBrackets = {
        roundOf16: [1, 3, 5, 7, 9, 11, 13, 15],
        quarterFinals: [1, 3, 5, 7],
        semiFinals: [1, 3],
        final: [1]
    };

    const teamFlags = {
        'Polska': {name: 'Poland', flag: 'Poland.png'},
        'Niemcy': {name: 'Germany', flag: 'Germany.png'},
        'Hiszpania': {name: 'Spain', flag: 'Spain.png'},
        'Francja': {name: 'France', flag: 'France.png'},
        'Włochy': {name: 'Italy', flag: 'Italy.png'},
        'Szwajcaria': {name: 'Switzerland', flag: 'Switzerland.png'},
        'Słowacja': {name: 'Slovakia', flag: 'Slovakia.png'},
        'Anglia': {name: 'England', flag: 'England.png'},
        'Turcja': {name: 'Turkey', flag: 'Turkey.png'},
        'Austria': {name: 'Austria', flag: 'Austria.png'},
        'Holandia': {name: 'Netherlands', flag: 'Netherlands.png'},
        'Rumunia': {name: 'Romania', flag: 'Romania.png'},
        'Belgia': {name: 'Belgium', flag: 'Belgium.png'},
        'Słowenia': {name: 'Slovenia', flag: 'Slovenia.png'},
        'Portugalia': {name: 'Portugal', flag: 'Portugal.png'},
        'Dania': {name: 'Denmark', flag: 'Denmark.png'},
        'Gruzja': {name: 'Georgia', flag: 'Georgia.png'},
        // Add any other mappings if needed...
    };

    function cleanName(name) {
        return name.replace(/\*/g, '').trim();
    }

    function getEnglishName(team) {
        const cleanedName = cleanName(team);
        return teamFlags[cleanedName] ? teamFlags[cleanedName].name : cleanedName;
    }

    function getPlaceholderText(matchNumber) {
        return `Winner of Match ${matchNumber}`;
    }

    function addMatches(roundId, teams, results) {
        const roundDiv = document.getElementById(roundId);
        teams.forEach((match, index) => {
            const matchDiv = document.createElement('div');
            matchDiv.className = 'match';

            const team1Name = match[0] ? getEnglishName(match[0]) : getPlaceholderText(results[index] * 2 - 1);
            const team2Name = match[1] ? getEnglishName(match[1]) : getPlaceholderText(results[index] * 2);

            const team1Flag = teamFlags[cleanName(match[0])] ? `<img src="static/flags/${teamFlags[cleanName(match[0])].flag}" alt="${team1Name} flag">` : '';
            const team2Flag = teamFlags[cleanName(match[1])] ? `<img src="static/flags/${teamFlags[cleanName(match[1])].flag}" alt="${team2Name} flag">` : '';

            matchDiv.innerHTML = `
                <div>${team1Flag} ${team1Name}</div>
                <div>${team2Flag} ${team2Name}</div>
            `;
            roundDiv.appendChild(matchDiv);
        });
    }

    fetch('static/final_teamBrackets.json')
        .then(response => response.json())
        .then(data => {
            console.log(data);
            teamBrackets.final = [
                [data.team_name_15, data.team_name_16]
            ];
            addMatches('final', teamBrackets.final, resultBrackets.final);
        })
        .catch(error => console.error('Error loading team names:', error));

    fetch('/static/one_eight_teamBrackets.json')
        .then(response => response.json())
        .then(data => {
            console.log(data);
            teamBrackets.roundOf16 = [
                [data.team_name_1, data.team_name_2],
                [data.team_name_5, data.team_name_6],
                [data.team_name_9, data.team_name_10],
                [data.team_name_13, data.team_name_14],
                [data.team_name_17, data.team_name_18],
                [data.team_name_21, data.team_name_22],
                [data.team_name_25, data.team_name_26],
                [data.team_name_29, data.team_name_30]
            ];
            addMatches('round-of-16', teamBrackets.roundOf16, resultBrackets.roundOf16);
        })
        .catch(error => console.error('Error loading team names:', error));

    fetch('static/one_four_teamBrackets.json')
        .then(response => response.json())
        .then(data => {
            console.log(data);
            teamBrackets.quarterFinals = [
                [data.team_name_3, data.team_name_4],
                [data.team_name_11, data.team_name_12],
                [data.team_name_19, data.team_name_20],
                [data.team_name_27, data.team_name_28]
            ];
            addMatches('quarter-finals', teamBrackets.quarterFinals, resultBrackets.quarterFinals);
        })
        .catch(error => console.error('Error loading team names:', error));

    fetch('static/one_two_teamBrackets.json')
        .then(response => response.json())
        .then(data => {
            console.log(data);
            teamBrackets.semiFinals = [
                [data.team_name_7, data.team_name_8],
                [data.team_name_23, data.team_name_24]
            ];
            addMatches('semi-finals', teamBrackets.semiFinals, resultBrackets.semiFinals);
        })
        .catch(error => console.error('Error loading team names:', error));
});
