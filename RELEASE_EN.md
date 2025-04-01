# Serial Debugger Release Notes

## Version Information
- Version: 1.0.0
- Release Date: 2024-04-01
- Runtime Environment: Windows 10/11

## Installation Instructions
1. Download `SerialDebugger.exe`
2. Double-click to run, no installation required
3. Allow firewall access if prompted on first run

## System Requirements
- Windows 10 or higher
- At least 100MB free disk space
- Serial port drivers properly installed

## Features
- Serial Port Configuration
  - Multiple baud rates (4800-1000000)
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

## Usage Instructions
1. Run the program
2. Select the correct port
3. Configure port parameters
4. Click "Open Port"
5. Start using

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

## Changelog
### v1.0.0 (2024-03-21)
- Initial release
- Basic serial debugging functionality
- Data transmission and file saving support

## Technical Support
For issues, please submit an Issue or contact technical support.

## License
MIT License 