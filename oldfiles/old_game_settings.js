/*document.addEventListener("DOMContentLoaded", () => {
    
    
    // Difficulty Settings for Levels 1 to 5
    const difficultySettings = {
        1: { gameSpeed: 1.5, obstacleFrequency: 0.03, minObstacleGap: 2500 },
        2: { gameSpeed: 2.5, obstacleFrequency: 0.1, minObstacleGap: 2300 },
        3: { gameSpeed: 3.5, obstacleFrequency: 0.2, minObstacleGap: 2100 },
        4: { gameSpeed: 4.5, obstacleFrequency: 0.3, minObstacleGap: 1900 },
        5: { gameSpeed: 5.5, obstacleFrequency: 0.4, minObstacleGap: 1700 },
    };

    // Global variables
    let connectionOn = false;
    let userLast = 0;
    let userAverage = 0;
    let userLastLevel = 1;
    let previousGamesCount = 0;

    let stressValues = [];
    let workloadValues = [];
    let stressSum = 0;
    let stressCount = 0;
    let stressAverage = 0;
    let workloadAverage = 0;
    const rollingWindowSize = 10;

    let currentDifficulty = 1; // Will be set after fetching user data
    let gameSpeed = difficultySettings[currentDifficulty].gameSpeed;
    let obstacleFrequency = difficultySettings[currentDifficulty].obstacleFrequency;
    let minObstacleGap = difficultySettings[currentDifficulty].minObstacleGap;


    let user_data = {}
    let gameStressAverage = 0;
    // DOM Elements
    const gameContainer = document.getElementById("gameContainer");
    const player = document.getElementById("player");
    const scoreDisplay = document.getElementById("score");
    const difficultyDisplay = document.getElementById("difficulty");
    const gameOverModal = document.getElementById("gameOverModal");
    const gameoverButton = document.getElementById('gameOverButton');
    const arrowButton = document.getElementById('arrowButton');
    

    let obstacles = [];
    let isJumping = false;
    let jumpHeight = 0;
    let score = 0;
    let gracePeriodActive = false;
    let lastObstacleSpawnTime = Date.now();

    // Fetch user data from the server at game start
    fetch('/api/user_data')
        .then(response => response.json())
        .then(data => {
            userLast = data.last;
            userAverage = data.avg;
            userLastLevel = data.last_level;
            previousGamesCount = data.games_played || 0;

            // Set currentDifficulty to user's last_level
            currentDifficulty = userLastLevel;
            if (currentDifficulty > 5) currentDifficulty = 5;
            if (currentDifficulty < 1) currentDifficulty = 1;

            const settings = difficultySettings[currentDifficulty];
            gameSpeed = settings.gameSpeed;
            obstacleFrequency = settings.obstacleFrequency;
            minObstacleGap = settings.minObstacleGap;
            difficultyDisplay.innerText = `Difficulty Level: ${currentDifficulty}`;
            console.log(`Set initial difficulty to level ${currentDifficulty}`);
        })
        .catch(error => {
            console.error('Error fetching user data:', error);
            // If error, set defaults
            currentDifficulty = 1;
            const settings = difficultySettings[currentDifficulty];
            gameSpeed = settings.gameSpeed;
            obstacleFrequency = settings.obstacleFrequency;
            minObstacleGap = settings.minObstacleGap;
            difficultyDisplay.innerText = `Difficulty Level: ${currentDifficulty}`;
        });

    // Grace Period Timer
    function startGracePeriod(duration) {
        gracePeriodActive = true;
        setTimeout(() => {
            gracePeriodActive = false;
        }, duration);
    }

    // Update Difficulty Function
    function updateDifficulty(level, applyGrace = false) {
        if (level > 5) level = 5;
        if (level < 1) level = 1;

        const settings = difficultySettings[level];
        gameSpeed = settings.gameSpeed;
        obstacleFrequency = settings.obstacleFrequency;
        minObstacleGap = settings.minObstacleGap;
        currentDifficulty = level;
        difficultyDisplay.innerText = `Difficulty Level: ${currentDifficulty}`;
        console.log(`Updated to difficulty level ${currentDifficulty}`);

        if (applyGrace) {
            startGracePeriod(200); // Apply grace period for difficulty change
        }
    }

    // Check connection status and fetch rolling averages every 5 seconds
    setInterval(() => {
        fetch('/api/connection_status')
            .then(response => response.json())
            .then(data => {
                connectionOn = data.status === 'connected';
                if (connectionOn) {
                    // Fetch rolling averages
                    fetch('/api/rolling_averages')
                        .then(response => response.json())
                        .then(data => {
                            let workload = parseFloat(data.rolling_avg_workload);
                            let stress = parseFloat(data.rolling_avg_stress);

                            if (!isNaN(workload) && !isNaN(stress)) {
                                workloadValues.push(workload);
                                stressValues.push(stress);

                                // Keep only the latest rollingWindowSize values
                                if (stressValues.length > rollingWindowSize) stressValues.shift();
                                if (workloadValues.length > rollingWindowSize) workloadValues.shift();

                                // Update stress sum and count
                                stressSum += stress;
                                stressCount++;

                                // Compute current averages
                                stressAverage = stressValues.reduce((a, b) => a + b, 0) / stressValues.length;
                                workloadAverage = workloadValues.reduce((a, b) => a + b, 0) / workloadValues.length;

                                console.log(`Stress avg: ${stressAverage.toFixed(2)}, Workload avg: ${workloadAverage.toFixed(2)}`);
                            }
                        })
                        .catch(error => {
                            console.error('Error fetching rolling averages:', error);
                        });
                }
            })
            .catch(error => {
                console.error('Error checking connection status:', error);
                connectionOn = false;
            });
    }, 5000); // Every 5 seconds

    // Adjust difficulty every 15 seconds
    setInterval(() => {
        if (connectionOn) {
            // Check if we have enough data
            if (stressValues.length > 0 && workloadValues.length > 0) {
                //let sumStressWorkload = stressValues[-1]+ workloadValues[-1];
                let currentStressAverage = stressAverage;

                console.log(`Sum of stress and workload: ${sumStressWorkload.toFixed(2)}`);

                if (stressValues[-1]+ workloadValues[-1] < 7){// &&  userAverage*1.5 <= currentStressAverage ) { //da cambiare
                    // Increase difficulty by 1 (max 5)
                    if (currentDifficulty < 5) {
                        updateDifficulty(currentDifficulty + 1, true);
                    }
                } else if (stressValues[-1]+ workloadValues[-1] >= 7 && currentStressAverage * 1.7 <= userAverage) {
                    // Keep difficulty the same
                    console.log('Keeping difficulty the same');
                } else {
                    // Decrease difficulty by 1 (min 1)
                    if (currentDifficulty > 1) {
                        updateDifficulty(currentDifficulty - 1, true);
                    }
                }
            }
        } else {
            // Connection is off, increase difficulty by 1 (up to max level 5)
            if (currentDifficulty < 5) {
                updateDifficulty(currentDifficulty + 1, true);
            }
        }
    }, 15000); // Every 15 seconds

    // Jump Logic
    function jump() {
        if (isJumping) return;
        isJumping = true;

        let jumpInterval = setInterval(() => {
            if (jumpHeight >= 130) {
                clearInterval(jumpInterval);
                let fallInterval = setInterval(() => {
                    if (jumpHeight <= 0) {
                        clearInterval(fallInterval);
                        isJumping = false;
                    }
                    jumpHeight -= 5;
                    player.style.bottom = jumpHeight + "px";
                }, 20);
            }
            jumpHeight += 5;
            player.style.bottom = jumpHeight + "px";
        }, 20);
    }

    // Spawn Obstacles with Proper Spacing
    function spawnObstacle() {
        if (gracePeriodActive) return; // Do not spawn obstacles during grace periods

        // Ensure proper spacing between obstacles
        const lastObstacle = obstacles[obstacles.length - 1];
        const currentTime = Date.now();

        // Adjusted condition to avoid overly tight gaps
        if (lastObstacle && currentTime - lastObstacleSpawnTime < minObstacleGap) return;

        // Create and spawn a new obstacle
        const obstacle = document.createElement("div");
        obstacle.classList.add("obstacle");
        obstacle.style.right = "0px";
        gameContainer.appendChild(obstacle);
        obstacles.push(obstacle);
        lastObstacleSpawnTime = currentTime; // Update last spawn time
    }

    // Move Obstacles and Check Collisions
    function moveObstacles() {
        obstacles.forEach((obstacle, index) => {
            let obstacleRight = parseInt(window.getComputedStyle(obstacle).right);
            obstacle.style.right = obstacleRight + gameSpeed + "px";

            let obstacleRect = obstacle.getBoundingClientRect();
            let playerRect = player.getBoundingClientRect();

            if (
                playerRect.left < obstacleRect.right &&
                playerRect.right > obstacleRect.left &&
                playerRect.bottom > obstacleRect.top
            ) {
                endGame();
            }

            if (obstacleRight > gameContainer.offsetWidth) {
                obstacles.shift();
                obstacle.remove();
                score++;
                scoreDisplay.innerText = `Score: ${score}`;
            }
        });

        if (Math.random() < obstacleFrequency) spawnObstacle();
    }

    // End Game and Reset
    function endGame() {
        // Calculate average stress during the game
        let gameStressAverage = stressSum / stressCount || 0;

        // Update previousGamesCount
        previousGamesCount++;

        // Prepare data to send to server
        const userData = {
            last: gameStressAverage,
            avg: ((userAverage * (previousGamesCount - 1)) + gameStressAverage) / previousGamesCount,
            last_level: currentDifficulty,
            games_played: previousGamesCount
        };

        // Send data to server
        fetch('/api/update_user_data', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(userData)
        })
        .then(response => response.json())
        .then(data => {
            console.log('User data updated:', data);
        })
        .catch(error => {
            console.error('Error updating user data:', error);
        });

        // Show the modal with the score
        gameOverModal.style.display = 'block';
        gameOverModal.querySelector('p').innerText = `Game Over :) Your score: ${score}`;

        // Stop the game
        obstacles.forEach(obstacle => obstacle.remove());
        obstacles = [];
        score = 0;
        isJumping = false;

        // Reset variables
        stressValues = [];
        workloadValues = [];
        stressSum = 0;
        stressCount = 0;
    }

    // Game Loop
    function gameLoop() {
        if (gameOverModal.style.display === 'block') return; // Stop the loop if game over
        moveObstacles();
        requestAnimationFrame(gameLoop);
    }

    // Start Game
    document.addEventListener("keydown", (e) => {
        if (gameOverModal.style.display === 'block') return;
        if (e.code === "Space") {
            jump();
            console.log('Jump function called');
        }
    });

    // Event Listeners
    gameoverButton.addEventListener("click", () => {
        // Redirect or reset the game
        fetch('/api/gamepreamble', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        })
        .then(() => {
            window.location.href = '/game_preamble.html';
        })
        .catch((error) => console.error('Error:', error));
    });

    arrowButton.addEventListener('click', () => {
        fetch('/api/gamepreamble', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
        })
        .then(() => {
            window.location.href = '/game_preamble.html';
        })
        .catch((error) => console.error('Error:', error));
    });

    startGracePeriod(100); // Initial grace period
    gameLoop();
});
*/


















