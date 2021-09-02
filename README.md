# baudrate values added more

By Craig Heffner, http://www.devttys0.com



	#sudo python3 baudrate.py -h
	-p <serial port>       Specify the serial port to use [/dev/ttyUSB0]
	-t <seconds>           Set the timeout period used when switching baudrates in auto detect mode [5]
	-c <num>               Set the minimum ASCII character threshold used during auto detect mode [25]
	-n <name>              Save the resulting serial configuration as <name> and automatically invoke minicom (implies -a)
	-a                     Enable auto detect mode
	-b                     Display supported baud rates and exit
	-q                     Do not display data read from the serial port
	-h                     Display help
	

forked from "https://github.com/devttys0/baudrate
