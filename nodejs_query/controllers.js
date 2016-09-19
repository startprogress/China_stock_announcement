var connectionpool = require('./connection');
var url = require('url');
var fs = require('fs');
var logger = require('./log').logger('normal');
var func = require('./func');



//主页面,显示当天的股票列表
exports.view = function(req, res){
  var querySql = 'SELECT Annc_Key, Symbol, Abbr_Name, Title, Annc_Date, Annc_Time, Format, Valid FROM sse_annc_list WHERE Annc_date = ?';
  var values = [func.currentDate()];
  connectionpool.getConnection(function(err, connection) {
    if (err) {
      console.error('CONNECTION error: ',err);
      res.statusCode = 503;
      res.send({
        result: 'error',
        err:    err.code
      });
      res.end();
    } else {
      connection.query(querySql, values, function(err, rows) {
        if (err) {
          console.error(err);
          res.statusCode = 500;
          res.send({
             result: 'error',
             err: err.code
          });
          res.end();
        }
        res.render('index', {
          announcements: rows,
          annctype: "sse"
        });
        logger.info('showQuery: ' + values + '  clientIP: ' + req.connection.remoteAddress);
        connection.release();
      });
    }
  });
};


//公告列表显示
exports.showQuery=function(req,res){
  var params = url.parse(req.url, true).query;
  var querySql;
  if (params.anncType === 'sse'){
    querySql = 'SELECT Annc_Key, Symbol, Abbr_Name, Title, Annc_Date, Annc_Time, Format, Valid FROM sse_annc_list WHERE ';
  }
  if (params.anncType === 'csrc'){
    querySql = 'SELECT Annc_Key, Symbol, Regu_Type, Title, Annc_Date, Annc_Time, Format, Valid FROM csrc_annc_list WHERE ';
  }
  var gets = [];
  if (params.symbol !== '' && params.symbol !== undefined){
    querySql += "symbol = ?";
    gets.push(params.symbol);
    if (params.dateRange !== '' && params.symbol !== undefined){
      querySql += ' and ';
    }
  }
  if (params.dateRange.length === 10){
    querySql += "Annc_date = ?";
    gets.push(params.dateRange);
  }
  if (params.dateRange.length === 21){
    querySql += "Annc_date >= ? and Annc_date <= ?";
    gets.push(params.dateRange.substring(0,10));
    gets.push(params.dateRange.substring(11,22));
  }
  connectionpool.getConnection(function(err, connection) {
    if (err) {
      console.error('CONNECTION error: ',err);
      res.statusCode = 503;
      res.send({
        result: 'error',
        err:    err.code
      });
      res.end();
    } else {
      connection.query(querySql, gets, function(err, rows) {
        if (err) {
          console.error(err);
          res.statusCode = 500;
          res.send({
             result: 'error',
             err: err.code
          });
          res.end();
        }
        res.render('index', {
          announcements: rows,
          annctype: params.anncType
        });
        logger.info('showQuery: ' + gets + '  clientIP: ' + req.connection.remoteAddress);
        connection.release();
      });
    }
  });
};


//公告列表查询
exports.listQuery=function(req,res){
  var params = url.parse(req.url, true).query;
  var querySql;
  if (params.anncType === 'sse'){
    querySql = 'SELECT Annc_Key, Symbol, Abbr_Name, Title, Annc_Date, Annc_Time, Format, Valid FROM sse_annc_list WHERE ';
  }
  if (params.anncType === 'csrc'){
    querySql = 'SELECT Annc_Key, Symbol, Regu_Type, Title, Annc_Date, Annc_Time, Format, Valid FROM csrc_annc_list WHERE ';
  }
  var gets = [];
  if (params.symbol !== '' && params.symbol !== undefined){
    querySql += "symbol = ?";
    gets.push(params.symbol);
    if (params.dateRange !== '' && params.symbol !== undefined){
      querySql += ' and ';
    }
  }
  if (params.dateRange.length === 10){
    querySql += "Annc_date = ?";
    gets.push(params.dateRange.substring(0,10));
  }
  if (params.dateRange.length === 21){
    querySql += "Annc_date >= ? and Annc_date <= ?";
    gets.push(params.dateRange.substring(0,10));
    gets.push(params.dateRange.substring(11,22));
  }
  connectionpool.getConnection(function(err, connection) {
    if (err) {
      console.error('CONNECTION error: ',err);
      res.statusCode = 503;
      res.send({
        result: 'error',
        err:    err.code
      });
      res.end();
    } else {
      connection.query(querySql, gets, function(err, rows) {
        if (err) {
          console.error(err);
          res.statusCode = 500;
          res.send({
             result: 'error',
             err: err.code
          });
          res.end();
        }
        res.send({
          'totalNum': rows.length,
          'announcements': rows
        });
        res.end();
        logger.info('listQuery: ' + gets + '  clientIP: ' + req.connection.remoteAddress);
        connection.release();
      });
    }
  });
};




//公告下载
exports.fileDownload=function(req,res){
  var params = url.parse(req.url, true).query;
  var anncKey = params.anncKey;
  var format = params.format;
  var filePath;
  if (params.anncType === 'sse'){
    filePath = '/data/annc_data/sse/content/' + anncKey.substring(6,10) + '/' + anncKey.substring(10, 12) + '/' + params.anncKey + '.' + format.toLowerCase();
  }else{
    filePath = '/data/annc_data/csrc/content/' + anncKey.substr(-10 ,4) + '/' + anncKey.substr(-6, 2) + '/' + params.anncKey + '.' + format.toLowerCase();
  }
  res.download(filePath);
  logger.info('fileDownload: ' + filePath + '  clientIP: ' + req.connection.remoteAddress);
};

//公告读取
exports.readFile=function(req, res){
  var mimeType ={
    "pdf": "application/pdf;charset = utf-8",
    "doc": "application/msword;charset = utf-8",
    "txt": "text/plain;charset = utf-8"
  };  
  var params = url.parse(req.url, true).query;
  var anncKey = params.anncKey;
  var format = params.format.toLowerCase();
  var filePath = "";
  if (params.anncType === 'sse'){
    filePath = '/data/annc_data/sse/content/' + anncKey.substring(6,10) + '/' + anncKey.substring(10, 12) + '/' + anncKey + '.' + format;
    console.log(filePath);
  }else{
    filePath = '/data/annc_data/csrc/content/' + anncKey.substr(-10,4) + '/' + anncKey.substr(-6, 2) + '/' + anncKey + '.' + format;
  }
  var contentType = mimeType[format] || "text/plain";

  fs.exists(filePath, function (exists) {
    if (!exists) {
      res.writeHead(404, {'Content-Type': 'text/plain;charset = utf8'});
      res.write(anncKey + "." + format + "   文件不存在" );
      res.end();
    } else {
      fs.readFile(filePath, "binary", function(err, file) {
        if (err) {
          res.writeHead(500, {'Content-Type': 'text/plain'});
          res.end(err);
        } else {
          res.writeHead(200, {'Content-Type': contentType});
          res.write(file, "binary");
          res.end();
        }
      });
    }
  });

  //fs.createReadStream(filePath, {encoding: 'utf-8'}).pipe(res);
  logger.info('readFile: ' + filePath + '  clientIP: ' + req.connection.remoteAddress);
};
