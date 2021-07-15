import ucryptolib
def connect():
    import network
    import time
    dec = ucryptolib.aes('', 1)
    enc_ssid = ''
    dec_ssid = dec.decrypt(enc_ssid)
    dec_ssid = str(dec_ssid)
    dec_ssid = dec_ssid.replace("b", '')
    dec_ssid = dec_ssid.replace("\\x00", '')
    dec_ssid = dec_ssid.replace("'", '')
    dec_ssid = dec_ssid.encode()
    
    enc_pw = ''
    dec_pw = dec.decrypt(enc_pw)
    dec_pw = str(dec_pw)
    dec_pw = dec_pw.replace("b", '')
    dec_pw = dec_pw.replace("\\x00", '')
    dec_pw = dec_pw.replace("'", '')
    dec_pw = dec_pw.encode()
    
    station = network.WLAN(network.STA_IF)
    if station.isconnected() == False:
        print('connecting to network...')
        station.active(True)
        # wifi_networks = station.scan()
        # status = station.status()
        station.connect(dec_ssid, dec_pw)
        print('still connecting ...')
        while station.isconnected() == False:
            time.sleep(3)
            
        print('connected!')
        print(station.ifconfig())
    else:
        print('already connected')
        print(station.ifconfig())