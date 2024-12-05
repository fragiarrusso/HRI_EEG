document.addEventListener("DOMContentLoaded", () => {
    
    
    // Difficulty Settings for Levels 1 to 5
    const difficultySettings = {
        1: { gameSpeed: 2, obstacleFrequency: 0.02, minObstacleGap: 2600},
        2: { gameSpeed: 3.5, obstacleFrequency: 0.1, minObstacleGap: 2000},
        3: { gameSpeed: 4, obstacleFrequency: 0.2, minObstacleGap: 1600 },
        4: { gameSpeed: 5, obstacleFrequency: 0.3, minObstacleGap: 1200 },
        5: { gameSpeed: 9.5, obstacleFrequency: 0.4, minObstacleGap: 1000 },
    };

    // Global variables
    let connectionOn = false;
    let userLast = 0;
    let userAverage = 0;
    let userLastLevel = 1;
    let previousGamesCount = 0;

    let workload=0
    let stress=0
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

        /*
        console.log("In 5s");
        console.log("connectionOn:", connectionOn);
        console.log("userAverage:", userAverage);
        console.log("stress", stress);
        console.log("workload:", workload);
        console.log("-------------------------------------")
        */
       
        fetch('/api/connection_status')
            .then(response => response.json())
            .then(data => {
                connectionOn = data.status === 'connected';
                if (connectionOn) {
                    fetch('/api/rolling_averages')
                        .then(response => response.json())
                        .then(data => {
                            workload = parseFloat(data.rolling_avg_workload);
                            stress = parseFloat(data.rolling_avg_stress);

                            if (!isNaN(workload) && !isNaN(stress)) {
                                workloadValues.push(workload);
                                stressValues.push(stress);

                                if (stressValues.length > rollingWindowSize) stressValues.shift();
                                if (workloadValues.length > rollingWindowSize) workloadValues.shift();

                                
                                stressSum += stress;
                                stressCount++;

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
        console.log("In 15s interval:");
        console.log("connectionOn:", connectionOn);
        console.log("userAverage:", userAverage);
        console.log("stress:", stress);
        console.log("workload", workload);
        

        if (connectionOn) {
            if (stress > 0 && workload > 0) {
                let curr_stress = stress;
                let curr_workload = workload;
                console.log("connectionOn && stress > 0 && workload> 0");
                console.log(`Sum of stress and workload: ${(curr_stress + curr_workload).toFixed(2)}`);

                if (curr_stress + curr_workload < 2.9 &&(isNaN(curr_stress) || curr_stress <= Math.max(userAverage*1.5,1.8)) ) {
                    console.log("increasing difficulty branch");
                    if (currentDifficulty < 5) {
                        updateDifficulty(currentDifficulty + 1, true);
                    }
                } else if (stress + workload >= 2.9 && (isNaN(curr_stress) || curr_stress + curr_workload < 3 && curr_stress <=Math.max(userAverage*1.3,1.7))) {
                    console.log('Keeping difficulty the same');
                } else {
                    console.log("In which branch we are? -> decreasing difficulty branch");
                    if (currentDifficulty > 1) {
                        updateDifficulty(currentDifficulty - 1, true);
                    }
                }
            }
        } else {
            console.log("In which branch we are? -> connectionOff branch");
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
        if (gracePeriodActive) return;

        const lastObstacle = obstacles[obstacles.length - 1];
        const currentTime = Date.now();

        if (lastObstacle && currentTime - lastObstacleSpawnTime < minObstacleGap) return;

        const obstacle = document.createElement("div");
        obstacle.classList.add("obstacle");
        obstacle.style.right = "0px";
        gameContainer.appendChild(obstacle);
        obstacles.push(obstacle);
        lastObstacleSpawnTime = currentTime;
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
        let gameStressAverage = stressSum / stressCount || 0;

        previousGamesCount++;

        const userData = {
            last: gameStressAverage,
            avg: ((userAverage * (previousGamesCount - 1)) + gameStressAverage) / previousGamesCount,
            last_level: currentDifficulty,
            games_played: previousGamesCount
        };

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

        gameOverModal.style.display = 'block';
        gameOverModal.querySelector('p').innerText = `Game Over :) Your score: ${score}`;

        obstacles.forEach(obstacle => obstacle.remove());
        obstacles = [];
        score = 0;
        isJumping = false;

        stressValues = [];
        workloadValues = [];
        stressSum = 0;
        stressCount = 0;
    }

    // Game Loop
    function gameLoop() {
        if (gameOverModal.style.display === 'block') return;
        moveObstacles();
        requestAnimationFrame(gameLoop);
    }

    document.addEventListener("keydown", (e) => {
        if (gameOverModal.style.display === 'block') return;
        if (e.code === "Space") {
            jump();
            console.log('Jump function called');
        }
    });

    gameoverButton.addEventListener("click", () => {
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

    startGracePeriod(100);
    gameLoop();
});

