"""Generate STEP and STL files for the RackMate T1 TEG-S380 shelf."""

from __future__ import annotations

from dataclasses import asdict
from pathlib import Path

try:
    import cadquery as cq
except ModuleNotFoundError as exc:
    raise SystemExit(
        "CadQuery is required. Install dependencies first with:\n"
        "  python -m pip install -r requirements.txt"
    ) from exc

from src.parameters import ShelfParameters
from src.shelf import build_full_shelf, build_split_shelf, calculated_dimensions
from src.test_coupon import build_mount_test_coupon


ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "output"


def main() -> None:
    params = ShelfParameters()
    params.validate()
    OUTPUT.mkdir(parents=True, exist_ok=True)

    models: dict[str, cq.Workplane] = {
        "rackmate_t1_teg_s380_shelf_full": build_full_shelf(params),
        "rackmate_t1_teg_s380_shelf_left": build_split_shelf(params, "left"),
        "rackmate_t1_teg_s380_shelf_right": build_split_shelf(params, "right"),
        "rackmate_t1_mount_test_coupon": build_mount_test_coupon(params),
    }

    print("Geometry validation:")
    for name, model in models.items():
        stats = validate_model(name, model)
        print(
            f"  {name}: valid={stats['valid']}, solids={stats['solids']}, "
            f"bbox={stats['bbox_x']:.2f} x {stats['bbox_y']:.2f} x {stats['bbox_z']:.2f} mm"
        )
        export_model(name, model, params)

    expected = [
        OUTPUT / "rackmate_t1_teg_s380_shelf_full.step",
        OUTPUT / "rackmate_t1_teg_s380_shelf_full.stl",
        OUTPUT / "rackmate_t1_teg_s380_shelf_left.step",
        OUTPUT / "rackmate_t1_teg_s380_shelf_left.stl",
        OUTPUT / "rackmate_t1_teg_s380_shelf_right.step",
        OUTPUT / "rackmate_t1_teg_s380_shelf_right.stl",
        OUTPUT / "rackmate_t1_mount_test_coupon.step",
        OUTPUT / "rackmate_t1_mount_test_coupon.stl",
    ]
    missing = [path for path in expected if not path.exists() or path.stat().st_size == 0]
    if missing:
        missing_text = "\n".join(f" - {path}" for path in missing)
        raise RuntimeError(f"Missing generated output files:\n{missing_text}")

    dims = calculated_dimensions(params)
    print("\nCalculated dimensions:")
    for key, value in asdict(dims).items():
        if isinstance(value, bool):
            print(f"  {key}: {value}")
        else:
            print(f"  {key}: {value:.2f} mm")

    print("\nGenerated files:")
    for path in expected:
        print(f"  {path.relative_to(ROOT)}")


def validate_model(name: str, model: cq.Workplane) -> dict[str, float | int | bool]:
    solids = model.solids().vals()
    valid = bool(model.val().isValid())
    if len(solids) != 1 or not valid:
        raise RuntimeError(f"{name} must be one valid solid; got solids={len(solids)}, valid={valid}")

    bbox = model.val().BoundingBox()
    return {
        "valid": valid,
        "solids": len(solids),
        "bbox_x": bbox.xlen,
        "bbox_y": bbox.ylen,
        "bbox_z": bbox.zlen,
    }


def export_model(name: str, model: cq.Workplane, params: ShelfParameters) -> None:
    step_path = OUTPUT / f"{name}.step"
    stl_path = OUTPUT / f"{name}.stl"

    for path in (step_path, stl_path):
        if path.exists():
            path.unlink()

    shape = model.val()
    shape.exportStep(str(step_path))
    shape.exportStl(
        str(stl_path),
        tolerance=params.stl_linear_tolerance,
        angularTolerance=params.stl_angular_tolerance,
    )

    for path in (step_path, stl_path):
        if not path.exists() or path.stat().st_size == 0:
            raise RuntimeError(f"Export failed for {name}: {path} was not created")


if __name__ == "__main__":
    main()
