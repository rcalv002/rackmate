"""Configurable dimensions for the RackMate T1 / TRENDnet TEG-S380 shelf.

All dimensions are millimeters.  The defaults are intentionally conservative:
they are based on the supplied measurements and leave modest clearance for PETG
printing variation.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ShelfParameters:
    """All meaningful dimensions used by the shelf and test coupon."""

    # Device envelope.
    switch_width: float = 241.3
    switch_depth: float = 104.8
    switch_height: float = 25.4

    # Rack measurements. These are RackMate T1-specific defaults, not 19-inch
    # rack assumptions.
    rack_clear_inside_width: float = 273.0
    mount_slot_center_spacing: float = 234.95
    rack_rail_depth: float = 6.35
    rack_rail_clearance: float = 1.0

    # Target print bed used for split/full fit reporting.
    print_bed_x: float = 256.0
    print_bed_y: float = 256.0

    # Switch fit inside the retaining walls.
    side_clearance_each_side: float = 1.8
    front_clearance: float = 1.0
    rear_extra_depth: float = 8.0

    # Structural dimensions.
    minimum_structural_wall: float = 3.0
    base_thickness: float = 4.0
    side_wall_thickness: float = 3.2
    front_wall_thickness: float = 3.2
    rear_wall_thickness: float = 3.2

    # Retaining wall heights above the tray floor surface.
    front_lip_height: float = 5.0
    side_wall_height: float = 5.0
    rear_wall_height: float = 9.0

    # Front mounting ears and horizontal slots.
    mounting_ear_height: float = 28.0
    mounting_ear_thickness: float = 3.2
    mounting_return_arm_width_x: float = 8.0
    mount_slot_width: float = 5.5
    mount_slot_length: float = 10.0
    mount_slot_edge_margin_x: float = 5.5
    mount_slot_z_center: float = 17.0

    # Vent pattern in the shelf floor.
    vent_columns: int = 6
    vent_rows: int = 2
    vent_opening_width_x: float = 22.0
    vent_opening_length_y: float = 34.0
    vent_border_x: float = 14.0
    vent_border_y: float = 16.0
    vent_minimum_rib: float = 6.0

    # Practical edge softening. Openings are already rounded; this adds small
    # fillets to exposed vertical edges when the CAD kernel can apply them.
    vertical_edge_fillet: float = 0.8

    # Split-shelf center joint. The left half carries full-thickness tongues
    # that nest into matching right-half pockets. M3 bolts through the seam
    # clamp both sides; use washers/nuts below the shelf.
    split_tongue_length_x: float = 18.0
    split_tongue_width_y: float = 20.0
    split_tongue_count: int = 3
    split_tongue_end_margin_y: float = 22.0
    split_tongue_clearance: float = 0.35
    split_bolt_count: int = 2
    split_bolt_end_margin_y: float = 40.0
    split_bolt_clearance_diameter: float = 3.4
    split_bolt_head_recess_diameter: float = 7.0
    split_bolt_head_recess_depth: float = 1.4

    # Test coupon.
    coupon_connector_bar_height: float = 5.0

    # Export tessellation.
    stl_linear_tolerance: float = 0.05
    stl_angular_tolerance: float = 0.08

    @property
    def tray_usable_width(self) -> float:
        return self.switch_width + (2.0 * self.side_clearance_each_side)

    @property
    def tray_outer_width(self) -> float:
        return self.tray_usable_width + (2.0 * self.side_wall_thickness)

    @property
    def tray_usable_depth(self) -> float:
        return self.front_clearance + self.switch_depth + self.rear_extra_depth

    @property
    def tray_outer_depth(self) -> float:
        return self.front_wall_thickness + self.tray_usable_depth + self.rear_wall_thickness

    @property
    def overall_depth(self) -> float:
        return self.mounting_ear_thickness + self.tray_y_min + self.tray_outer_depth

    @property
    def mounting_ear_width(self) -> float:
        return self.mount_slot_length + (2.0 * self.mount_slot_edge_margin_x)

    @property
    def overall_width(self) -> float:
        return max(self.tray_outer_width, self.mount_slot_center_spacing + self.mounting_ear_width)

    @property
    def overall_height(self) -> float:
        return max(
            self.base_thickness + self.rear_wall_height,
            self.mounting_ear_height,
        )

    @property
    def mounting_ear_y_min(self) -> float:
        return -self.mounting_ear_thickness

    @property
    def mounting_ear_y_max(self) -> float:
        return 0.0

    @property
    def mounting_ear_y_center(self) -> float:
        return (self.mounting_ear_y_min + self.mounting_ear_y_max) / 2.0

    @property
    def tray_y_min(self) -> float:
        return self.rack_rail_depth + self.rack_rail_clearance

    @property
    def tray_y_max(self) -> float:
        return self.tray_y_min + self.tray_outer_depth

    @property
    def switch_left_x(self) -> float:
        return -self.switch_width / 2.0

    @property
    def switch_right_x(self) -> float:
        return self.switch_width / 2.0

    @property
    def switch_front_y(self) -> float:
        return self.tray_y_min + self.front_wall_thickness + self.front_clearance

    @property
    def switch_rear_y(self) -> float:
        return self.switch_front_y + self.switch_depth

    def validate(self) -> None:
        """Fail early for dimensions that would create unusable or weak parts."""

        errors: list[str] = []

        required_tray_width = self.switch_width + (2.0 * self.side_clearance_each_side)
        if self.tray_usable_width < required_tray_width:
            errors.append(
                "usable tray width must be at least switch_width plus two side clearances "
                f"({required_tray_width:.2f} mm required, {self.tray_usable_width:.2f} mm configured)"
            )

        if self.overall_width >= self.rack_clear_inside_width:
            errors.append(
                "overall shelf width must remain below the measured rack clearance "
                f"({self.overall_width:.2f} mm >= {self.rack_clear_inside_width:.2f} mm)"
            )

        for name, value in (
            ("base_thickness", self.base_thickness),
            ("side_wall_thickness", self.side_wall_thickness),
            ("front_wall_thickness", self.front_wall_thickness),
            ("rear_wall_thickness", self.rear_wall_thickness),
            ("mounting_ear_thickness", self.mounting_ear_thickness),
            ("mounting_return_arm_width_x", self.mounting_return_arm_width_x),
        ):
            if value < self.minimum_structural_wall:
                errors.append(
                    f"{name} must be at least the minimum structural wall "
                    f"({value:.2f} mm < {self.minimum_structural_wall:.2f} mm)"
                )

        if not 4.0 <= self.front_lip_height <= 6.0:
            errors.append("front_lip_height should be in the requested 4-6 mm range")
        if not 4.0 <= self.side_wall_height <= 6.0:
            errors.append("side_wall_height should be in the requested 4-6 mm range")
        if not 8.0 <= self.rear_wall_height <= 10.0:
            errors.append("rear_wall_height should be in the requested 8-10 mm range")

        if self.mounting_ear_width < self.mount_slot_length + (2.0 * self.minimum_structural_wall):
            errors.append("mounting ears do not leave the minimum material beside each slot")

        if self.rack_rail_depth <= 0.0:
            errors.append("rack_rail_depth must be positive")
        if self.rack_rail_clearance < 0.0:
            errors.append("rack_rail_clearance cannot be negative")

        slot_bottom = self.mount_slot_z_center - (self.mount_slot_width / 2.0)
        slot_top = self.mount_slot_z_center + (self.mount_slot_width / 2.0)
        if slot_bottom < self.minimum_structural_wall:
            errors.append("mount slots are too close to the bottom of the mounting ears")
        if slot_top > self.mounting_ear_height - self.minimum_structural_wall:
            errors.append("mount slots are too close to the top of the mounting ears")

        vent_gap_x = self._grid_gap(
            available=self.tray_usable_width,
            count=self.vent_columns,
            opening=self.vent_opening_width_x,
            border=self.vent_border_x,
        )
        vent_gap_y = self._grid_gap(
            available=self.tray_usable_depth,
            count=self.vent_rows,
            opening=self.vent_opening_length_y,
            border=self.vent_border_y,
        )
        if vent_gap_x < self.vent_minimum_rib:
            errors.append(
                f"vent x ribs are too narrow ({vent_gap_x:.2f} mm < {self.vent_minimum_rib:.2f} mm)"
            )
        if vent_gap_y < self.vent_minimum_rib:
            errors.append(
                f"vent y ribs are too narrow ({vent_gap_y:.2f} mm < {self.vent_minimum_rib:.2f} mm)"
            )

        if self.split_tongue_width_y <= 0 or self.split_tongue_length_x <= 0:
            errors.append("split tongue dimensions must be positive")
        if self.split_tongue_count < 1:
            errors.append("split_tongue_count must be at least one")
        if self.split_bolt_count < 1:
            errors.append("split_bolt_count must be at least one")
        if self.split_bolt_head_recess_depth >= self.base_thickness:
            errors.append("split bolt head recess depth must be less than base thickness")

        max_left_split_width = (self.tray_outer_width / 2.0) + self.split_tongue_length_x
        if max_left_split_width > self.print_bed_x:
            errors.append(
                "left split half exceeds the configured print bed width "
                f"({max_left_split_width:.2f} mm > {self.print_bed_x:.2f} mm)"
            )
        if self.overall_depth > self.print_bed_y:
            errors.append(
                "split shelf depth exceeds the configured print bed depth "
                f"({self.overall_depth:.2f} mm > {self.print_bed_y:.2f} mm)"
            )

        if errors:
            joined = "\n - ".join(errors)
            raise ValueError(f"Invalid shelf parameters:\n - {joined}")

    @staticmethod
    def _grid_gap(available: float, count: int, opening: float, border: float) -> float:
        if count <= 1:
            return available - (2.0 * border) - opening
        return (available - (2.0 * border) - (count * opening)) / (count - 1)
