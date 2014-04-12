(function(){
var module = angular.module('window_module', []);

/***
This directive allows access to variables windowHeight and windowWidth 
in $scope whenever the window is resized if the attribute 'resizable' is added to any div


module.directive('resizable', function($window){
    return function($scope) {
        $scope.initializeWindowSize = function() {
            $scope.windowHeight = $window.innerHeight;
            $scope.windowWidth = $window.innerWidth;
        };
        $scope.initializeWindowSize();
        
        angular.element($window).bind('resize', function() {
            $scope.initializeWindowSize();
            $scope.$apply();
        });
    };
});
***/

})();