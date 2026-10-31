# VisPy2810 review screenshots

These are native `SceneCanvas.render()` captures from separately built and installed Python3.12 wheels at base064ccec1 and PR head6e81c118. No PR source is changed by this evidence branch.

The cyan marker is rendered at a known30degree polar angle. The pointer passed to the scene's actual inverse transform is its Cartesian centre. The cross draws the returned CPU polar coordinate mapped back to Cartesian:60degrees before,30degrees after. All labels and markers in the PNGs are rendered by VisPy. The forward-only scene pixels are byte-identical; this demonstrates a CPU inverse readout correction, not a change in forward plotting.

Renderer: D3D12/NVIDIA GeForce RTX5070. `provenance.json` records source, image and script hashes and measured coordinates. This is a known-coordinate rendering example, not recorded data or a general GUI/backend result.

With each checkout built into a separate install directory and the GLFW/FreeType dependencies installed:

```sh
python render_readout.py --source /path/to/base-checkout --package /path/to/base-install --label "Before: main064ccec1" --output before.png
python render_readout.py --source /path/to/pr-checkout --package /path/to/pr-install --label "After: PR2810" --output after.png
```
