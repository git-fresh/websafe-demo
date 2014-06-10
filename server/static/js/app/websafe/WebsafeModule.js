(function(){

var module = angular.module('websafe_module', [
    'websafe_service',
    'ui.bootstrap',
    'ui.select2',
    'websafe_config',
    'ngSanitize'
]);

module.config(['$tooltipProvider', function($tooltipProvider){
    $tooltipProvider.setTriggers({
        'mouseenter': 'mouseleave',
        'click': 'click',
        'focus': 'blur',
        'onTrigger': 'offTrigger'
    });
}]);

module.controller('ModalCtrl', [
    '$scope',
    '$modalInstance',
    function($scope, $modalInstance){
        //TODO: make pdf report generation using jsPDF 
        $scope.viewPdf = function () {
            window.open('/api/pdf?q=' + $scope.$parent.impact.name);
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
    '$modal',
    '$timeout',
    '$rootScope',
    'MapFunctions',
    'WebsafeFunctions',
    'WebsafeConfig',
    function($scope, $window, $modal, $timeout, $rootScope, MapFunctions, WebsafeFunctions, WebsafeConfig){
        $scope.init = function(){
            $scope.help_toggle = false;
            $scope.hazard = { type: 'haz' };
            $scope.exposure = { type: 'exp' };
            $scope.impact_functions = WebsafeConfig.impact_functions;
            $scope.impact = {impact_function : WebsafeConfig.impact_functions[0].value};
            $scope.html = '';
            $scope.resultReady = false;
            $scope.l = null;
            $('.legend_hazard').draggable();
            $('.legend_exposure').draggable();
            $('.legend_impact').draggable();
            MapFunctions.removeAllWMSLayers();
        };
        $scope.init();

        $scope.exposure_selector = { width: '250px' };
        $scope.hazard_selector = { width: '250px' };

        $scope.onTrigger = function(target){
            $timeout(function() { $(target).trigger('onTrigger'); }, 0);
        };

        $scope.offTrigger = function(target){
            $timeout(function() { $(target).trigger('offTrigger'); }, 0);
        };
        
        $scope.showHelp = function(){ $scope.help_toggle = true; };
        $scope.hideHelp = function(){ $scope.help_toggle = false; };

        // This function creates and opens a modal instance
        $scope.open = function () {
            var modalInstance = $modal.open({
                templateUrl: 'calculateResults.html',
                controller: 'ModalCtrl',
                scope: $scope
            });
        };

        MapFunctions.fetchLayers(WebsafeConfig.exposure_url)
            .then(function(data){ $scope.exposure_list = data; });
        MapFunctions.fetchLayers(WebsafeConfig.hazard_url)
            .then(function(data){ $scope.hazard_list = data; });

        // this is a listener for every change in the layer selectors(exposure and hazard)
        $scope.layerChanged = function(layer){
            if (layer.name != ''){
                if (layer.layer != null){
                    $rootScope.map.removeLayer(layer.layer);
                }

                if ($scope.exposure.layer != null){
                    $scope.impact.showLegend = false;
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
                layer.showLegend = true;
            }
        };

        /*
         * this is the function to be called when you click the calculate button
         * this connects to the backend api and runs the InaSAFE calculate function
         */
        $scope.calculate = function(){
            var params = {};

            if ($scope.exposure.name == ''){
                alert('Please select exposure layer.');
            }else if ($scope.hazard.name == ''){
                alert('Please select hazard layer.');
            }else{
                $scope.l = Ladda.create( document.querySelector( '.ladda-button' ) );
                $scope.l.start();

                params = {
                    'exposure_name' : $scope.exposure.name,
                    'hazard_name' : $scope.hazard.name,
                    'impact_function' : $scope.impact.impact_function
                };

                WebsafeFunctions.calculate(params)
                .then(function(data){
                    $scope.l.stop();
                    $scope.impact.name = data.resource;
                    $scope.impact.impact_resource = 'impact:' + data.resource;

                    MapFunctions.removeAllWMSLayers();
                    $scope.hazard.showLegend = false;
                    $scope.exposure.showLegend = false;

                    var impact_layer = MapFunctions.fetchWMSLayer(data.resource);
                    $scope.impact.legend = MapFunctions.getLegend(data.resource);
                    $rootScope.map.addLayer(impact_layer);
                    $scope.impact.showLegend = true;

                    MapFunctions.fetchBbox(impact_layer.resource_name)
                    .then(function(extent){
                        MapFunctions.zoomToExtent(extent);
                    });

                    $scope.resultReady = true;
                    $scope.html = data.html;
                    
                    $scope.open();              // open the modal for result
                }, function(status){ 
                    $scope.l.stop();
                    alert('An internal server error(500) has occurred!');
                });
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