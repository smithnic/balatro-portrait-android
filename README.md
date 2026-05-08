# Balatro Portrait Mode (Android)

An unofficial portrait-mode mod for Balatro on Android.

> **You must own [Balatro on Steam](https://store.steampowered.com/app/2379780/Balatro/) to use this mod.**

## What this mod does

- Rotates the game layout to portrait orientation
- Scales cards, jokers, and consumables for comfortable one-handed phone use
- Repositions the hand, play area, deck, and UI panels to fit a tall screen
- Tuned for a 412×912 dp screen (e.g. Samsung Galaxy S23 series) but works on similar Android phones

## Known Issues

- Rotating into landscape mode currently still uses the portrait layout so the interface becomes too small

## Prerequisites

- Balatro installed via Steam on Windows
- Python 3.6 or later
- [balatro-mobile-maker](https://github.com/blake502/balatro-mobile-maker)

## Build steps

### 1. Patch the exe

Run the patcher from this repo's directory:

```
python patch.py
```

This reads `Balatro.exe` from the default Steam path and writes `Balatro-portrait.exe` next to it.

If Balatro is installed somewhere else, pass the path explicitly:

```
python patch.py "D:\Steam\steamapps\common\Balatro\Balatro.exe"
```

### 2. Set up balatro-mobile-maker

- Rename `Balatro-portrait.exe` → `Balatro.exe`
- Place it in the same directory as `balatro-mobile-maker.exe`

### 3. Run balatro-mobile-maker

Run `balatro-mobile-maker.exe`. When it asks whether to apply the **landscape patch**, choose **No** — the portrait mod already handles orientation.

### 4. Install the APK

```
adb install balatro.apk
```

If a previous version is already installed (install will fail with a signature error):

```
adb uninstall com.unofficial.balatro
adb install balatro.apk
```

## Legal

This repo contains only the modifications to Balatro's Lua files — no original game assets, audio, textures, or unmodified code. A legitimate Steam copy of Balatro is required to build the APK.

Balatro is created by [LocalThunk](https://localthunk.com/).