/*

document.addEventListener("DOMContentLoaded", () => {
    // Difficulty Settings for Levels 1 to 5
    const difficultySettings = {
        1: { gameSpeed: 1.5, obstacleFrequency: 0.01, minObstacleGap: 2500 },
        2: { gameSpeed: 2.5, obstacleFrequency: 0.02, minObstacleGap: 2300 },
        3: { gameSpeed: 3.5, obstacleFrequency: 0.03, minObstacleGap: 2100 },
        4: { gameSpeed: 4.5, obstacleFrequency: 0.04, minObstacleGap: 1900 },
        5: { gameSpeed: 5.5, obstacleFrequency: 0.05, minObstacleGap: 1700 },
    };

    // Global variables
    let connectionOn = false;
    let userLast = 0;
    let userAverage = 0;
    let userLastLevel = 1;
    let previousGamesCount = 0;

    let stressValues = [];
    let workloadValues = [];
    let stressSum = 0;
    let stressCount = 0;
    let stressAverage = 0;
    let workloadAverage = 0;
    const rollingWindowSize = 10;

    let currentDifficulty = 1; // Will be set after fetching user data
    let gameSpeed = difficultySettings[currentDifficulty].gameSpeed;
    let obstacleFrequency = difficultySettings[currentDifficulty].obstacleFrequency;
    let minObstacleGap = difficultySettings[currentDifficulty].minObstacleGap;

    // DOM Elements
    const gameContainer = document.getElementById("gameContainer");
    const player = document.getElementById("player");
    const scoreDisplay = document.getElementById("score");
    const difficultyDisplay = document.getElementById("difficulty");
    const gameOverModal = document.getElementById("gameOverModal");
    const gameoverButton = document.getElementById('gameOverButton');
    const arrowButton = document.getElementById('arrowButton');

    let obstacles = [];
    let isJumping = false;
    let jumpHeight = 0;
    let score = 0;
    let gracePeriodActive = false;
    let lastObstacleSpawnTime = Date.now();

    // Fetch user data from the server at game start
    fetch('/api/user_data')
        .then(response => response.json())
        .then(data => {
            userLast = data.last;
            userAverage = data.avg;
            userLastLevel = data.last_level;
            previousGamesCount = data.games_played || 0;

            // Set currentDifficulty to user's last_level
            currentDifficulty = userLastLevel;
            if (currentDifficulty > 5) currentDifficulty = 5;
            if (currentDifficulty < 1) currentDifficulty = 1;

            const settings = difficultySettings[currentDifficulty];
            gameSpeed = settings.gameSpeed;
            obstacleFrequency = settings.obstacleFrequency;
            minObstacleGap = settings.minObstacleGap;
            difficultyDisplay.innerText = `Difficulty Level: ${currentDifficulty}`;
            console.log(`Set initial difficulty to level ${currentDifficulty}`);
        })
        .catch(error => {
            console.error('Error fetching user data:', error);
            // If error, set defaults
            currentDifficulty = 1;
            const settings = difficultySettings[currentDifficulty];
            gameSpeed = settings.gameSpeed;
            obstacleFrequency = settings.obstacleFrequency;
            minObstacleGap = settings.minObstacleGap;
            difficultyDisplay.innerText = `Difficulty Level: ${currentDifficulty}`;
        });

    // Grace Period Timer
    function startGracePeriod(duration) {
        gracePeriodActive = true;
        setTimeout(() => {
            gracePeriodActive = false;
        }, duration);
    }

    // Update Difficulty Function
    function updateDifficulty(level, applyGrace = false) {
        if (level > 5) level = 5;
        if (level < 1) level = 1;

        const settings = difficultySettings[level];
        gameSpeed = settings.gameSpeed;
        obstacleFrequency = settings.obstacleFrequency;
        minObstacleGap = settings.minObstacleGap;
        currentDifficulty = level;
        difficultyDisplay.innerText = `Difficulty Level: ${currentDifficulty}`;
        console.log(`Updated to difficulty level ${currentDifficulty}`);

        if (applyGrace) {
            startGracePeriod(200); // Apply grace period for difficulty change
        }
    }

    // Check connection status and fetch rolling averages every 5 seconds
    setInterval(() => {
        fetch('/api/connection_status')
            .then(response => response.json())
            .then(data => {
                connectionOn = data.status === 'connected';
                if (connectionOn) {
                    // Fetch rolling averages
                    fetch('/api/rolling_averages')
                        .then(response => response.json())
                        .then(data => {
                            let workload = parseFloat(data.rolling_avg_workload);
                            let stress = parseFloat(data.rolling_avg_stress);

                            if (!isNaN(workload) && !isNaN(stress)) {
                                workloadValues.push(workload);
                                stressValues.push(stress);

                                // Keep only the latest rollingWindowSize values
                                if (stressValues.length > rollingWindowSize) stressValues.shift();
                                if (workloadValues.length > rollingWindowSize) workloadValues.shift();

                                // Update stress sum and count
                                stressSum += stress;
                                stressCount++;

                                // Compute current averages
                                stressAverage = stressValues.reduce((a, b) => a + b, 0) / stressValues.length;
                                workloadAverage = workloadValues.reduce((a, b) => a + b, 0) / workloadValues.length;

                                console.log(`Stress avg: ${stressAverage.toFixed(2)}, Workload avg: ${workloadAverage.toFixed(2)}`);
                            }
                        })
                        .catch(error => {
                            console.error('Error fetching rolling averages:', error);
                        });
                }
            })
            .catch(error => {
                console.error('Error checking connection status:', error);
                connectionOn = false;
            });
    }, 5000); // Every 5 seconds

    // Adjust difficulty every 15 seconds
    setInterval(() => {
        if (connectionOn) {
            // Check if we have enough data
            if (stressValues.length > 0 && workloadValues.length > 0) {
                let sumStressWorkload = stressAverage + workloadAverage;
                let currentStressAverage = stressAverage;

                console.log(`Sum of stress and workload: ${sumStressWorkload.toFixed(2)}`);

                if (sumStressWorkload < 3.2 && currentStressAverage * 1.5 <= userAverage) {
                    // Increase difficulty by 1 (max 5)
                    if (currentDifficulty < 5) {
                        updateDifficulty(currentDifficulty + 1, true);
                    }
                } else if (sumStressWorkload >= 3.3 && sumStressWorkload <= 3.5 && currentStressAverage * 1.7 <= userAverage) {
                    // Keep difficulty the same
                    console.log('Keeping difficulty the same');
                } else {
                    // Decrease difficulty by 1 (min 1)
                    if (currentDifficulty > 1) {
                        updateDifficulty(currentDifficulty - 1, true);
                    }
                }
            }
        } else {
            // Connection is off, increase difficulty by 1 (up to max level 5)
            if (currentDifficulty < 5) {
                updateDifficulty(currentDifficulty + 1, true);
            }
        }
    }, 15000); // Every 15 seconds

    // Jump Logic
    function jump() {
        if (isJumping) return;
        isJumping = true;

        let jumpInterval = setInterval(() => {
            if (jumpHeight >= 120) {
                clearInterval(jumpInterval);
                let fallInterval = setInterval(() => {
                    if (jumpHeight <= 0) {
                        clearInterval(fallInterval);
                        isJumping = false;
                    }
                    jumpHeight -= 5;
                    player.style.bottom = jumpHeight + "px";
                }, 20);
            }
            jumpHeight += 5;
            player.style.bottom = jumpHeight + "px";
        }, 20);
    }

    // Spawn Obstacles with Proper Spacing
    function spawnObstacle() {
        if (gracePeriodActive) return; // Do not spawn obstacles during grace periods

        // Ensure proper spacing between obstacles
        const lastObstacle = obstacles[obstacles.length - 1];
        const currentTime = Date.now();

        // Adjusted condition to avoid overly tight gaps
        if (lastObstacle && currentTime - lastObstacleSpawnTime < minObstacleGap) return;

        // Create and spawn a new obstacle
        const obstacle = document.createElement("div");
        obstacle.classList.add("obstacle");
        obstacle.style.right = "0px";
        gameContainer.appendChild(obstacle);
        obstacles.push(obstacle);
        lastObstacleSpawnTime = currentTime; // Update last spawn time
    }

    // Move Obstacles and Check Collisions
    function moveObstacles() {
        obstacles.forEach((obstacle, index) => {
            let obstacleRight = parseInt(window.getComputedStyle(obstacle).right);
            obstacle.style.right = obstacleRight + gameSpeed + "px";

            let obstacleRect = obstacle.getBoundingClientRect();
            let playerRect = player.getBoundingClientRect();

            if (
                playerRect.left < obstacleRect.right &&
                playerRect.right > obstacleRect.left &&
                playerRect.bottom > obstacleRect.top
            ) {
                endGame();
            }

            if (obstacleRight > gameContainer.offsetWidth) {
                obstacles.shift();
                obstacle.remove();
                score++;
                scoreDisplay.innerText = `Score: ${score}`;
            }
        });

        if (Math.random() < obstacleFrequency) spawnObstacle();
    }

    // End Game and Reset
    function endGame() {
        // Calculate average stress during the game
        let gameStressAverage = stressSum / stressCount || 0;

        // Update previousGamesCount
        previousGamesCount++;

        // Prepare data to send to server
        const userData = {
            last: gameStressAverage,
            avg: ((userAverage * (previousGamesCount - 1)) + gameStressAverage) / previousGamesCount,
            last_level: currentDifficulty,
            games_played: previousGamesCount
        };

        // Send data to server
        fetch('/api/update_user_data', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(userData)
        })
        .then(response => response.json())
        .then(data => {
            console.log('User data updated:', data);
        })
        .catch(error => {
            console.error('Error updating user data:', error);
        });

        // Show the modal with the score
        gameOverModal.style.display = 'block';
        gameOverModal.querySelector('p').innerText = `Game Over :) Your score: ${score}`;

        // Stop the game
        obstacles.forEach(obstacle => obstacle.remove());
        obstacles = [];
        score = 0;
        isJumping = false;

        // Reset variables
        stressValues = [];
        workloadValues = [];
        stressSum = 0;
        stressCount = 0;
    }

    // Game Loop
    function gameLoop() {
        if (gameOverModal.style.display === 'block') return; // Stop the loop if game over
        moveObstacles();
        requestAnimationFrame(gameLoop);
    }

    // Start Game
    document.addEventListener("keydown", (e) => {
        if (gameOverModal.style.display === 'block') return;
        if (e.code === "Space") {
            jump();
            console.log('Jump function called');
        }
    });

    // Event Listeners
    gameoverButton.addEventListener("click", () => {
        // Redirect or reset the game
        fetch('/api/gamepreamble', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        })
        .then(() => {
            window.location.href = '/game_preamble.html';
        })
        .catch((error) => console.error('Error:', error));
    });

    arrowButton.addEventListener('click', () => {
        fetch('/api/gamepreamble', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
        })
        .then(() => {
            window.location.href = '/game_preamble.html';
        })
        .catch((error) => console.error('Error:', error));
    });

    startGracePeriod(100); // Initial grace period
    gameLoop();
});


*/

