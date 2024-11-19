const express = require('express');
const path = require('path');
const fs = require('fs');

const app = express();
const PORT = 3000;

// Middleware to parse JSON and serve static files
app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

// File to store user data
const USERS_FILE = path.join(__dirname, 'users.json');

// Check if users.json exists, if not create it
if (!fs.existsSync(USERS_FILE)) {
    fs.writeFileSync(USERS_FILE, JSON.stringify([]));
}

// Route to handle user submission
app.post('/api/submit-name', (req, res) => {
    const { name } = req.body;

    if (!name || typeof name !== 'string') {
        return res.status(400).json({ error: 'Invalid name' });
    }

    // Read existing users
    const users = JSON.parse(fs.readFileSync(USERS_FILE, 'utf8'));

    // Check if user exists
    let user = users.find((user) => user.name === name);

    if (!user) {
        // Create new user
        user = { name, last: 0, avg: 0 };
        users.push(user);
        fs.writeFileSync(USERS_FILE, JSON.stringify(users, null, 2));
        return res.json({ exists: false });
    }

    // User exists
    res.json({ exists: true });
});

// Dummy route for the left button action
app.post('/api/left-button', (req, res) => {
    res.json({ message: 'Left button action triggered!' });
});

// Start the server
app.listen(PORT, () => {
    console.log(`Server is running at http://localhost:${PORT}`);
});


/*
    const net = require('net');

    // Configura il server TCP
    const port = 9001;
    const host = 'localhost';
    
    // Crea un nuovo client TCP per connettersi al client Python
    const server = net.createServer((socket) => { 
       console.log('Client Python connesso');
       const responde = JSON.stringify({message: 'Messaggio ricevuto con successo' });
       socket.write(response);
       // Gestisci la disconnessione del client
       socket.on('end', () => {
             console.log('Client Python disconnesso');
       });
    });
    
    // Avvia il server TCP
    server.listen(port,host, () => {
        console.log('Server TCP in ascolto su $(host):$(port}')
    });
  */