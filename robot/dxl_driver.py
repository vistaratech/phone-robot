"""Dynamixel XL430-W250-T driver (Protocol 2.0) + a mock for desk testing."""
import math, time

TICKS_PER_RAD = 4096 / (2 * math.pi)
VEL_UNIT_RAD_S = 0.229 * 2 * math.pi / 60   # 0.229 rpm per unit

# XL430 control table
ADDR_OPERATING_MODE = 11
ADDR_TORQUE_ENABLE = 64
ADDR_GOAL_POSITION = 116
ADDR_PRESENT_LOAD = 126          # 2 bytes, then velocity (4), position (4)
READ_LEN = 10


def _s(v, bits):
    return v - (1 << bits) if v >= (1 << (bits - 1)) else v


class BaseDriver:
    def __init__(self, joints):
        self.joints = joints
        self.n = len(joints)
        self.lo = [j["min"] for j in joints]
        self.hi = [j["max"] for j in joints]

    def clamp(self, q):
        return [min(max(x, a), b) for x, a, b in zip(q, self.lo, self.hi)]

    def set_torque(self, on: bool): ...
    def write_positions(self, q): ...
    def read_state(self): ...   # -> (q, dq, load)
    def close(self): ...


class MockDriver(BaseDriver):
    """First-order lag toward the goal. No hardware needed."""
    def __init__(self, joints):
        super().__init__(joints)
        self.q = [0.0] * self.n
        self.goal = [0.0] * self.n
        self.dq = [0.0] * self.n
        self.torque = False
        self._t = time.monotonic()

    def set_torque(self, on):
        self.torque = on

    def write_positions(self, q):
        self.goal = self.clamp(q)

    def read_state(self):
        now = time.monotonic(); dt = now - self._t; self._t = now
        if self.torque and dt > 0:
            a = min(1.0, dt * 20.0)
            new = [p + a * (g - p) for p, g in zip(self.q, self.goal)]
            self.dq = [(n - p) / dt for n, p in zip(new, self.q)]
            self.q = new
        return list(self.q), list(self.dq), [0.0] * self.n


class DxlDriver(BaseDriver):
    def __init__(self, joints, port, baudrate, protocol=2.0):
        super().__init__(joints)
        from dynamixel_sdk import (PortHandler, PacketHandler,
                                   GroupSyncWrite, GroupSyncRead)
        self.ph = PortHandler(port)
        self.pk = PacketHandler(protocol)
        if not self.ph.openPort():
            raise RuntimeError(f"cannot open {port}")
        if not self.ph.setBaudRate(baudrate):
            raise RuntimeError(f"cannot set baudrate {baudrate}")
        self.ids = [j["id"] for j in joints]
        self.sign = [j["sign"] for j in joints]
        self.off = [j["offset"] for j in joints]
        self.sw = GroupSyncWrite(self.ph, self.pk, ADDR_GOAL_POSITION, 4)
        self.sr = GroupSyncRead(self.ph, self.pk, ADDR_PRESENT_LOAD, READ_LEN)
        for i in self.ids:
            self.sr.addParam(i)
        for i in self.ids:  # position control mode, torque off
            self.pk.write1ByteTxRx(self.ph, i, ADDR_TORQUE_ENABLE, 0)
            self.pk.write1ByteTxRx(self.ph, i, ADDR_OPERATING_MODE, 3)

    def set_torque(self, on):
        for i in self.ids:
            self.pk.write1ByteTxRx(self.ph, i, ADDR_TORQUE_ENABLE, 1 if on else 0)

    def _to_ticks(self, k, rad):
        return 2048 + round(self.sign[k] * (rad + self.off[k]) * TICKS_PER_RAD)

    def _to_rad(self, k, ticks):
        return self.sign[k] * (ticks - 2048) / TICKS_PER_RAD - self.off[k]

    def write_positions(self, q):
        q = self.clamp(q)
        self.sw.clearParam()
        for k, i in enumerate(self.ids):
            t = max(0, min(4095, self._to_ticks(k, q[k])))
            self.sw.addParam(i, [t & 0xFF, (t >> 8) & 0xFF, (t >> 16) & 0xFF, (t >> 24) & 0xFF])
        self.sw.txPacket()

    def read_state(self):
        q, dq, load = [], [], []
        self.sr.txRxPacket()
        for k, i in enumerate(self.ids):
            if not self.sr.isAvailable(i, ADDR_PRESENT_LOAD, READ_LEN):
                q.append(float("nan")); dq.append(0.0); load.append(0.0); continue
            ld = _s(self.sr.getData(i, ADDR_PRESENT_LOAD, 2), 16)
            vel = _s(self.sr.getData(i, ADDR_PRESENT_LOAD + 2, 4), 32)
            pos = self.sr.getData(i, ADDR_PRESENT_LOAD + 6, 4)
            q.append(self._to_rad(k, pos))
            dq.append(self.sign[k] * vel * VEL_UNIT_RAD_S)
            load.append(ld / 10.0)  # percent
        return q, dq, load

    def close(self):
        self.set_torque(False)
        self.ph.closePort()


def make_driver(cfg, mock=False):
    if mock:
        return MockDriver(cfg["joints"])
    return DxlDriver(cfg["joints"], cfg["serial_port"], cfg["baudrate"], cfg.get("protocol", 2.0))
