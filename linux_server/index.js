const CONFIG = {
    SERVER_PORT: 8080
};

import express from 'express';
import expressLayouts from 'express-ejs-layouts';
import bodyParser from 'body-parser';
import fetch from 'node-fetch';

const app = express();

app.set('view engine', 'ejs');
app.use(expressLayouts);
app.use(express.static('public'))
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));

/* Database Setup */

process.addListener('exit', (_) => {
    /* Cleanup code goes here */
});

app.get('/', (req, res) => {
    res.render('index', { 
        session: req.session
    });
});

app.get('/info/:param', (req, res) => {
    fetch('http://localhost:8081/info/' + req.params.param, {
        method: 'GET'
    })
    .then(response => response.text())
    .then(data => {
        res.send(data);
    })
    .catch(reason => res.send('Error: ' + reason)); 
});

app.listen(CONFIG.SERVER_PORT, () => console.log(`Serverul rulează la adresa http://localhost:${CONFIG.SERVER_PORT}`));