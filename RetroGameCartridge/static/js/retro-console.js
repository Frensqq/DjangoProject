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

// Функция для обновления экрана
function updateScreen(screenContent, message, isSpecial = false) {
    screenContent.innerHTML = message;
    screenContent.classList.add('screen-text-animation');
    setTimeout(() => {
        screenContent.classList.remove('screen-text-animation');
    }, 300);
    
    // Добавляем звуковой эффект (пиканье)
    playBeep();
}

// Функция для воспроизведения звука
function playBeep() {
    try {
        const audioContext = new (window.AudioContext || window.webkitAudioContext)();
        const oscillator = audioContext.createOscillator();
        const gainNode = audioContext.createGain();
        
        oscillator.connect(gainNode);
        gainNode.connect(audioContext.destination);
        
        oscillator.frequency.value = 880;
        gainNode.gain.value = 0.1;
        
        oscillator.start();
        gainNode.gain.exponentialRampToValueAtTime(0.00001, audioContext.currentTime + 0.1);
        oscillator.stop(audioContext.currentTime + 0.1);
        
        // Закрываем контекст после звука
        setTimeout(() => audioContext.close(), 200);
    } catch(e) {
        // Если звук не поддерживается, просто игнорируем
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
            counterSpan.textContent = clickCount;
            
            const factIndex = parseInt(this.getAttribute('data-fact'));
            const fact = retroFacts[factIndex % retroFacts.length];
            
            updateScreen(screenContent, `🎮 Кнопка ${this.textContent} нажата!<br>📖 ${fact}`);
        });
    });
    
    // Обработчики для D-Pad
    document.querySelectorAll('.dpad-btn').forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.stopPropagation();
            clickCount++;
            counterSpan.textContent = clickCount;
            
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
            
            updateScreen(screenContent, `🎮 Нажато: ${direction.toUpperCase()}<br>${message}`);
        });
    });
    
    // Дополнительная анимация: случайный факт при наведении на консоль
    const consoleCard = document.getElementById('retroConsole');
    let hoverTimeout;
    
    consoleCard.addEventListener('mouseenter', () => {
        hoverTimeout = setTimeout(() => {
            const randomFact = retroFacts[Math.floor(Math.random() * retroFacts.length)];
            updateScreen(screenContent, `🤔 Знаете ли вы?<br>${randomFact}`);
        }, 2000);
    });
    
    consoleCard.addEventListener('mouseleave', () => {
        clearTimeout(hoverTimeout);
        updateScreen(screenContent, `Нажми на кнопки!<br>👇👇👇`);
    });
    
    // Эффект при загрузке страницы
    setTimeout(() => {
        updateScreen(screenContent, '🎮 Ретро-консоль готова!<br>Нажми на кнопки!');
    }, 500);
}

// Запускаем инициализацию после загрузки страницы
document.addEventListener('DOMContentLoaded', initRetroConsole);