"""
This module will get historical sensor data from PurpleAir.com based on their API https://api.purpleair.com/#api-sensors-get-sensor-history.
All sensors are defined in the config.py file and they are grouped by a location name. 
For each sensor, data are saved in a csv file at data/:location/pm/sensor_index.csv. This path is configurable in config.py.
By default, csv will check the last entry's time_stamp and get new data from that time_stamp till execution time. Those time intervals can also be specified from command line arguments.
All requested data will append the same csv file. Duplicate values will be rejected. 
Also, the csv is sorted by 'time_stamp' in ascending order
Due to purpleAir's API request restrictions, we will use each api read key for around 990 requests per run.
You can define more read keys if you have, and extends those requests.
CAUTION! The script doesn't check if you have already run it for max Requests. So be careful not to get your keys disabled.
Check the config.py file for available parameters.
"""

import config

import argparse
import math
from datetime import datetime, timedelta
import os
import pandas as pd
import requests


MAX_REQUESTS     = config.purpleAir['max_requests_per_key']
READ_KEYS        = iter(config.purpleAir['read_keys'])

REQUEST_PARAMS = {
    "headers": {
        "X-API-Key": next(READ_KEYS)
    },
    "url": "https://api.purpleair.com/v1/sensors/:sensor/history",
    "datetime_format": '%Y-%m-%dT%H:%M:%SZ'
}
AVERAGE_MINS = config.purpleAir['request']['average']

ARGPARSE_DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'
START_TIMESTAMP = datetime.strptime(config.purpleAir['start_timestamp'], ARGPARSE_DATETIME_FORMAT)

DATETIME_HOUR_NOW = datetime.now().replace(minute=0, second=0, microsecond=0)

CSV_TIMESTAMP_COL = 'time_stamp'


class Counter:
    total_requests = 0
    key_requests   = 0


class Sensor:
    def __init__(self, location, index):
        self.location = location
        self.index = index
        self.url = REQUEST_PARAMS["url"].replace(':sensor', str(index))
        self.csv_filepath = os.path.join(config.DATA_DIR, location, str(index) + '.csv')
        self._makedir()


    def get_data(self, start_timestamp, end_timestamp, csv):

        batch    = timedelta(days=config.purpleAir['batch_days'])
        interval = end_timestamp - start_timestamp

        print('\n{} {}, getting data from {}, to {}...'.format(self.location, self.index, start_timestamp, end_timestamp))

        for i in range(math.ceil(interval / batch)):

            start_date_param = (start_timestamp + batch * i)
            end_date_tmp     = start_date_param + batch 
            end_date_param   = end_date_tmp if end_date_tmp < end_timestamp else end_timestamp

            print("{} {}, batch {}, {} - {}".format(self.location, self.index, i+1, start_date_param, end_date_param - timedelta(minutes=AVERAGE_MINS)), end=", ")
            # print()
            try:

                response = requests.get(url=self.url, params={
                    'start_timestamp': start_date_param.strftime(REQUEST_PARAMS["datetime_format"]), 
                    'end_timestamp'  : end_date_param.strftime(REQUEST_PARAMS["datetime_format"]), 
                    'average'        : AVERAGE_MINS, 
                    'fields'         : ','.join(config.purpleAir['request']['fields']) # fileds need to be comma separated
                    },
                    headers=REQUEST_PARAMS["headers"]
                )

                Counter.total_requests += 1
                Counter.key_requests   += 1

                response.raise_for_status()
                response_df      = pd.DataFrame(response.json()['data'], columns=response.json()['fields'])
                measurements_len = len(response_df.index)

                response_df = csv.remove_existing_rows_from_df(response_df, CSV_TIMESTAMP_COL)
                measurements_len_after_remove = len(response_df.index)
                measurements_existing         = measurements_len - measurements_len_after_remove
                
                response_df.sort_values(by=[CSV_TIMESTAMP_COL], inplace=True)
                response_df.to_csv(csv.file_path, mode='a',  index=False, header=csv.is_empty())

                print("Measurements: {}, Existing: {}, Saved: {}".format(measurements_len, measurements_existing, measurements_len_after_remove))
                
                if Counter.key_requests >= MAX_REQUESTS:
                    new_key = next(READ_KEYS)
                    REQUEST_PARAMS['headers']['X-API-Key'] = new_key
                    print("Key changed to: ", new_key)
                    Counter.key_requests = 0 
                
            except StopIteration as e:
                print("We run out of keys. Total requests: ", Counter.total_requests)
                exit()

            except requests.exceptions.RequestException as e:
                print("Exception: ",e.response.text)
                exit()

            except Exception as e:
                print("Exception: ", e)
                exit()


    def _makedir(self):
        os.makedirs(os.path.dirname(self.csv_filepath), exist_ok=True)


