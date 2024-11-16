// Difficulty Settings for Levels 1 to 7
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
    if (Date.now() - lastDifficultyChangeTime >= 24000+10) { // 45 seconds passed
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
    alert(`Game Over! Your score: ${score}`);
    obstacles.forEach((obstacle) => obstacle.remove());
    obstacles = [];
    score = 0;
    isJumping = false;
    updateDifficulty(1); // Reset to Level 1
    startGracePeriod(100); // 2-second grace period
}

// Game Loop
function gameLoop() {
    moveObstacles();
    requestAnimationFrame(gameLoop);
}

// Start Game
document.addEventListener("keydown", (e) => {
    if (e.code === "Space") jump();
});

startGracePeriod(100); // Initial grace period
gameLoop();