/*
const difficultySettings = {
    1: { gameSpeed: 2, obstacleFrequency: 0.001, minObstacleGap: 400 },
    2: { gameSpeed: 3, obstacleFrequency: 0.002, minObstacleGap: 300 },
    3: { gameSpeed: 4, obstacleFrequency: 0.035, minObstacleGap: 240 },
    4: { gameSpeed: 5, obstacleFrequency: 0.035, minObstacleGap: 210 },
    5: { gameSpeed: 6, obstacleFrequency: 0.035, minObstacleGap: 180 },
    6: { gameSpeed: 7, obstacleFrequency: 0.05, minObstacleGap: 150 },
    7: { gameSpeed: 7, obstacleFrequency: 0.06, minObstacleGap: 120 },
};

let currentDifficulty = 1; // Default to level 1
let gameSpeed = difficultySettings[currentDifficulty].gameSpeed;
let obstacleFrequency = difficultySettings[currentDifficulty].obstacleFrequency;
let minObstacleGap = difficultySettings[currentDifficulty].minObstacleGap;


const gameContainer = document.getElementById("gameContainer");
const player = document.getElementById("player");
const scoreDisplay = document.getElementById("score");
const difficultyDisplay = document.getElementById("difficulty");
const gameOverModal = document.getElementById("gameOverModal");

let obstacles = [];
let isJumping = false;
let jumpHeight = 0;
let score = 0;
let gracePeriodActive = false;
let lastObstacleSpawnTime = Date.now();
let lastDifficultyChangeTime = Date.now();

// Grace Period Timer
function startGracePeriod(duration) {
    gracePeriodActive = true;
    setTimeout(() => {
        gracePeriodActive = false;
    }, duration);
}

// Fetch rolling averages if connected
// Variabili globali per salvare i valori di workload e stress
let savedWorkload = 0;
let savedStress = 0;

function wait(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}


async function updateDifficulty(level, applyGrace = false) {
    try {
        // Fetch rolling averages if connected
        const response = await fetch('/api/rolling_averages');
        const data = await response.json();  // Parsing la risposta come JSON

        let workload = data.rolling_avg_workload;  // Estrai il valore di "rolling_avg_workload"
        let stress = data.rolling_avg_stress;  // Estrai il valore di "rolling_avg_stress"

        // Converti i valori a numeri
        workload = parseFloat(workload);  // Converte il valore di workload in un numero
        stress = parseFloat(stress);  // Converte il valore di stress in un numero

        // Salva i valori nelle variabili globali
        savedWorkload = workload;
        savedStress = stress;

        // Ora puoi utilizzare `savedWorkload` e `savedStress` nel resto del codice
        console.log("Saved Workload:", savedWorkload);
        console.log("Saved Stress:", savedStress);

        // Aspetta un secondo prima di proseguire
        await wait(1000);  // Attende 1000 millisecondi (1 secondo)

        // Ora puoi usare i valori appena ottenuti
        workload_stress = parseFloat(savedStress + savedWorkload);  // Quando arriva qui, usa il valore appena ricevuto da fetch
        if (workload_stress>1) {
        

        if (workload_stress > 3.5) {   // se stressato tanto diminuisce di 1
            current_level = level - 2;
            if (current_level<1) {
                current_level=1
            }}

        else if (workload_stress <3) {
            current_level = level;
            if (current_level>5) {
                current_level=5
            }
        } 

        else {
            current_level=level-1;
        }

        const settings = difficultySettings[current_level];
        gameSpeed = settings.gameSpeed;
        obstacleFrequency = settings.obstacleFrequency;
        minObstacleGap = settings.minObstacleGap;
        currentDifficulty = current_level;
        difficultyDisplay.innerText = `Difficulty Level: ${current_level}`;
        console.log(`Updated to difficulty level ${current_level}`);

        if (applyGrace) {
            startGracePeriod(200); // Apply grace period for difficulty increase
        }}
    else {
        currentDifficulty=level
        if (currentDifficulty > 5){
            currentDifficulty=5
        }
        const settings = difficultySettings[currentDifficulty];
        gameSpeed = settings.gameSpeed;
        obstacleFrequency = settings.obstacleFrequency;
        minObstacleGap = settings.minObstacleGap;
        difficultyDisplay.innerText = `Difficulty Level: ${currentDifficulty}`;
        console.log(`Updated to difficulty level ${currentDifficulty}`);
    
        if (applyGrace) {
            startGracePeriod(200); // Apply grace period for difficulty increase
        }}
    } catch (error) {
        
    }  // Gestione degli errori in caso di problemi con la richiesta fetch
}




setInterval(() => {
    if (Date.now() - lastDifficultyChangeTime >= 5000) { // 45 seconds passed
        if (currentDifficulty < 7) {
            updateDifficulty(currentDifficulty + 1, true); // Increment with grace period
        }
        lastDifficultyChangeTime = Date.now();
    }
}, 5000); // Check every second

// Jump Logic
function jump() {
    if (isJumping) return;
    isJumping = true;

    let jumpInterval = setInterval(() => {
        if (jumpHeight >= 120) { // Increased jump height
            clearInterval(jumpInterval);
            let fallInterval = setInterval(() => {
                if (jumpHeight <= 0) {
                    clearInterval(fallInterval);
                    isJumping = false;
                }
                jumpHeight -= 5;
                player.style.bottom = jumpHeight + "px";
            }, 20);
        }
        jumpHeight += 5;
        player.style.bottom = jumpHeight + "px";
    }, 20);
}

// Spawn Obstacles with Proper Spacing
function spawnObstacle() {
    if (gracePeriodActive) return; // Do not spawn obstacles during grace periods

    // Ensure proper spacing between obstacles
    const lastObstacle = obstacles[obstacles.length - 1];
    const currentTime = Date.now();

    // Adjusted condition to avoid overly tight gaps
    if (lastObstacle && currentTime - lastObstacleSpawnTime < minObstacleGap) return;

    // Create and spawn a new obstacle
    const obstacle = document.createElement("div");
    obstacle.classList.add("obstacle");
    obstacle.style.right = "0px";
    gameContainer.appendChild(obstacle);
    obstacles.push(obstacle);
    lastObstacleSpawnTime = currentTime; // Update last spawn time
}

// Move Obstacles and Check Collisions
function moveObstacles() {
    obstacles.forEach((obstacle, index) => {
        let obstacleRight = parseInt(window.getComputedStyle(obstacle).right);
        obstacle.style.right = obstacleRight + gameSpeed + "px";

        let obstacleRect = obstacle.getBoundingClientRect();
        let playerRect = player.getBoundingClientRect();

        if (
            playerRect.left < obstacleRect.right &&
            playerRect.right > obstacleRect.left &&
            playerRect.bottom > obstacleRect.top
        ) {
            endGame();
        }

        if (obstacleRight > gameContainer.offsetWidth) {
            obstacles.shift();
            obstacle.remove();
            score++;
            scoreDisplay.innerText = `Score: ${score}`;
        }
    });

    if (Math.random() < obstacleFrequency) spawnObstacle();
}

// End Game and Reset
function endGame() {
    // 1. Show the modal with the score
    gameOverModal.style.display = 'block';
    gameOverModal.querySelector('p').innerText = `Game Over :) Your score: ${score}`;

    // 2. Stop the game (so it doesn't continue)
    obstacles.forEach(obstacle => obstacle.remove());
    obstacles = [];
    score = 0;
    isJumping = false;

    // 3. Reset difficulty (back to level 1)
    updateDifficulty(1);

    // 4. Activate a grace period of 2 seconds
    startGracePeriod(2000);
}

// Game Loop
// Game Loop
function gameLoop() {
    if (gameOverModal.style.display === 'block') return; // Blocca il ciclo se il modale è attivo
    moveObstacles();
    requestAnimationFrame(gameLoop);
}


// Start Game
document.addEventListener("keydown", (e) => {
    if (gameOverModal.style.display === 'block') return;
    if (e.code === "Space") jump();
});






startGracePeriod(100); // Initial grace period
gameLoop();


*/

