# Bill of materials (for THIS design)

Prices intentionally left out - check suppliers (and India import duty). The PhoneBot paper claims ~$400
excluding the phone; the 13 servos are the biggest single cost, so verify against their official BOM.

| Qty | Part | Notes |
|---|---|---|
| 13 | DYNAMIXEL XL430-W250-T | 12 leg joints + 1 torso yaw. Order 3-pin TTL cables with them |
| 1 | U2D2 (USB <-> TTL/RS-485) | Optional: U2D2 Power Hub board makes wiring cleaner |
| 1 | Single-board computer with Wi-Fi | My suggestion: Raspberry Pi Zero 2 W (or Pi 4 / Orange Pi). Runs `robot/server.py` |
| 1 | 3S LiPo, 11.1 V, ~1000-1500 mAh | With balance lead. Use a LiPo-safe charger + low-voltage alarm |
| 1 | 5 V / 3 A buck converter (DC-DC) | Powers the SBC from the 3S pack |
| 1 | Main switch + inline fuse holder | Fuse sizing: see docs/WIRING.md |
| 1 | Android/iOS smartphone, ~150 x 72 mm | Sits in the torso cradle. Needs Wi-Fi. Old phones are fine |
| 1 | Wireless gamepad (optional) | Plugs into the SBC (USB dongle / Bluetooth) |
| - | M2.5 + M2 screws, nuts, standoffs | Servo mounting uses small metric screws; buy an assorted kit |
| - | Filament: PETG or nylon (PLA ok for prototypes) | Print `cad/stl/*` (or your improved parts); legs x2 |
| - | Wire (silicone 18-20 AWG), XT30 connectors, heat shrink | Power distribution |
| - | Velcro strap / foam tape | Battery + phone retention |

Printable parts (cad/stl): pelvis, torso, hip_yaw_link x2, hip_roll_link x2, thigh x2, shank x2, ankle_link x2, foot x2.
`phone_reference` is only a visual stand-in for the phone - do not print.
