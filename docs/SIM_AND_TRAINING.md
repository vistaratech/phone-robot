# Simulation & walking policy (NOT included - this is the hard part)

Included: `urdf/phonebot.urdf` (13 revolute joints, masses ~1.8 kg total, inertias from the meshes, joint limits from config),
and `sim/fk_check.py` (joint-order + standing-height sanity check).

Roadmap to walking:
1. Load the URDF in a physics sim (MuJoCo / Isaac / PyBullet - convert to MJCF if needed).
2. Model the actuator: position-controlled XL430 (P gain, ~1.4 N*m peak, ~5.5 rad/s) with delay/latency and noise.
3. Train a PPO velocity-tracking policy with domain randomization (mass, friction, latency, IMU noise).
4. Export to ONNX. Observation = IMU (gyro + gravity), joint q/dq, previous action, velocity command; action = joint-position
   offsets around STAND (`tools/fake_phone.py: OnnxPolicy` and `phone-app/src/policy.ts` mark where to plug it in).
   The observation layout in the code is a PLACEHOLDER - it must match your training env.
5. Test on the hung robot first, then on the floor with a safety harness.
