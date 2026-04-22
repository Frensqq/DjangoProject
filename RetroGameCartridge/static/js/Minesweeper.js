var canvas = document.getElementById('minesweeper');
var context = canvas.getContext('2d');

var size = 8;
var cellSize = canvas.width / size;

var board = [];
var revealed = [];
var flags = [];
var gameOver = false;
var gameRunning = true;
var totalMines = 10;

function initGame() {
    for (var i = 0; i < size; i++) {
        board[i] = [];
        revealed[i] = [];
        flags[i] = [];
        for (var j = 0; j < size; j++) {
            board[i][j] = 0;
            revealed[i][j] = false;
            flags[i][j] = false;
        }
    }
    
    var minesPlaced = 0;
    while (minesPlaced < totalMines) {
        var x = Math.floor(Math.random() * size);
        var y = Math.floor(Math.random() * size);
        if (board[x][y] !== 'M') {
            board[x][y] = 'M';
            minesPlaced++;
        }
    }
    
    for (var i = 0; i < size; i++) {
        for (var j = 0; j < size; j++) {
            if (board[i][j] === 'M') continue;
            var count = 0;
            for (var dx = -1; dx <= 1; dx++) {
                for (var dy = -1; dy <= 1; dy++) {
                    var ni = i + dx, nj = j + dy;
                    if (ni >= 0 && ni < size && nj >= 0 && nj < size && board[ni][nj] === 'M') {
                        count++;
                    }
                }
            }
            board[i][j] = count;
        }
    }
}

function showGameOver(message) {
    gameOver = true;
    gameRunning = false;
    
    const btn = document.getElementById('startStopBtn');
    btn.textContent = 'Новая игра';
    btn.classList.remove('btn-danger');
    btn.classList.add('btn-success');
    
    context.fillStyle = '#2d1b36';
    context.fillRect(0, canvas.height / 2 - 40, canvas.width, 80);
    
    context.strokeStyle = '#ffde6b';
    context.lineWidth = 3;
    context.strokeRect(10, canvas.height / 2 - 40, canvas.width - 20, 80);
    
    context.fillStyle = '#ff9966';
    context.font = '20px "Press Start 2P", monospace';
    context.textAlign = 'center';
    context.textBaseline = 'middle';
    context.fillText(message, canvas.width / 2, canvas.height / 2);
}

function draw() {
    context.clearRect(0, 0, canvas.width, canvas.height);
    
    for (var i = 0; i < size; i++) {
        for (var j = 0; j < size; j++) {
            var x = j * cellSize;
            var y = i * cellSize;
            
            if (revealed[i][j]) {
                context.fillStyle = '#3a2a3e';
                context.fillRect(x, y, cellSize - 1, cellSize - 1);
                
                if (board[i][j] === 'M') {
                    context.fillStyle = '#ff4444';
                    context.font = '20px monospace';
                    context.textAlign = 'center';
                    context.textBaseline = 'middle';
                    context.fillText('💣', x + cellSize/2, y + cellSize/2);
                } else if (board[i][j] > 0) {
                    var colors = ['#ffffff', '#4a9eff', '#4eff4e', '#ff4444', '#ff44ff', '#ffff44', '#44ffff', '#ff8844'];
                    context.fillStyle = colors[board[i][j]];
                    context.font = 'bold 18px "Press Start 2P", monospace';
                    context.textAlign = 'center';
                    context.textBaseline = 'middle';
                    context.fillText(board[i][j], x + cellSize/2, y + cellSize/2);
                }
            } else {
                context.fillStyle = '#2d1b36';
                context.fillRect(x, y, cellSize - 1, cellSize - 1);
                context.fillStyle = '#4a2a5e';
                context.fillRect(x + 2, y + 2, cellSize - 5, cellSize - 5);
                
                if (flags[i][j]) {
                    context.fillStyle = '#ff4444';
                    context.font = '20px monospace';
                    context.textAlign = 'center';
                    context.textBaseline = 'middle';
                    context.fillText('🚩', x + cellSize/2, y + cellSize/2);
                }
            }
            
            context.strokeStyle = '#6bff6b';
            context.lineWidth = 1;
            context.strokeRect(x, y, cellSize, cellSize);
        }
    }
    
    if (gameOver) {
        showGameOver('GAME OVER');
    }
}

function revealCell(i, j) {
    if (i < 0 || i >= size || j < 0 || j >= size) return;
    if (revealed[i][j]) return;
    if (flags[i][j]) return;
    if (gameOver) return;
    
    revealed[i][j] = true;
    
    if (board[i][j] === 'M') {
        showGameOver('GAME OVER');
        draw();
        return;
    }
    
    if (board[i][j] === 0) {
        for (var dx = -1; dx <= 1; dx++) {
            for (var dy = -1; dy <= 1; dy++) {
                revealCell(i + dx, j + dy);
            }
        }
    }
    
    draw();
}

function checkWin() {
    var opened = 0;
    for (var i = 0; i < size; i++) {
        for (var j = 0; j < size; j++) {
            if (revealed[i][j]) opened++;
        }
    }
    
    if (opened === size * size - totalMines && !gameOver) {
        gameOver = true;
        gameRunning = false;
        
        const btn = document.getElementById('startStopBtn');
        btn.textContent = 'Новая игра';
        btn.classList.remove('btn-danger');
        btn.classList.add('btn-success');
        
        context.fillStyle = '#2d1b36';
        context.fillRect(0, canvas.height / 2 - 40, canvas.width, 80);
        
        context.strokeStyle = '#ffde6b';
        context.lineWidth = 3;
        context.strokeRect(10, canvas.height / 2 - 40, canvas.width - 20, 80);
        
        context.fillStyle = '#6bff6b';
        context.font = '20px "Press Start 2P", monospace';
        context.textAlign = 'center';
        context.textBaseline = 'middle';
        context.fillText('YOU WIN!', canvas.width / 2, canvas.height / 2);
    }
}

canvas.addEventListener('click', function(e) {
    if (gameOver) return;
    
    var rect = canvas.getBoundingClientRect();
    var scaleX = canvas.width / rect.width;
    var scaleY = canvas.height / rect.height;
    
    var mouseX = (e.clientX - rect.left) * scaleX;
    var mouseY = (e.clientY - rect.top) * scaleY;
    
    var col = Math.floor(mouseX / cellSize);
    var row = Math.floor(mouseY / cellSize);
    
    if (row >= 0 && row < size && col >= 0 && col < size) {
        revealCell(row, col);
        checkWin();
    }
});

canvas.addEventListener('contextmenu', function(e) {
    e.preventDefault();
    if (gameOver) return;
    
    var rect = canvas.getBoundingClientRect();
    var scaleX = canvas.width / rect.width;
    var scaleY = canvas.height / rect.height;
    
    var mouseX = (e.clientX - rect.left) * scaleX;
    var mouseY = (e.clientY - rect.top) * scaleY;
    
    var col = Math.floor(mouseX / cellSize);
    var row = Math.floor(mouseY / cellSize);
    
    if (row >= 0 && row < size && col >= 0 && col < size && !revealed[row][col]) {
        flags[row][col] = !flags[row][col];
        draw();
    }
});

const startStopBtn = document.getElementById('startStopBtn');
startStopBtn.addEventListener('click', function() {
    initGame();
    gameOver = false;
    gameRunning = true;
    draw();
    startStopBtn.textContent = 'Новая игра';
});

initGame();
draw();