(function(){
var module = angular.module('toolbar_module', ['map_module']);

module.controller('SearchCtrl', function($scope, $rootScope){
    //var map = $rootScope.map;
    
    // for autocomplete of search item
	/*
    google.maps.event.addListener(
		new google.maps.places.Autocomplete(
            document.getElementById('area')),
        'place_changed',
		showSearchResult
	);
    */
    
    
    // function for search button
    function showSearchResult() {
        var place = this.getPlace();
        var duration = 5000;
        var start = +new Date();
        var viewMap2d = $rootScope.map.getView().getView2D();

        var pan = ol.animation.pan({
            duration: duration,
            source: viewMap2d.getCenter(),
            start: start
        });

        var bounce = ol.animation.bounce({
            duration: duration,
            resolution: 4 * viewMap2d.getResolution(),
            start: start
        });

        $rootScope.map.beforeRender(pan, bounce);
 
        viewMap2d.setCenter(
            ol.proj.transform( [
                    place.geometry.location[Object.keys(place.geometry.location)[1]],
                    place.geometry.location[Object.keys(place.geometry.location)[0]]
                ],
                'EPSG:4326', 
                'EPSG:3857'
            )
        );

        viewMap2d.setZoom(13);
    }
});
})();