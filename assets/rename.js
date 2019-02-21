const fs = require('fs');

const names = JSON.parse(fs.readFileSync('./names.json'));

Object.keys(names).map(old => {
  if (names[old]) {
    fs.renameSync(`parts-${old}.png`, `${names[old]}.png`);
  }
});

