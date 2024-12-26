// Configuration
const canvas = document.getElementById('matrix-canvas');
const ctx = canvas.getContext('2d');
const fontSize = 18;
const columns = Math.floor(window.innerWidth / fontSize);
const characters = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZあいうえおかきくけこさしすせそたちつてとなにぬねのはひふへほまみむめもやゆよらりるれろわをンャュョキャキュキョシャシュショチャチュチョニャニュニョヒャヒュヒョミャミュミョリャリュリョابتثجحخدذرزسشصضطظعغفقكلمنهويءآأؤإئًٌٍَُِّْ1234567890!@#$%^&*()_-+=[]{}|;:,.<>/?~`\'"\\çéèêëîïôöùü'.split('').filter((c) => /\S/.test(c)).join('').repeat(4).substring(0, 200);

const drops = [];
const speed = 100;

canvas.width = window.innerWidth;
canvas.height = window.innerHeight;

for (let i = 0; i < columns; i++) {
  drops[i] = 1;
}

function draw() {
  ctx.fillStyle = 'rgba(0, 0, 0, 0.1)';
  ctx.fillRect(0, 0, canvas.width, canvas.height);

  ctx.fillStyle = '#0F0';
  ctx.font = `${fontSize}px monospace`;

  for (let i = 0; i < drops.length; i++) {
    const index = Math.floor(Math.random() * characters.length);
    const character = characters[index];

    if (drops[i] === 1) {
      ctx.fillStyle = '#0F0';
    } else {
      ctx.fillStyle = 'rgba(0, 255, 0, 0.8)';
    }

    ctx.fillText(character, i * fontSize, drops[i] * fontSize);

    if (drops[i] * fontSize > canvas.height && Math.random() > 0.975) {
      drops[i] = 0;
    }

    drops[i]++;
  }
}

function update() {
  draw();
  setTimeout(update, speed);
}

update();
