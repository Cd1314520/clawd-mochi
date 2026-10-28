# 3D case & assembly

The case is by Yousuf Amanuel (upstream) and licensed **CC BY-NC-SA 4.0**. See [`models/LICENSE-models.md`](../models/LICENSE-models.md).

## Which file to print

| File | Use it when |
| ---- | ----------- |
| [`models/clawd_mochi/clawd_mochi_v1_holes_2.2mm.stl`](../models/clawd_mochi/clawd_mochi_v1_holes_2.2mm.stl) | **Recommended.** Same case with the 4 screw holes widened from 1.6 mm to 2.2 mm. The original holes were too tight for the screws on this build |
| [`models/clawd_mochi/clawd_mochi_v1_holes_2.2mm.step`](../models/clawd_mochi/clawd_mochi_v1_holes_2.2mm.step) | You want to edit it in CAD (Fusion 360, FreeCAD…). STEP has units built in |
| [`models/clawd_mochi/clawd_mochi_v1.stl`](../models/clawd_mochi/clawd_mochi_v1.stl) / `.3mf` | The original, unmodified upstream case |

Both STL files contain the **body and the back plate side by side**. Print them together. Outer size of the layout: 63.94 × 97.75 × 38.00 mm.

### Print settings (from upstream)

| Setting      | Value                               |
| ------------ | ----------------------------------- |
| Material     | PLA or PETG                         |
| Layer height | 0.15–0.20 mm                        |
| Infill       | 15% gyroid                          |
| Supports     | Yes, for the display window overhang |
| Orientation  | Face-down, flat back on build plate |

Suggested colours: orange body, matte black back plate.

## What changed in the 2.2 mm version

Only the four screw holes:

- **Back plate:** 2 through-holes at the bottom (the 3.6 mm counterbore above them is unchanged).
- **Body:** 2 blind holes drilled down into the screw posts from the top face, about 4.4 mm deep.

The rest of the geometry is unchanged. [`enlarge_screw_holes.py`](../models/clawd_mochi/enlarge_screw_holes.py) rebuilds both files
from the upstream STL (Python + `trimesh` + `manifold3d` boolean cut, then a STEP export). It checks that the result is a closed solid, that the outer size is unchanged,
and that the holes are really 2.2 mm.

The STEP file is converted from a mesh, so in CAD it's a real solid made of flat triangle faces, not a parametric model with editable features.
You can still add holes, cut, and extrude on it.

> **Fusion 360 tip:** opening an *STL* makes Fusion assume centimetres, so the model shows up 10× too big. Choose **Millimeter** in the
> Insert Mesh dialog, or open the STEP instead.

## Assembly

What worked on this build. No soldering needed if your boards came with pins already soldered on.

1. **Test-fit first.** Put the display in the front window and close the back plate before gluing anything.
2. **Wires stay inside.** All 8 display wires live inside the case. The **9 × 3 mm slot in the back plate is only for the USB-C cable**.
   (Upstream's notes suggest threading the wires through the slot. On this build that wasn't needed.)
3. **Fix the boards.** Double-sided tape didn't hold here. **E6000** glue did, but it's permanent.
   If you might want to open the case again, use thick double-sided foam tape instead. Avoid super glue (CA) for the same reason.
4. **Screws:** 2× M2 × 6 mm. Upstream says these hold the display through its bezel holes. In the model, the two counterbored holes in the back
   plate also line up with the two screw posts in the body.
5. Run the USB-C cable through the back-plate slot and close it up.

✅ Plug it in. The boot splash should be centred in the window. If it's rotated, check how the display sits. The firmware uses `tft.setRotation(1)`.
