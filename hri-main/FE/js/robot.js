//WEBSOCKET INIT
const ws = new WebSocket('ws://localhost:23456');

const LEVELS = {
    'BEGINNER': 0,
    'INTERMEDIATE': 1,
    'PRO': 2
}

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

//INIT
welcome_screen = document.getElementById("fullscreen-image")
want_play = document.getElementById("want-play")
initButton = document.getElementById("start")
initButton.addEventListener('click', () => {
    welcome_screen.style.display = 'none';
    want_play.style.display = 'block';

})

//WANT TO PLAY
loginContainer = document.getElementsByClassName('login-container')[0]

button_yes = document.getElementById("yes")
button_no = document.getElementById("no")
button_yes.addEventListener('click', () => {
    loginContainer.style.display = 'block';
    want_play.style.display = 'none';
    ws.send(JSON.stringify({play: true}))

})
button_no.addEventListener('click', () => {
    welcome_screen.style.display = 'flex';
    want_play.style.display = 'none';
    ws.send(JSON.stringify({play: false}))
})



//LOGIN
function getLevel(){
    var apiUrl = 'http://127.0.0.1:5000/api/getLevel';
    let username = sessionStorage.getItem('username');

    fetch(apiUrl, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
            username: username
        })//TODO change username
    })
    .then(response => response.json())
    .then(response => {
        console.log("level, ", response)
        //TODO make changes
        sessionStorage.setItem('level', response);
        
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

game_choose = document.getElementById("game-choose")
game = document.getElementById("game-container")
loginForm = document.getElementById('loginForm')

document.getElementById('loginForm').addEventListener('submit', async function(event) {
    event.preventDefault();

    var username = document.getElementById('username').value;
    sessionStorage.setItem('username', username);

    ws.send(JSON.stringify({username: username}))

    // getLevel()

    // loginContainer.style.display = 'none';
    // game_choose.style.display = 'block';
    
});


//CHANGE GAME
button_tris = document.getElementById("tris")
button_shoot = document.getElementById("shoot")
game_shoot_title = document.getElementById("game-shoot")

button_tris.addEventListener('click', () => {
    game.style.display = 'flex';
    game_choose.style.display = 'none';

    ws.send(JSON.stringify({game: 'tris'}))
})

button_shoot.addEventListener('click', () => {
    game_shoot_title.style.display = 'block';
    game_choose.style.display = 'none';

    ws.send(JSON.stringify({game: 'shoot'}))

})

//TRIS GAME
function initBoardGame(){
    return [null, null, null, null, null, null, null, null, null]
}

function setWinner(winner){
    undoButton.disabled = true;
    restartButton.disabled = true;
    closeButton.disabled = true;

    // Change button style
    undoButton.style.opacity = 0.5;
    restartButton.style.opacity = 0.5;
    closeButton.style.opacity = 0.5;

    var apiUrl = 'http://127.0.0.1:5000/api/setResultMatch';
    // Get item
    let username = sessionStorage.getItem('username');

    fetch(apiUrl, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
            username: username,
            winner: winner
        })//TODO change username
    })
    .then(response => response.json())
    .then(response => {
        undoButton.disabled = false;
        restartButton.disabled = false;
        closeButton.disabled = false;

        // Change button style
        undoButton.style.opacity = 1;
        restartButton.style.opacity = 1;
        closeButton.style.opacity = 1;
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

function checkLevel(){
    var apiUrl = 'http://127.0.0.1:5000/api/checkLevel';
    let username = sessionStorage.getItem('username');

    fetch(apiUrl, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
            username: username
        })//TODO change username
    })
    .then(response => response.json())
    .then(response => {
        let level = response['level']
        let change = response['change']
        
        //TODO make changes
        
        
        let curr_level = sessionStorage.getItem('level');
        sessionStorage.setItem('level', level);
        
        if(change == 'not_changed') return;

        if (LEVELS[curr_level] < LEVELS[level]) console.log('congrats, u leveled up')
        else console.log("not great, u leveled down")
        
    })
    .catch(error => {
        console.error('Error:', error);
    });
}



let boardGame = initBoardGame()

const winningCombinations = [
    [0, 1, 2], [3, 4, 5], [6, 7, 8], // Orizzontali
    [0, 3, 6], [1, 4, 7], [2, 5, 8], // Verticali
    [0, 4, 8], [2, 4, 6]            // Diagonali
];

const board = document.getElementById('tic-tac-toe-board');
const undoButton = document.getElementById('undo');
const restartButton = document.getElementById('restart');
const closeButton = document.getElementById('close');
// const game = document.getElementById("game-container")
// const loginContainer = document.getElementsByClassName('login-container')[0]

let moves = [];
let currentPlayer = 'O';
let gameActive = true;

// Inizializza la scacchiera
for (let i = 0; i < 9; i++) {
    let cell = document.createElement('div');
    cell.addEventListener('click', () => makeMove(cell, i));
    board.appendChild(cell);
}

