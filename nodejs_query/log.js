var log4js = require('log4js');
log4js.configure({
  appenders: [
    {
      type: 'file', 
      filename: 'logs/server.log', 
      maxLogSize: 1024*1024,
      backups:4,
      category: 'normal' 
    }
  ]
});

exports.logger=function(name){
  var logger = log4js.getLogger(name);
  logger.setLevel('INFO');
  return logger;
};
