"""Parametric CAD for an original ~48 cm, 13-DoF humanoid (PhoneBot-class layout).

Independent design - NOT the PhoneBot authors' CAD. Parts are simplified solids
(brackets + XL430 envelope blocks) for layout, URDF/sim and as a starting point
for your own printable design. Units: mm. Each part's origin = the axis of the
joint that moves it; limbs hang along -Z.

    pip install cadquery
    python generate_cad.py        # writes step/*.step and stl/*.stl
"""
import os
import cadquery as cq

HERE = os.path.dirname(os.path.abspath(__file__))
SERVO = (34.0, 28.5, 46.5)   # XL430 envelope (x, y, z) - verify against datasheet


def B(x, y, z, cx=0.0, cy=0.0, cz=0.0, fillet=0.0):
    w = cq.Workplane("XY").box(x, y, z)
    if fillet:
        w = w.edges("|Z").fillet(fillet)
    return w.translate((cx, cy, cz))


def servo(cx, cy, cz, dims=SERVO):
    return B(*dims, cx=cx, cy=cy, cz=cz)


def union(*ws):
    out = ws[0]
    for w in ws[1:]:
        out = out.union(w)
    return out


# --- leg geometry (mm) - must match urdf/generate_urdf.py --------------------
HIP_Y = 40; HIP_YAW_DZ = 25; ROLL_DZ = 28; PITCH_DZ = 28
THIGH = 95; SHANK = 95; ANKLE_DZ = 25; SOLE_DZ = 22


def parts():
    P = {}
    # pelvis: frame + 3 servos (2x hip yaw, 1x torso yaw)
    P["pelvis"] = union(
        B(50, 100, 50, cz=-8, fillet=4),
        servo(0, HIP_Y, -HIP_YAW_DZ), servo(0, -HIP_Y, -HIP_YAW_DZ),
        servo(0, 0, 24),
    )
    # torso: base plate, electronics bay, phone cradle on the front
    cradle = B(14, 80, 156, cx=34, cz=55, fillet=3).cut(B(9, 74, 150, cx=36, cz=55))
    P["torso"] = union(
        B(60, 80, 6, cz=3, fillet=3),
        B(46, 70, 70, cx=-6, cz=41, fillet=3),
        cradle,
    )
    # leg links: bar to the child joint + the child joint's servo
    P["hip_yaw_link"] = union(B(40, 34, 10, cz=-5), servo(0, 0, -ROLL_DZ, (46.5, 28.5, 34.0)))
    P["hip_roll_link"] = union(B(34, 34, 12, cz=-6), servo(0, 0, -PITCH_DZ))
    P["thigh"] = union(B(30, 12, THIGH, cz=-THIGH / 2), servo(0, 0, -THIGH))
    P["shank"] = union(B(30, 12, SHANK, cz=-SHANK / 2), servo(0, 0, -SHANK))
    P["ankle_link"] = union(B(30, 30, 10, cz=-5), servo(0, 0, -ANKLE_DZ, (46.5, 28.5, 34.0)))
    P["foot"] = union(
        B(100, 60, 5, cx=10, cz=-SOLE_DZ + 2.5, fillet=6),
        B(30, 34, SOLE_DZ - 5, cz=-(SOLE_DZ - 5) / 2 - 0.0),
    )
    # reference only: a generic 150 x 72 x 8 phone
    P["phone_reference"] = cq.Workplane("XY").box(8, 72, 150).edges("|X").fillet(8)
    return P


if __name__ == "__main__":
    for name, wp in parts().items():
        cq.exporters.export(wp, os.path.join(HERE, "step", f"{name}.step"))
        cq.exporters.export(wp, os.path.join(HERE, "stl", f"{name}.stl"), tolerance=0.05)
        print("wrote", name)
