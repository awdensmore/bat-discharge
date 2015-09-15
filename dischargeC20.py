import serial
import time
import sys

# Theory of operation
# Discharge the battery at the industry standard "C20" rate in order
# to determine the battery's actual capacity as a ratio of it's 
# rated capacity (ie, determine the State of Health, SoH).
# Discharging ends under one of two conditions: battery has completed
# its cycle as per its rating, or voltage has reached a minimum.
# Data is logged by polling voltage from RLP

# User Configurable Settings
ev =  10500 # Ending voltage in mV
cap = 7500 # Battery's capacity is mAh
c_rate = 0.05 # Discharge rate. Should be 0.05 (ie C-20)
log_int = 60 # logging interval in seconds
usb_id = "/dev/ttyUSB0"

ser = serial.Serial(usb_id, 115200, timeout=1)
time.sleep(0.1)

def rlp_read(digits):
	time.sleep(0.5)
	ser.write('read\r')
	time.sleep(0.2)
	bytes = ser.inWaiting() - 1
	start = -1 * (digits + 1)
	ret_str = ser.read(bytes)
	return int(ret_str[start:])

def rlp_write(dcr):
	time.sleep(0.05)
	ser.write('set ' + str(dcr) + '\r')

# Return the name of the log file as "log_YYYY-MM-DD-HH-MM"
def rlp_date():
	t = time.localtime(time.time())
	yr = str(t.tm_year)
	mon = str(format(t.tm_mon, '02d'))
	day = str(format(t.tm_mday, '02d'))
	hr = str(format(t.tm_hour+2, '02d')) # UTC + 2, SAST
	mn = str(format(t.tm_min, '02d'))
	y = "log_" + yr + "-" + mon + "-" + day + "-" + hr + "-" + mn
	return y

# Write one entry to the log file
def rlp_log(log_name, t_time, v):
	# log_name = name of the log file
	# t_time = seconds test has been running
	# v = voltage to record in log file
	global c_rate
	with open(log_name, 'a') as log:
		log.write(str(format(t_time/60, '.0f'))+", "+str(v)+", "+str(c_rate)+"\n")

# End the discharge test
def rlp_end():
	rlp_write(0)
	ser.close()
	sys.exit()

def main():
	global ev
	global log_int
	global cap
	global c_rate
	log_name = rlp_date()
	log_entries = 0
	v = rlp_read(5)
	dr = int(cap * c_rate)
	end = 20*60*60 # end time in seconds

	# Verify battery can be discharged
	if (v < ev):
		print("Bat voltage too low, exiting")
		ser.close()
		sys.exit()

	# Begin discharge
	stime = time.time()
	rlp_write(dr)
	while(1):
		v = rlp_read(5)
		now = time.time() - stime
		
		# Log voltage and current per logging interval
		if now > (log_entries * log_int):
			rlp_log(log_name, now, v)
			log_entries = log_entries + 1

		# Terminate script when ending voltage is reached
		if v < ev:
			print("Reached min voltage, exiting")
			rlp_log(log_name, now, v)
			rlp_end()
		elif now >= end:
			print("Reached 20 hours of test, exiting")
			rlp_end()

main()
