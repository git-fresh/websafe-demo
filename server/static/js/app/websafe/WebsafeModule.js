(function(){

var module = angular.module('websafe_module', [
    'utils',
    'config',
    'map_service',
    'ui.bootstrap',
    'ngSanitize'
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
            $scope.loaded = true;
            $scope.l = null;
            MapFunctions.removeAllWMSLayers();
        }

        $scope.init();

        $scope.open = function () {
            var modalInstance = $modal.open({
                templateUrl: 'calculateResults.html',
                controller: ModalInstanceCtrl,
                resolve: {
                    html: function () {
                        return $scope.html;
                    },
                    resource: function(){
                        return $scope.impact.impact_resource;
                    }
                }
            });
        };

        var ModalInstanceCtrl = function ($scope, $modalInstance, html, resource) {
            $scope.html = html;

            $scope.viewPdf = function () {
                window.open('/api/pdf?q=' + resource);
                $modalInstance.close();
            };

            $scope.close = function () {
                $modalInstance.dismiss('cancel');
            };
        };

        var unbind = $rootScope.$on('layer changed', function(event, layer_info){
            if (layer_info.type == 'hazard'){
                $scope.hazard.hazard_name = layer_info.name;
                $scope.hazard.hazard_title = layer_info.title;
                if ($scope.hazard.layer != null){
                    $rootScope.map.removeLayer($scope.hazard.layer);
                }
                $scope.hazard.layer = layer_info.layer;
            }else if (layer_info.type == 'exposure'){
                $scope.exposure.exposure_name = layer_info.name;
                $scope.exposure.exposure_title = layer_info.title;
                if ($scope.exposure.layer != null){
                    $rootScope.map.removeLayer($scope.exposure.layer);
                }
                $scope.exposure.layer = layer_info.layer;
            }
            $rootScope.map.addLayer(layer_info.layer);
        });
        $scope.$on('$destroy', unbind);
        
        $scope.showHelp = function(){
            $scope.help_toggle = true;
        };
        
        $scope.hideHelp = function(){
            $scope.help_toggle = false;
        };

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
                    $scope.loaded = false;

                    $http.get(calculate_url, {params: {
                        'exposure_title' : $scope.exposure.exposure_title,
                        'hazard_title' : $scope.hazard.hazard_title,
                        'impact_function' : $scope.impact.impact_function
                    }}).success(function(data, status, headers, config) {
                        $scope.l.stop();
                        $scope.resultReady = true;
                        $scope.loaded = true;
                        $scope.html = data.html;
                        $scope.impact.impact_resource = data.layer.resource;

                        MapFunctions.removeAllWMSLayers();
                        var impact_layer = MapFunctions.fetchWMSLayer(data.layer.resource);
                        $rootScope.map.addLayer(impact_layer);
                        MapFunctions.zoomToExtent($rootScope.extent);
                        $scope.open();
                    }).error(function(data, status, headers, config) {
                        $scope.l.stop();
                        alert('An internal server error(500) has occurred!');
                    })
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
        var url = 'http://localhost:8080/geoserver/rest/layers.json';
        var api_url = 'http://localhost:5000/api/layers';

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
                            alert("Layer not available.");
                        }else if (data.coverage != null){
                            var bbox = data.coverage.nativeBoundingBox;
                            var extent = [bbox.minx, bbox.miny, bbox.maxx, bbox.maxy];
                            $rootScope.extent = extent;
                            layer_info.layer = MapFunctions.fetchWMSLayer(layer.name);
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