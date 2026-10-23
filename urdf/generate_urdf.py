"""Builds phonebot.urdf from cad/stl, computing inertials from the meshes.
Joint order == robot/config.yaml == the 13-vector sent by the phone."""
import os, yaml, trimesh
HERE = os.path.dirname(os.path.abspath(__file__))
STL = os.path.join(HERE, "..", "cad", "stl")
cfg = yaml.safe_load(open(os.path.join(HERE, "..", "robot", "config.yaml")))
LIM = {j["name"]: (j["min"], j["max"]) for j in cfg["joints"]}

MASS = {"pelvis": 0.30, "torso": 0.45, "hip_yaw_link": 0.09, "hip_roll_link": 0.09,
        "thigh": 0.10, "shank": 0.10, "ankle_link": 0.09, "foot": 0.05}  # kg (sums ~1.8 with phone)
EFFORT, VEL = 1.4, 5.5   # XL430-W250 @ ~11.1 V, approx - check datasheet


def link_xml(name, mesh):
    m = trimesh.load(os.path.join(STL, f"{mesh}.stl")); m.apply_scale(0.001)
    mass = MASS[mesh]; m.density = mass / m.volume
    c = m.center_mass; I = m.moment_inertia
    return f'''  <link name="{name}">
    <visual><geometry><mesh filename="../cad/stl/{mesh}.stl" scale="0.001 0.001 0.001"/></geometry></visual>
    <collision><geometry><mesh filename="../cad/stl/{mesh}.stl" scale="0.001 0.001 0.001"/></geometry></collision>
    <inertial><origin xyz="{c[0]:.5f} {c[1]:.5f} {c[2]:.5f}"/><mass value="{mass}"/>
      <inertia ixx="{I[0][0]:.3e}" ixy="{I[0][1]:.3e}" ixz="{I[0][2]:.3e}" iyy="{I[1][1]:.3e}" iyz="{I[1][2]:.3e}" izz="{I[2][2]:.3e}"/></inertial>
  </link>
'''


def joint_xml(name, parent, child, xyz, axis):
    lo, hi = LIM[name]
    return f'''  <joint name="{name}" type="revolute">
    <parent link="{parent}"/><child link="{child}"/>
    <origin xyz="{xyz[0]} {xyz[1]} {xyz[2]}"/><axis xyz="{axis[0]} {axis[1]} {axis[2]}"/>
    <limit lower="{lo}" upper="{hi}" effort="{EFFORT}" velocity="{VEL}"/>
  </joint>
'''


out = ['<?xml version="1.0"?>\n<robot name="phonebot_like">\n']
out.append(link_xml("pelvis", "pelvis")); out.append(link_xml("torso", "torso"))
out.append(joint_xml("torso_yaw", "pelvis", "torso", (0, 0, 0.030), (0, 0, 1)))
for s, y in (("l", 0.040), ("r", -0.040)):
    for ln, mesh in (("hip_yaw_link", "hip_yaw_link"), ("hip_roll_link", "hip_roll_link"),
                     ("thigh", "thigh"), ("shank", "shank"), ("ankle_link", "ankle_link"), ("foot", "foot")):
        out.append(link_xml(f"{s}_{ln}", mesh))
    out.append(joint_xml(f"{s}_hip_yaw", "pelvis", f"{s}_hip_yaw_link", (0, y, -0.025), (0, 0, 1)))
    out.append(joint_xml(f"{s}_hip_roll", f"{s}_hip_yaw_link", f"{s}_hip_roll_link", (0, 0, -0.028), (1, 0, 0)))
    out.append(joint_xml(f"{s}_hip_pitch", f"{s}_hip_roll_link", f"{s}_thigh", (0, 0, -0.028), (0, 1, 0)))
    out.append(joint_xml(f"{s}_knee", f"{s}_thigh", f"{s}_shank", (0, 0, -0.095), (0, 1, 0)))
    out.append(joint_xml(f"{s}_ankle_pitch", f"{s}_shank", f"{s}_ankle_link", (0, 0, -0.095), (0, 1, 0)))
    out.append(joint_xml(f"{s}_ankle_roll", f"{s}_ankle_link", f"{s}_foot", (0, 0, -0.025), (1, 0, 0)))
out.append("</robot>\n")
# joints were emitted left-leg-first, which matches config order (torso, l*, r*)
open(os.path.join(HERE, "phonebot.urdf"), "w").write("".join(out))
print("wrote phonebot.urdf")
