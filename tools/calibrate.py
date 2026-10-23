"""Zero-pose calibration. Torque is turned OFF; you pose the robot by hand in its
zero pose (legs straight, feet flat, torso facing forward), press Enter, and this writes
robot/config.calibrated.yaml with each joint's `offset` so that pose reads 0 rad.
`sign` you still set by hand: +angle must follow the URDF axes (see docs/ASSEMBLY.md).

  python calibrate.py --config ../robot/config.yaml
"""
import argparse, math, yaml
from dynamixel_sdk import PortHandler, PacketHandler

TPR = 4096 / (2 * math.pi)
ap = argparse.ArgumentParser(); ap.add_argument("--config", default="../robot/config.yaml")
a = ap.parse_args()
cfg = yaml.safe_load(open(a.config))
ph, pk = PortHandler(cfg["serial_port"]), PacketHandler(2.0)
assert ph.openPort() and ph.setBaudRate(cfg["baudrate"]), "cannot open serial port"
for j in cfg["joints"]:
    pk.write1ByteTxRx(ph, j["id"], 64, 0)
input("Torque OFF. Hold the robot in its ZERO pose, then press Enter... ")
for j in cfg["joints"]:
    ticks, rc, _ = pk.read4ByteTxRx(ph, j["id"], 132)
    if rc != 0:
        print(f"{j['name']}: no response (ID {j['id']}) - offset unchanged"); continue
    j["offset"] = round(j["sign"] * (ticks - 2048) / TPR, 4)
    print(f"{j['name']:<15} ID {j['id']:>2} ticks {ticks:>4} -> offset {j['offset']:+.4f} rad")
out = a.config.replace(".yaml", ".calibrated.yaml")
yaml.safe_dump(cfg, open(out, "w"), sort_keys=False); print("wrote", out)
