const fs = require('fs');

const filePath = 'd:/sedaily/Project/external_one/src/features/chat/components/AssistantMessage.jsx';
let content = fs.readFileSync(filePath, 'utf8');

// Replace all occurrences of fontSize: "19px" with fontSize: "18px"
content = content.replace(/fontSize: "19px"/g, 'fontSize: "18px"');

fs.writeFileSync(filePath, content);
console.log('Font size updated from 19px to 18px');