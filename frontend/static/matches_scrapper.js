const axios = require('axios');
const cheerio = require('cheerio');

const url = 'https://pl.wikipedia.org/wiki/Mistrzostwa_Europy_w_Pi%C5%82ce_No%C5%BCnej_2024';

axios.get(url)
    .then(response => {
        const html = response.data;
        const $ = cheerio.load(html);

        const matchDetails = [];

        $('table.mecz-pilkarski tbody tr').each((index, element) => {
            const date = $(element).find('td').eq(0).text().trim();
            const team1 = $(element).find('td').eq(1).text().trim();
            const score = $(element).find('td').eq(2).text().trim();
            const team2 = $(element).find('td').eq(3).text().trim();
            const location = $(element).find('td').eq(4).text().trim();

            matchDetails.push({ date, team1, score, team2, location });
        });

        console.log(matchDetails);
    })
    .catch(error => {
        console.error('Error fetching the webpage:', error);
    });