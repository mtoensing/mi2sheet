# mi2sheet

Tutorial in german language: https://marc.tv/raspberry-pi-temperatur-bluetooth-google-spreadsheet/ 

## Find mac address

`sudo blescan`

## Poll for data

Edit poll.sh and add mac address. 

`./poll.sh `

## Poll and write to spreadsheet

Edit pollandwrite.sh and add spreadsheet name. Don't forget to add a client_secret.json

`./pollandwrite.sh `

# Credits
Xiaomi MI Temperature and Humidity Sensor with BLE and LCD
https://github.com/ratcashdev/mitemp 

Bluetooth LowEnergy wrapper for different python backends.
https://github.com/ChristianKuehnel/btlewrap
