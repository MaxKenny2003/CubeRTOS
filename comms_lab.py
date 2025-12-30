# Script to convert from Beacon to RAP packet

file_path = "alphabeacon.txt"  # Replace with your file path

with open(file_path, "r") as f:
    sync_chars = f.read(4)
    print(f"Sync Characters: '{sync_chars}'")

    primary_id = f.read(4)
    print(f"Primary ID: '{primary_id}'")

    secondary_id = f.read(4)
    print(f"Secondary ID: '{secondary_id}'")

    flags = f.read(2)
    tap = '00'
    dap = '01'
    cap = '02'
    beacon = '03'
    if flags == beacon:
        print(f"Flags: Beacon")
    if flags == dap:
        print(f"Flags: DAP")

    length = f.read(4)
    # print(f"Length: '{length}'")
    decimal_value = int(length, 16)
    print(f"Length: {decimal_value}")

    with open(file_path, "r") as f:
        f.seek(0)
        header = f.read(18)
        header_bytes = bytes.fromhex(header)
        def fletcher16(data):
            sum1 = 0
            sum2 = 0
            modulus = 255  # 2^8 - 1

            for byte in data:
                sum1 = (sum1 + byte) % modulus
                sum2 = (sum2 + sum1) % modulus

            return (sum2 << 8) | sum1

        header_checksum = fletcher16(header_bytes)

        print(f"Header checksum: {header_checksum}")

        storedCS = f.read(4)

        remaining = f.read()

        data = remaining[0:-12]

        data_checksum = fletcher16(bytes.fromhex(data))

        print(f"Data checksum: {data_checksum}")

