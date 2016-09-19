var mysql = require('mysql');
var connectionpool = mysql.createPool({
  host : '',
  user : '',
  password : '',
  database : 'annc'
});
module.exports = connectionpool;
