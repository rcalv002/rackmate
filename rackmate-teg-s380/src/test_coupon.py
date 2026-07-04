"""Minimal mounting coupon for checking RackMate T1 screw spacing."""

from __future__ import annotations

import cadquery as cq

from .parameters import ShelfParameters
from .shelf import _apply_practical_fillets, _box, _cut_mounting_slots


def build_mount_test_coupon(params: ShelfParameters) -> cq.Workplane:
    """Build a lightweight slot-spacing coupon with both mounting ears."""

    params.validate()

    left_center = -params.mount_slot_center_spacing / 2.0
    right_center = params.mount_slot_center_spacing / 2.0
    x_min = left_center - (params.mounting_ear_width / 2.0)
    x_max = right_center + (params.mounting_ear_width / 2.0)

    left_ear = _box(
        x_min,
        x_min + params.mounting_ear_width,
        params.mounting_ear_y_min,
        params.mounting_ear_y_max,
        0.0,
        params.mounting_ear_height,
    )
    right_ear = _box(
        x_max - params.mounting_ear_width,
        x_max,
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
