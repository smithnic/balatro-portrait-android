# Balatro Portrait Mode (Android)

An unofficial portrait-mode mod for Balatro on Android.

> **You must own [Balatro on Steam](https://store.steampowered.com/app/2379780/Balatro/) to use this mod.**

## What this mod does

- Rotates the game layout to portrait orientation
- Scales cards, jokers, and consumables for comfortable one-handed phone use
- Repositions the hand, play area, deck, and UI panels to fit a tall screen
- Tuned for a 412×912 dp screen (e.g. Samsung Galaxy S23 series) but works on similar Android phones
- Stretches the play area to the phone's aspect ratio, so tall screens are filled edge to edge
- Keeps card tooltips on screen for cards near the edges
- Locks the device to portrait (auto-rotate won't flip it into landscape)

## Prerequisites

- Balatro installed via Steam on Windows
- Python 3.6 or later
- [balatro-mobile-maker](https://github.com/blake502/balatro-mobile-maker), in a folder on a Windows drive
- `adb` from Android SDK platform-tools (under WSL, `adb.exe` on `PATH`)

## Build (WSL)

`build.sh` runs the whole pipeline: it patches the exe, stages it in mobile-maker's folder as `Balatro.exe`, runs `balatro-mobile-maker.exe`, copies `balatro.apk` back here, and installs it with `adb.exe`:

```
export MOBILE_MAKER_DIR="/mnt/c/path/to/balatro-mobile-maker"
./build.sh
```

- `--balatro PATH`: use a Balatro.exe other than the default Steam install
- `--no-install`: build only, don't run `adb.exe install`

mobile-maker is interactive. Answer **yes** to building for Android, **No** to the landscape orientation patch, and **No** to its automatic install, since the script installs afterwards.

## Build (manual)

### 1. Patch the exe

Run the patcher from this repo's directory:

```
python patch.py        # python3 under WSL
```

This reads `Balatro.exe` from the default Steam path (`C:\Program Files (x86)\...` on Windows, `/mnt/c/Program Files (x86)/...` under WSL) and writes `Balatro-portrait.exe` next to it.

If Balatro is installed somewhere else, pass the path explicitly:

```
python patch.py "D:\Steam\steamapps\common\Balatro\Balatro.exe"
```

### 2. Set up balatro-mobile-maker

- Rename `Balatro-portrait.exe` → `Balatro.exe`
- Place it in the same directory as `balatro-mobile-maker.exe`

### 3. Run balatro-mobile-maker

Run `balatro-mobile-maker.exe`. When it asks whether to apply the **landscape patch**, choose **No**. The mod handles orientation itself (portrait lock), and the patch's search text no longer exists in this mod's files, so it would have no effect anyway.

### 4. Install the APK

```
adb install balatro.apk
```

(Under WSL, use `adb.exe`.) If a previous version is already installed, the install fails with a signature error. Uninstalling **deletes the app's saves**, so back them up first:

```
adb uninstall com.unofficial.balatro
adb install balatro.apk
```

## How the portrait lock works

On Android, LÖVE/SDL picks the screen orientation from the window settings at runtime, overriding the APK manifest. A resizable window allows any rotation. A non-resizable window is locked to portrait or landscape depending on whether its width is less than its height. `conf.lua` and `G.FUNCS.apply_window_changes` (`functions/button_callbacks.lua`) make the window non-resizable on Android/iOS and always pass portrait dimensions.

The window size passed there is the full display size from `love.window.getDesktopDimensions`, swapped to portrait. The game starts in landscape (the manifest says so), and the size LÖVE reports at that point excludes the system bars; reused for the portrait window, it leaves a black strip at the top of the screen.

## Legal

This repo contains only the modifications to Balatro's Lua files — no original game assets, audio, textures, or unmodified code. A legitimate Steam copy of Balatro is required to build the APK.

Balatro is created by [LocalThunk](https://localthunk.com/).
