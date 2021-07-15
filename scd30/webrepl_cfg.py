import ucryptolib
dec = ucryptolib.aes('', 1)
enc_val = ''
dec_val = dec.decrypt(enc_val)
dec_val = str(dec_val)
dec_val = dec_val.replace("b", '')
dec_val = dec_val.replace("\\x00", '')
dec_val = dec_val.replace("'", '')
PASS = dec_val