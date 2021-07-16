import utime
import ntptime
import machine
import ubinascii
import reg_stapi
import connect_wifi
from scd30 import SCD30

#==========mandatory parameters===============
thing_name = 'ckw1'
thing_desc = 'scd30 at home'
freq = 10 # in seconds, at least 6 seconds
#==========optional parameters================
loc_name = 'home'
loc_desc = 'study table'
coordinates = [0,0,0]
#==================constants==================
uid = machine.unique_id()
uid = ubinascii.hexlify(machine.unique_id()).decode()
pins = 'i2c-scd30'
# datastream info
ds_descs = ['co2', 'air_temp', 'rel humidity']
ds_snr_ids = [5,5,5]
ds_obs_id = [5,1,3]
ds_obs_types = ['http://www.opengis.net/def/observationType/OGC-OM/2.0/OM_Measurement',
                'http://www.opengis.net/def/observationType/OGC-OM/2.0/OM_Measurement',
                'http://www.opengis.net/def/observationType/OGC-OM/2.0/OM_Measurement']
ds_uom_names = ['parts per million', 'degree celsius', '%']
ds_uom_syms = ['ppm', 'degC', '%']
ds_uom_defs = ['no. particles per a million particles',
               'http://www.qudt.org/qudt/owl/1.0.0/unit/Instances.html#DegreeCelsius',
               'percentage of humidity in the air']
#==================main script==========================
#setup the led light
led = machine.Pin(13, machine.Pin.OUT) # LED on the board
connect_wifi.connect()
settime = True
while settime == True:
    try:
        ntptime.settime()
        settime = False
        led.value(0)
    except:
        led.value(1)
        utime.sleep_ms(1000)

#check if it is register in the frost-server database
thingid_ls = reg_stapi.get_thingid(thing_name, thing_desc, uid)
nthingid_ls = len(thingid_ls)
if nthingid_ls == 0:
    #register the device on the database
    thingid = reg_stapi.post_thing(thing_name, thing_desc, uid, pins, loc_name, loc_desc, coordinates)
    
    #register the datastreams with the thingid
    ds_id_d = reg_stapi.post_datastreams(thingid, thing_name, ds_descs, ds_snr_ids, ds_obs_id, ds_obs_types,
                                        ds_uom_names, ds_uom_syms, ds_uom_defs)
elif nthingid_ls == 1:
    #it is already registered get the info of the device
    thingid = reg_stapi.get_thingid(thing_name, thing_desc, uid)[0]
    
    ds_id_d = {}
    for cnt,desc in enumerate(ds_descs):
        ds_name = thing_name + '_' + desc
        dsid_ls = reg_stapi.get_dsid(thingid, ds_name, desc)
        dsid = dsid_ls[0]['@iot.id']
        ds_id_d[desc] = dsid
else:
    #registered more than once, double check the database
    print('more than 1 thing registration on the database, please check the database')

#retrieve observations from sensor
i2cbus = machine.SoftI2C(scl=machine.Pin(22), sda=machine.Pin(23))
scd30 = SCD30(i2cbus, 0x61)

print('ThingId', thingid)
print('DsIDS', ds_id_d)

while True:
    # Wait for sensor data to be ready to read (by default every 2 seconds)
    try:
        while scd30.get_status_ready() != 1:
            utime.sleep_ms(2000)
        
        led.value(0)
        cur_time = utime.localtime()
        t = utime.mktime(cur_time)
        t-=4*3600 #new jersey time is -400
        cur_time2 = utime.localtime(t)
        mea = scd30.read_measurement()
        yr = str(cur_time2[0])
        mth = str(cur_time2[1])
        day = str(cur_time2[2])
        hr = str(cur_time2[3])
        mins = str(cur_time2[4])
        sec = str(cur_time2[5])
        tz = '-0400'
        time_str = yr + '-' + mth + '-' + day + 'T' + hr + ':' + mins + ':' + sec + tz
        #print(cur_time2)
        #print(time_str)
        #print(mea)
        for cnt,desc in enumerate(ds_descs):
            ds_id = ds_id_d[desc]
            result = mea[cnt]
            #posting the data to the database takes about 2 seconds
            #with doing 3 posting it takes about 6 seconds
            reg_stapi.post_obs(time_str, result, ds_id)
        utime.sleep_ms(freq*1000 - 6000)
            
    except OSError:
        led.value(1)
        #print('OSerror')
        #machine.reset()
        continue
