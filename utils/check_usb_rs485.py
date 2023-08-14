import asyncio
import sys

from pymodbus import pymodbus_apply_logging_config
from pymodbus.client import AsyncModbusSerialClient
from pymodbus.exceptions import ModbusException
from pymodbus.pdu import ExceptionResponse
from pymodbus.payload import BinaryPayloadDecoder
from pymodbus.constants import Endian


args = sys.argv
PORT = args[1]


async def run_async_simple_client(port, slave, address, len_bytes):
    pymodbus_apply_logging_config("WARNING")

    client = AsyncModbusSerialClient(
        port,
        timeout=5,
        retries=3,
        baudrate=9600,
        bytesize=8,
        parity="N",
        stopbits=2,
    )

    print("connect to server")
    await client.connect()
    assert client.connected

    print("get and verify data")
    try:
        response = await client.read_input_registers(address, len_bytes, slave=slave)
    except ModbusException as exc:
        print(f"Received ModbusException({exc}) from library")
        client.close()
        return
    if response.isError():
        print(f"Received Modbus library error({response})")
        client.close()
        return
    if isinstance(response, ExceptionResponse):  # pragma no cover
        print(f"Received Modbus library exception ({response})")
        client.close()
    else:
        raw_data = response.encode()
        print(f'Get raw data: {raw_data} : {type(raw_data)}')
        decoder = BinaryPayloadDecoder.fromRegisters(
            response.registers,
            byteorder=Endian.Big,
            wordorder=Endian.Little
        )
        decoded_data = decoder.decode_32bit_int()
        print(f'Decoded data: {decoded_data}')

    print("close connection")
    client.close()


if __name__ == "__main__":
    asyncio.run(
        run_async_simple_client(
            PORT,  # /dev/ttyUSB0
            27,
            6162,
            4
        ),
        debug=True
    )
