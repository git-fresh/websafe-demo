(function(){

var module = angular.module('websafe_module', [
    'utils',
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
    function($scope, $window, $rootScope, $http, MapFunctions, $modal){
        $scope.init = function(){
            $scope.help_toggle = false;
            $scope.hazard = {};
            $scope.exposure = {};
            $scope.impact = {};
            $scope.impact_resource = '';
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
                        return $scope.impact_resource;
                    }
                }
            });
        };

        var ModalInstanceCtrl = function ($scope, $modalInstance, html, resource) {
            $scope.html = html;

            $scope.viewPdf = function () {
                window.open('/api/pdf?q='+resource);
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
            }else if (layer_info.type == 'exposure'){
                $scope.exposure.exposure_name = layer_info.name;
                $scope.exposure.exposure_title = layer_info.title;
            }
        });
        $scope.$on('$destroy', unbind);
        
        $scope.showHelp = function(){
            $scope.help_toggle = true;
        };
        
        $scope.hideHelp = function(){
            $scope.help_toggle = false;
        };

        $scope.calculate = function(){
            var calculate_url = 'http://localhost:5000/api/calculate'
            if (($scope.exposure.exposure_name == '') || ($scope.hazard.hazard_name == '')){
                //TODO: error handling, don't calculate
            }else{
                if (($scope.exposure.exposure_title != '') || ($scope.hazard.hazard_title != '')){
                    $scope.l = Ladda.create( document.querySelector( '.ladda-button' ) );
                    $scope.l.start();
                    $scope.loaded = false;

                    $http.get(calculate_url, {params: {
                        'exposure_title' : $scope.exposure.exposure_title,
                        'hazard_title' : $scope.hazard.hazard_title,
                        //'exposure_subcategory' : $scope.exposure_subcategory,
                        //'hazard_subcategory' : $scope.hazard_subcategory
                        'exposure_subcategory' : 'structure',
                        'hazard_subcategory' : 'flood'
                    }}).success(function(data, status, headers, config) {
                        $scope.l.stop();
                        $scope.resultReady = true;
                        $scope.loaded = true;
                        $scope.html = data.html;
                        $scope.impact_resource = data.layer.resource;
                        $scope.open();

                        //TODO: remove other layers
                        MapFunctions.addLayer(data.layer.resource);
                        MapFunctions.zoomToExtent($rootScope.extent);
                    })
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
        var geoserver_url = 'http://localhost:8080/geoserver/';
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
                }
            }).then(function(){
                $http.get(api_url, {params: {'api': resource_link }})
                .success(function(data, status, headers, config) {
                    var bbox = data.featureType.nativeBoundingBox;
                    var extent = [bbox.minx, bbox.miny, bbox.maxx, bbox.maxy];
                    if (layer_info.type == 'exposure') $rootScope.extent = extent;

                    MapFunctions.addLayer(layer.name);
                    MapFunctions.zoomToExtent(extent);

                    layer_info.title = data.featureType.title;
                    $rootScope.$emit('layer changed', layer_info);
                });
            });
        }
    }
]);
})();