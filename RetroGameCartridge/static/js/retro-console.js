// Факты о ретро-играх
const retroFacts = [
    "🎮 Первая игра Super Mario Bros вышла в 1985 году!",
    "🕹️ Самой продаваемой консолью всех времен является PlayStation 2 (155 млн копий)!",
    "👾 Тетрис был создан советским программистом Алексеем Пажитновым в 1984 году!",
    "⚡ Pong (1972) считается первой коммерчески успешной видеоигрой!",
    "🌟 Pac-Man был создан, чтобы привлечь в аркады девушек!",
    "🎵 Саундтрек к The Legend of Zelda написал один человек за 3 недели!",
    "💰 Самая дорогая игра - Stadium Events (NES), стоит более $40,000!",
    "🎨 Mario изначально назывался Jumpman и был плотником!"
];

let clickCount = 0;
let audioContext = null;

// Функция для получения случайного факта
function getRandomFact() {
    const randomIndex = Math.floor(Math.random() * retroFacts.length);
    return retroFacts[randomIndex];
}

// Функция для обновления экрана
function updateScreen(screenContent, message) {
    if (!screenContent) return;
    screenContent.innerHTML = message;
    screenContent.classList.add('screen-text-animation');
    setTimeout(() => {
        screenContent.classList.remove('screen-text-animation');
    }, 300);
    
    playBeep();
}

// Функция для воспроизведения звука
function playBeep() {
    try {
        if (!audioContext) {
            audioContext = new (window.AudioContext || window.webkitAudioContext)();
        }
        
        const oscillator = audioContext.createOscillator();
        const gainNode = audioContext.createGain();
        
        oscillator.connect(gainNode);
        gainNode.connect(audioContext.destination);
        
        oscillator.frequency.value = 880;
        gainNode.gain.value = 0.1;
        
        oscillator.start();
        gainNode.gain.exponentialRampToValueAtTime(0.00001, audioContext.currentTime + 0.1);
        oscillator.stop(audioContext.currentTime + 0.1);
        
        if (audioContext.state === 'suspended') {
            audioContext.resume();
        }
    } catch(e) {
        console.log("Audio not supported");
    }
}

// Инициализация консоли
function initRetroConsole() {
    const screenContent = document.getElementById('screenContent');
    const counterSpan = document.getElementById('clickCounter');
    
    if (!screenContent) return;
    
    // Обработчики для кнопок A, B, X, Y
    document.querySelectorAll('.retro-btn').forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.stopPropagation();
            clickCount++;
            if (counterSpan) counterSpan.textContent = clickCount;
            
            // Показываем случайный факт
            const randomFact = getRandomFact();
            const buttonText = this.textContent;
            
            updateScreen(screenContent, `📖 ${randomFact}`);
        });
    });
    
    // Обработчики для D-Pad
    document.querySelectorAll('.dpad-btn').forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.stopPropagation();
            clickCount++;
            if (counterSpan) counterSpan.textContent = clickCount;
            
            const direction = this.getAttribute('data-direction');
            let message = '';
            
            switch(direction) {
                case 'up':
                    message = '⬆️ Вверх! Двигаемся к вершинам ретро-гейминга!';
                    break;
                case 'down':
                    message = '⬇️ Вниз! Погружаемся в историю видеоигр!';
                    break;
                case 'left':
                    message = '⬅️ Влево! Возвращаемся в 80-е и 90-е!';
                    break;
                case 'right':
                    message = '➡️ Вправо! Мчимся сквозь время!';
                    break;
            }
            
            // Добавляем случайный факт для D-Pad
            const randomFact = getRandomFact();
            updateScreen(screenContent, `<br>${message}<br>📖 ${randomFact}`);
        });
    });
    
    // Дополнительная анимация: случайный факт при наведении на консоль
    const consoleCard = document.getElementById('retroConsole');
    let hoverTimeout;
    

    
    // Эффект при загрузке страницы
    setTimeout(() => {
        updateScreen(screenContent, '🎮 Ретро-консоль готова!<br>Нажми на кнопки!');
    }, 500);
}

// Запускаем инициализацию после загрузки страницы
document.addEventListener('DOMContentLoaded', initRetroConsole);