import serial


def open_serial_port(port_name, baud_rate) -> serial.Serial:
    ser = serial.Serial()
    ser.baudrate = baud_rate
    ser.port = port_name
    ser.open()
    if ser.is_open:
        return ser
    return None


def close_serial_port(ser_port: serial.Serial):
    if ser_port.is_open:
        ser_port.close()
    else:
        print('Port ' + ser_port.name + ' is already closed')


def write_to_serial_port(target_port: serial.Serial, data_to_write: str):
    if target_port.is_open:
        target_port.write(bytes(data_to_write))
    else:
        print('Port ' + target_port.name + ' is closed')

