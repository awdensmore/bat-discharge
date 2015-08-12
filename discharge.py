import serial
import time
import sys

# Theory of operation
# Discharge the battery as per the "dr" rate in user settings
# until the voltage reaches "ev". At that point, reduce the
# discharge rate by 20%, then continue to discharge until the
# voltage again reaches "ev". Iterate until the discharge rate
# reaches "dr_min", then stop discharging and exit.

# User Configurable Settings
ev = 10500 # Ending voltage in mV
dr = 1500 # Discharge rate in mA
dr_min = 200 # end discharging when rate is reduced to this

ser = serial.Serial('/dev/cu.usbserial-DAXYHK1F', 115200, timeout=1)
time.sleep(0.1)

def rlp_read(digits):
	time.sleep(0.05)
	ser.write('read\r')
	time.sleep(0.1)
	bytes = ser.inWaiting() - 1
	start = -1 * (digits + 1)
	ret_str = ser.read(bytes)
	return int(ret_str[start:])

def rlp_write(dcr):
	time.sleep(0.05)
	ser.write('set ' + str(dcr) + '\r')

def main():
	global dr
	global ev
	v = rlp_read(5)
	if (v < ev):
		print("Bat voltage too low, exiting")
		ser.close()
		sys.exit()
	rlp_write(dr)
	while(1):
		v = rlp_read(5)
		if v < ev:
			dr = dr * 0.8
			rlp_write(dr)
		if dr <= dr_min:
			print("Reached min discharge rate, exiting")
			rlp_write(0)
			ser.close()
			sys.exit()

main()
#print rlp_read(5)
#rlp_write(200)
#print rlp_read(5)
#rlp_write(100)
