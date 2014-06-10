(function(){
var module = angular.module('noahApp', [
    'map_module',
    'toolbar_module',
    'sidebar_module',
    'websafe_module',
    'ngRoute',
    'ngAnimate'
]);

//configure the routing for the sidebar ng-view    
module.config([
    '$routeProvider',
    function($routeProvider){
        $routeProvider
        .when('/', {
            controller: 'SidebarCtrl'
        }).when('/websafe', {
            controller: 'WebsafeCtrl',
            templateUrl:'/api/websafe'
        }).otherwise({redirectTo:'/'});
    }
]);
    
module.run(
    function($rootScope, $window){
        //set some global defaults
        $rootScope.map = null;
        $rootScope.navbar = $('.navbar');
        $rootScope.footer = $('#footer');
        $rootScope.mapdiv = $('#map');
        $rootScope.toolbar = $('#toolbar');
    
        function initWindowSize(){
            $rootScope.windowHeight = $window.innerHeight;
            $rootScope.windowWidth = $window.innerWidth;
        }; 
        
        initWindowSize();
        
        angular.element($window).bind('resize', function(){
            initWindowSize();
            $rootScope.$apply();
        });
        
        //this updates the map and other UI size when the window is resized
        $rootScope.$watch('windowHeight', function(newVal, oldVal){
            var mapHeight = newVal - 
                            $rootScope.navbar.height() -
                            $rootScope.footer.height();
            var sideMenuHeight = mapHeight - $rootScope.toolbar.height();
            var websafeHeight = mapHeight - $rootScope.toolbar.height();
        
            $rootScope.mapdiv.height(mapHeight);
            $rootScope.map.updateSize();
            if ($('#sidemenu')) { 
                $('#sidemenu').css('height', sideMenuHeight); 
            }
            
            if ($('.websafe_window')) { 
                $('.websafe_window').css({'overflow': 'auto', 'height': websafeHeight});
            }
        });
    }
);
})();