##########################################################################
##
##
## purpleAir parameters
##
##
##########################################################################

purpleAir = {
    
    # The api read keys. Each key will be used for max_requests_per_key (see below) requests
    'read_keys': [
        'XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX',
    ],

    # Maximum number of requests allowed per key
    'max_requests_per_key': 10, 

    # Default date from which we will start getting data for each sensor. In YYYY-MM-DD HH:mm:ss format
    'start_timestamp': '2021-01-01 00:00:00',
    
    # Batch days for each request. How many days will be included to each request. Values: 1 - 14. Higher days means less requests.
    'batch_days': 14,

    # Parameters related to get sensor history request.
    # https://api.purpleair.com/#api-sensors-get-sensor-history
    'request': {

        # The desired average in minutes, one of the following: 0 (real-time), 10 (default if not specified), 30, 60, 360 (6 hour), 1440 (1 day) 
        'average': 60,

        # For the available fields check the docs 
        # https://api.purpleair.com/#api-sensors-get-sensor-history
        'fields' : [

            # Environmental fields:
            'humidity', 'humidity_a', 'humidity_b', 
            'temperature', 'temperature_a', 'temperature_b', 
            'pressure', 'pressure_a', 'pressure_b',

            # Miscellaneous fields:
            'voc', 'voc_a', 'voc_b', 'analog_input',

            # PM1.0 fields:
            'pm1.0_atm', 'pm1.0_atm_a', 'pm1.0_atm_b', 
            'pm1.0_cf_1', 'pm1.0_cf_1_a', 'pm1.0_cf_1_b',

            # PM2.5 fields:
            'pm2.5_alt', 'pm2.5_alt_a', 'pm2.5_alt_b', 
            'pm2.5_atm', 'pm2.5_atm_a', 'pm2.5_atm_b', 
            'pm2.5_cf_1', 'pm2.5_cf_1_a', 'pm2.5_cf_1_b',

            # PM10.0 fields:
            'pm10.0_atm', 'pm10.0_atm_a', 'pm10.0_atm_b', 
            'pm10.0_cf_1', 'pm10.0_cf_1_a', 'pm10.0_cf_1_b',

            # Visibility fields:
            'scattering_coefficient', 'scattering_coefficient_a', 'scattering_coefficient_b', 
            'deciviews', 'deciviews_a', 'deciviews_b', 
            'visual_range', 'visual_range_a', 'visual_range_b',

            # Particle count fields:
            '0.3_um_count', '0.3_um_count_a', '0.3_um_count_b', 
            '0.5_um_count', '0.5_um_count_a', '0.5_um_count_b', 
            '1.0_um_count', '1.0_um_count_a', '1.0_um_count_b', 
            '2.5_um_count', '2.5_um_count_a', '2.5_um_count_b', 
            '5.0_um_count', '5.0_um_count_a', '5.0_um_count_b', 
            '10.0_um_count', '10.0_um_count_a', '10.0_um_count_b',

        ],
    },

    

    
}

##########################################################################
##
##
## PurpleAir Sensors
##
##
##########################################################################

devices = {
    # Each sub dict must consist of a location's name e.g. 'my_group' and each location must have a 'sensors' key key.
    # 'sensors' represents PurpleAir sensors. Consists of an array of sensor's indexes
    
    'agrinio': [ 
        95543, 99711, 99701, 95561, 
        95789, 99633, 95759, 95889,
        98829, 95713, 99629, 95635, 
        99663, 93837, 95847, 
        99451
    ],

    'athens': [ 
        99711, 99701 
    ],

    'patras': [ 
        121511, 749, 116409, 101597, 
        56453, 101611, 23759, 5078 
    ],

    'osaka':  [],
}


##########################################################################
##
##
## CSV storage directory
##
##
##########################################################################

# The main storage directory 
DATA_DIR    = 'data'