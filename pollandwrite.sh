#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

python3 $DIR/mi2sheet.py --backend bluepy pollandwrite 4c:65:a8:dc:69:9c '/home/pi/mi2sheet/client_secret.json' 'sensor-data' 0 2
