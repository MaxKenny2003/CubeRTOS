import argparse
import time
from ads7828 import ADS7828


TEST_CHANNELS = [
    ("I_5V0",        0x48, 0, 0.012, 100),  # name, addr, ch, Rsense, Gain
    ("I_3V3",        0x48, 2, 0.005, 100),
    ("I_VBATT_RAW",  0x48, 6, 0.012, 100),
    ("I_VBATT",      0x49, 6, 0.012, 100),  # ADC1 ch6 corresponds to global ch14
]


def read_voltage(adc: ADS7828, ch: int, avg: int, dt: float) -> float:
    if avg and avg > 1:
        return adc.read_channel_single_ended_averaged(
            ch, num_measurements=avg, dt=dt
        )
    return adc.read_channel_single_ended(ch)


def main():
    p = argparse.ArgumentParser(description="Read Eddy PDU currents via ADS7828")
    p.add_argument("--bus", type=int, default=1, help="I2C bus number (default: 1)")
    p.add_argument("--avg", type=int, default=10, help="Averaging samples (default: 10)")
    p.add_argument("--dt", type=float, default=0.01, help="Delay between avg samples in seconds (default: 0.01)")
    p.add_argument("--interval", type=float, default=0.0, help="Repeat interval seconds (0 = single shot)")
    args = p.parse_args()

    try:
        adc0 = ADS7828(address=0x48, smbus_num=args.bus)
        adc1 = ADS7828(address=0x49, smbus_num=args.bus)
    except Exception as e:
        print(f"Error initializing ADCs: {e}")
        return 1

    addr_to_adc = {0x48: adc0, 0x49: adc1}

    def one_pass():
        rows = []
        for name, addr, ch, rsense, gain in TEST_CHANNELS:
            try:
                adc = addr_to_adc[addr]
                v = read_voltage(adc, ch, args.avg, args.dt)
                i = v / (rsense * gain)
                rows.append((name, addr, ch, v, i))
            except Exception as e:
                rows.append((name, addr, ch, float("nan"), float("nan")))
                print(f"Read error for {name} (0x{addr:02X} ch{ch}): {e}")

        # Pretty print
        print("\nCurrents (computed from ADC voltage):")
        for name, addr, ch, v, i in rows:
            print(f"- {name:12s} ADC 0x{addr:02X} ch{ch}: {i:8.3f} A   (Vadc={v:6.4f} V)")

    if args.interval > 0:
        try:
            while True:
                one_pass()
                time.sleep(args.interval)
        except KeyboardInterrupt:
            pass
    else:
        one_pass()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

