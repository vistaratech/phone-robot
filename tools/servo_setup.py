"""DYNAMIXEL XL430-W250-T bring-up tool (U2D2). Connect ONE servo at a time when setting IDs.

  python servo_setup.py scan                      # find servos on common baud rates
  python servo_setup.py set-id --from 1 --to 5    # change ID (bus at --baud)
  python servo_setup.py set-baud --id 1 --to 1000000
  python servo_setup.py info --ids 1-13           # model, voltage, temperature, hw errors
  python servo_setup.py wiggle --id 5             # +-0.1 rad torque test (be careful!)

NOT tested against real hardware by the author - try on a bench servo first.
"""
import argparse, time
from dynamixel_sdk import PortHandler, PacketHandler

A_MODEL, A_ID, A_BAUD, A_MODE = 0, 7, 8, 11
A_TORQUE, A_HWERR, A_GOAL, A_PVOLT, A_PTEMP, A_PPOS = 64, 70, 116, 144, 146, 132
BAUD = {9600: 0, 57600: 1, 115200: 2, 1000000: 3, 2000000: 4, 3000000: 5, 4000000: 6}
XL430_W250_MODEL = 1060


def open_bus(port, baud):
    ph = PortHandler(port)
    if not (ph.openPort() and ph.setBaudRate(baud)):
        raise SystemExit(f"cannot open {port} @ {baud}")
    return ph, PacketHandler(2.0)


def ids(spec):
    out = []
    for part in spec.split(","):
        a, _, b = part.partition("-")
        out += range(int(a), int(b or a) + 1)
    return out


def cmd_scan(a):
    for baud in (57600, 1000000, 115200, 2000000, 3000000, 4000000, 9600):
        ph, pk = open_bus(a.port, baud)
        found, _ = pk.broadcastPing(ph)
        print(f"baud {baud:>8}: {sorted(found) if found else 'none'}")
        ph.closePort()


def cmd_set_id(a):
    ph, pk = open_bus(a.port, a.baud)
    pk.write1ByteTxRx(ph, a.from_id, A_TORQUE, 0)
    rc, err = pk.write1ByteTxRx(ph, a.from_id, A_ID, a.to)
    print("ok" if rc == 0 and err == 0 else f"failed rc={rc} err={err}")


def cmd_set_baud(a):
    ph, pk = open_bus(a.port, a.baud)
    pk.write1ByteTxRx(ph, a.id, A_TORQUE, 0)
    rc, err = pk.write1ByteTxRx(ph, a.id, A_BAUD, BAUD[a.to])
    print("ok - reconnect at the new baud" if rc == 0 and err == 0 else f"failed rc={rc} err={err}")


def cmd_info(a):
    ph, pk = open_bus(a.port, a.baud)
    for i in ids(a.ids):
        model, rc, _ = pk.read2ByteTxRx(ph, i, A_MODEL)
        if rc != 0:
            print(f"ID {i:>2}: no response"); continue
        volt, _, _ = pk.read2ByteTxRx(ph, i, A_PVOLT)
        temp, _, _ = pk.read1ByteTxRx(ph, i, A_PTEMP)
        hw, _, _ = pk.read1ByteTxRx(ph, i, A_HWERR)
        tag = "XL430-W250" if model == XL430_W250_MODEL else f"model {model}"
        print(f"ID {i:>2}: {tag} | {volt/10:.1f} V | {temp} C | hw_err={hw:#04x}")


def cmd_wiggle(a):
    ph, pk = open_bus(a.port, a.baud)
    pk.write1ByteTxRx(ph, a.id, A_TORQUE, 0); pk.write1ByteTxRx(ph, a.id, A_MODE, 3)
    pos, _, _ = pk.read4ByteTxRx(ph, a.id, A_PPOS)
    pk.write1ByteTxRx(ph, a.id, A_TORQUE, 1)
    d = int(0.1 * 4096 / 6.2832)
    for tgt in (pos + d, pos - d, pos):
        pk.write4ByteTxRx(ph, a.id, A_GOAL, tgt); time.sleep(0.6)
    pk.write1ByteTxRx(ph, a.id, A_TORQUE, 0); print("done")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", default="/dev/ttyUSB0"); ap.add_argument("--baud", type=int, default=57600)
    sp = ap.add_subparsers(dest="c", required=True)
    sp.add_parser("scan").set_defaults(f=cmd_scan)
    s = sp.add_parser("set-id"); s.add_argument("--from", dest="from_id", type=int, required=True)
    s.add_argument("--to", type=int, required=True); s.set_defaults(f=cmd_set_id)
    s = sp.add_parser("set-baud"); s.add_argument("--id", type=int, required=True)
    s.add_argument("--to", type=int, choices=list(BAUD), required=True); s.set_defaults(f=cmd_set_baud)
    s = sp.add_parser("info"); s.add_argument("--ids", default="1-13"); s.set_defaults(f=cmd_info)
    s = sp.add_parser("wiggle"); s.add_argument("--id", type=int, required=True); s.set_defaults(f=cmd_wiggle)
    a = ap.parse_args(); a.f(a)
