
### Options

- `-p <serial port>`: Specify the serial port to use [/dev/ttyUSB0]
- `-t <seconds>`: Set the timeout period used when switching baud rates in auto-detect mode [5]
- `-c <num>`: Set the minimum ASCII character threshold used during auto-detect mode [25]
- `-n <name>`: Save the resulting serial configuration as `<name>` and automatically invoke Minicom (implies -a)
- `-a`: Enable auto-detect mode
- `-b`: Display supported baud rates and exit
- `-q`: Do not display data read from the serial port
- `-h`: Display help

## Credits

This code was originally created by Craig Heffner and can be found at [devttys0/baudrate](https://github.com/devttys0/baudrate). This version has been forked and improved.

## How to Use

1. Install the required Python packages by running `pip install -r requirements.txt`.

2. Run the script with the desired command-line arguments, for example:
