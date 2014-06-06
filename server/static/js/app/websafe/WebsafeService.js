(function(){

var module = angular.module('websafe_service', [
    'websafe_config'
    ]);

module.factory('MapFunctions', [
    '$rootScope',
    '$http',
    '$q',
    '$timeout',
    'WebsafeConfig',
    function ($rootScope, $http, $q, $timeout, WebsafeConfig) {
        var geoserver_url = 'http://localhost:8080/geoserver/wms';

        // define some constants
        var map = $rootScope.map;
        var gmap = $rootScope.gmap;
        var view = map.getView();
        var proj = 'EPSG:4326';
        var version = '1.1.1';

        return {
            fetchLayers : function(url){
                var deferred = $q.defer();

                $http.get(url).success(function(data, status, headers, config) {
                    deferred.resolve(data);
                }).error(function(data, status, headers, config){
                    deferred.reject(status);
                });

                return deferred.promise;
            },

            fetchWMSLayer : function(resource_name){
                var layer = new ol.layer.Image({
                    source: new ol.source.ImageWMS({
                        url: geoserver_url,
                        params: {
                            'SERVICE': 'WMS',
                            'VERSION': version,
                            'LAYERS': resource_name,
                            'SRS': proj
                        },
                        serverType: 'geoserver'
                    })
                });
                return layer;
            },

            fetchBbox : function(resource_name){
                var deferred = $q.defer();
                var parser = new ol.format.WMSCapabilities();
                var getcapabilites_json = {};

                $http.get(WebsafeConfig.getcapabilities_url)
                .success(function(data, status, headers, config) {
                    getcapabilites_json = parser.read(data);
                    var layer_list = getcapabilites_json.Capability.Layer.Layer;
                    var layer = null;

                    for(var i=0; i<layer_list.length; i++){
                        layer = layer_list[i];
                        if (layer.Name == resource_name){
                            deferred.resolve(layer.BoundingBox[0].extent);
                        }
                    }
                }).error(function(data, status, headers, config){
                    console.log('Fetching Bounding Box from GeoServer failed!');
                });

                return deferred.promise;
            },

            getWMSLayers : function(){
                var layers = [];

                map.getLayers().forEach(function(layer) {
                    if (layer instanceof ol.layer.Image){
                        layers.push(layer);
                    }
                });

                return layers;
            },

            getAllLayers : function(){
                return map.getLayers().getArray();
            },

            removeAllWMSLayers : function(){
                var layer_array = [];

                // first populate a temp array of the layers to be removed
                map.getLayers().forEach(function(layer) {
                    if (layer instanceof ol.layer.Image){
                        layer_array.push(layer);
                    }
                });

                // remove all the layers in the temp array
                for(var i=0; i < layer_array.length; i++){
                    map.removeLayer(layer_array[i]);
                }
            },

            zoomToExtent : function(extent){
                var center = ol.extent.getCenter(extent);
                var resolution = view.getResolutionForExtent(extent, map.getSize());
                resolution = 40;
                var duration = 2000;
                var start = +new Date();

                var pan = ol.animation.pan({
                    duration: duration,
                    source: map.getView().getCenter(),
                    start: start
                });

                var zoom = ol.animation.zoom({
                    duration: duration,
                    resolution: map.getView().getResolution()
                });

                map.beforeRender(zoom, pan);

                view.setResolution(resolution);
                view.setCenter(ol.proj.transform(center, 'EPSG:4326', 'EPSG:3857'));
            },

            getLegend : function(layer_name){
                var url = geoserver_url + '?REQUEST=GetLegendGraphic&VERSION=' +
                        version + '&FORMAT=image/png&WIDTH=20&HEIGHT=20&LAYER=' +
                        layer_name + '&LEGEND_OPTIONS=fontName:Arial;forceLabels:on;';

                return url;
            }
        }
    }
]);

module.factory('WebsafeFunctions', [
    '$rootScope',
    '$http',
    '$q',
    'WebsafeConfig',
    function ($rootScope, $http, $q, WebsafeConfig) {

        return {
            calculate : function(params){
                var deferred = $q.defer();

                $http.get(WebsafeConfig.calculate_url, {params : params}).success(function(data, status, headers, config) {
                    deferred.resolve(data);
                }).error(function(data, status, headers, config){
                    deferred.reject(status);
                });

                return deferred.promise;
            }
        }
    }
]);

})();