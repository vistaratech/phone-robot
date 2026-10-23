"""Desk-test client that plays the phone's role (runs on a PC).

  python fake_phone.py --url ws://<robot-ip>:8765 --seconds 5

Replace StandPolicy with OnnxPolicy once you have a trained locomotion policy.
"""
import argparse, asyncio, json, math, time
import websockets

N = 13
# neutral crouch (rad) in the config.yaml joint order - tune for your robot
STAND = [0.0,  0.0, 0.0, -0.4, 0.8, -0.4, 0.0,   0.0, 0.0, -0.4, 0.8, -0.4, 0.0]


class StandPolicy:
    def act(self, obs, t):
        q = list(STAND)
        q[0] = 0.15 * math.sin(2 * math.pi * 0.5 * t)   # gentle torso sway
        return q


class OnnxPolicy:
    """obs layout is a PLACEHOLDER - must match how you trained the policy."""
    def __init__(self, path, action_scale=0.25):
        import numpy as np, onnxruntime as ort
        self.np, self.s = np, ort.InferenceSession(path)
        self.inp = self.s.get_inputs()[0].name; self.scale = action_scale
        self.last = np.zeros(N, dtype=np.float32)

    def act(self, obs, t):
        np = self.np
        x = np.concatenate([obs["q"], obs["dq"], self.last]).astype(np.float32)[None]
        self.last = self.s.run(None, {self.inp: x})[0][0]
        return (np.array(STAND) + self.scale * self.last).tolist()


async def main(url, seconds, hz):
    pol = StandPolicy()
    obs = {"q": [0.0] * N, "dq": [0.0] * N}
    async with websockets.connect(url) as ws:
        async def reader():
            async for raw in ws:
                m = json.loads(raw)
                if m.get("type") == "state":
                    obs.update(q=m["q"], dq=m["dq"]); obs["torque"] = m["torque"]
        rt = asyncio.create_task(reader())
        await ws.send(json.dumps({"type": "torque", "enable": True}))
        t0 = time.time()
        while time.time() - t0 < seconds:
            t = time.time() - t0
            await ws.send(json.dumps({"type": "cmd", "q": pol.act(obs, t)}))
            await asyncio.sleep(1 / hz)
        print("final q[0..4]:", [round(x, 3) for x in obs["q"][:5]], "torque:", obs.get("torque"))
        await ws.send(json.dumps({"type": "torque", "enable": False}))
        rt.cancel()


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", default="ws://localhost:8765")
    ap.add_argument("--seconds", type=float, default=5)
    ap.add_argument("--hz", type=float, default=50)
    a = ap.parse_args()
    asyncio.run(main(a.url, a.seconds, a.hz))
