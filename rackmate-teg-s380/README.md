# RackMate T1 TRENDnet TEG-S380 Shelf

Parametric CadQuery model for a shallow 1U front-mounted shelf/cradle that holds a TRENDnet TEG-S380 switch in a GeeekPi/DeskPi RackMate T1 mini rack.

The model uses millimeters internally and does not assume standard 19-inch or conventional 10-inch rack geometry. The default rack measurements are the supplied RackMate T1 measurements.

## Generated Parts

Running `python generate.py` creates:

- `output/rackmate_t1_teg_s380_shelf_full.step`
- `output/rackmate_t1_teg_s380_shelf_full.stl`
- `output/rackmate_t1_teg_s380_shelf_left.step`
- `output/rackmate_t1_teg_s380_shelf_left.stl`
- `output/rackmate_t1_teg_s380_shelf_right.step`
- `output/rackmate_t1_teg_s380_shelf_right.stl`
- `output/rackmate_t1_mount_test_coupon.step`
- `output/rackmate_t1_mount_test_coupon.stl`

The one-piece shelf is for larger printers or beds that can accept the full width. The split shelf is intended for 256 x 256 mm beds.

## Required Software

- Python 3.10, 3.11, or 3.12
- CadQuery 2.5.2, pinned in `requirements.txt`

CadQuery may not install cleanly on every Python 3.13 environment because it depends on OpenCascade/OCP wheels. Use Python 3.12 if installation fails.

## Installation

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Generate CAD Files

```powershell
python generate.py
```

The generator validates parameters, checks that each model is one connected valid solid, exports STEP and STL, verifies that every requested output file exists, and prints the final calculated dimensions.

## Default Dimensions

All values are in `src/parameters.py`.

| Parameter | Default | Purpose |
| --- | ---: | --- |
| `switch_width` | 241.3 | TEG-S380 body width |
| `switch_depth` | 104.8 | TEG-S380 body depth |
| `switch_height` | 25.4 | TEG-S380 body height reference |
| `rack_clear_inside_width` | 273.0 | Measured clear width between RackMate T1 front rails |
| `mount_slot_center_spacing` | 234.95 | Left/right rack mounting slot center spacing |
| `rack_rail_depth` | 6.35 | Front-to-back depth reserved behind each printed ear for the 1/4 in rack rail |
| `rack_rail_clearance` | 1.0 | Extra clearance behind the rail before the tray starts |
| `print_bed_x` | 256.0 | Print-bed width used for fit checks |
| `print_bed_y` | 256.0 | Print-bed depth used for fit checks |
| `side_clearance_each_side` | 1.8 | Clearance between switch and each side wall |
| `front_clearance` | 1.0 | Gap behind the front retaining lip |
| `rear_extra_depth` | 8.0 | Extra tray depth behind the switch |
| `minimum_structural_wall` | 3.0 | Minimum allowed structural wall |
| `base_thickness` | 4.0 | Tray floor thickness |
| `side_wall_thickness` | 3.2 | Side wall thickness |
| `front_wall_thickness` | 3.2 | Front retaining lip thickness |
| `rear_wall_thickness` | 3.2 | Rear wall thickness |
| `front_lip_height` | 5.0 | Front retaining lip height above tray floor |
| `side_wall_height` | 5.0 | Side retaining wall height above tray floor |
| `rear_wall_height` | 9.0 | Rear retaining wall height above tray floor |
| `mounting_ear_height` | 28.0 | Front mounting ear height |
| `mounting_ear_thickness` | 3.2 | Thickness of the forward mounting ears |
| `mounting_return_arm_width_x` | 8.0 | Width of the inboard arms that connect front ears back to the tray |
| `mount_slot_width` | 5.5 | Vertical height of each horizontal mounting slot |
| `mount_slot_length` | 10.0 | Horizontal length of each mounting slot |
| `mount_slot_edge_margin_x` | 5.5 | Material outside each slot end |
| `mount_slot_z_center` | 17.0 | Slot center height from the print bed |
| `vent_columns` | 6 | Number of vent columns in the floor |
| `vent_rows` | 2 | Number of vent rows in the floor |
| `vent_opening_width_x` | 22.0 | Vent slot width across the shelf |
| `vent_opening_length_y` | 34.0 | Vent slot length front-to-back |
| `vent_border_x` | 14.0 | Solid margin before the first/last vent column |
| `vent_border_y` | 16.0 | Solid margin before the first/last vent row |
| `vent_minimum_rib` | 6.0 | Minimum rib width allowed between vents |
| `vertical_edge_fillet` | 0.8 | Practical exposed vertical-edge fillet radius |
| `split_tongue_length_x` | 18.0 | Center-joint tongue engagement length |
| `split_tongue_width_y` | 20.0 | Center-joint tongue width |
| `split_tongue_count` | 3 | Number of split-joint tongues |
| `split_tongue_end_margin_y` | 22.0 | End margin before first/last split tongue |
| `split_tongue_clearance` | 0.35 | Clearance around right-half tongue pockets |
| `split_bolt_count` | 2 | Number of M3 seam clamp holes |
| `split_bolt_end_margin_y` | 40.0 | End margin before first/last seam bolt |
| `split_bolt_clearance_diameter` | 3.4 | M3 clearance hole diameter |
| `split_bolt_head_recess_diameter` | 7.0 | Top counterbore/recess diameter at seam |
| `split_bolt_head_recess_depth` | 1.4 | Top counterbore/recess depth |
| `coupon_connector_bar_height` | 5.0 | Low bar connecting coupon ears |
| `stl_linear_tolerance` | 0.05 | STL tessellation tolerance |
| `stl_angular_tolerance` | 0.08 | STL angular tessellation tolerance |

