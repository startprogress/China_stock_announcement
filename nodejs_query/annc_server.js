var express = require('express');
var app = express();
//前端渲染为html
var ejs = require('ejs');
app.engine('.html', ejs.__express);
app.set('view engine', 'html');
app.set('views', __dirname + '/views');
//路径设置
app.use(express.static(__dirname + '/public'));
require('./routes')(app);
app.listen(3000);
console.log('Listening on port 3000');
