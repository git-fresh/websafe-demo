(function(){
var attribution = null;
var layers = [];

//some default configurations for the map
var center = [122.5, 12.151436];
var zoom = 5;
var maxZoom = 18;
var map = null;


var module = angular.module('map_module', []);

module.controller('MapCtrl', function($scope, $rootScope){
    attribution = new ol.Attribution({
        html: 'Tiles &copy; <a href="http://services.arcgisonline.com/ArcGIS/' +
            'rest/services/World_Topo_Map/MapServer">ArcGIS</a>'
    });

    /*
    layers.push(
        new ol.layer.Tile({
            preload: Infinity,
            source: new ol.source.OSM({
                url: '//{a-c}.tile.openstreetmap.org/{z}/{x}/{y}.png'
            })
        })  
    );
    */
    
    layers.push(
        new ol.layer.Tile({
            preload: Infinity,
            source: new ol.source.BingMaps({
                key: 'AqNJQ7F0LgqtsrECYKwo3ijiZyyDhrT2LF3GcP3zmi_DPTGlwJE8cx__OvSQlijW',
                imagerySet: 'Road'
            })
        })
    );
        
    //this initializes the map
    $rootScope.map = new ol.Map({
        target: 'map',
        layers: layers,
        renderer: ol.RendererHint.CANVAS,
        view: new ol.View2D({
            center: ol.proj.transform(center, 'EPSG:4326', 'EPSG:3857'),
            zoom: zoom,
            maxZoom: maxZoom
        })
    });
});

})();