## Test Coupon

Print `rackmate_t1_mount_test_coupon.stl` first. It contains the same left and right mounting ears and horizontal slots as the shelf, connected by a narrow low bar. Use it to verify:

- the 234.95 mm default mounting center spacing,
- the 5.5 x 10 mm horizontal slot size,
- screw fit in the RackMate T1 rails,
- whether your measured rack spacing needs adjustment.

If the coupon does not fit, measure the horizontal center-to-center distance between the rack holes and update `mount_slot_center_spacing` in `src/parameters.py`, then rerun `python generate.py`.

## Printing

Recommended PETG settings:

- 0.20 mm layer height
- 4 walls/perimeters
- 25-35% infill
- 5 top and bottom layers
- no supports
- brim recommended for the thin upright test coupon

Print the shelf parts flat on the tray bottom. The retaining walls, mounting ears, rounded vent openings, and slot openings are designed for support-free printing. The mounting slots bridge a short span; tune cooling and bridge speed for PETG.

## Split Shelf Assembly

Open `docs/split_assembly_top_view.svg` for a top-view assembly diagram.
Open `docs/mounting_front_view.svg` for a front-view diagram showing how the ears screw to the RackMate rails.
Open `docs/mounting_side_stack.svg` for the side-view front-to-back screw stack.
Open `docs/mounting_top_insertion.svg` for the top-view rail pocket and insertion concept.

The tray body slides into the rack opening, behind the front rail plane. The printed mounting ears sit on the front face of the rails like normal rack ears. The model leaves an open rail pocket between the front ears and the tray body, sized by `rack_rail_depth` plus `rack_rail_clearance`. Narrow inboard return arms connect the ears back to the tray while leaving the rail area open.

The screw order from the front is:

1. screw head,
2. printed mounting-ear slot,
3. RackMate rail hole/thread.

The split shelf uses three center tongues on the left half, matching clearance pockets on the right half, and two M3 seam-clamp holes.
The split exports intentionally omit the innermost vent column beside the seam, leaving a continuous reinforced rail around the tongue pockets.

1. Print `rackmate_t1_teg_s380_shelf_left.stl` and `rackmate_t1_teg_s380_shelf_right.stl`.
2. Deburr the tongue and pocket edges lightly if needed.
3. Slide the left tongues into the right pockets until the front and rear lips align.
4. Install two M3 screws through the seam holes from the top.
5. Use washers and nuts underneath the shelf, or equivalent low-profile M3 hardware.
6. Keep screw heads below or flush with the counterbore recesses so the switch bottom remains supported.

The split joint is mechanical and does not rely on glue.

## Adjusting Fit

Change dimensions in `src/parameters.py`, then run:

```powershell
python generate.py
```

The generator fails with a useful error if the switch clearance is impossible, the model is too wide for the measured rack clearance, structural walls are below 3 mm, vent ribs are too thin, split parts exceed the configured bed, or generated geometry is invalid/disconnected.
