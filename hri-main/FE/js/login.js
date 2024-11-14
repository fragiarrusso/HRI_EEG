function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}


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

game = document.getElementById("game-container")
loginContainer = document.getElementsByClassName('login-container')[0]
loginForm = document.getElementById('loginForm')

document.getElementById('loginForm').addEventListener('submit', async function(event) {
    event.preventDefault();

    var username = document.getElementById('username').value;
    var apiUrl = 'http://127.0.0.1:5000/api/loginUser';

    fetch(apiUrl, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ username: username })
    })
    .then(response => response.json())
    .then(async (data) => {
        getLevel()
        console.log("ok")
        document.getElementById('message').textContent = data.message;
        document.getElementById('message').style.color = 'red';

        // Set item
        sessionStorage.setItem('username', username);

        // // Remove item
        


        await sleep(1000)

        loginContainer.style.display = 'none';
        game.style.display = 'flex';
    })
    .catch(error => {
        console.error('Error:', error);
    });
});