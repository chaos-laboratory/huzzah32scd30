# This file is executed on every boot (including wake-boot from deepsleep)
#import esp
#esp.osdebug(None)

#import connect_wifi
#connect_wifi.connect()
import webrepl
webrepl.start()
