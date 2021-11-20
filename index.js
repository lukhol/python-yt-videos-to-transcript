const text = require('./results.json');

console.log('All objects: ' + Object.keys(text).length);

const withWykop = Object.entries(text)
    .map(arr => ({ key: arr[0], value: arr[1] }))
    .filter(a => a.value.includes('wykop'));

console.log('All with wykop: ' + withWykop.length);

console.log(text['o_rxgLXPBMc'])

