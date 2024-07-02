//TODO

document.addEventListener("DOMContentLoaded", async function () {

    // Function to fetch JSON data
    async function fetchJSON(file) {
        const response = await fetch(`/backend/${file}`);
        return await response.json();
    }

    // Load all the necessary JSON files
    const one_eight_teamBrackets = await fetchJSON('one_eight_resultBrackets.json');
    const one_eight_resultBrackets = await fetchJSON('one_eight_resultBracket.json');
    const one_four_teamBrackets = await fetchJSON('one_four_teamBrackets.json');
    const one_four_resultBrackets = await fetchJSON('one_four_resultBracket.json');
    const one_two_teamBrackets = await fetchJSON('one_two_teamBrackets.json');
    const one_two_resultBrackets = await fetchJSON('one_two_resultBracket.json');
    const final_teamBrackets = await fetchJSON('final_teamBrackets.json');
    const final_resultBrackets = await fetchJSON('final_resultBracket.json');

    // Function to add matches to the DOM
    function addMatches(roundId, teams, results) {
        const roundDiv = document.getElementById(roundId);
        roundDiv.innerHTML = '';  // Clear previous matches
        teams.forEach((match, index) => {
            const matchDiv = document.createElement('div');
            matchDiv.className = 'match';
            matchDiv.innerHTML = `
                <div>${match[0]} ${results[index] === 0 ? '(Winner)' : ''}</div>
                <div>${match[1]} ${results[index] === 1 ? '(Winner)' : ''}</div>
            `;
            roundDiv.appendChild(matchDiv);
        });
    }

    // Add matches to each round
    addMatches('round-of-16', one_eight_teamBrackets, one_eight_resultBrackets);
    addMatches('quarter-finals', one_four_teamBrackets, one_four_resultBrackets);
    addMatches('semi-finals', one_two_teamBrackets, one_two_resultBrackets);
    addMatches('final', final_teamBrackets, final_resultBrackets);
});
