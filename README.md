# PhoneBot-class humanoid - full starter package (A to Z)

A smartphone-brained, 13-DoF, ~48 cm humanoid: **original design + software**, inspired by the public description at
https://phonebot.dev/ . It is NOT a copy of the authors' work and contains NONE of their files (CAD, BOM, video, paper, code,
trained policy). Those are CC BY-NC 4.0 - download them from the site yourself and respect the license (non-commercial).

## What is inside
| Folder | What |
|---|---|
| `cad/` | `generate_cad.py` (CadQuery) -> `step/` + `stl/` for 8 parts + phone reference, `preview.png` |
| `urdf/` | `phonebot.urdf` (+ generator) - 13 joints, same order as the code |
| `sim/` | `fk_check.py` - verifies joint order, height (~481 mm), flat feet in STAND pose |
| `robot/` | Onboard server: WebSocket <-> XL430 sync read/write, rate limit, joint limits, watchdog, gamepad, mock mode |
| `phone-app/` | React Native + TypeScript controller (connect, torque, 50 Hz policy loop, live joint telemetry) |
| `tools/` | `servo_setup.py` (scan/ID/baud/info), `calibrate.py` (zero offsets), `fake_phone.py` (PC test client + ONNX hook) |
| `docs/` | BOM, wiring, servo setup, assembly, sim/training roadmap |

## Quick start
    pip install -r requirements.txt cadquery trimesh yourdfpy matplotlib
    # 1) no hardware: simulated servos
    cd robot && python server.py --mock         # terminal 1
    cd tools && python fake_phone.py            # terminal 2
    # 2) regenerate models / URDF / check
    python cad/generate_cad.py && python urdf/generate_urdf.py && python sim/fk_check.py
    # 3) real robot: docs/SERVO_SETUP.md -> docs/WIRING.md -> docs/ASSEMBLY.md

## Honest status
- Verified in the sandbox: mock server + test client end-to-end; CAD export; URDF loads, joint order matches config, STAND pose
  keeps feet flat; tools compile and CLI parses.
- NOT verified: anything on real servos/hardware, the React Native app on a device, print strength/fit of the parts.
- Placeholders you must set: servo IDs/signs/offsets/limits (`robot/config.yaml`), XL430 specs (check ROBOTIS datasheet).
- Missing on purpose: walking policy + training pipeline, visual tracking/SLAM (see docs/SIM_AND_TRAINING.md).
- Safety: first tests with the robot hung in the air, a current-limited supply, and a hand on the power switch.
