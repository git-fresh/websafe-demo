(function(){
    
var module = angular.module('websafe_config', []);

module.factory('WebsafeConfig', function() {
    return {

        hazard_url : 'hazards',
        exposure_url : 'exposures',
        calculate_url : 'api/calculate',
        getcapabilities_url : 'getcapabilities',


        impact_functions : [
            {label: 'Be Flooded', value: 'structure'},
            {label: 'Need Evacuation', value: 'population'}
        ]

    };
});
})();