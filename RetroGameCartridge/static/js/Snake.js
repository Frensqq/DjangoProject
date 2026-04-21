var canvas = document.getElementById('gameSnake');
    var context = canvas.getContext('2d');
    var grid = 16;
    var count = 0;
    var gameRunning = false;
    var gameOver = false;
    var animationId = null;
    
    var snake = {
        x: 160,
        y: 160,
        dx: grid,
        dy: 0,
        cells: [],
        maxCells: 4
    };
    
    var apple = {
        x: 320,
        y: 320
    };
    
    function getRandomInt(min, max) {
        return Math.floor(Math.random() * (max - min)) + min;
    }
    
    function resetGame() {
        snake = {
            x: 160,
            y: 160,
            dx: grid,
            dy: 0,
            cells: [],
            maxCells: 4
        };
        apple = {
            x: 320,
            y: 320
        };
        count = 0;
        gameOver = false;
        context.clearRect(0, 0, canvas.width, canvas.height);
    }
    
    function showGameOver() {
        gameOver = true;
        gameRunning = false;
        
        const btn = document.getElementById('startStopBtn');
        btn.textContent = 'Начать игру';
        btn.classList.remove('btn-danger');
        btn.classList.add('btn-success');
        
        // Рисуем сообщение Game Over
        const rectX = canvas.width / 2 - 100;
        const rectY = canvas.height / 2 - 30;
        const rectWidth = 200;
        const rectHeight = 60;
        
        context.fillStyle = '#2d1b36';
        context.fillRect(rectX, rectY, rectWidth, rectHeight);
        
        context.strokeStyle = '#ffde6b';
        context.lineWidth = 3;
        context.strokeRect(rectX, rectY, rectWidth, rectHeight);
        
        context.fillStyle = '#ff9966';
        context.font = '16px "Press Start 2P", monospace';
        context.textAlign = 'center';
        context.textBaseline = 'middle';
        context.fillText('GAME OVER', canvas.width / 2, canvas.height / 2);
    }
    
    function loop() {
        if (!gameRunning || gameOver) return;
        
        animationId = requestAnimationFrame(loop);
        
        if (++count < 20) {
            return;
        }
        count = 0;
        context.clearRect(0, 0, canvas.width, canvas.height);
        
        snake.x += snake.dx;
        snake.y += snake.dy;
        
        if (snake.x < 0 || snake.x >= canvas.width || snake.y < 0 || snake.y >= canvas.height) {
        showGameOver();
        return;
        }
        snake.cells.unshift({ x: snake.x, y: snake.y });
        
        if (snake.cells.length > snake.maxCells) {
            snake.cells.pop();
        }
        
        context.fillStyle = 'red';
        context.fillRect(apple.x, apple.y, grid - 1, grid - 1);
        
        context.fillStyle = '#6bff6b';
        snake.cells.forEach(function (cell, index) {
            context.fillRect(cell.x, cell.y, grid - 1, grid - 1);
            
            if (cell.x === apple.x && cell.y === apple.y) {
                snake.maxCells++;
                apple.x = getRandomInt(0, 25) * grid;
                apple.y = getRandomInt(0, 25) * grid;
            }
            
            for (var i = index + 1; i < snake.cells.length; i++) {
                if (cell.x === snake.cells[i].x && cell.y === snake.cells[i].y) {
                    showGameOver();
                    return;
                }
            }
        });
    }
    
    document.addEventListener('keydown', function (e) {
        if (!gameRunning || gameOver) return;
        
        if (e.key === 'ArrowLeft' || e.key === 'ArrowRight' || e.key === 'ArrowUp' || e.key === 'ArrowDown') {
            e.preventDefault();
        }
        
        if (e.which === 37 && snake.dx === 0) {
            snake.dx = -grid;
            snake.dy = 0;
        } else if (e.which === 38 && snake.dy === 0) {
            snake.dy = -grid;
            snake.dx = 0;
        } else if (e.which === 39 && snake.dx === 0) {
            snake.dx = grid;
            snake.dy = 0;
        } else if (e.which === 40 && snake.dy === 0) {
            snake.dy = grid;
            snake.dx = 0;
        }
    });
    
    const startStopBtn = document.getElementById('startStopBtn');
    startStopBtn.addEventListener('click', function() {
        if (gameRunning) {
            gameRunning = false;
            if (animationId) {
                cancelAnimationFrame(animationId);
                animationId = null;
            }
            startStopBtn.textContent = 'Начать игру';
            startStopBtn.classList.remove('btn-danger');
            startStopBtn.classList.add('btn-success');
        } else {
            resetGame();
            gameRunning = true;
            gameOver = false;
            startStopBtn.textContent = 'Остановить';
            startStopBtn.classList.remove('btn-success');
            startStopBtn.classList.add('btn-danger');
            loop();
        }
    });