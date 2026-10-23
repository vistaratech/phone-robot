# Servo bring-up (do this before assembling)

1. Install `pip install dynamixel-sdk` and connect ONE servo to the U2D2 (12 V bench supply or 3S).
2. `python tools/servo_setup.py scan` -> note the baud it answers on (factory default is usually 57600).
3. Give it its final ID: `python tools/servo_setup.py set-id --from 1 --to <ID>`  (IDs per `robot/config.yaml`: 1 torso_yaw,
   2-7 left leg [hip yaw, hip roll, hip pitch, knee, ankle pitch, ankle roll], 8-13 right leg same order).
4. Raise baud to 1 Mbps: `python tools/servo_setup.py set-baud --id <ID> --to 1000000` (then use `--baud 1000000`).
5. Label the servo with a sticker (ID + joint name). Repeat for all 13.
6. Connect all 13, run `python tools/servo_setup.py --baud 1000000 info --ids 1-13` - every ID should answer with a sane voltage.
7. Optional bench check: `wiggle --id N` (small +-0.1 rad move). The Dynamixel Wizard 2.0 GUI from ROBOTIS can do all of this too.
