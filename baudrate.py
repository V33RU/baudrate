import sys
import time
import serial
import subprocess
import argparse
import tty
import termios
import getch
from threading import Thread

class RawInput:
    def __init__(self):
        try:
            self.impl = RawInputWindows()
        except ImportError:
            self.impl = RawInputUnix()

    def __call__(self):
        return self.impl()

class RawInputUnix:
    def __call__(self):
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

class RawInputWindows:
    def __call__(self):
        return getch.getch()

class BaudrateDetector:
    BAUDRATES = [
    "110", "150", "300", "600", "800", "1200", "1600", "1800", "2400", "2604", "3200", "4800",
    "5208", "6400", "9600", "9606", "10417", "12800", "14400", "15625", "14406", "19200", "19211",
    "25600", "26042", "28800", "31250", "38400", "38422", "52083", "57600", "57692", "78600",
    "104167", "115200", "115384", "156250", "230400", "230769", "256000", "312500", "460800",
    "461538", "921600", "923076",
    ]

    def __init__(self, port, threshold, timeout, name, auto, verbose):
        self.port = port
        self.threshold = threshold
        self.timeout = timeout
        self.name = name
        self.autoDetect = auto
        self.verbose = verbose
        self.index = 0
        self.validCharacters = []
        self.ctlc = False
        self.serial = None

        self._generateCharList()

    def _generateCharList(self):
        self.validCharacters = [chr(i) for i in range(32, 127)]

    def openSerialPort(self):
        try:
            self.serial = serial.Serial(self.port, timeout=self.timeout)
        except serial.SerialException as e:
            print(f"Error opening serial port: {e}")
            sys.exit(1)

    def closeSerialPort(self):
        if self.serial:
            self.serial.close()

    def nextBaudrate(self, updn):
        self.index += updn

        if self.index >= len(self.BAUDRATES):
            self.index = 0
        elif self.index < 0:
            self.index = len(self.BAUDRATES) - 1

        self.serial.flush()
        self.serial.baudrate = int(self.BAUDRATES[self.index])
        self.serial.flush()

    def detectBaudrate(self):
        count = 0
        whitespace = 0
        punctuation = 0
        vowels = 0
        startTime = 0
        timedOut = False
        clearCounters = False

        if not self.autoDetect:
            self.thread = Thread(target=self.handleKeypress)
            self.thread.start()

        while True:
            if startTime == 0:
                startTime = time.time()

            byte = self.serial.read(1)

            if byte:
                if self.autoDetect and byte in self.validCharacters:
                    if byte.isspace():
                        whitespace += 1
                    elif byte in '.,:;?!':
                        punctuation += 1
                    elif byte in 'aeiouAEIOU':
                        vowels += 1

                    count += 1
                else:
                    clearCounters = True

                sys.stderr.buffer.write(byte)

                if count >= self.threshold and whitespace > 0 and punctuation > 0 and vowels > 0:
                    break
                elif (time.time() - startTime) >= self.timeout:
                    timedOut = True
            else:
                timedOut = True

            if timedOut and self.autoDetect:
                startTime = 0
                self.nextBaudrate(-1)
                clearCounters = True
                timedOut = False

            if clearCounters:
                whitespace = 0
                punctuation = 0
                vowels = 0
                count = 0
                clearCounters = False

            if self.ctlc:
                break

        return self.BAUDRATES[self.index]

    def handleKeypress(self):
        userinput = RawInput()
        while not self.ctlc:
            c = userinput()
            if c in 'uUAdD':
                self.nextBaudrate(1)
            elif c == '\x03':
                self.ctlc = True

    def minicomConfig(self):
        config = f"########################################################################\n"
        config += f"# Minicom configuration file - use \"minicom -s\" to change parameters.\n"
        config += f"pu port             {self.port}\n"
        config += f"pu baudrate         {self.BAUDRATES[self.index]}\n"
        config += f"pu bits             8\n"
        config += f"pu parity           N\n"
        config += f"pu stopbits         1\n"
        config += f"pu rtscts           No\n"
        config += f"########################################################################\n"

        if self.name:
            try:
                with open(f"/etc/minicom/minirc.{self.name}", "w") as configFile:
                    configFile.write(config)
                return True, config
            except Exception as e:
                return False, f"Error saving minicom config file: {str(e)}"
        else:
            return False, "Configuration name not provided."

def main():
    parser = argparse.ArgumentParser(description="Baudrate Detector")
    parser.add_argument('-p', '--port', default='/dev/ttyUSB0', help="Serial port to use")
    parser.add_argument('-t', '--timeout', type=int, default=5, help="Timeout period for baudrate detection")
    parser.add_argument('-c', '--threshold', type=int, default=25, help="Minimum ASCII character threshold")
    parser.add_argument('-n', '--name', help="Save configuration as <name> and run minicom")
    parser.add_argument('-a', '--auto', action='store_true', help="Enable auto detect mode")
    parser.add_argument('-q', '--quiet', action='store_true', help="Suppress data display")
    args = parser.parse_args()

    baudrateDetector = BaudrateDetector(
        port=args.port,
        threshold=args.threshold,
        timeout=args.timeout,
        name=args.name,
        auto=args.auto,
        verbose=not args.quiet
    )

    try:
        baudrateDetector.openSerialPort()
        detectedRate = baudrateDetector.detectBaudrate()
        print(f"Detected baudrate: {detectedRate}")

        if args.name:
            success, config = baudrateDetector.minicomConfig()
            if success:
                print("Configuration saved.")
                runMinicom = input("Run minicom now [Y/n]? ").strip().lower() != 'n'
                if runMinicom:
                    subprocess.call(["minicom", args.name])
            else:
                print(config)

    except KeyboardInterrupt:
        pass
    finally:
        baudrateDetector.closeSerialPort()

if __name__ == '__main__':
    main()
