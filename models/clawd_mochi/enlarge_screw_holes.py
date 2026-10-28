"""Rebuilds clawd_mochi_v1_holes_2.2mm.{stl,step} from the upstream clawd_mochi_v1.stl.

Widens the four M2 screw holes from 1.6 mm to 2.2 mm diameter; nothing else changes.
  - back plate: 2 through-holes (z 0-1); the 3.6 mm counterbore above them is untouched
  - body:       2 blind holes drilled down from the top face (z 38 -> ~33.55)

  pip install trimesh manifold3d cadquery-ocp
  python enlarge_screw_holes.py

Derived from Clawd Mochi by yousifamanuel, CC BY-NC-SA 4.0 - see ../LICENSE-models.md
"""
from pathlib import Path

import numpy as np
import trimesh

HERE = Path(__file__).parent
SRC = HERE / "clawd_mochi_v1.stl"
OUT = "clawd_mochi_v1_holes_2.2mm"
NEW_D = 2.2

BACK_HOLES = [(96.75, 59.93), (155.25, 59.93)]  # through-holes in the back plate
TOP_HOLES = [(96.75, 109.05), (155.25, 109.05)]  # blind holes in the body
BLIND_BOTTOM = 33.55                             # measured floor of the original blind holes


def drill(mesh, x, y, z0, z1):
    cyl = trimesh.creation.cylinder(radius=NEW_D / 2, height=z1 - z0, sections=64)
    cyl.apply_translation([x, y, (z0 + z1) / 2])
    return mesh.difference(cyl, engine="manifold")


def write_step(mesh, path):
    # ponytail: one planar face per triangle - a valid solid, not parametric CAD
    from OCP.BRep import BRep_Builder
    from OCP.BRepBuilderAPI import (BRepBuilderAPI_MakeFace, BRepBuilderAPI_MakePolygon,
                                    BRepBuilderAPI_MakeSolid, BRepBuilderAPI_Sewing)
    from OCP.gp import gp_Pnt
    from OCP.IFSelect import IFSelect_RetDone
    from OCP.Interface import Interface_Static
    from OCP.STEPControl import STEPControl_AsIs, STEPControl_Writer
    from OCP.TopAbs import TopAbs_SHELL
    from OCP.TopExp import TopExp_Explorer
    from OCP.TopoDS import TopoDS, TopoDS_Compound

    sew = BRepBuilderAPI_Sewing(1e-4)
    for tri in mesh.triangles:
        poly = BRepBuilderAPI_MakePolygon(*(gp_Pnt(*map(float, p)) for p in tri), True)
        sew.Add(BRepBuilderAPI_MakeFace(poly.Wire()).Face())
    sew.Perform()

    comp, builder = TopoDS_Compound(), BRep_Builder()
    builder.MakeCompound(comp)
    exp = TopExp_Explorer(sew.SewedShape(), TopAbs_SHELL)
    while exp.More():  # body and back plate are separate shells -> separate solids
        builder.Add(comp, BRepBuilderAPI_MakeSolid(TopoDS.Shell_s(exp.Current())).Solid())
        exp.Next()

    Interface_Static.SetCVal_s("write.step.unit", "MM")
    w = STEPControl_Writer()
    w.Transfer(comp, STEPControl_AsIs)
    assert w.Write(str(path)) == IFSelect_RetDone, "STEP write failed"


def main():
    src = trimesh.load(SRC)
    m = src
    for x, y in BACK_HOLES:
        m = drill(m, x, y, -0.5, 1.5)        # stays inside the 3.6 mm counterbore
    for x, y in TOP_HOLES:
        m = drill(m, x, y, BLIND_BOTTOM, 38.5)

    # self-check: solid, same outside, holes are now 2.2 mm
    assert m.is_watertight and m.is_volume, "result is not a closed solid"
    assert np.allclose(m.bounds, src.bounds, atol=1e-3), "outer dimensions changed"
    a = np.linspace(0, 2 * np.pi, 12, endpoint=False)
    ring = lambda x, y, z, r: np.c_[x + r * np.cos(a), y + r * np.sin(a), np.full(12, z)]
    for x, y, z in [(*BACK_HOLES[0], 0.5), (*BACK_HOLES[1], 0.5), (*TOP_HOLES[0], 36), (*TOP_HOLES[1], 36)]:
        assert not m.contains(ring(x, y, z, 1.05)).any(), f"hole at {x},{y} not widened"
        assert m.contains(ring(x, y, z, 1.20)).all(), f"wall at {x},{y} missing"

    m.export(HERE / f"{OUT}.stl")
    write_step(m, HERE / f"{OUT}.step")
    print("extents mm:", np.round(m.extents, 2), "| volume removed mm^3:",
          round(src.volume - m.volume, 2))


if __name__ == "__main__":
    main()
