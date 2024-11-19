const net = require('net');

// Configura il server TCP
const port = 9001;
const host = 'localhost';

const server = net.createServer((socket) => {

  console.log('Client Python connesso');
  const response = JSON.stringify({ message: 'Messaggio ricevuto con successo' });
  socket.write(response);

  // Gestisci la disconnessione del client
  socket.on('end', () => {
    console.log('Client Python disconnesso');
  });
});

// Avvia il server TCP
server.listen(port, host, () => {
  console.log(`Server TCP in ascolto su ${host}:${port}`);
});
