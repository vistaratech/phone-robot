# Assembly & first power-up (for this design)

1. Generate/print parts (`cad/generate_cad.py` -> `cad/stl/`). These parts are simplified layout geometry: check fit against
   real servos with calipers, add screw holes/horn interfaces, and test-print before committing to all parts. Treat structural
   strength as UNVERIFIED.
2. Pre-set servo IDs (docs/SERVO_SETUP.md).
3. Build each leg bottom-up: foot <- ankle roll servo <- ankle link <- ankle pitch servo <- shank <- knee servo <- thigh <-
   hip pitch servo <- hip roll link <- hip roll servo <- hip yaw link <- hip yaw servo (mounted in the pelvis).
   Joint axes follow `urdf/phonebot.urdf`: yaw = Z, roll = X (forward), pitch/knee = Y (left).
4. Mount the torso yaw servo on the pelvis, torso on its horn; fit battery + SBC + buck converter in the torso bay and the phone
   in the front cradle.
5. Wire per docs/WIRING.md. Hang the robot from a stand so feet are off the ground.
6. Flash the SBC (Raspberry Pi OS), `pip install -r requirements.txt`, edit `robot/config.yaml` (IDs, signs, limits).
7. Calibrate: `python tools/calibrate.py` -> hold zero pose -> writes `robot/config.calibrated.yaml`; use it as your config.
   Check each joint's sign: positive command must match the URDF axis (flip `sign` to -1 where it doesn't; mirrored left/right
   servos usually need opposite signs on yaw/roll).
8. `python robot/server.py`, open the phone app, Connect -> Torque ON -> "Run stand policy". Keep a hand on the power switch.
