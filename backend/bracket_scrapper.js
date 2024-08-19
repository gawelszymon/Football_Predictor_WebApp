const axios = require('axios');
const cheerio = require('cheerio');

const url = 'https://pl.wikipedia.org/wiki/Mistrzostwa_Europy_w_Pi%C5%82ce_No%C5%BCnej_2024';
const fs = require('fs');

axios.get(url)
    .then(response => {
        const html = response.data;
        const $ = cheerio.load(html);

        const matchDetails = [];
        const matchResult = [];

        $('#mw-content-text > div.mw-content-ltr.mw-parser-output > div:nth-child(164) > table tbody tr td').each((index, element) => {
            const date = $(element).text().trim();

            if (date.includes('Hiszpania') || date.includes('Gruzja') || date.includes('Niemcy') || date.includes('Dania') || date.includes('Portugalia')
                || date.includes('Słowenia') || date.includes('Francja') || date.includes('Belgia') || date.includes('Rumunia') || date.includes('Holandia') 
                || date.includes('Austria') || date.includes('Turcja') || date.includes('Anglia') || date.includes('Słowacja') || date.includes('Szwajcaria')
                || date.includes('Włochy') || date.includes('Zwycięzca meczu 42') || date.includes('Zwycięzca meczu 41') || date.includes('Zwycięzca meczu 43')
                || date.includes('Zwycięzca meczu 44') || date.includes('Zwycięzca meczu 45') || date.includes('Zwycięzca meczu 46') || date.includes('Zwycięzca meczu 47')
                || date.includes('Zwycięzca meczu 48') || date.includes('Zwycięzca meczu 49') || date.includes('Zwycięzca meczu 50')) {
                matchDetails.push(date);
            }

        });

        $('td[rowspan="2"][style^="border:solid #aaa;border-width:"]').each((index, element) => {
            
            let date = $(element).text().trim();

            let penalties = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12'];
            let regex = /^0 \((\d+)\)$/;
            let match = date.match(regex);

            if (date === '0' || date === '1' || date === '2' || date === '3' || date === '4' || date === '5' ||
                date === '6' || date === '7' || date === '8' || date === '9' || date === '' || date === '' || date === 'B1' || date === 'F3' || 
                date === 'A1' || date === 'C2' || date === 'F1' || date === 'C3' ||
                date === 'D2' || date === 'E2' || date === 'E1' || date === 'D3' || date === 'D1' || date === 'F2' ||
                date === 'C1' || date === 'E3' || date === 'A2' || date === 'B2' || (match && penalties.includes(match[1]))) {

                if (date === '') {
                    date = 'lack_of_data';
                }

                matchResult.push(date);
            }

        });

        let teamBrackets = {};
        const hashBrackets = {};
        const resultBrackets = {}

        for (let i = 0; i < matchDetails.length; i++) {
            const a = `team_name_${i + 1}`;
            teamBrackets[a] = matchDetails[i];
        }

        let k = 1;
        for (let i = 0; i < matchResult.length; i = i+2) {
            const b = `team_hash_${k}`;
            hashBrackets[b] = matchResult[i];
            k++;
        }

        let j = 1;
        for (let i = 1; i < matchResult.length; i = i+2) {
            const b = `team_result_${j}`;
            resultBrackets[b] = matchResult[i];
            j++;
        }

        let one_eight_teamBrackets = JSON.parse(JSON.stringify(teamBrackets));
        delete one_eight_teamBrackets['team_name_3'];
        delete one_eight_teamBrackets['team_name_4'];
        delete one_eight_teamBrackets['team_name_7'];
        delete one_eight_teamBrackets['team_name_8'];
        delete one_eight_teamBrackets['team_name_11'];
        delete one_eight_teamBrackets['team_name_12'];
        delete one_eight_teamBrackets['team_name_15'];
        delete one_eight_teamBrackets['team_name_16'];
        delete one_eight_teamBrackets['team_name_19'];
        delete one_eight_teamBrackets['team_name_20'];
        delete one_eight_teamBrackets['team_name_23'];
        delete one_eight_teamBrackets['team_name_24'];
        delete one_eight_teamBrackets['team_name_27'];
        delete one_eight_teamBrackets['team_name_28'];

        let one_four_teamBrackets = JSON.parse(JSON.stringify(teamBrackets));
        delete one_four_teamBrackets['team_name_1'];
        delete one_four_teamBrackets['team_name_2'];
        delete one_four_teamBrackets['team_name_5'];
        delete one_four_teamBrackets['team_name_6'];
        delete one_four_teamBrackets['team_name_7'];
        delete one_four_teamBrackets['team_name_8'];
        delete one_four_teamBrackets['team_name_9'];
        delete one_four_teamBrackets['team_name_10'];
        delete one_four_teamBrackets['team_name_13'];
        delete one_four_teamBrackets['team_name_14'];
        delete one_four_teamBrackets['team_name_15'];
        delete one_four_teamBrackets['team_name_16'];
        delete one_four_teamBrackets['team_name_17'];
        delete one_four_teamBrackets['team_name_18'];
        delete one_four_teamBrackets['team_name_21'];
        delete one_four_teamBrackets['team_name_22'];
        delete one_four_teamBrackets['team_name_23'];
        delete one_four_teamBrackets['team_name_24'];
        delete one_four_teamBrackets['team_name_25'];
        delete one_four_teamBrackets['team_name_26'];
        delete one_four_teamBrackets['team_name_29'];
        delete one_four_teamBrackets['team_name_30'];


        let one_two_teamBrackets = JSON.parse(JSON.stringify(teamBrackets));
        for (let i in one_two_teamBrackets) {
            if (i !== "team_name_7" && i !== "team_name_8" && i !== "team_name_23" && i !== "team_name_24") {
                delete one_two_teamBrackets[i];
            }
        }

        let final_teamBrackets = JSON.parse(JSON.stringify(teamBrackets));
        for (let i in final_teamBrackets) {
            if (i !== "team_name_15" && i !== "team_name_16") {
                delete final_teamBrackets[i];
            }
        }

        let one_eight_Result = JSON.parse(JSON.stringify(resultBrackets));
        delete one_eight_Result['team_result_3'];
        delete one_eight_Result['team_result_4'];
        delete one_eight_Result['team_result_7'];
        delete one_eight_Result['team_result_8'];
        delete one_eight_Result['team_result_11'];
        delete one_eight_Result['team_result_12'];
        delete one_eight_Result['team_result_15'];
        delete one_eight_Result['team_result_16'];
        delete one_eight_Result['team_result_19'];
        delete one_eight_Result['team_result_20'];
        delete one_eight_Result['team_result_23'];
        delete one_eight_Result['team_result_24'];
        delete one_eight_Result['team_result_27'];
        delete one_eight_Result['team_result_28'];

        let one_four_Result = JSON.parse(JSON.stringify(resultBrackets));
        delete one_four_Result['team_result_1'];
        delete one_four_Result['team_result_2'];
        delete one_four_Result['team_result_5'];
        delete one_four_Result['team_result_6'];
        delete one_four_Result['team_result_7'];
        delete one_four_Result['team_result_8'];
        delete one_four_Result['team_result_9'];
        delete one_four_Result['team_result_10'];
        delete one_four_Result['team_result_13'];
        delete one_four_Result['team_result_14'];
        delete one_four_Result['team_result_15'];
        delete one_four_Result['team_result_16'];
        delete one_four_Result['team_result_17'];
        delete one_four_Result['team_result_18'];
        delete one_four_Result['team_result_21'];
        delete one_four_Result['team_result_22'];
        delete one_four_Result['team_result_23'];
        delete one_four_Result['team_result_24'];
        delete one_four_Result['team_result_25'];
        delete one_four_Result['team_result_26'];
        delete one_four_Result['team_result_29'];
        delete one_four_Result['team_result_30'];

        let one_two_Result = JSON.parse(JSON.stringify(resultBrackets));
        for (let i in one_two_Result) {
            if (i !== "team_result_7" && i !== "team_result_8" && i !== "team_result_23" && i !== "team_result_24") {
                delete one_two_Result[i];
            }
        }

        let final_Result = JSON.parse(JSON.stringify(resultBrackets));
        for (let i in final_Result) {
            if (i !== "team_result_15" && i !== "team_result_16") {
                delete final_Result[i];
            }
        }

        //console.log(one_eight_Result);

        //console.log(Object.values(teamBrackets)[0])

        fs.writeFile('frontend/static/one_eight_teamBrackets.json', JSON.stringify(one_eight_teamBrackets, null, 2), err => {
            if (err) throw err;
            console.log('Json data saved');
        });

        fs.writeFile('frontend/static/one_four_teamBrackets.json', JSON.stringify(one_four_teamBrackets, null, 2), err => {
            if (err) throw err;
            console.log('Json data saved');
        });

        fs.writeFile('frontend/static/one_two_teamBrackets.json', JSON.stringify(one_two_teamBrackets, null, 2), err => {
            if (err) throw err;
            console.log('Json data saved');
        });

        fs.writeFile('frontend/static/final_teamBrackets.json', JSON.stringify(final_teamBrackets, null, 2), err => {
            if (err) throw err;
            console.log('Json data saved');
        });

        fs.writeFile('frontend/static/one_eight_resultBrackets.json', JSON.stringify(one_eight_Result, null, 2), err => {
            if (err) throw err;
            console.log('Json data saved');
        });

        fs.writeFile('frontend/static/one_four_resultBrackets.json', JSON.stringify(one_four_Result, null, 2), err => {
            if (err) throw err;
            console.log('Json data saved');
        });

        fs.writeFile('frontend/static/one_two_resultBrackets.json', JSON.stringify(one_two_Result, null, 2), err => {
            if (err) throw err;
            console.log('Json data saved');
        });

        fs.writeFile('frontend/static/final_resultBrackets.json', JSON.stringify(final_Result, null, 2), err => {
            if (err) throw err;
            console.log('Json data saved');
        });
    })
    .catch(error => {
        console.error('Error fetching the webpage:', error);
    });