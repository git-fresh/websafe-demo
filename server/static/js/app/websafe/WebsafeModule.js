(function(){

var module = angular.module('websafe_module', [
    'map_service',
    'websafe_service',
    'ui.bootstrap',
    'ui.select2',
    'websafe_config',
    'ngSanitize'
]);
/*
module.controller('ModalCtrl', [
    '$scope',
    '$modalInstance',
    function($scope, $modalInstance){
        $scope.viewPdf = function () {
            
            $modalInstance.close();
        };

        $scope.close = function () {
            $modalInstance.dismiss('cancel');
        };
    }
]);
*/

module.controller('WebsafeCtrl', [
    '$scope',
    '$http',
    '$window',
    '$rootScope',
    'MapFunctions',
    'WebsafeFunctions',
    'WebsafeConfig',
    function($scope, $http, $window, $rootScope, MapFunctions, WebsafeFunctions, WebsafeConfig){
        $scope.init = function(){
            $scope.help_toggle = false;
            $scope.hazard = {};
            $scope.exposure = {};
            $scope.impact_functions = WebsafeConfig.impact_functions;
            $scope.impact = {impact_function : WebsafeConfig.impact_functions[0].value};
            $scope.html = '';
            $scope.resultReady = false;
            $scope.l = null;
            MapFunctions.removeAllWMSLayers();
        };
        $scope.init();

        $scope.exposure_selector = { width: '250px' };
        $scope.hazard_selector = { width: '250px' };
        
        $scope.showHelp = function(){ $scope.help_toggle = true; };
        $scope.hideHelp = function(){ $scope.help_toggle = false; };

        /*
        // TODO: modal init
        // This function creates and opens a modal instance
        $scope.open = function () {
            var modalInstance = $modal.open({
                templateUrl: 'calculateResults.html',
                controller: 'ModalCtrl',
                scope: $scope
            });
        };

        // This is a listener for changes in layer(exposure or hazard)
        var layer_change_listener = $rootScope.$on('layer changed', function(event, layer_info){
            if (layer_info.type == 'hazard'){
                $scope.hazard.hazard_name = layer_info.name;
                $scope.hazard.hazard_title = layer_info.title;
                $scope.hazard.layer = layer_info.layer;
            }else if (layer_info.type == 'exposure'){
                $scope.exposure.exposure_name = layer_info.name;
                $scope.exposure.exposure_title = layer_info.title;
                $scope.exposure.layer = layer_info.layer;
                $scope.exposure.legend = layer_info.legendUrl;
                $scope.exposure.showLegend = true;
                $('.legend_exposure').draggable();
            }
            $rootScope.map.addLayer(layer_info.layer);
        });
        $scope.$on('$destroy', layer_change_listener);      // this unbinds the listener when the scope is destroyed
        */

        MapFunctions.fetchLayers(WebsafeConfig.exposure_url)
            .then(function(data){ $scope.exposure_list = data; });
        MapFunctions.fetchLayers(WebsafeConfig.hazard_url)
            .then(function(data){ $scope.hazard_list = data; });

        //
        $scope.hazardChanged = function(hazard){
            if (hazard.name != ''){
                if ($scope.hazard.layer != null){
                    $rootScope.map.removeLayer($scope.hazard.layer);
                }

                $scope.hazard.resource_name = "hazard:" + hazard.name;
                MapFunctions.fetchBbox($scope.hazard.resource_name)
                    .then(function(extent){
                        console.log(extent);
                        MapFunctions.zoomToExtent(extent);
                    });

                $scope.hazard.layer = MapFunctions.fetchWMSLayer($scope.hazard.resource_name);
                //$scope.hazard.legend = MapFunctions.getLegend(data.resource_name);
                $rootScope.map.addLayer($scope.hazard.layer);

                //make legends function by getting sld
                //$('.legend_hazard').draggable();
                //$scope.hazard.showLegend = true;
            }
        };

        $scope.exposureChanged = function(exposure){
            var data = {};
        };

        $scope.calculate = function(){
            var params = {};

            if ($scope.exposure.data == null){
                alert('Please select exposure layer.');
            }else if ($scope.hazard.data == null){
                alert('Please select hazard layer.');
            }else{
                $scope.l = Ladda.create( document.querySelector( '.ladda-button' ) );
                $scope.l.start();

                WebsafeFunctions.calculate(params)
                .then(function(data){
                    $scope.l.stop();

                    $scope.resultReady = true;
                    $scope.html = data.html;
                    
                    //$scope.open();              // open the result modal
                }, function(status){
                    $scope.l.stop();
                    console.log('Error: ' + status);
                });
                /*
                if (($scope.exposure.exposure_title != '') || ($scope.hazard.hazard_title != '')){

                    $http.get(calculate_url, {params: {
                        'exposure_title' : $scope.exposure.exposure_title,
                        'hazard_title' : $scope.hazard.hazard_title,
                        'impact_function' : $scope.impact.impact_function
                    }}).success(function(data, status, headers, config) {
                        $scope.impact.impact_resource = data.layer.resource;

                        MapFunctions.removeAllWMSLayers();
                        $scope.hazard.showLegend = false;
                        $scope.exposure.showLegend = false;

                        var impact_layer = MapFunctions.fetchWMSLayer(data.layer.resource);
                        $scope.impact.legend = MapFunctions.getLegend(data.layer.resource);
                        $rootScope.map.addLayer(impact_layer);
                        $scope.impact.showLegend = true;
                        $('.legend_impact').draggable();
                        MapFunctions.zoomToExtent($rootScope.extent);
                    });
                }else{
                    alert('An error has occurred!');
                }
                */
            }
        };

        // initialize the websafe window height
        var mapHeight = $window.innerHeight - 
                        $rootScope.navbar.height() -
                        $rootScope.footer.height();
        var websafeHeight = mapHeight - $rootScope.toolbar.height();
        $('.websafe_window').css({'height': websafeHeight});
    }
]);

})();