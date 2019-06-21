#!/usr/bin/env python3
"""Write sensor data to spreadsheet"""

import argparse
import re
import logging
import sys
import gspread
import datetime

from btlewrap import available_backends, BluepyBackend, GatttoolBackend, PygattBackend
from mitemp_bt.mitemp_bt_poller import MiTempBtPoller, \
    MI_TEMPERATURE, MI_HUMIDITY, MI_BATTERY
from oauth2client.service_account import ServiceAccountCredentials

def valid_mitemp_mac(mac, pat=re.compile(r"4C:65:A8:[0-9A-F]{2}:[0-9A-F]{2}:[0-9A-F]{2}")):
    """Check for valid mac adresses."""
    if not pat.match(mac.upper()):
        raise argparse.ArgumentTypeError('The MAC address "{}" seems to be in the wrong format'.format(mac))
    return mac


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


    return data


def write(args):
    keyfile = '/home/pi/mi2sheet/client_secret.json'
    # use creds to create a client to interact with the Google Drive API
    scopes = ['https://www.googleapis.com/auth/spreadsheets', "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
    #print("Authorizing")
    creds = ServiceAccountCredentials.from_json_keyfile_name(keyfile, scopes)
    client = gspread.authorize(creds)
    sheet = client.open("sensor-data").sheet1
    row = poll(args);
    index = 2
    #print("Writing to sheet")
    #print(row)
    sheet.insert_row(row, index, value_input_option='USER_ENTERED')

def writesheet(args):
    keyfile = args.keyfile
    # use creds to create a client to interact with the Google Drive API
    scopes = ['https://www.googleapis.com/auth/spreadsheets', "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
    #print("Authorizing")
    creds = ServiceAccountCredentials.from_json_keyfile_name(keyfile, scopes)
    client = gspread.authorize(creds)
    sheet = client.open("sensor-data").sheet1
    row = poll(args);
    index = 2
    #print("Writing to sheet")
    #print(row)
    sheet.insert_row(row, index, value_input_option='USER_ENTERED')

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
    #print(row)
    sheet.insert_row(row, rowindex, value_input_option='USER_ENTERED')


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
    parser_poll.add_argument('mac', type=valid_mitemp_mac)
    parser_poll.set_defaults(func=poll)

    parser_poll = subparsers.add_parser('write', help='write data from a sensor to spreadsheet')
    parser_poll.add_argument('mac', type=valid_mitemp_mac)
    parser_poll.set_defaults(func=write)

    parser_poll = subparsers.add_parser('pollandwrite', help='poll and write data from a sensor to spreadsheet')
    parser_poll.add_argument('mac', type=valid_mitemp_mac)
    parser_poll.add_argument('keyfile', type=str)
    parser_poll.add_argument('sheetname', type=str)
    parser_poll.add_argument('worksheet', type=int, default=0)
    parser_poll.add_argument('rowindex', type=int, default=2)
    parser_poll.set_defaults(func=pollandwrite)

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
