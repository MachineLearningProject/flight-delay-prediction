var flightPredict = angular.module('flightPredict', ['ngRoute', 'ngResource']);

flightPredict.config(function ($routeProvider) {

  $routeProvider
    .when('/', {
      templateUrl: 'static/partials/main.html'
    })
    .otherwise({redirectTo: '/'});

});
