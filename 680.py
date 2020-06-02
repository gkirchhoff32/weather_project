import board
import busio
import adafruit_bme680
import time
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import datetime as dt

### INITIALIZE ###
real_time = True



### LOG DATA ###

i2c = busio.I2C(board.SCL, board.SDA)
sensor = adafruit_bme680.Adafruit_BME680_I2C(i2c)
##sensor.sea_level_pressure = 1013.25 # hPa

def animate(i):
        
        temps.append(sensor.temperature)
        humid.append(sensor.humidity)
        press.append(sensor.pressure/10)
        times.append(dt.datetime.now().strftime('%H:%M:%S'))

        Temps=temps[-50:]
        Humid=humid[-50:]
        Press=press[-50:]
        Times=times[-50:]
        
        ax1.clear(),ax2.clear(),ax3.clear()
        ax1.set_title('Temperature')
        ax2.set_title('Humidity')
        ax3.set_title('Pressure')
        ax1.set_ylabel('Temperature (C)')
        ax2.set_ylabel('Humidity (%)')
        ax3.set_ylabel('Pressure (kPa)')
        ax3.ticklabel_format(useOffset=False)
        fig.autofmt_xdate()
        ax3.xaxis.set_major_locator(plt.MaxNLocator(10))
        ax1.plot(Times,Temps,color='b')
        ax2.plot(Times,Humid,color='g')
        ax3.plot(Times,Press,color='r')

if real_time:
        temps = []
        humid = []
        press = []
        times = []
        
        fig=plt.figure(figsize=(16,16))
        ax1 = fig.add_subplot(311)
        ax2 = fig.add_subplot(312)
        ax3 = fig.add_subplot(313)
        ani = animation.FuncAnimation(fig,animate,interval=1000)
##        plt.tight_layout()
        plt.show()

while True:
	print('\n')
	print('Temperature: {0:.2f} degrees C'.format(sensor.temperature))
	print('Gas: {0} ohms'.format(sensor.gas))
	print('Humidity: {0:.2f}%'.format(sensor.humidity))
	print('Pressure: {0:.2f}kPa'.format(sensor.pressure/10))
##	print('Altitude: {} meters'.format(sensor.altitude))

	time.sleep(1)