function checkForWin() {
    for (let i = 0; i < winningCombinations.length; i++) {
        const [a, b, c] = winningCombinations[i];
        if (board.children[a].textContent && board.children[a].textContent === board.children[b].textContent && board.children[a].textContent === board.children[c].textContent) {
            gameActive = false;
            drawLine(i); // Funzione per disegnare la linea
            setWinner(board.children[a].textContent == 'X' ? 'AI' : 'HUMAN')
            return true;
        }
    }
    return false;
}

function checkForDraw() {
    console.log(boardGame)
    for (let i = 0; i < 9; i++){
        if (boardGame[i] == null) return;
    }

    setWinner('DRAW')
}

function drawLine(index) {
    let line = document.createElement('div');
    line.classList.add('line');
    if (index < 3) line.classList.add('horizontal');
    else if (index < 6) line.classList.add('vertical', );
    else line.classList.add('diagonal-' + (index === 6 ? 'down' : 'up'));
    line.style.display = 'block';
    if (index === 0) line.style.top = '50px';
    else if (index === 1) line.style.top = '155px';
    else if (index === 2) line.style.top = '260px';
    else if (index === 3) line.style.left = '50px';
    else if (index === 4) line.style.left = '155px';
    else if (index === 5) line.style.left = '260px';
    board.appendChild(line);
}

function makeMove(cell, index) {
    if (!gameActive || cell.textContent || moves.includes(index)) return;
    cell.textContent = currentPlayer;
    moves.push(index);
    boardGame[index] = currentPlayer

    var apiUrl = 'http://127.0.0.1:5000/api/makeMove';
    let username = sessionStorage.getItem('username')


    fetch(apiUrl, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ boardGame: boardGame, username: username})
    })
    .then(response => response.json())
    .then(async (data) => {
        if (checkForWin()) return;

        aiMove = data.aiMove;
        if (aiMove != null){
            board.children[aiMove].textContent = 'X';
            moves.push(aiMove);
            boardGame[aiMove] = 'X'
        }
        

        checkForWin()
        checkForDraw()

    })
    .catch(error => {
        console.error('Error:', error);
    });


    
}

undoButton.addEventListener('click', () => {
    if (moves.length === 0 || !gameActive) return;
    let lastMove = moves.pop();
    boardGame[lastMove] = null
    board.children[lastMove].textContent = '';

    lastMove = moves.pop();
    boardGame[lastMove] = null
    board.children[lastMove].textContent = '';

    // Rimuovi eventuali linee disegnate
    let line = board.querySelector('.line');
    if (line) line.remove();

    gameActive = true;

});

restartButton.addEventListener('click', () => {
    checkLevel()
    moves = [];
    boardGame = initBoardGame();
    gameActive = true;
    Array.from(board.children).forEach(cell => {
        if (cell.className !== 'line') cell.textContent = '';
    });
    currentPlayer = 'O';
    let line = board.querySelector('.line');
    if (line) line.remove();
});

closeButton.addEventListener('click', () => {
    boardGame = initBoardGame();
    moves = [];
    for (let i = 0; i < board.children.length; i++){
        board.children[i].textContent = '';
    }
    gameActive = true;
    document.getElementById('message').textContent = '';
    sessionStorage.removeItem('username');
    let line = board.querySelector('.line');
    if (line) line.remove();
    // game.style.display = 'none';
    // loginContainer.style.display = 'block';

    ws.send(JSON.stringify({winner: null}))
});


function handleChangePage(page){
    if(page == 'welcome'){
        game.style.display = 'none';
        loginContainer.style.display = 'none';
        game_choose.style.display = 'none';
        want_play.style.display = 'none';
        welcome_screen.style.display = 'flex';
        game_shoot_title.style.display = 'none';

    }else if(page == 'want_play'){
        game.style.display = 'none';
        loginContainer.style.display = 'none';
        game_choose.style.display = 'none';
        want_play.style.display = 'block';
        welcome_screen.style.display = 'none';
        game_shoot_title.style.display = 'none';

    }else if(page == 'login'){
        game.style.display = 'none';
        loginContainer.style.display = 'block';
        game_choose.style.display = 'none';
        want_play.style.display = 'none';
        welcome_screen.style.display = 'none';
        game_shoot_title.style.display = 'none';

    }else if(page == 'choose_game'){
        game.style.display = 'none';
        loginContainer.style.display = 'none';
        game_choose.style.display = 'block';
        want_play.style.display = 'none';
        welcome_screen.style.display = 'none';
        game_shoot_title.style.display = 'none';

    }else if(page == 'tris'){
        game.style.display = 'flex';
        loginContainer.style.display = 'none';
        game_choose.style.display = 'none';
        want_play.style.display = 'none';
        welcome_screen.style.display = 'none';
        game_shoot_title.style.display = 'none';
        
    }
}


//WEBSOCKET
ws.onmessage = function(event) {
    data = JSON.parse(event.data)
    console.log("message_received: ", data)
    if(data.action == 'change_page') handleChangePage(data.page)

};

ws.onopen = function() {
    console.log('WebSocket connection established');
    // ws.send(JSON.stringify({message: 'Hello server!'}));
};

ws.onerror = function(event) {
    console.error('WebSocket error: ', event);
};

ws.onclose = function(event) {
    console.log('WebSocket connection closed', event);
};