class Csv:

    def __init__(self, file_path):
        self.file_path = file_path
    
    def create_file(self):
        try:
            
            open(self.file_path, "x")

        except FileExistsError as e:
            pass


    def get_last_datetime(self, column, datetime_format):
        try:
            df = pd.read_csv(self.file_path, usecols=[column])
            return datetime.strptime(df[column].max(), datetime_format)
            
        except Exception as e:
            return None


    def remove_existing_rows_from_df(self, df, column):
        if self.is_empty():
            return df

        csv_df = pd.read_csv(self.file_path)
        return df[df[column].isin(csv_df[column]) == False]


    def is_empty(self):
        return os.stat(self.file_path).st_size == 0

    def sort(self, column=CSV_TIMESTAMP_COL):
        csv_df = pd.read_csv(self.file_path)
        csv_df.sort_values(by=[column], inplace=True)
        csv_df.to_csv(self.file_path, index=False)




def datetime_strptime(str_datetime):
    return datetime.strptime(str_datetime, REQUEST_PARAMS['datetime_format'])


def argparse_datetime(str_datetime):
    return datetime.strptime(str_datetime, ARGPARSE_DATETIME_FORMAT)


def argparser():
    parser = argparse.ArgumentParser(
        description="Get PurpleAir sensor data and store them in .csv files",
        epilog = """Example usage:\n 
            {} --start '2022-01-01 00:00:00' --end '2023-02-01 23:59:59' --locations patras athens \t This will fetch data for all sensors in patras and athens from 2022-01-01 00:00:00 to 2023-02-01 23:59:59.
        """.format(argparse._sys.argv[0])
    )
    
    parser.add_argument('-l',  '--locations',
        nargs='+', 
        default=list(config.devices.keys()), 
        choices=list(config.devices.keys()), 
        # metavar='', 
        help="Get data only for sensors in specified locations"
    )
    
    parser.add_argument('-s', '--start',
        metavar="'{}'".format(ARGPARSE_DATETIME_FORMAT.replace('%', '')),
        default=None,
        type=argparse_datetime,
        help="Get sensors' data starting from the specified datetime. Format: '{}' Quoted. Usage: --start '{}'".format(ARGPARSE_DATETIME_FORMAT.replace('%', ''), DATETIME_HOUR_NOW - timedelta(days=60))
    )

    parser.add_argument('-e', '--end',
        metavar="'{}'".format(ARGPARSE_DATETIME_FORMAT.replace('%', '')),
        default=None,
        type=argparse_datetime,
        help="Get sensor's data until the specified datetime. Format: '{}' Quoted. Usage: --end '{}'".format(ARGPARSE_DATETIME_FORMAT.replace('%', ''), DATETIME_HOUR_NOW)
    )

    return parser.parse_args()



if __name__== '__main__':
    args = argparser()

    sensors = []
    for location in set(args.locations):
        for sensor_index in config.devices[location]:
            sensors.append(Sensor(location, sensor_index))

    for sensor in sensors:
        
        csv = Csv(sensor.csv_filepath)
        csv.create_file()

        sensor_last_timestamp = csv.get_last_datetime(column='time_stamp', datetime_format= REQUEST_PARAMS['datetime_format'])
        sensor_last_timestamp = sensor_last_timestamp + timedelta(minutes=AVERAGE_MINS) if sensor_last_timestamp else None
        
        start_timestamp = args.start or sensor_last_timestamp or START_TIMESTAMP
        end_timestamp   = args.end or DATETIME_HOUR_NOW
        
        sensor.get_data(start_timestamp, end_timestamp, csv)

        # Sort the csv file if we get earlier measurements than we already have saved in the csv.
        if sensor_last_timestamp and start_timestamp < sensor_last_timestamp:
            csv.sort()
        


    print("Total Requests:", Counter.total_requests)
