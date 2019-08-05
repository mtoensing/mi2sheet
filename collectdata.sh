#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

python3 $DIR/mi2sheet.py writePiTmp "pizero"
python3 $DIR/mi2sheet.py writePiTmp "pi4"

python3 $DIR/mi2sheet.py --backend bluepy writeMiSensor 58:2d:34:34:77:4b "mi3"
python3 $DIR/mi2sheet.py --backend bluepy writeMiSensor 4c:65:a8:dc:69:9c "mi1"
python3 $DIR/mi2sheet.py --backend bluepy writeMiSensor 58:2d:34:30:ed:80 "mi2"
