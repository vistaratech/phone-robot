"""PhoneBot onboard-computer server.

Phone  --(WebSocket/JSON over Wi-Fi)-->  this server  --(U2D2/TTL)-->  13 servos
Phone  <--(joint state + gamepad)--                     <--(sync read)--

Messages from phone:
  {"type":"cmd","q":[13 joint targets, rad]}
  {"type":"torque","enable":true|false}
Messages to phone (stream):
  {"type":"state","t":<s>,"q":[...],"dq":[...],"load":[...],"torque":bool,"pad":{...}|null}
"""
import argparse, asyncio, json, logging, time
import websockets, yaml
from dxl_driver import make_driver
from gamepad import Gamepad

log = logging.getLogger("phonebot")


class Robot:
    def __init__(self, cfg, mock):
        self.cfg = cfg
        self.drv = make_driver(cfg, mock)
        self.n = self.drv.n
        self.pad = Gamepad()
        self.goal = None            # last accepted goal (rad)
        self.cmd = None             # latest raw command from phone
        self.last_cmd_t = 0.0
        self.torque = False
        self.q, self.dq, self.load = [0.0] * self.n, [0.0] * self.n, [0.0] * self.n
        self.clients = set()

    def on_message(self, raw):
        try:
            m = json.loads(raw)
        except ValueError:
            return
        if m.get("type") == "cmd":
            q = m.get("q")
            if isinstance(q, list) and len(q) == self.n and all(isinstance(x, (int, float)) for x in q):
                self.cmd, self.last_cmd_t = [float(x) for x in q], time.monotonic()
        elif m.get("type") == "torque":
            self.set_torque(bool(m.get("enable")))

    def set_torque(self, on):
        if on and not self.torque:
            self.goal = list(self.q)        # start from where we are: no jump
            self.drv.write_positions(self.goal)
        self.drv.set_torque(on); self.torque = on
        log.info("torque %s", "ON" if on else "OFF")

    async def control_loop(self):
        dt = 1.0 / self.cfg["control_hz"]
        vmax = self.cfg["max_joint_speed"] * dt
        hold_s = self.cfg["stale_hold_s"]; off_s = self.cfg.get("stale_torque_off_s", 0)
        while True:
            t0 = time.monotonic()
            self.q, self.dq, self.load = self.drv.read_state()
            if self.torque and self.goal is not None:
                stale = t0 - self.last_cmd_t
                if self.cmd is None or stale > hold_s:
                    target = list(self.q)            # watchdog: hold current pose
                    if off_s and stale > off_s:
                        self.set_torque(False)
                else:
                    target = self.drv.clamp(self.cmd)
                self.goal = [g + max(-vmax, min(vmax, t - g)) for g, t in zip(self.goal, target)]
                self.drv.write_positions(self.goal)
            await asyncio.sleep(max(0.0, dt - (time.monotonic() - t0)))

    async def feedback_loop(self):
        dt = 1.0 / self.cfg["feedback_hz"]
        while True:
            if self.clients:
                msg = json.dumps({"type": "state", "t": time.time(), "q": self.q, "dq": self.dq,
                                  "load": self.load, "torque": self.torque, "pad": self.pad.state()})
                websockets.broadcast(self.clients, msg)
            await asyncio.sleep(dt)

    async def handler(self, ws):
        self.clients.add(ws); log.info("phone connected: %s", ws.remote_address)
        try:
            async for raw in ws:
                self.on_message(raw)
        finally:
            self.clients.discard(ws); log.info("phone disconnected")

    async def run(self):
        async with websockets.serve(self.handler, self.cfg["host"], self.cfg["port"]):
            log.info("listening on ws://%s:%d", self.cfg["host"], self.cfg["port"])
            await asyncio.gather(self.control_loop(), self.feedback_loop())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="config.yaml")
    ap.add_argument("--mock", action="store_true", help="no hardware, simulated servos")
    a = ap.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
    cfg = yaml.safe_load(open(a.config))
    robot = Robot(cfg, a.mock)
    try:
        asyncio.run(robot.run())
    except KeyboardInterrupt:
        pass
    finally:
        robot.drv.close()


if __name__ == "__main__":
    main()
