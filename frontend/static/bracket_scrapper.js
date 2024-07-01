const axios = require('axios');
const cheerio = require('cheerio');

const url = 'https://pl.wikipedia.org/wiki/Mistrzostwa_Europy_w_Pi%C5%82ce_No%C5%BCnej_2024';

axios.get(url)
    .then(response => {
        const html = response.data;
        const $ = cheerio.load(html);

        const matchDetails = [];

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

        const brackets = {};

        for (let i = 0; i < matchDetails.length; i++) {
            const variableName = `team${i + 1}`;
            brackets[variableName] = matchDetails[i];
        }

        console.log(brackets);
    })
    .catch(error => {
        console.error('Error fetching the webpage:', error);
    });
