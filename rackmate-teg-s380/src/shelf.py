"""CadQuery shelf geometry for the RackMate T1 TRENDnet TEG-S380 cradle."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import cadquery as cq

from .parameters import ShelfParameters


SplitSide = Literal["left", "right"]


@dataclass(frozen=True)
class CalculatedDimensions:
    tray_usable_width: float
    tray_outer_width: float
    tray_outer_depth: float
    overall_depth: float
    overall_width: float
    overall_height: float
    switch_side_clearance_each_side: float
    rear_extra_depth: float
    mount_slot_center_spacing: float
    mount_slot_width: float
    mount_slot_length: float
    full_fits_256_bed: bool
    split_left_width: float
    split_right_width: float


def calculated_dimensions(params: ShelfParameters) -> CalculatedDimensions:
    """Return the dimensions users most often need after generation."""

    return CalculatedDimensions(
        tray_usable_width=params.tray_usable_width,
        tray_outer_width=params.tray_outer_width,
        tray_outer_depth=params.tray_outer_depth,
        overall_depth=params.overall_depth,
        overall_width=params.overall_width,
        overall_height=params.overall_height,
        switch_side_clearance_each_side=params.side_clearance_each_side,
        rear_extra_depth=params.rear_extra_depth,
        mount_slot_center_spacing=params.mount_slot_center_spacing,
        mount_slot_width=params.mount_slot_width,
        mount_slot_length=params.mount_slot_length,
        full_fits_256_bed=(
            params.overall_width <= params.print_bed_x
            and params.overall_depth <= params.print_bed_y
        ),
        split_left_width=_calculated_split_left_width(params),
        split_right_width=_calculated_split_right_width(params),
    )


def build_full_shelf(params: ShelfParameters) -> cq.Workplane:
    """Build the one-piece tray with both mounting ears."""

    params.validate()

    x_min = -params.tray_outer_width / 2.0
    x_max = params.tray_outer_width / 2.0
    model = _build_tray_section(params, x_min=x_min, x_max=x_max)
    model = _add_mounting_ear(params, model, side="left")
    model = _add_mounting_ear(params, model, side="right")
    model = _cut_mounting_slots(params, model)
    model = _cut_vent_openings(params, model)
    return _apply_practical_fillets(params, model).clean()


def build_split_shelf(params: ShelfParameters, side: SplitSide) -> cq.Workplane:
    """Build one half of the center-split shelf.

    The left half includes full-thickness tongues. The right half includes
    matching clearance pockets. Both halves include half-round M3 seam-clamp
    holes that become full holes when the parts are assembled.
    """

    params.validate()

    if side == "left":
        model = _build_tray_section(
            params,
            x_min=-params.tray_outer_width / 2.0,
            x_max=0.0,
        )
        model = _add_mounting_ear(params, model, side="left")
        model = _add_split_tongues(params, model)
    elif side == "right":
        model = _build_tray_section(
            params,
            x_min=0.0,
            x_max=params.tray_outer_width / 2.0,
        )
        model = _add_mounting_ear(params, model, side="right")
        model = _cut_split_pockets(params, model)
    else:
        raise ValueError(f"Unknown split side: {side}")

    model = _cut_mounting_slots(params, model)
    model = _cut_vent_openings(params, model, split_side=side)
    model = _cut_split_bolt_features(params, model)
    return _apply_practical_fillets(params, model).clean()


def _build_tray_section(params: ShelfParameters, *, x_min: float, x_max: float) -> cq.Workplane:
    """Build a rectangular tray section clipped to an x range."""

    floor = _box(
        x_min,
        x_max,
        _tray_y(params, 0.0),
        _tray_y(params, params.tray_outer_depth),
        0.0,
        params.base_thickness,
    )

    # The front lip is deliberately low so it retains the switch without
    # blocking the TEG-S380 front ports, LEDs, labels, or DC input.
    front_lip = _box(
        x_min,
        x_max,
        _tray_y(params, 0.0),
        _tray_y(params, params.front_wall_thickness),
        0.0,
        params.base_thickness + params.front_lip_height,
    )

    rear_wall = _box(
        x_min,
        x_max,
        _tray_y(params, params.tray_outer_depth - params.rear_wall_thickness),
        _tray_y(params, params.tray_outer_depth),
        0.0,
        params.base_thickness + params.rear_wall_height,
    )

    model = floor.union(front_lip).union(rear_wall)

    tray_left = -params.tray_outer_width / 2.0
    tray_right = params.tray_outer_width / 2.0
    side_z = params.base_thickness + params.side_wall_height

    if x_min <= tray_left + params.side_wall_thickness:
        model = model.union(
            _box(
                tray_left,
                tray_left + params.side_wall_thickness,
                _tray_y(params, 0.0),
                _tray_y(params, params.tray_outer_depth),
                0.0,
                side_z,
            )
        )

    if x_max >= tray_right - params.side_wall_thickness:
        model = model.union(
            _box(
                tray_right - params.side_wall_thickness,
                tray_right,
                _tray_y(params, 0.0),
                _tray_y(params, params.tray_outer_depth),
                0.0,
                side_z,
            )
        )

    return model


def _add_mounting_ear(
    params: ShelfParameters,
    model: cq.Workplane,
    *,
    side: Literal["left", "right"],
) -> cq.Workplane:
    center_x = _slot_center_x(params, side)
    ear = _box(
        center_x - (params.mounting_ear_width / 2.0),
        center_x + (params.mounting_ear_width / 2.0),
        params.mounting_ear_y_min,
        params.mounting_ear_y_max,
        0.0,
        params.mounting_ear_height,
    )
    return_arm = _box(
        *_return_arm_x_range(params, side),
        params.mounting_ear_y_min,
        params.tray_y_min,
        0.0,
        params.mounting_ear_height,
    )
    return model.union(ear).union(return_arm)


def _add_split_tongues(params: ShelfParameters, model: cq.Workplane) -> cq.Workplane:
    for y_center in _even_positions(
        params.split_tongue_end_margin_y,
        params.tray_outer_depth - params.split_tongue_end_margin_y,
        params.split_tongue_count,
    ):
        y_abs = _tray_y(params, y_center)
        tongue = _box(
            0.0,
            params.split_tongue_length_x,
            y_abs - (params.split_tongue_width_y / 2.0),
            y_abs + (params.split_tongue_width_y / 2.0),
            0.0,
            params.base_thickness,
        )
        model = model.union(tongue)
    return model


def _cut_split_pockets(params: ShelfParameters, model: cq.Workplane) -> cq.Workplane:
    clearance = params.split_tongue_clearance
    for y_center in _even_positions(
        params.split_tongue_end_margin_y,
        params.tray_outer_depth - params.split_tongue_end_margin_y,
        params.split_tongue_count,
    ):
        y_abs = _tray_y(params, y_center)
        pocket = _box(
            -clearance,
            params.split_tongue_length_x + clearance,
            y_abs - (params.split_tongue_width_y / 2.0) - clearance,
            y_abs + (params.split_tongue_width_y / 2.0) + clearance,
            -0.5,
            params.base_thickness + 0.5,
        )
        model = model.cut(pocket)
    return model


def _cut_split_bolt_features(params: ShelfParameters, model: cq.Workplane) -> cq.Workplane:
    for y_local in _even_positions(
        params.split_bolt_end_margin_y,
        params.tray_outer_depth - params.split_bolt_end_margin_y,
        params.split_bolt_count,
    ):
        y_center = _tray_y(params, y_local)
        through_hole = (
            cq.Workplane("XY")
            .center(0.0, y_center)
            .circle(params.split_bolt_clearance_diameter / 2.0)
            .extrude(params.base_thickness + 2.0)
            .translate((0.0, 0.0, -1.0))
        )
        head_recess = (
            cq.Workplane("XY")
            .center(0.0, y_center)
            .circle(params.split_bolt_head_recess_diameter / 2.0)
            .extrude(params.split_bolt_head_recess_depth + 0.2)
            .translate(
                (
                    0.0,
                    0.0,
                    params.base_thickness - params.split_bolt_head_recess_depth,
                )
            )
        )
        model = model.cut(through_hole).cut(head_recess)
    return model


def _cut_mounting_slots(params: ShelfParameters, model: cq.Workplane) -> cq.Workplane:
    for side in ("left", "right"):
        center_x = _slot_center_x(params, side)
        cutter = (
            cq.Workplane("XZ")
            .center(center_x, params.mount_slot_z_center)
            .slot2D(params.mount_slot_length, params.mount_slot_width, angle=0.0)
            .extrude(params.mounting_ear_thickness + 2.0, both=True)
            .translate((0.0, params.mounting_ear_y_center, 0.0))
        )
        model = model.cut(cutter)
    return model


def _cut_vent_openings(
    params: ShelfParameters,
    model: cq.Workplane,
    *,
    split_side: SplitSide | None = None,
) -> cq.Workplane:
    x_centers = _grid_centers(
        -params.tray_usable_width / 2.0,
        params.tray_usable_width / 2.0,
        params.vent_border_x,
        params.vent_opening_width_x,
        params.vent_columns,
    )
    y_centers = _grid_centers(
        _tray_y(params, params.front_wall_thickness),
        _tray_y(params, params.front_wall_thickness + params.tray_usable_depth),
        params.vent_border_y,
        params.vent_opening_length_y,
        params.vent_rows,
    )

    for x_center in x_centers:
        if _vent_intersects_split_seam_keepout(params, x_center, split_side):
            continue
        for y_center in y_centers:
            cutter = (
                cq.Workplane("XY")
                .center(x_center, y_center)
                .slot2D(params.vent_opening_length_y, params.vent_opening_width_x, angle=90.0)
                .extrude(params.base_thickness + 2.0)
                .translate((0.0, 0.0, -1.0))
            )
            model = model.cut(cutter)
    return model


def _vent_intersects_split_seam_keepout(
    params: ShelfParameters,
    x_center: float,
    split_side: SplitSide | None,
) -> bool:
    """Leave a continuous seam rail on split parts.

    The right half has full-depth pockets for the left-half tongues. If the
    innermost vent column overlaps those pockets, CadQuery correctly reports
    small disconnected floor islands. The keepout preserves a solid rib beside
    the mechanical joint and improves bending stiffness after assembly.
    """

    if split_side is None:
        return False

    half_vent_width = params.vent_opening_width_x / 2.0
    seam_keepout = params.split_tongue_length_x + params.vent_minimum_rib

    if split_side == "left":
        return x_center + half_vent_width > -seam_keepout
    if split_side == "right":
        return x_center - half_vent_width < seam_keepout

    raise ValueError(f"Unknown split side: {split_side}")


def _apply_practical_fillets(params: ShelfParameters, model: cq.Workplane) -> cq.Workplane:
    if params.vertical_edge_fillet <= 0:
        return model

    try:
        return model.edges("|Z").fillet(params.vertical_edge_fillet)
    except Exception:
        # Rounded vent openings and slots remain even if a global exposed-edge
        # fillet fails for a customized parameter set.
        return model


def _slot_center_x(params: ShelfParameters, side: Literal["left", "right"]) -> float:
    sign = -1.0 if side == "left" else 1.0
    return sign * params.mount_slot_center_spacing / 2.0


def _calculated_split_left_width(params: ShelfParameters) -> float:
    x_min = min(
        -params.tray_outer_width / 2.0,
        _slot_center_x(params, "left") - (params.mounting_ear_width / 2.0),
    )
    x_max = max(0.0, params.split_tongue_length_x)
    return x_max - x_min


def _calculated_split_right_width(params: ShelfParameters) -> float:
    x_min = 0.0
    x_max = max(
        params.tray_outer_width / 2.0,
        _slot_center_x(params, "right") + (params.mounting_ear_width / 2.0),
    )
    return x_max - x_min


def _return_arm_x_range(
    params: ShelfParameters,
    side: Literal["left", "right"],
) -> tuple[float, float]:
    """Return an inboard x range that connects a front ear to the rear tray.

    The space directly behind each slotted ear is reserved for the rack rail.
    These arms sit toward the tray opening, so the rail can occupy the gap while
    the printed part remains mechanically connected.
    """

    center_x = _slot_center_x(params, side)
    half_ear = params.mounting_ear_width / 2.0

    if side == "left":
        inner_edge = center_x + half_ear
        return (
            inner_edge - params.mounting_ear_thickness,
            inner_edge + params.mounting_return_arm_width_x,
        )

    inner_edge = center_x - half_ear
    return (
        inner_edge - params.mounting_return_arm_width_x,
        inner_edge + params.mounting_ear_thickness,
    )


def _tray_y(params: ShelfParameters, local_y: float) -> float:
    return params.tray_y_min + local_y


def _box(
    x_min: float,
    x_max: float,
    y_min: float,
    y_max: float,
    z_min: float,
    z_max: float,
) -> cq.Workplane:
    return (
        cq.Workplane("XY")
        .box(x_max - x_min, y_max - y_min, z_max - z_min)
        .translate(
            (
                (x_min + x_max) / 2.0,
                (y_min + y_max) / 2.0,
                (z_min + z_max) / 2.0,
            )
        )
    )


def _grid_centers(
    start: float,
    end: float,
    border: float,
    opening: float,
    count: int,
) -> list[float]:
    first = start + border + (opening / 2.0)
    last = end - border - (opening / 2.0)
    return _even_positions(first, last, count)


def _even_positions(start: float, end: float, count: int) -> list[float]:
    if count < 1:
        raise ValueError("count must be at least one")
    if count == 1:
        return [(start + end) / 2.0]
    step = (end - start) / (count - 1)
    return [start + (index * step) for index in range(count)]
