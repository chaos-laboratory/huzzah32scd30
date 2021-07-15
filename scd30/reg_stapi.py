import ujson
import urequests
import ubinascii
import ucryptolib

def decrypt(key):
    dec = ucryptolib.aes(key, 1)
    enc_val = ''
    dec_val = dec.decrypt(enc_val)
    dec_val = str(dec_val)
    dec_val = dec_val[1:]
    dec_val = dec_val.replace("\\x00", '')
    dec_val = dec_val.replace("'", '')
    return dec_val

def get_thingid(thing_name, thing_desc, uid):
    url = '' 
    #check if this thing already exist on the database
    #only if the name, desciption and unique id 
    filter_obj = "Things?$filter=name eq '" + thing_name + "' and description eq '" +\
                 thing_desc + "' and properties/uid eq '"+ uid + "'&$expand=Locations($select=name),Datastreams($select=id)&$select=id"
    filter_obj = filter_obj.replace(" ", "%20")
    filter_obj = filter_obj.replace("'", "%27")
    response = urequests.get(url+filter_obj)
    parse = response.json()
    thing_ls = parse['value']

    thingid_ls = []
    for thing in thing_ls:
        thingid = thing['@iot.id']
        thingid_ls.append(thingid)

    return thingid_ls

def get_dsid(thing_id, ds_name, ds_desc):
    url = '' 
    filter_obj = "Datastreams?$filter=name eq '" + ds_name + "' and description eq '" +\
                 ds_desc + "' and Things/id eq '"+ str(thing_id) + "'&$select=id"
    filter_obj = filter_obj.replace(" ", "%20")
    filter_obj = filter_obj.replace("'", "%27")
    response = urequests.get(url+filter_obj)
    parse = response.json()
    ds_ls = parse['value']
    return ds_ls

def post_thing(thing_name, thing_desc, uid, pins, loc_name, loc_desc, coordinates):
    url = '' 
    use_pass = decrypt('')
    
    loc_data = {
                    'name': loc_name,
                    'description': loc_desc,
                    'encodingType': 'application/vnd.geo+json',
                    'location': {
                                    "type": "Point",
                                    "coordinates": coordinates
                                }
                }
    
    thingloc_data = {
                        'name': thing_name,
                        'description': thing_desc,
                        'properties': {'uid': uid, 'pins': pins},
                        'Locations': [loc_data]
                     }
    
    headers = {'Authorization' : 'Basic ' + use_pass}
    response = urequests.post(url + 'Things', headers = headers,
                              json = thingloc_data)
    response.close()
    if response.status_code == 201:
        #check the thing and return its id
        thingid_ls = get_thingid(thing_name, thing_desc, uid)
        thingid = thingid_ls[0]
        #post the datastreams 
        return thingid
    else:
        return None

def post_datastreams(thing_id, thing_name, ds_descs, ds_snr_ids, ds_obs_id, ds_obs_types,
                     ds_uom_names, ds_uom_syms, ds_uom_defs):
    url = ''
    use_pass = decrypt('')
    
    ds_data = {
                'name': '',
                'description': '',
                'observationType': '',
                'unitOfMeasurement': '',
                'Thing':{'@iot.id':thing_id},
                'ObservedProperty':{},
                'Sensor':{}
                }
    
    ds_uom = {'name': '',
              'symbol': '',
              'definition': ''}
    
    ds_id_d = {}
    for cnt,desc in enumerate(ds_descs):
        ds_name = thing_name + '_' + desc
        ds_data['name'] = ds_name
        ds_data['description'] = desc
        ds_data['observationType'] = ds_obs_types[cnt]
        
        ds_uom['name'] = ds_uom_names[cnt]
        ds_uom['symbol'] = ds_uom_syms[cnt]
        ds_uom['definition'] = ds_uom_defs[cnt]
        ds_data['unitOfMeasurement'] = ds_uom
        
        ds_data['ObservedProperty'] = {'@iot.id':ds_obs_id[cnt]}
        ds_data['Sensor'] = {'@iot.id':ds_snr_ids[cnt]}
        #post the datastream
        headers = {'Authorization' : 'Basic ' + use_pass}
        response = urequests.post(url + 'Datastreams', headers = headers,
                                  json = ds_data)
        response.close()
        if response.status_code == 201:
            #check the datastream and return its id
            dsid_ls = get_dsid(thing_id, ds_name, desc)
            dsid = dsid_ls[0]['@iot.id']
            ds_id_d[desc] = dsid
            
    return ds_id_d

def post_obs(time_str, result, ds_id):
    url = ''
    use_pass = decrypt('')
    
    obs_data = {
                    'phenomenonTime': time_str,
                    'resultTime': time_str,
                    'result': result,
                    'Datastream':{'@iot.id':ds_id}
                }
    
    headers = {'Authorization' : 'Basic ' + use_pass}
    response = urequests.post(url + 'Observations', headers = headers,
                              json = obs_data)
    response.close()
    #if response.status_code == 201:
    #    print('successfully posted')
