import asyncio

from pymodbus import pymodbus_apply_logging_config

from pymodbus.client import (
    AsyncModbusSerialClient,
)
from pymodbus.exceptions import ModbusException
from pymodbus.pdu import ExceptionResponse
from pymodbus.transaction import (
    ModbusRtuFramer,
)
from pymodbus.payload import BinaryPayloadDecoder
from pymodbus.constants import Endian


async def run_async_simple_client(port, slave, address, len_bytes):
    """Run async client."""
    pymodbus_apply_logging_config("DEBUG")

    client = AsyncModbusSerialClient(
        port,
        framer=ModbusRtuFramer,
        # timeout=10,
        # retries=3,
        # retry_on_empty=False,
        # close_comm_on_error=False,
        # strict=True,
        baudrate=9600,
        bytesize=8,
        parity="N",
        stopbits=2,
        # handle_local_echo=False,
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
            "COM5",
            27,
            6162,
            4
        ),
        debug=True
    )
