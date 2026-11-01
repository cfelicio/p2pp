#!/usr/bin/env python3
"""
Regression test for PrusaSlicer 2.8/2.9 config-comment parsing.

PrusaSlicer 2.8+ writes comma-separated filament lists in the final
`; prusaslicer_config` block, for example:
    ; filament_type = PLA,PLA,PLA,PLA
    ; filament_colour = #FF0000,#00FF00,#0000FF,#FFFF00

The old parser split only on semicolons, so these became one long string and
p2pp raised IndexError in omega.reduce_filament_types().

Run from the repository root:
    python3 tests/test_psconfig_29.py
or with pytest:
    pytest tests/test_psconfig_29.py
"""

import os
import sys
import types

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

# p2pp imports Qt-backed modules at import time. Mock the GUI for this parser
# test so it can run without PyQt5 or a display.
for module_name in ("image_rc", "p2pp.gui"):
    if module_name not in sys.modules:
        mock = types.ModuleType(module_name)
        mock.create_logitem = lambda *args, **kwargs: None
        mock.create_erroritem = lambda *args, **kwargs: None
        mock.log_warning = lambda *args, **kwargs: None
        mock.log_error = lambda *args, **kwargs: None
        mock.log_info = lambda *args, **kwargs: None
        mock.progress_string = lambda *args, **kwargs: None
        mock.show_infobox = lambda *args, **kwargs: None
        mock.dialog_insert_rows = lambda *args, **kwargs: []
        mock.app = types.SimpleNamespace(sync=lambda: None)
        sys.modules[module_name] = mock

import p2pp.variables as v
from p2pp.psconfig import parse_config_parameters


CONFIG_BLOCK = r"""
; end_gcode = ; EXTRA_CONFIG_VARIABLES\n; wipe_tower_x = {wipe_tower_x}\nM104 S0
; EXTRA_CONFIG_VARIABLES
; filament_colour = #FF0000,#00FF00,#0000FF,#FFFF00
; filament_type = PLA,PLA,PLA,PLA
; nozzle_diameter = 0.4,0.4,0.4,0.4
; first_layer_temperature = 215,215,215,215
; first_layer_bed_temperature = 60,60,60,60
; start_gcode = ;P2PP PALETTE3\n;P2PP PRINTERPROFILE=50325050494e464f50325050494e464f\n;P2PP LINEARPINGLENGTH=350\n;P2PP SPLICEOFFSET=30
"""


def test_prusaslicer_29_comma_separated_filaments():
    v.input_gcode = CONFIG_BLOCK.splitlines()
    parse_config_parameters()

    assert v.palette3 is True
    assert v.colors == 4
    assert v.filament_count == 4
    assert v.filament_type == ["PLA", "PLA", "PLA", "PLA"]
    assert v.filament_color_code[:4] == ["FF0000", "00FF00", "0000FF", "FFFF00"]


if __name__ == "__main__":
    test_prusaslicer_29_comma_separated_filaments()
    print("PrusaSlicer 2.8/2.9 config parser test passed.")