/*
const difficultySettings = {
    1: { gameSpeed: 1.5, obstacleFrequency: 0.008, minObstacleGap: 2500 },  // Distanza tra ostacoli per livello 1
    2: { gameSpeed: 2.5, obstacleFrequency: 0.008, minObstacleGap: 2500 },  // Distanza e frequenza uguali al livello 1
    3: { gameSpeed: 3.5, obstacleFrequency: 0.008, minObstacleGap: 2500 },  // Frequenza invariata, distanza invariata
    4: { gameSpeed: 4.5, obstacleFrequency: 0.008, minObstacleGap: 2500 },
    5: { gameSpeed: 5.5, obstacleFrequency: 0.008, minObstacleGap: 2500 },
};


let currentDifficulty = 1; // Default to level 1
let gameSpeed = difficultySettings[currentDifficulty].gameSpeed;
let obstacleFrequency = difficultySettings[currentDifficulty].obstacleFrequency;
let minObstacleGap = difficultySettings[currentDifficulty].minObstacleGap;
let connected = false

const gameContainer = document.getElementById("gameContainer");
const player = document.getElementById("player");
const scoreDisplay = document.getElementById("score");
const difficultyDisplay = document.getElementById("difficulty");
const gameOverModal = document.getElementById("gameOverModal");

let obstacles = [];
let isJumping = false;
let jumpHeight = 0;
let score = 0;
let gracePeriodActive = false;
let lastObstacleSpawnTime = Date.now();
let lastDifficultyChangeTime = Date.now();

// Grace Period Timer
function startGracePeriod(duration) {
    gracePeriodActive = true;
    setTimeout(() => {
        gracePeriodActive = false;
    }, duration);
}




// Update Difficulty
function updateDifficulty(level, applyGrace = false) {
    const settings = difficultySettings[level];
    gameSpeed = settings.gameSpeed;
    obstacleFrequency = settings.obstacleFrequency;
    minObstacleGap = settings.minObstacleGap;
    currentDifficulty = level;
    difficultyDisplay.innerText = `Difficulty Level: ${level}`;
    console.log(`Updated to difficulty level ${level}`);

    if (applyGrace) {
        startGracePeriod(200); // Apply grace period for difficulty increase
    }
}

// Fetch difficulty from the server periodically
setInterval(() => {
    fetch('/api/difficulty')
        .then(response => response.json())
        .then(data => {
            const newDifficulty = data.difficulty;

            // Check if difficulty has increased
            const difficultyIncreased = newDifficulty > currentDifficulty;
            updateDifficulty(newDifficulty, difficultyIncreased);
        })
        .catch(err => console.error('Error fetching difficulty:', err));
}, 25000); // Check the server every 25 seconds

// Automatic Difficulty Increase
setInterval(() => {
    if (Date.now() - lastDifficultyChangeTime >= 5000) { // 45 seconds passed
        if (currentDifficulty < 7) {
            updateDifficulty(currentDifficulty + 1, true); // Increment with grace period
        }
        lastDifficultyChangeTime = Date.now();
    }
}, 10000); // Check every second

// Jump Logic
function jump() {
    if (isJumping) return;
    isJumping = true;

    let jumpInterval = setInterval(() => {
        if (jumpHeight >= 120) { // Increased jump height
            clearInterval(jumpInterval);
            let fallInterval = setInterval(() => {
                if (jumpHeight <= 0) {
                    clearInterval(fallInterval);
                    isJumping = false;
                }
                jumpHeight -= 5;
                player.style.bottom = jumpHeight + "px";
            }, 20);
        }
        jumpHeight += 5;
        player.style.bottom = jumpHeight + "px";
    }, 20);
}

// Spawn Obstacles with Proper Spacing
function spawnObstacle() {
    if (gracePeriodActive) return; // Do not spawn obstacles during grace periods

    // Ensure proper spacing between obstacles
    const lastObstacle = obstacles[obstacles.length - 1];
    const currentTime = Date.now();

    // Adjusted condition to avoid overly tight gaps
    if (lastObstacle && currentTime - lastObstacleSpawnTime < minObstacleGap) return;

    // Create and spawn a new obstacle
    const obstacle = document.createElement("div");
    obstacle.classList.add("obstacle");
    obstacle.style.right = "0px";
    gameContainer.appendChild(obstacle);
    obstacles.push(obstacle);
    lastObstacleSpawnTime = currentTime; // Update last spawn time
}

// Move Obstacles and Check Collisions
function moveObstacles() {
    obstacles.forEach((obstacle, index) => {
        let obstacleRight = parseInt(window.getComputedStyle(obstacle).right);
        obstacle.style.right = obstacleRight + gameSpeed + "px";

        let obstacleRect = obstacle.getBoundingClientRect();
        let playerRect = player.getBoundingClientRect();

        if (
            playerRect.left < obstacleRect.right &&
            playerRect.right > obstacleRect.left &&
            playerRect.bottom > obstacleRect.top
        ) {
            endGame();
        }

        if (obstacleRight > gameContainer.offsetWidth) {
            obstacles.shift();
            obstacle.remove();
            score++;
            scoreDisplay.innerText = `Score: ${score}`;
        }
    });

    if (Math.random() < obstacleFrequency) spawnObstacle();
}

// End Game and Reset
function endGame() {
    // 1. Show the modal with the score
    gameOverModal.style.display = 'block';
    gameOverModal.querySelector('p').innerText = `Game Over :) Your score: ${score}`;

    // 2. Stop the game (so it doesn't continue)
    obstacles.forEach(obstacle => obstacle.remove());
    obstacles = [];
    score = 0;
    isJumping = false;

    // 3. Reset difficulty (back to level 1)
    updateDifficulty(1);

    // 4. Activate a grace period of 2 seconds
    startGracePeriod(2000);
}

// Game Loop
// Game Loop
function gameLoop() {
    if (gameOverModal.style.display === 'block') return; // Blocca il ciclo se il modale è attivo
    moveObstacles();
    requestAnimationFrame(gameLoop);
}


// Start Game
document.addEventListener("keydown", (e) => {
    if (gameOverModal.style.display === 'block') return;
    if (e.code === "Space") jump();
});

startGracePeriod(100); // Initial grace period
gameLoop();


*/



















