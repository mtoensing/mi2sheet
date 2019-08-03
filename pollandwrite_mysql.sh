#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

python3 $DIR/mi2sheet.py --backend bluepy pollandwrite_mysql 58:2d:34:34:77:4b "mi"
