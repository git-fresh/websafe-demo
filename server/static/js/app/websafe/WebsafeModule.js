(function(){

var module = angular.module('websafe_module', [
    'utils',
    'config',
    'map_service',
    'ui.bootstrap',
    'ngSanitize'
]);

module.controller('ModalCtrl', [
    '$scope',
    '$modalInstance',
    function($scope, $modalInstance){
        $scope.viewPdf = function () {
            window.open('/api/pdf?q=' + $scope.$parent.impact.impact_resource);
            $modalInstance.close();
        };

        $scope.close = function () {
            $modalInstance.dismiss('cancel');
        };
    }
]);

module.controller('WebsafeCtrl', [
    '$scope',
    '$window',
    '$rootScope',
    '$http',
    'MapFunctions',
    '$modal',
    'Config',
    function($scope, $window, $rootScope, $http, MapFunctions, $modal, Config){
        $scope.init = function(){
            $scope.help_toggle = false;
            $scope.hazard = {};
            $scope.exposure = {};
            $scope.impact_functions = Config.impact_functions;
            $scope.impact = {impact_function : Config.impact_functions[0].value};
            $scope.html = '';
            $scope.resultReady = false;
            $scope.l = null;
            MapFunctions.removeAllWMSLayers();
        };
        $scope.init();

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
                if ($scope.hazard.layer != null){
                    $rootScope.map.removeLayer($scope.hazard.layer);
                }
                $scope.hazard.hazard_name = layer_info.name;
                $scope.hazard.hazard_title = layer_info.title;
                $scope.hazard.layer = layer_info.layer;
                $scope.hazard.legend = layer_info.legendUrl;
                $scope.hazard.showLegend = true;
                $('.legend_hazard').draggable();
            }else if (layer_info.type == 'exposure'){
                if ($scope.exposure.layer != null){
                    $rootScope.map.removeLayer($scope.exposure.layer);
                }
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
        
        $scope.showHelp = function(){
            $scope.help_toggle = true;
        };
        
        $scope.hideHelp = function(){
            $scope.help_toggle = false;
        };

        // This uses the server's calculate api
        $scope.calculate = function(){
            var calculate_url = 'http://localhost:5000/api/calculate';
            if ($scope.exposure.exposure_name == null){
                alert('Please select exposure layer.');
            }else if ($scope.hazard.hazard_name == null){
                alert('Please select hazard layer.');
            }else{
                if (($scope.exposure.exposure_title != '') || ($scope.hazard.hazard_title != '')){
                    $scope.l = Ladda.create( document.querySelector( '.ladda-button' ) );
                    $scope.l.start();

                    $http.get(calculate_url, {params: {
                        'exposure_title' : $scope.exposure.exposure_title,
                        'hazard_title' : $scope.hazard.hazard_title,
                        'impact_function' : $scope.impact.impact_function
                    }}).success(function(data, status, headers, config) {
                        $scope.l.stop();
                        $scope.resultReady = true;
                        $scope.html = data.html;
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
                        $scope.open();              // open the result modal
                    }).error(function(data, status, headers, config) {
                        $scope.l.stop();
                        alert('An internal server error(500) has occurred!');
                    });
                }else{
                    alert('An error has occurred!');
                }
            }
        };
        
        var mapHeight = $window.innerHeight - 
                        $rootScope.navbar.height() -
                        $rootScope.footer.height();
        var sideMenuHeight = mapHeight - $rootScope.toolbar.height();
        $('.inasafe_window').css({'overflow': 'auto', 'height': sideMenuHeight});
    }
]);

module.controller('FileTreeCtrl', [
    '$scope',
    '$element',
    '$http',
    '$rootScope',
    'Base64',
    'MapFunctions',
    function ($scope, $element, $http, $rootScope, Base64, MapFunctions){
        var base_url = 'http://localhost:';
        var url = base_url + '8080/geoserver/rest/layers.json';
        var api_url = 'api/layers';

        // populate the file tree with all the available layers from geoserver
        $http.get(api_url, {params: {'api': url }})
        .success(function(data, status, headers, config) {
            var layers = data.layers.layer;
            $scope.layers = layers;
        });

        $scope.showLayer = function(layer){
            var resource_link = '';
            var layer_info = {name : layer.name};
            
            $http.get(api_url, {params: {'api': layer.href }})
            .success(function(data, status, headers, config) {
                resource_link = data.layer.resource.href;

                if (resource_link.indexOf("/hazard/") != -1){
                    layer_info.type = 'hazard';
                }else if (resource_link.indexOf("/exposure/") != -1){
                    layer_info.type = 'exposure';
                }else if (resource_link.indexOf("/impact/") != -1){
                    layer_info.type = 'impact';
                }else{
                    layer_info.type = 'exposure';
                }
            }).then(function(){
                if (layer_info.type == 'impact'){
                    alert('Please choose a hazard layer and exposure layer combination.');
                }else{
                    $http.get(api_url, {params: {'api': resource_link }})
                    .success(function(data, status, headers, config) {
                        if ((data.featureType == null) && (data.coverage == null)){
                            alert("Layer is not of type exposure or hazard.");
                        }else if (data.coverage != null){
                            var bbox = data.coverage.nativeBoundingBox;
                            var extent = [bbox.minx, bbox.miny, bbox.maxx, bbox.maxy];
                            $rootScope.extent = extent;
                            layer_info.layer = MapFunctions.fetchWMSLayer(layer.name);
                            layer_info.legendUrl = MapFunctions.getLegend(layer.name);
                            MapFunctions.zoomToExtent(extent);

                            layer_info.title = data.coverage.title;
                            $rootScope.$emit('layer changed', layer_info);

                        }else{
                            var bbox = data.featureType.nativeBoundingBox;
                            var extent = [bbox.minx, bbox.miny, bbox.maxx, bbox.maxy];
                            if (layer_info.type == 'exposure'){
                                $rootScope.extent = extent;
                            }

                            layer_info.layer = MapFunctions.fetchWMSLayer(layer.name);
                            layer_info.legendUrl = MapFunctions.getLegend(layer.name);
                            MapFunctions.zoomToExtent(extent);

                            layer_info.title = data.featureType.title;
                            $rootScope.$emit('layer changed', layer_info);
                        }
                    });
                }
            });
        }
    }
]);

})();