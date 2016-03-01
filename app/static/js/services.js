var app = angular.module('flightPredict')

app.factory('Airport', ["$resource",
  function ($resource) {
    return $resource('/status/:id',
                      { id: "@id"},
                      {
                        'query':  {method:'GET', isArray:false},
                      });
}]);

app.factory('Predict', ["$resource",
  function ($resource) {
    return $resource('/predict/:id',
                      { id: "@id"},
                      {
                        'query':  {method:'GET', isArray:false},
                      });
}]);
