"""Sanity-check the URDF: joint order vs config, standing height, flat feet in the STAND pose,
and write a preview image.   python fk_check.py"""
import os, numpy as np, yaml
from yourdfpy import URDF
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

HERE = os.path.dirname(os.path.abspath(__file__))
cfg = yaml.safe_load(open(os.path.join(HERE, "..", "robot", "config.yaml")))
robot = URDF.load(os.path.join(HERE, "..", "urdf", "phonebot.urdf"), build_scene_graph=True, load_meshes=True)

names = [j["name"] for j in cfg["joints"]]
assert robot.actuated_joint_names == names, (robot.actuated_joint_names, names)
print("joint order matches config.yaml (13 joints)")

STAND = [0.0, 0.0, 0.0, -0.4, 0.8, -0.4, 0.0, 0.0, 0.0, -0.4, 0.8, -0.4, 0.0]


def report(q, label):
    robot.update_cfg(np.array(q))
    b = robot.scene.bounds
    T = robot.get_transform("l_foot", "pelvis")
    print(f"{label}: total height {1000*(b[1][2]-b[0][2]):.0f} mm | l_foot tilt vs pelvis "
          f"{np.degrees(np.arccos(np.clip(T[2,2],-1,1))):.2f} deg | pelvis above sole "
          f"{1000*(-T[2,3]+0.022):.0f} mm")


report([0.0] * 13, "straight legs")
report(STAND, "STAND pose  ")

mesh = robot.scene.dump(concatenate=True)
fig = plt.figure(figsize=(9, 5))
for k, (el, az) in enumerate(((10, 0), (10, 90))):
    ax = fig.add_subplot(1, 2, k + 1, projection="3d")
    ax.add_collection3d(Poly3DCollection(mesh.vertices[mesh.faces], alpha=0.9, facecolor="#9db4c0", edgecolor="#2b3a42", linewidths=0.2))
    c = mesh.bounds.mean(axis=0); r = (mesh.bounds[1] - mesh.bounds[0]).max() / 2
    ax.set_xlim(c[0]-r, c[0]+r); ax.set_ylim(c[1]-r, c[1]+r); ax.set_zlim(c[2]-r, c[2]+r)
    ax.view_init(elev=el, azim=az); ax.set_axis_off()
plt.tight_layout(); out = os.path.join(HERE, "..", "cad", "preview.png"); plt.savefig(out, dpi=110)
print("saved", os.path.abspath(out))
