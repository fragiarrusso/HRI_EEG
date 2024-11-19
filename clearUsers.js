const fs = require('fs');

// Percorso del file JSON
const filePath = './users.json';

// Funzione per pulire il file JSON
function clearUsers() {
    // Svuota l'array e salva nel file JSON
    fs.writeFileSync(filePath, JSON.stringify([], null, 2), 'utf-8');
    console.log('Il database degli utenti è stato pulito.');
}

// Esegui la funzione
clearUsers();
