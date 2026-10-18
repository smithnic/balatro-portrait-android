#!/usr/bin/env bash
# Build and install the portrait APK from WSL.
#
#   ./build.sh [--balatro PATH] [--no-install] [MOBILE_MAKER_DIR]
#
# Steps: patch.py -> copy patched exe into balatro-mobile-maker's folder as
# Balatro.exe -> run balatro-mobile-maker.exe (interactive) -> copy balatro.apk
# back here -> adb.exe install.
#
# MOBILE_MAKER_DIR is the folder containing balatro-mobile-maker.exe; pass it as
# an argument or set it in the environment.

set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PACKAGE="com.unofficial.balatro"

usage() {
    sed -n '2,11p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'
    exit 1
}

balatro_exe=""
install=1
mm_dir="${MOBILE_MAKER_DIR:-}"

while [[ $# -gt 0 ]]; do
    case "$1" in
        --balatro) [[ $# -ge 2 ]] || usage; balatro_exe="$2"; shift 2 ;;
        --no-install) install=0; shift ;;
        -h|--help) usage ;;
        -*) echo "Unknown option: $1" >&2; usage ;;
        *) mm_dir="$1"; shift ;;
    esac
done

if [[ -z "$mm_dir" ]]; then
    echo "ERROR: balatro-mobile-maker folder not given (argument or MOBILE_MAKER_DIR)." >&2
    usage
fi
mm_dir="$(cd "$mm_dir" && pwd)"
if [[ ! -f "$mm_dir/balatro-mobile-maker.exe" ]]; then
    echo "ERROR: balatro-mobile-maker.exe not found in $mm_dir" >&2
    exit 1
fi
if [[ "$mm_dir" != /mnt/* ]]; then
    echo "WARNING: $mm_dir is not on a Windows drive (/mnt/...); mobile-maker may not work from a WSL path." >&2
fi
if [[ $install -eq 1 ]] && ! command -v adb.exe >/dev/null; then
    echo "ERROR: adb.exe not on PATH (Android SDK platform-tools). Use --no-install to skip installing." >&2
    exit 1
fi

echo "==> Patching Balatro.exe"
patch_args=()
[[ -n "$balatro_exe" ]] && patch_args+=("$balatro_exe")
python3 "$REPO_DIR/patch.py" "${patch_args[@]}"

echo "==> Staging patched exe in $mm_dir"
# mobile-maker uses Balatro.exe from its own folder, else falls back to the
# unpatched Steam copy - so it must be there.
cp "$REPO_DIR/Balatro-portrait.exe" "$mm_dir/Balatro.exe"
# Move the old APK aside so mobile-maker doesn't prompt about a previous build
# and a stale APK can't be mistaken for the new one.
if [[ -f "$mm_dir/balatro.apk" ]]; then
    mv -f "$mm_dir/balatro.apk" "$mm_dir/balatro.apk.prev"
fi

echo
echo "==> Running balatro-mobile-maker"
echo "    - Build for Android: yes"
echo "    - FPS cap patch: NO (the mod caps mobile at 60 fps itself; yes overrides that)"
echo "    - Landscape orientation patch: NO (it has no effect on this mod anyway)"
if [[ $install -eq 1 ]]; then
    echo "    - Automatically install: NO (this script installs afterwards)"
fi
echo
# mobile-maker can exit non-zero (or be closed with Ctrl+C at its last prompt)
# even after a successful build, so judge success by whether balatro.apk appeared.
mm_status=0
trap 'echo >&2' INT
(cd "$mm_dir" && ./balatro-mobile-maker.exe) || mm_status=$?
trap - INT
if [[ $mm_status -ne 0 ]]; then
    echo "NOTE: mobile-maker exited with status $mm_status; checking for the APK anyway." >&2
fi

if [[ ! -f "$mm_dir/balatro.apk" ]]; then
    echo "ERROR: mobile-maker did not produce $mm_dir/balatro.apk" >&2
    exit 1
fi
cp "$mm_dir/balatro.apk" "$REPO_DIR/balatro.apk"
echo "==> APK copied to $REPO_DIR/balatro.apk"

if [[ $install -eq 0 ]]; then
    exit 0
fi

echo "==> Installing with adb.exe"
if ! out="$(adb.exe install -r "$(wslpath -w "$REPO_DIR/balatro.apk")" 2>&1)"; then
    echo "$out" >&2
    if grep -q "INSTALL_FAILED_UPDATE_INCOMPATIBLE" <<<"$out"; then
        echo >&2
        echo "The installed app has a different signature. Uninstalling DELETES its saves -" >&2
        echo "back them up first, then:" >&2
        echo "  adb.exe uninstall $PACKAGE" >&2
        echo "  adb.exe install \"$(wslpath -w "$REPO_DIR/balatro.apk")\"" >&2
    fi
    exit 1
fi
echo "$out"
