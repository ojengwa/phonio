angular.module("Softphone", []);

function PhoneCtrl($scope) {
    var currentConnection;

    $scope.ready = function() {
        return "ready" === $scope.state
    };

    $scope.talking = function() {
        return "talking" === $scope.state
    };

    $scope.ringing = function() {
        return "ringing" === $scope.state
    };

    $scope.setState = function(state) {
        $scope.state = state;
    };


    $scope.pickup = function() {
        currentConnection.accept();
        $scope.setState("talking");
    };

    $scope.hangup = function() {
        $scope.setState("ready");
        if (currentConnection.status() === "open") {
            currentConnection.disconnect();
        }
    };

    Twilio.Device.incoming(function(connection) {
        currentConnection = connection;
        $scope.$apply(function(scope) {
            scope.setState("ringing");
        });
    });

    Twilio.Device.disconnect(function(connection) {
        if ($scope.$$phase === "$apply") return;

        $scope.$apply(function(scope) {
            scope.hangup();
        });
    });

    Twilio.Device.cancel(function(connection) {
        $scope.$apply(function(scope) {
            scope.setState("ready");
        });
    });

    Twilio.Device.ready(function(device) {
        $scope.$apply(function(scope) {
            scope.setState("ready");
        });
    });
};
