(function(){
    
var module = angular.module('config', []);

module.factory('Config', function() {
    return {
        impact_functions : [
            {label: 'Be Flooded', value: 'structure'},
            {label: 'Need Evacuation', value: 'population'}
        ]
    };
});
})();