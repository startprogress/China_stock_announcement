module.exports = function(app){
  var controllers = require('./controllers');
  app.get('/', controllers.view);
  app.get('/query', controllers.listQuery);
  app.get('/show', controllers.showQuery);
  app.get('/down', controllers.fileDownload);
  app.get('/read', controllers.readFile);
};
