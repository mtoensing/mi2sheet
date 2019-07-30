#!/usr/bin/env python3
"""Write sensor data to spreadsheet"""

import argparse
import re
import logging
import sys
import gspread
import datetime
import pymysql
import json
import urllib.request

from btlewrap import available_backends, BluepyBackend, GatttoolBackend, PygattBackend
from mitemp_bt.mitemp_bt_poller import MiTempBtPoller, \
    MI_TEMPERATURE, MI_HUMIDITY, MI_BATTERY
from oauth2client.service_account import ServiceAccountCredentials

def pollweather(args):

    apikey = args.apikey
    city = args.city
    # Note f before first quote of string
    apiurl = f"http://api.openweathermap.org/data/2.5/weather?q={city}&APPID={apikey}&units=metric"

    req = urllib.request.Request(apiurl)
    r = urllib.request.urlopen(req).read()
    jsonreponse = json.loads(r.decode('utf-8'))

    temperature = jsonreponse['main']['temp']
    humidity = jsonreponse['main']['humidity']
    wind = jsonreponse['wind']['speed']

    data = [temperature,humidity,wind]

    return data

def writeweather(args):

    row = pollweather(args)

    temperature = row[0];
    humidity = row[1];
    wind = row[2];
    city = args.city

    writeMySQL(args, city , None, 'temperature', temperature, None , None )
    writeMySQL(args, city , None, 'humidity', humidity, None , None )
    writeMySQL(args, city , None, 'wind', wind, None , None )


def pollData(args):
    """Poll data from the sensor."""
    backend = _get_backend(args)
    poller = MiTempBtPoller(args.mac, backend)

    #print("Getting data from Mi Temperature and Humidity Sensor")
    #print("FW: {}".format(poller.firmware_version()))
    #print("Name: {}".format(poller.name()))
    #print("Battery: {}".format(poller.parameter_value(MI_BATTERY)))
    #print("Temperature: {}".format(poller.parameter_value(MI_TEMPERATURE)))
    #print("Humidity: {}".format(poller.parameter_value(MI_HUMIDITY)))

    name = format(poller.name())
    battery = format(poller.parameter_value(MI_BATTERY))
    temperature = format(poller.parameter_value(MI_TEMPERATURE))
    humidity = format(poller.parameter_value(MI_HUMIDITY))

    data = [temperature,humidity,battery]
    print(data)
    return data

def poll(args):
    """Poll data from the sensor."""
    backend = _get_backend(args)
    poller = MiTempBtPoller(args.mac, backend)

    #print("Getting data from Mi Temperature and Humidity Sensor")
    #print("FW: {}".format(poller.firmware_version()))
    #print("Name: {}".format(poller.name()))
    #print("Battery: {}".format(poller.parameter_value(MI_BATTERY)))
    #print("Temperature: {}".format(poller.parameter_value(MI_TEMPERATURE)))
    #print("Humidity: {}".format(poller.parameter_value(MI_HUMIDITY)))

    name = format(poller.name())
    battery = format(poller.parameter_value(MI_BATTERY))
    temperature = format(poller.parameter_value(MI_TEMPERATURE))
    humidity = format(poller.parameter_value(MI_HUMIDITY))

    #print("Compiling this data")
    now = datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S")
    data = [now,temperature,humidity,battery]
    print(data)
    return data

def pollandwrite(args):

    keyfile = args.keyfile
    sheetname = args.sheetname
    worksheet = args.worksheet
    rowindex = args.rowindex

    # use creds to create a client to interact with the Google Drive API
    scopes = ['https://www.googleapis.com/auth/spreadsheets', "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
    #print("Authorizing")
    creds = ServiceAccountCredentials.from_json_keyfile_name(keyfile, scopes)
    client = gspread.authorize(creds)
    sheet = client.open(sheetname).get_worksheet(worksheet)
    row = poll(args);
    #print("Writing to sheet")
    sheet.insert_row(row, rowindex, value_input_option='USER_ENTERED')

def pollandwrite_mysql(args):

    row = pollData(args);

    temperature = row[0];
    humidity = row[1];
    battery = row[2];
    device = args.device

    writeMySQL(args, device, None, 'temperature', temperature, None , None )
    writeMySQL(args, device, None, 'humidity', humidity, None , None )
    writeMySQL(args, device, None, 'battery', battery, None , None )

def writeMySQL(args,device ,type ,event ,value ,reading ,unit):

    db = pymysql.connect(args.server,args.user,args.password,args.db )

    # prepare a cursor object using cursor() method
    cursor = db.cursor()

    # Prepare SQL query to INSERT a record into the database.
    sql = "INSERT INTO history (TIMESTAMP,DEVICE,TYPE,EVENT,VALUE,READING,UNIT) VALUES (NOW(), %s, %s, %s, %s,%s ,%s)"
    val = (device ,type ,event ,value ,reading ,unit)

    try:
       # Execute the SQL command
       cursor.execute(sql, val)
    except:
       print ("Error: unable write")

    # disconnect from server
    db.close()

def _get_backend(args):
    """Extract the backend class from the command line arguments."""
    if args.backend == 'gatttool':
        backend = GatttoolBackend
    elif args.backend == 'bluepy':
        backend = BluepyBackend
    elif args.backend == 'pygatt':
        backend = PygattBackend
    else:
        raise Exception('unknown backend: {}'.format(args.backend))
    return backend


def list_backends(_):
    """List all available backends."""
    backends = [b.__name__ for b in available_backends()]
    print('\n'.join(backends))


def main():
    """Main function.

    Mostly parsing the command line arguments.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('--backend', choices=['gatttool', 'bluepy', 'pygatt'], default='gatttool')
    parser.add_argument('-v', '--verbose', action='store_const', const=True)
    subparsers = parser.add_subparsers(help='sub-command help', )

    parser_poll = subparsers.add_parser('poll', help='poll data from a sensor')
    parser_poll.add_argument('mac', type=str)
    parser_poll.set_defaults(func=poll)

    parser_poll = subparsers.add_parser('pollandwrite', help='poll and write data from a sensor to spreadsheet')
    parser_poll.add_argument('mac', type=str)
    parser_poll.add_argument('keyfile', type=str)
    parser_poll.add_argument('sheetname', type=str)
    parser_poll.add_argument('worksheet', type=int, default=0)
    parser_poll.add_argument('rowindex', type=int, default=2)
    parser_poll.set_defaults(func=pollandwrite)

    parser_poll = subparsers.add_parser('pollandwrite_mysql', help='poll and write data from a sensor to mysql')
    parser_poll.add_argument('mac', type=str)
    parser_poll.add_argument('server', type=str)
    parser_poll.add_argument('user', type=str)
    parser_poll.add_argument('password', type=str)
    parser_poll.add_argument('db', type=str)
    parser_poll.add_argument('device', type=str)
    parser_poll.set_defaults(func=pollandwrite_mysql)

    parser_poll = subparsers.add_parser('writeweather', help='poll and return weather')
    parser_poll.add_argument('server', type=str)
    parser_poll.add_argument('user', type=str)
    parser_poll.add_argument('password', type=str)
    parser_poll.add_argument('db', type=str)
    parser_poll.add_argument('apikey', type=str)
    parser_poll.add_argument('city', type=str)
    parser_poll.set_defaults(func=writeweather)

    parser_scan = subparsers.add_parser('backends', help='list the available backends')
    parser_scan.set_defaults(func=list_backends)

    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)

    if not hasattr(args, "func"):
        parser.print_help()
        sys.exit(0)

    args.func(args)


if __name__ == '__main__':
    main()
