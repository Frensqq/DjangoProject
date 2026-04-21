    // получаем доступ к холсту
    const canvas = document.getElementById('game');
    const context = canvas.getContext('2d');
    // размер квадратика
    const grid = 32;
    // массив с последовательностями фигур, на старте — пустой
    var tetrominoSequence = [];

    // с помощью двумерного массива следим за тем, что находится в каждой клетке игрового поля
    var playfield = [];

    // заполняем сразу массив пустыми ячейками
    for (let row = -2; row < 20; row++) {
        playfield[row] = [];
        for (let col = 0; col < 10; col++) {
            playfield[row][col] = 0;
        }
    }

    const tetrominos = {
        'I': [[0,0,0,0], [1,1,1,1], [0,0,0,0], [0,0,0,0]],
        'J': [[1,0,0], [1,1,1], [0,0,0]],
        'L': [[0,0,1], [1,1,1], [0,0,0]],
        'O': [[1,1], [1,1]],
        'S': [[0,1,1], [1,1,0], [0,0,0]],
        'Z': [[1,1,0], [0,1,1], [0,0,0]],
        'T': [[0,1,0], [1,1,1], [0,0,0]]
    };

    const colors = {
        'I': 'cyan',
        'O': 'yellow',
        'T': 'purple',
        'S': 'green',
        'Z': 'red',
        'J': 'blue',
        'L': 'orange'
    };

    let count = 0;
    let tetromino = null;
    let rAF = null;
    let gameOver = false;
    let gameRunning = false;

    function getRandomInt(min, max) {
        return Math.floor(Math.random() * (max - min + 1)) + min;
    }

    function generateSequence() {
        const sequence = ['I', 'J', 'L', 'O', 'S', 'T', 'Z'];
        while (sequence.length) {
            const rand = getRandomInt(0, sequence.length - 1);
            const name = sequence.splice(rand, 1)[0];
            tetrominoSequence.push(name);
        }
    }

    function getNextTetromino() {
        if (tetrominoSequence.length === 0) {
            generateSequence();
        }
        const name = tetrominoSequence.pop();
        const matrix = tetrominos[name];
        const col = playfield[0].length / 2 - Math.ceil(matrix[0].length / 2);
        const row = name === 'I' ? -1 : -2;
        return { name: name, matrix: matrix, row: row, col: col };
    }

    function rotate(matrix) {
        const N = matrix.length - 1;
        return matrix.map((row, i) => row.map((val, j) => matrix[N - j][i]));
    }

    function isValidMove(matrix, cellRow, cellCol) {
        for (let row = 0; row < matrix.length; row++) {
            for (let col = 0; col < matrix[row].length; col++) {
                if (matrix[row][col] && (
                    cellCol + col < 0 ||
                    cellCol + col >= playfield[0].length ||
                    cellRow + row >= playfield.length ||
                    playfield[cellRow + row][cellCol + col]
                )) {
                    return false;
                }
            }
        }
        return true;
    }

    function placeTetromino() {
        for (let row = 0; row < tetromino.matrix.length; row++) {
            for (let col = 0; col < tetromino.matrix[row].length; col++) {
                if (tetromino.matrix[row][col]) {
                    if (tetromino.row + row < 0) {
                        showGameOver();
                        return;
                    }
                    playfield[tetromino.row + row][tetromino.col + col] = tetromino.name;
                }
            }
        }

        for (let row = playfield.length - 1; row >= 0; ) {
            if (playfield[row].every(cell => !!cell)) {
                for (let r = row; r >= 0; r--) {
                    for (let c = 0; c < playfield[r].length; c++) {
                        playfield[r][c] = playfield[r-1] ? playfield[r-1][c] : 0;
                    }
                }
            } else {
                row--;
            }
        }
        tetromino = getNextTetromino();
    }

    function showGameOver() {
    if (rAF) {
        cancelAnimationFrame(rAF);
        rAF = null;
    }
    gameOver = true;
    gameRunning = false;
    
    const btn = document.getElementById('startStopBtn');
    btn.textContent = 'Начать игру';
    btn.classList.remove('btn-danger');
    btn.classList.add('btn-success');
    
    context.fillStyle = '#2d1b36';
    context.fillRect(canvas.width / 2 - 100, canvas.height / 2 - 30, 200, 60);
    
    context.fillStyle = '#ff9966';
    context.font = '20px "Press Start 2P", monospace';
    context.textAlign = 'center';
    context.textBaseline = 'middle';
    context.fillText('GAME OVER', canvas.width / 2, canvas.height / 2);

}

    function resetGame() {
        // Очищаем игровое поле
        for (let row = -2; row < 20; row++) {
            for (let col = 0; col < 10; col++) {
                playfield[row][col] = 0;
            }
        }
        tetrominoSequence = [];
        tetromino = getNextTetromino();
        count = 0;
        gameOver = false;
        
        // Очищаем канвас
        context.clearRect(0, 0, canvas.width, canvas.height);
    }

    function loop() {
        if (!gameRunning || gameOver) return;
        
        rAF = requestAnimationFrame(loop);
        context.clearRect(0, 0, canvas.width, canvas.height);

        // Рисуем игровое поле
        for (let row = 0; row < 20; row++) {
            for (let col = 0; col < 10; col++) {
                if (playfield[row][col]) {
                    const name = playfield[row][col];
                    context.fillStyle = colors[name];
                    context.fillRect(col * grid, row * grid, grid - 1, grid - 1);
                }
            }
        }

        // Рисуем текущую фигуру
        if (tetromino && gameRunning) {
            if (++count > 35) {
                tetromino.row++;
                count = 0;
                if (!isValidMove(tetromino.matrix, tetromino.row, tetromino.col)) {
                    tetromino.row--;
                    placeTetromino();
                }
            }

            context.fillStyle = colors[tetromino.name];
            for (let row = 0; row < tetromino.matrix.length; row++) {
                for (let col = 0; col < tetromino.matrix[row].length; col++) {
                    if (tetromino.matrix[row][col]) {
                        context.fillRect(
                            (tetromino.col + col) * grid,
                            (tetromino.row + row) * grid,
                            grid - 1, grid - 1
                        );
                    }
                }
            }
        }
    }

    function startGame() {
        if (gameRunning) {
            // Остановка игры
            gameRunning = false;
            if (rAF) {
                cancelAnimationFrame(rAF);
                rAF = null;
            }
            const btn = document.getElementById('startStopBtn');
            btn.textContent = 'Начать игру';
            btn.classList.remove('btn-danger');
            btn.classList.add('btn-success');
        } else {
            // Запуск игры
            resetGame();
            gameRunning = true;
            gameOver = false;
            const btn = document.getElementById('startStopBtn');
            btn.textContent = 'Остановить';
            btn.classList.remove('btn-success');
            btn.classList.add('btn-danger');
            loop();
        }
    }

    document.addEventListener('keydown', function(e) {
        if (!gameRunning || gameOver) return;
        
        // Предотвращаем прокрутку страницы
        if (e.key === 'ArrowUp' || e.key === 'ArrowDown' || e.key === 'ArrowLeft' || e.key === 'ArrowRight') {
            e.preventDefault();
        }
        
        // Стрелки влево и вправо
        if (e.key === 'ArrowLeft' || e.key === 'ArrowRight') {
            const col = e.key === 'ArrowLeft' ? tetromino.col - 1 : tetromino.col + 1;
            if (isValidMove(tetromino.matrix, tetromino.row, col)) {
                tetromino.col = col;
            }
        }

        // Стрелка вверх — поворот
        if (e.key === 'ArrowUp') {
            const matrix = rotate(tetromino.matrix);
            if (isValidMove(matrix, tetromino.row, tetromino.col)) {
                tetromino.matrix = matrix;
            }
        }

        // Стрелка вниз — ускорить падение
        if (e.key === 'ArrowDown') {
            const row = tetromino.row + 1;
            if (!isValidMove(tetromino.matrix, row, tetromino.col)) {
                tetromino.row = row - 1;
                placeTetromino();
                return;
            }
            tetromino.row = row;
        }
    });

    const startStopBtn = document.getElementById('startStopBtn');
startStopBtn.addEventListener('click', function() {
    if (gameRunning) {
        // Остановка игры
        gameRunning = false;
        if (rAF) {
            cancelAnimationFrame(rAF);
            rAF = null;
        }
        startStopBtn.textContent = 'Начать игру';
        startStopBtn.classList.remove('btn-danger');
        startStopBtn.classList.add('btn-success');
    } else {
        // Запуск игры
        if (gameOver) {
            resetGame();
        }
        gameRunning = true;
        gameOver = false;
        startStopBtn.textContent = 'Остановить';
        startStopBtn.classList.remove('btn-success');
        startStopBtn.classList.add('btn-danger');
        loop();
    }
});

    // Инициализация (игра не запущена)
    tetromino = getNextTetromino();