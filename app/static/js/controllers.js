var app = angular.module('flightPredict')

app.controller('mainController', ['$scope', 'Airport', 'Predict',
  function ($scope, Airport, Predict) {
    var response = Airport.query(function(){
      $scope.airportStatuses = response.items;
    });
    $scope.airportPredictions = Predict.query();
    var directions = {
      "0,1" : "North",
      "0.707,0.707" : "Northeast",
      "1,0" : "East",
      "0.707,-0.707" : "Southeast",
      "0,-1" : "South",
      "-0.707,-0.707" : "Southwest",
      "-1,0" : "West",
      "-0.707,0.707" : "Northwest",
      "0,0" : "Variable",
    }
    $scope.transformWindDirection = function(x, y) {
      var key = String(x) + "," + String(y);
      return directions[key];
    };

    $scope.orderPredicate = 'time';
    $scope.orderReverse = true;
    $scope.order = function(orderPredicate) {
      $scope.orderReverse = ($scope.orderPredicate === orderPredicate) ? !$scope.orderReverse : false;
      $scope.orderPredicate = orderPredicate;
    };

}]);
