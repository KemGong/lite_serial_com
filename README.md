# Lite Serial Debugger

A simple and user-friendly serial port debugging tool with data transmission, file saving, and other features.

## Features

- Serial Port Configuration
  - Multiple baud rate options (4800-1000000)
  - Configurable data bits, stop bits, and parity
  - Automatic port detection
  - Real-time port list refresh

- Data Reception
  - ASCII/HEX format display
  - Timestamp support
  - Packet display support
  - Configurable receive timeout
  - Auto-wrap support
  - Data saving to file

- Data Transmission
  - Single transmission
  - Loop transmission
  - Configurable delay
  - Multi-line text support

- Interface Features
  - Clear receive area
  - Auto-wrap toggle
  - File save status display
  - Port connection status display

## Requirements

- Python 3.6+
- Dependencies:
  - pyserial
  - tkinter (Python standard library)

## Installation

1. Clone or download this project
2. Install dependencies:
   ```bash
   pip install pyserial
   ```

## Usage

1. Run the program:
   ```bash
   python serial_debugger.py
   ```

2. Serial Port Setup:
   - Select the correct port
   - Set baud rate (default: 115200)
   - Configure data bits, stop bits, and parity
   - Click "Open Port" button

3. Data Reception:
   - Choose display mode (ASCII/HEX)
   - Toggle timestamp display
   - Enable/disable packet display
   - Set receive timeout
   - Toggle auto-wrap

4. Data Transmission:
   - Enter data in the send area
   - Click "Send" button to transmit
   - For loop transmission, check "Loop Send" and set delay

5. Data Saving:
   - Click "Select Save File" button
   - Choose save location
   - Data will be automatically saved
   - Click again to stop saving

## Notes

- Ensure proper port access permissions
- Make sure port is open before sending data
- Loop send delay cannot be less than 10ms
- Ensure write permissions for file saving

## Common Issues

1. Cannot Open Port
   - Check if port is in use by other programs
   - Verify port permissions
   - Confirm correct port parameters

2. Data Reception Issues
   - Verify baud rate matches
   - Check data bits, stop bits, and parity settings
   - Review packet display timeout settings

3. File Save Failures
   - Check file path permissions
   - Ensure sufficient disk space
   - Verify file isn't locked by other programs

## License

MIT License 