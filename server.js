const express = require('express');
const path = require('path');
const fs = require('fs');
const net = require('net');

const app = express();
const PORT = 3000;

// Middleware to parse JSON and serve static files
app.use(express.json());
app.use(express.static(path.join(__dirname, 'web_interfaces/public')));

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

    const users = JSON.parse(fs.readFileSync(USERS_FILE, 'utf8'));

    let user = users.find((user) => user.name === name);

    if (!user) {
        user = { name, last: 0, avg: 0 };
        users.push(user);
        fs.writeFileSync(USERS_FILE, JSON.stringify(users, null, 2));
        return res.json({ exists: false });
    }

    res.json({ exists: true, message: `Il tuo nickname "${name}" è già registrato. Confermi di essere tu?` });
});

// User wants to do exercises
app.post('/api/exercise', (req, res) => {
    const message = JSON.stringify({ type: 'exercise', message: "Let's do some exercises" });

    tcpClient.write(message, (err) => {
        if (err) {
            console.error('Error sending message to TCP server:', err);
            return res.status(500).json({ error: 'Failed to notify TCP server' });
        }
        console.log('Exercise message sent to TCP server:', message);
    });

    res.json({ message: "Let's do some exercises" });
});

// Interact with user according to actions on screen
app.post('/api/say', (req, res) => {
    const { message } = req.body;

    if (!message || typeof message !== 'string') {
        return res.status(400).json({ error: 'Invalid message' });
    }

    const tcpMessage = JSON.stringify({ type: 'say', message });

    tcpClient.write(tcpMessage, (err) => {
        if (err) {
            console.error("Error sending 'say' message to TCP server:", err);
            return res.status(500).json({ error: 'Failed to notify TCP server' });
        }
        console.log('Say message sent to TCP server:', tcpMessage);
    });

    res.json({ message: 'Message sent to TCP server successfully' });
});

// TCP Client Configuration
const TCP_PORT = 9001;
const TCP_HOST = 'localhost';

const tcpClient = new net.Socket();

function connectToTCPServer() {
    tcpClient.connect(TCP_PORT, TCP_HOST, () => {
        console.log(`Connected to TCP server at ${TCP_HOST}:${TCP_PORT}`);
    });
}

tcpClient.on('error', (err) => {
    console.error('Error in TCP client:', err);
    setTimeout(connectToTCPServer, 1000); // Retry after 1 second
});

tcpClient.on('close', () => {
    console.log('Disconnected from TCP server');
});

tcpClient.on('data', (data) => {
    console.log('Message from TCP server:', data.toString());
});

// Cleanup on exit
process.on('SIGINT', () => {
    console.log("Shutting down Node.js server...");
    tcpClient.destroy(); // Close TCP client
    process.exit();
});

// Start connection and Express server
connectToTCPServer();

const server = app.listen(PORT, () => {
    console.log(`Express server is running at http://localhost:${PORT}`);
});

// Close Express server on exit
process.on('SIGINT', () => {
    server.close(() => {
        console.log('Express server closed');
    });
});

/*

const express = require('express');
const path = require('path');
const fs = require('fs');

const app = express();
const PORT = 3000;

// Middleware to parse JSON and serve static files
app.use(express.json());
app.use(express.static(path.join(__dirname, 'web_interfaces/public')));

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
        // If user doesn't exist, create a new one
        user = { name, last: 0, avg: 0 };
        users.push(user);
        fs.writeFileSync(USERS_FILE, JSON.stringify(users, null, 2));
        return res.json({ exists: false });
    }

    // If user exists, send a confirmation message
    res.json({ exists: true, message: `Il tuo nickname "${name}" è già registrato. Confermi di essere t?` });
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