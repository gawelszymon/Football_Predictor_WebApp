const axios = require('axios');
const cheerio = require('cheerio');

const url = 'https://pl.wikipedia.org/wiki/Mistrzostwa_Europy_w_Pi%C5%82ce_No%C5%BCnej_2024';

axios.get(url)
    .then(response => {
        const html = response.data;
        const $ = cheerio.load(html);

        const matchDetails = [];
        const matchResult = [];

        // Zmodyfikowany selektor CSS, aby odnosił się do konkretnej tabeli
        $('#mw-content-text > div.mw-content-ltr.mw-parser-output > div:nth-child(164) > table tbody tr td').each((index, element) => {
            // Tutaj możesz przetwarzać elementy wewnątrz wskazanej tabeli
            const date = $(element).text().trim();
            //const teams = $(element).find('td').eq(1).text().trim();

            // Przykład dodania danych do tablicy matchDetails
            if (date.includes('Hiszpania') || date.includes('Gruzja') || date.includes('Niemcy') || date.includes('Dania') || date.includes('Portugalia')
                || date.includes('Słowenia') || date.includes('Francja') || date.includes('Belgia') || date.includes('Rumunia') || date.includes('Holandia') 
                || date.includes('Austria') || date.includes('Turcja') || date.includes('Anglia') || date.includes('Słowacja') || date.includes('Szwajcaria')
                || date.includes('Włochy') || date.includes('Zwycięzca meczu 42') || date.includes('Zwycięzca meczu 41') || date.includes('Zwycięzca meczu 43')
                || date.includes('Zwycięzca meczu 44') || date.includes('Zwycięzca meczu 45') || date.includes('Zwycięzca meczu 46') || date.includes('Zwycięzca meczu 47')
                || date.includes('Zwycięzca meczu 48') || date.includes('Zwycięzca meczu 49') || date.includes('Zwycięzca meczu 50')) {
                matchDetails.push(date);
            }

        });

        $('td[rowspan="2"]').each((index, element) => {
            // Tutaj możesz przetwarzać elementy wewnątrz wskazanej tabeli
            let date = $(element).text().trim();

            if (date === '0' || date === '1' || date === '2' || date === '3' || date === '4' || date === '5' ||
                date === '6' || date === '7' || date === '8' || date === '9' || date === '' || date === '' || date === 'B1' || date === 'F3' || 
                date === 'A1' || date === 'C2' || date === 'F1' || date === 'C3' ||
                date === 'D2' || date === 'E2' || date === 'E1' || date === 'D3' || date === 'D1' || date === 'F2' ||
                date === 'C1' || date === 'E3' || date === 'A2' || date === 'B2') {

                if (date === '') {
                    date = 'nwm';
                }

                matchResult.push(date);
            }

        });

        const matchesBrackets = {};
        const resultsBrackets = {};

        for (let i = 0; i < matchDetails.length; i++) {
            const a = `team${i + 1}`;
            matchesBrackets[a] = matchDetails[i];
        }

        for (let i = 0; i < matchResult.length; i = i+1) {
            const b = `result${i + 1}`;
            resultsBrackets[b] = matchResult[i];
        }
        
        delete resultsBrackets['result17'];
        delete resultsBrackets['result34'];
        delete resultsBrackets['result47'];
        delete resultsBrackets['result64'];


        console.log(matchesBrackets);
        console.log(resultsBrackets);
    })
    .catch(error => {
        console.error('Error fetching the webpage:', error);
    });
