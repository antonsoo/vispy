"""Render an actual VisPy polar scene and CPU inverse readout overlay."""

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

import numpy as np

p = argparse.ArgumentParser()
p.add_argument("--source", type=Path, required=True)
p.add_argument("--package", type=Path, required=True)
p.add_argument("--label", required=True)
p.add_argument("--output", type=Path, required=True)
a = p.parse_args()
sys.path.insert(0, str(a.package.resolve()))
import vispy
from vispy import app, gloo, scene
from vispy.io import write_png
from vispy.visuals.transforms import PolarTransform, STTransform

assert Path(vispy.__file__).resolve().parent.parent == a.package.resolve()
relative = Path("vispy/visuals/transforms/nonlinear.py")
assert (a.package / relative).read_bytes() == (a.source / relative).read_bytes()
app.use_app("glfw")
canvas = scene.SceneCanvas(size=(620, 600), show=False, bgcolor="#16202c", px_scale=1)
canvas.set_current()
renderer = gloo.gl.glGetParameter(gloo.gl.GL_RENDERER)
outer = STTransform(scale=(170, -170), translate=(310, 265))
polar = PolarTransform()
angles = np.linspace(0, 2 * np.pi, 361)
for radius in [0.5, 1.0]:
    grid = scene.visuals.Line(
        pos=np.column_stack([radius * np.cos(angles), radius * np.sin(angles)]),
        color="#586271",
        width=1,
        parent=canvas.scene,
    )
    grid.transform = outer
for line in [[[-1.15, 0], [1.15, 0]], [[0, -1.15], [0, 1.15]]]:
    grid = scene.visuals.Line(
        pos=np.asarray(line, np.float32), color="#586271", parent=canvas.scene
    )
    grid.transform = outer

theta = np.deg2rad(30.0)
coordinates = np.array([[theta, 1.0]], np.float32)
marker = scene.visuals.Markers(
    pos=coordinates, face_color="#4de4f5", edge_width=0, size=16, parent=canvas.scene
)
marker.transform = outer * polar
common = canvas.render()
true_xy = np.array([[np.cos(theta), np.sin(theta), 0.0, 1.0]])
pointer = outer.map(true_xy)
recovered = marker.node_transform(canvas.scene).imap(pointer)
returned = np.column_stack(
    [
        recovered[:, 1] * np.cos(recovered[:, 0]),
        recovered[:, 1] * np.sin(recovered[:, 0]),
    ]
)
correct = bool(np.allclose(recovered[0, :2], [theta, 1.0], atol=1e-6))
cross = scene.visuals.Markers(
    pos=returned.astype(np.float32),
    face_color="#7ef09c" if correct else "#ff7070",
    edge_color="#7ef09c" if correct else "#ff7070",
    edge_width=2,
    size=25,
    symbol="+",
    parent=canvas.scene,
)
cross.transform = outer
if not correct:
    line = scene.visuals.Line(
        pos=np.vstack([true_xy[0, :2], returned[0]]).astype(np.float32),
        color="#ff7070",
        width=2,
        parent=canvas.scene,
    )
    line.transform = outer


def text(message, x, y, size=14, color="white", anchor_x="center"):
    scene.visuals.Text(
        message,
        pos=(x, y),
        font_size=size,
        color=color,
        anchor_x=anchor_x,
        anchor_y="center",
        parent=canvas.scene,
    )


text(a.label, 310, 25, 19)
text("Actual VisPy rendering + CPU coordinate readout", 310, 57, 12, "#c0ccd8")
text("+x", 520, 265, 13, "#c0ccd8")
text("+y", 310, 57 + 18, 13, "#c0ccd8")
text("cyan dot: original point at 30 deg", 310, 464, 14, "#4de4f5")
text("cross: CPU readout mapped back to Cartesian", 310, 491, 12, "#c0ccd8")
text(f"Expected: theta = 30.0 deg, radius = 1.000", 310, 528, 14)
text(
    f"CPU imap: theta = {np.rad2deg(recovered[0,0]):.1f} deg, radius = {recovered[0,1]:.3f}",
    310,
    559,
    16,
    "#7ef09c" if correct else "#ff7070",
)
canvas.update()
image = canvas.render()
write_png(str(a.output), image)
write_png(str(a.output.with_name(a.output.stem + "-forward-only.png")), common)
canvas.close()
report = dict(
    source=str(a.source.resolve()),
    package=str(a.package.resolve()),
    head=subprocess.check_output(
        ["git", "-C", str(a.source), "rev-parse", "HEAD"], text=True
    ).strip(),
    renderer=renderer,
    vispy=vispy.__version__,
    numpy=np.__version__,
    expected_theta_degrees=30.0,
    returned_theta_degrees=float(np.rad2deg(recovered[0, 0])),
    returned_radius=float(recovered[0, 1]),
    correct=correct,
    pointer=pointer.tolist(),
    nonlinear_sha256=hashlib.sha256((a.source / relative).read_bytes()).hexdigest(),
    screenshot_sha256=hashlib.sha256(a.output.read_bytes()).hexdigest(),
    forward_rgba_sha256=hashlib.sha256(common.tobytes()).hexdigest(),
    back_projected_shift_pixels=float(
        170 * np.linalg.norm(returned[0] - true_xy[0, :2])
    ),
    expected_xy=true_xy.tolist(),
    returned_xy=returned.tolist(),
)
a.output.with_suffix(".json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps(report, indent=2))
