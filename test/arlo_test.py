from pyarlo import PyArlo

def set_arlo_mode(mode_name):

    arlo  = PyArlo('fredrik@jagare-lilja.se', '3rNQFmBLNBrK')
    
    if arlo == None or arlo.base_stations == None:
        print('Could not read arlo mode.')
        return
    
    base = arlo.base_stations[0]
    
    base_mode = base.mode
    print("Is mode " + base_mode)

    if base_mode != mode_name:
        print("Setting mode " + mode_name)
        base.mode = mode_name
        base.update()
    else:
        print("Mode not set")

def get_arlo_mode():

    arlo  = PyArlo('fredrik@jagare-lilja.se', '3rNQFmBLNBrK')
    
    if arlo == None or arlo.base_stations == None:
        print('Could not read arlo mode.')
        return
    
    base = arlo.base_stations[0]

    arlo_mode = base.mode
    print("Is mode " + arlo_mode)
    return arlo_mode
     
if __name__ == '__main__':
    get_arlo_mode()
    set_arlo_mode('schedule')
    get_arlo_mode()