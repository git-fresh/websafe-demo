(function(){

var module = angular.module('websafe_module', [
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
    '$window',
    '$rootScope',
    'MapFunctions',
    'WebsafeFunctions',
    'WebsafeConfig',
    function($scope, $window, $rootScope, MapFunctions, WebsafeFunctions, WebsafeConfig){
        $scope.init = function(){
            $scope.help_toggle = false;
            $scope.hazard = { type: 'haz' };
            $scope.exposure = { type: 'exp' };
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
        */

        MapFunctions.fetchLayers(WebsafeConfig.exposure_url)
            .then(function(data){ $scope.exposure_list = data; });
        MapFunctions.fetchLayers(WebsafeConfig.hazard_url)
            .then(function(data){ $scope.hazard_list = data; });

        $scope.layerChanged = function(layer){
            if (layer.name != ''){
                if (layer.layer != null){
                    $rootScope.map.removeLayer(layer.layer);
                }

                layer.resource_name = layer.type == "haz" ?
                    "hazard:" + layer.name : "exposure:" + layer.name;
                MapFunctions.fetchBbox(layer.resource_name)
                    .then(function(extent){
                        MapFunctions.zoomToExtent(extent);
                    });

                layer.layer = MapFunctions.fetchWMSLayer(layer.resource_name);
                layer.legend = MapFunctions.getLegend(layer.resource_name);
                $rootScope.map.addLayer(layer.layer);

                //make legends function by getting sld
                $('.legend_hazard').draggable();
                $('.legend_exposure').draggable();
                layer.showLegend = true;
            }
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