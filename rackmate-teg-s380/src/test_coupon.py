"""Minimal mounting coupon for checking RackMate T1 screw spacing."""

from __future__ import annotations

import cadquery as cq

from .parameters import ShelfParameters
from .shelf import (
    _add_front_return_web,
    _add_mounting_ear,
    _apply_practical_fillets,
    _box,
    _cut_mounting_slots,
    _mounting_ear_x_range,
    _tray_y,
)


def build_mount_test_coupon(params: ShelfParameters) -> cq.Workplane:
    """Build a lightweight slot-spacing coupon with both mounting ears."""

    params.validate()

    left_ear_x_min, left_ear_x_max = _mounting_ear_x_range(params, "left")
    right_ear_x_min, right_ear_x_max = _mounting_ear_x_range(params, "right")
    x_min = left_ear_x_min
    x_max = right_ear_x_max

    left_ear = _box(
        left_ear_x_min,
        left_ear_x_max,
        params.mounting_ear_y_min,
        params.mounting_ear_y_max,
        0.0,
        params.mounting_ear_height,
    )
    right_ear = _box(
        right_ear_x_min,
        right_ear_x_max,
        params.mounting_ear_y_min,
        params.mounting_ear_y_max,
        0.0,
        params.mounting_ear_height,
    )

    # A shallow bar connects the ears so the coupon verifies the complete
    # horizontal center spacing while using very little filament.
    connector = _box(
        x_min,
        x_max,
        params.mounting_ear_y_min,
        params.mounting_ear_y_max,
        0.0,
        params.coupon_connector_bar_height,
    )

    model = left_ear.union(right_ear).union(connector)
    model = _cut_mounting_slots(params, model)
    return _apply_practical_fillets(params, model).clean()


def build_front_fit_coupon(params: ShelfParameters) -> cq.Workplane:
    """Build a shallow front section for testing rack-rail pocket fit.

    This coupon keeps the full-width front mounting geometry but trims the tray
    to a short front stub, so it verifies insertion, rail-pocket depth, screw
    slot alignment, and the strengthened return web without printing the full
    shelf body.
    """

    params.validate()

    x_min = -params.tray_outer_width / 2.0
    x_max = params.tray_outer_width / 2.0
    y_front = _tray_y(params, 0.0)
    y_back = _tray_y(params, params.front_fit_coupon_tray_depth)

    floor = _box(
        x_min,
        x_max,
        y_front,
        y_back,
        0.0,
        params.base_thickness,
    )
    front_lip = _box(
        x_min,
        x_max,
        y_front,
        _tray_y(params, params.front_wall_thickness),
        0.0,
        params.base_thickness + params.front_lip_height,
    )

    tray_left = -params.tray_outer_width / 2.0
    tray_right = params.tray_outer_width / 2.0
    side_z = params.base_thickness + params.side_wall_height
    left_wall = _box(
        tray_left,
        tray_left + params.side_wall_thickness,
        y_front,
        y_back,
        0.0,
        side_z,
    )
    right_wall = _box(
        tray_right - params.side_wall_thickness,
        tray_right,
        y_front,
        y_back,
        0.0,
        side_z,
    )

    model = floor.union(front_lip).union(left_wall).union(right_wall)
    model = _add_front_return_web(params, model, x_min=x_min, x_max=x_max)
    model = _add_mounting_ear(params, model, side="left")
    model = _add_mounting_ear(params, model, side="right")
    model = _cut_mounting_slots(params, model)
    return _apply_practical_fillets(params, model).clean()
