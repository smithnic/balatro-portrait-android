#!/usr/bin/env python3
"""
Balatro Portrait Mode Patcher

Injects portrait-mode Lua modifications into Balatro.exe.
The patched exe can then be passed to balatro-mobile-maker to build an APK.

Usage:
    python patch.py                          # uses default Steam path (Windows or WSL)
    python patch.py "C:/path/to/Balatro.exe"
    python patch.py "C:/path/to/Balatro.exe" -o patched.exe
"""

import argparse
import io
import struct
import sys
import zipfile
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent

# Files in this repo that replace their counterparts inside Balatro.exe
PATCHED_FILES = [
    "blind.lua",
    "card.lua",
    "conf.lua",
    "game.lua",
    "globals.lua",
    "main.lua",
    "functions/common_events.lua",
    "functions/UI_definitions.lua",
    "functions/button_callbacks.lua",
]

# Default Steam install locations, checked in order (native Windows, then WSL)
DEFAULT_BALATRO_PATHS = [
    r"C:\Program Files (x86)\Steam\steamapps\common\Balatro\Balatro.exe",
    "/mnt/c/Program Files (x86)/Steam/steamapps/common/Balatro/Balatro.exe",
]


def default_balatro_path() -> str:
    """Return the first default Steam path that exists, or the first candidate if none do."""
    for p in DEFAULT_BALATRO_PATHS:
        if Path(p).exists():
            return p
    return DEFAULT_BALATRO_PATHS[0]


def find_zip_start(data: bytes) -> int:
    """Return the byte offset where the Love2D .love zip begins inside the exe."""
    # Love2D appends a .love (zip) file to the runtime exe.
    # Locate it via the End-of-Central-Directory record, which is always near
    # the tail of a zip and contains the central-directory offset from zip start.
    eocd_sig = b"PK\x05\x06"
    pos = data.rfind(eocd_sig)
    if pos == -1:
        raise ValueError(
            "No zip signature found — is this a valid Love2D executable?"
        )

    # EOCD layout (all little-endian):
    #   +0  4 bytes  signature
    #   +4  2 bytes  disk number
    #   +6  2 bytes  start disk
    #   +8  2 bytes  entries on disk
    #  +10  2 bytes  total entries
    #  +12  4 bytes  size of central directory
    #  +16  4 bytes  offset of central directory from start of zip
    #  +20  2 bytes  comment length
    cd_size = struct.unpack_from("<I", data, pos + 12)[0]
    cd_offset_in_zip = struct.unpack_from("<I", data, pos + 16)[0]

    # Central directory ends just before the EOCD record.
    cd_pos_in_file = pos - cd_size
    zip_start = cd_pos_in_file - cd_offset_in_zip

    if zip_start < 0:
        raise ValueError("Computed zip start is negative — invalid exe structure.")

    return zip_start


def patch(input_path: Path, output_path: Path) -> None:
    print(f"Reading {input_path} ...")
    data = input_path.read_bytes()

    zip_start = find_zip_start(data)
    exe_prefix = data[:zip_start]
    zip_bytes = data[zip_start:]
    print(f"  Embedded zip at offset {zip_start:,} ({zip_start / 1024 / 1024:.1f} MB into exe)")

    # Build a set of normalised names for fast lookup
    patch_map = {p.replace("\\", "/"): SCRIPT_DIR / p for p in PATCHED_FILES}

    new_zip_buf = io.BytesIO()
    replaced = []
    kept_original = []

    with zipfile.ZipFile(io.BytesIO(zip_bytes), "r") as src:
        with zipfile.ZipFile(new_zip_buf, "w", compression=zipfile.ZIP_DEFLATED) as dst:
            for info in src.infolist():
                name = info.filename.replace("\\", "/")
                if name in patch_map:
                    patch_file = patch_map[name]
                    if patch_file.exists():
                        dst.write(patch_file, info.filename)
                        replaced.append(name)
                    else:
                        dst.writestr(info, src.read(info.filename))
                        kept_original.append(name)
                        print(f"  WARNING: patch source not found: {patch_file}")
                else:
                    dst.writestr(info, src.read(info.filename))

    if not replaced:
        print("ERROR: No files were patched. Check that PATCHED_FILES paths match the zip contents.")
        sys.exit(1)

    print(f"  Patched:        {', '.join(replaced)}")
    if kept_original:
        print(f"  Kept original:  {', '.join(kept_original)}")

    patched_data = exe_prefix + new_zip_buf.getvalue()
    output_path.write_bytes(patched_data)
    print(f"Written to {output_path} ({len(patched_data) / 1024 / 1024:.1f} MB)")
    print()
    print("Next step: run balatro-mobile-maker pointing at this patched exe.")
    print("  NOTE: when balatro-mobile-maker asks to apply the landscape patch, say NO.")
    print("        Its FPS cap patch is optional: the mod already caps mobile at 60 fps.")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        "input",
        nargs="?",
        default=None,
        help="Path to original Balatro.exe (default: first existing of "
        + ", ".join(DEFAULT_BALATRO_PATHS) + ")",
    )
    parser.add_argument(
        "-o", "--output",
        default="Balatro-portrait.exe",
        help="Output filename (default: Balatro-portrait.exe)",
    )
    args = parser.parse_args()

    input_path = Path(args.input or default_balatro_path())
    output_path = Path(args.output)
    if not output_path.is_absolute():
        output_path = SCRIPT_DIR / output_path

    if not input_path.exists():
        print(f"ERROR: Input not found: {input_path}")
        if args.input is None:
            print("Checked default Steam locations:")
            for p in DEFAULT_BALATRO_PATHS:
                print(f"  {p}")
        print("Pass the path to Balatro.exe as the first argument.")
        return 1

    missing = [f for f in PATCHED_FILES if not (SCRIPT_DIR / f).exists()]
    if missing:
        print("ERROR: Missing patch sources:")
        for f in missing:
            print(f"  {SCRIPT_DIR / f}")
        return 1

    patch(input_path, output_path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