// Difficulty Settings for Levels 1 to 7
// Difficulty Settings for Levels 1 to 7
// Difficulty Settings for Levels 1 to 7


/*
const difficultySettings = {
    1: { gameSpeed: 2, obstacleFrequency: 0.015, minObstacleGap: 350 },
    2: { gameSpeed: 3, obstacleFrequency: 0.02, minObstacleGap: 300 },
    3: { gameSpeed: 4, obstacleFrequency: 0.035, minObstacleGap: 240 },
    4: { gameSpeed: 5, obstacleFrequency: 0.035, minObstacleGap: 210 },
    5: { gameSpeed: 6, obstacleFrequency: 0.035, minObstacleGap: 180 },
    6: { gameSpeed: 7, obstacleFrequency: 0.05, minObstacleGap: 150 },
    7: { gameSpeed: 7, obstacleFrequency: 0.06, minObstacleGap: 120 },
};

let currentDifficulty = 1; // Default to level 1
let gameSpeed = difficultySettings[currentDifficulty].gameSpeed;
let obstacleFrequency = difficultySettings[currentDifficulty].obstacleFrequency;
let minObstacleGap = difficultySettings[currentDifficulty].minObstacleGap;

const gameContainer = document.getElementById("gameContainer");
const player = document.getElementById("player");
const scoreDisplay = document.getElementById("score");
const difficultyDisplay = document.getElementById("difficulty");
const gameOverModal = document.getElementById("gameOverModal"); // Modale di Game Over
const gameOverButton = document.getElementById("gameOverButton"); // Bottone nel modale

let obstacles = [];
let isJumping = false;
let jumpHeight = 0;
let score = 0;
let gracePeriodActive = false;
let lastObstacleSpawnTime = Date.now();
let lastDifficultyChangeTime = Date.now();

// Grace Period Timer
function startGracePeriod(duration) {
    gracePeriodActive = true;
    setTimeout(() => {
        gracePeriodActive = false;
    }, duration);
}


// Update Difficulty
function updateDifficulty(level, applyGrace = false) {
    const settings = difficultySettings[level];
    gameSpeed = settings.gameSpeed;
    obstacleFrequency = settings.gameFrequency;
    minObstacleGap = settings.minObstacleGap;
    currentDifficulty = level;
    difficultyDisplay.innerText = `Difficulty Level: ${level}`;
    console.log(`Updated to difficulty level ${level}`);

    if (applyGrace) {
        startGracePeriod(200); // Apply grace period for difficulty increase
    }
}

setInterval(() => {
    fetch('/api/difficulty')
        .then(response => response.json())
        .then(data => {
            const newDifficulty = data.difficulty;

            // Check if difficulty has increased
            const difficultyIncreased = newDifficulty > currentDifficulty;
            updateDifficulty(newDifficulty, difficultyIncreased);
        })
        .catch(err => console.error('Error fetching difficulty:', err));
}, 25000); // Check the server every 25 seconds

// Automatic Difficulty Increase
setInterval(() => {
    if (Date.now() - lastDifficultyChangeTime >= 24000 + 10) { // 45 seconds passed
        if (currentDifficulty < 7) {
            updateDifficulty(currentDifficulty + 1, true); // Increment with grace period
        }
        lastDifficultyChangeTime = Date.now();
    }
}, 1000); // Check every second

// Jump Logic
function jump() {
    if (isJumping) return;
    isJumping = true;

    let jumpInterval = setInterval(() => {
        if (jumpHeight >= 120) { // Increased jump height
            clearInterval(jumpInterval);
            let fallInterval = setInterval(() => {
                if (jumpHeight <= 0) {
                    clearInterval(fallInterval);
                    isJumping = false;
                }
                jumpHeight -= 5;
                player.style.bottom = jumpHeight + "px";
            }, 20);
        }
        jumpHeight += 5;
        player.style.bottom = jumpHeight + "px";
    }, 20);
}

// Spawn Obstacles with Proper Spacing
function spawnObstacle() {
    if (gracePeriodActive) return; // Do not spawn obstacles during grace periods

    // Ensure proper spacing between obstacles
    const lastObstacle = obstacles[obstacles.length - 1];
    const currentTime = Date.now();
    if (lastObstacle && currentTime - lastObstacleSpawnTime < minObstacleGap / gameSpeed * 1000) return;

    // Create and spawn a new obstacle
    const obstacle = document.createElement("div");
    obstacle.classList.add("obstacle");
    obstacle.style.right = "0px";
    gameContainer.appendChild(obstacle);
    obstacles.push(obstacle);
    lastObstacleSpawnTime = currentTime; // Update last spawn time
}

// Move Obstacles and Check Collisions
function moveObstacles() {
    obstacles.forEach((obstacle, index) => {
        let obstacleRight = parseInt(window.getComputedStyle(obstacle).right);
        obstacle.style.right = obstacleRight + gameSpeed + "px";

        let obstacleRect = obstacle.getBoundingClientRect();
        let playerRect = player.getBoundingClientRect();

        if (
            playerRect.left < obstacleRect.right &&
            playerRect.right > obstacleRect.left &&
            playerRect.bottom > obstacleRect.top
        ) {
            endGame(); // Game over if collision happens
        }

        if (obstacleRight > gameContainer.offsetWidth) {
            obstacles.shift();
            obstacle.remove();
            score++;
            scoreDisplay.innerText = `Score: ${score}`;
        }
    });

    if (Math.random() < obstacleFrequency) spawnObstacle();
}

// End Game, Show Modal, and Wait for User Interaction
function endGame() {
    // 1. Mostra il modale con il punteggio
    gameOverModal.style.display = 'block';
    gameOverModal.querySelector('p').innerText = `Game Over :) Your score: ${score}`;

    // 2. Ferma il gioco (in modo che non continui)
    obstacles.forEach(obstacle => obstacle.remove());
    obstacles = [];
    score = 0;
    isJumping = false;

    // 3. Resetta la difficoltà (torna al livello 1)
    updateDifficulty(1);

    // 4. Attiva la grace period di 2 secondi
    startGracePeriod(2000);
}




// Game Loop
function gameLoop() {
    moveObstacles();
    requestAnimationFrame(gameLoop);
}

// Gestisci l'interazione con il tasto spazio
document.addEventListener("keydown", (e) => {
    if (e.code === "Space") jump();
});

startGracePeriod(1); // Periodo di grazia iniziale
gameLoop();
*/