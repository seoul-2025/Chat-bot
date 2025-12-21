const fs = require('fs');

const filePath = 'd:/sedaily/Project/external_one/src/features/chat/components/UserMessage.jsx';
let content = fs.readFileSync(filePath, 'utf8');

// Replace fontFamily in UserMessage with gothic font
content = content.replace(/fontFamily: '"Tiempos Text", "Source Serif 4", "Noto Serif KR", serif'/g, 'fontFamily: \'-apple-system, BlinkMacSystemFont, "Malgun Gothic", "맑은 고딕", sans-serif\'');

fs.writeFileSync(filePath, content);
console.log('UserMessage font changed to gothic');