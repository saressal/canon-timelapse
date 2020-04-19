import gphoto2 as gp
import os, sys, subprocess
import pytz, warnings, time
from datetime import timedelta
from datetime import datetime
from astral import Astral
from pysolar.solar import get_altitude
from fmi import FMI

warnings.simplefilter('ignore',UserWarning)

def main():

    while(True):
        sunrise,sunset = get_sun()

        # Take pictures until sunset
        while(datetime.time(datetime.now()) < datetime.time(sunset)):
            fname = datetime.now().strftime('%Y_%m_%d_%H_%M_%S')+'.jpg'
            take_image(fname)
            time.sleep(600)

        # Wait until sunrise to continue imaging
        print(datetime.now().strftime('%Y %m %d')+' doned, sleeping until sunrise'))
        wait = sunrise-datetime.now(pytz.timezone("Europe/Helsinki"))
        time.sleep(wait.seconds)

    return  0

def init_camera():
    camera = gp.Camera()
    camera.init()
    
    return camera

def take_image(fpath=None):
    camera = init_camera()
    config_camera(camera)

    file_path = camera.capture(gp.GP_CAPTURE_IMAGE)
    camera_file = camera.file_get(file_path.folder,file_path.name,gp.GP_FILE_TYPE_NORMAL)

    if not fpath: fpath = file_path.name

    camera_file.save(fpath)
    print(fpath+' captured')
    camera.exit()

    return fpath

def config_camera(camera):
    
    # Get weather data and sun location
    weather, altitude = get_weather()

    # Configure white balance
    if altitude < 10: wb = 'Shade'
    else: 
        if weather.cloud_coverage > 50: wb = 'Cloudy'
        else: wb = 'Cloudy'

    cfg = camera.get_config()
    wb_cfg = cfg.get_child_by_name('whitebalance')
    # Options
    # Auto
    # Daylight
    # Shade
    # Cloudy
    wb_cfg.set_value(wb)
    camera.set_config(cfg)

def get_sun():
    a = Astral()
    a.solar_depression = 'civil'
    city = a['Helsinki']
    sun = city.sun(date=datetime.now(),local = True)
    sunset = sun['dusk']
    sun = city.sun(date=datetime.now()+timedelta(days=1),local = True)
    sunrise = sun['dawn']

    return sunrise,sunset

def get_weather():
    f = FMI(place='Kumpula')
    latestWeather = f.observations()[-1]
    date = datetime.now(pytz.timezone("Europe/Helsinki"))
    sun_altitude = get_altitude(60.188137, 24.953949, date)

    return latestWeather,sun_altitude

if __name__ == "__main__":
    sys.exit(main())