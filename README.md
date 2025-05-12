# 🎵 SomaFM Tray Player

A minimalist GTK tray app that lets you stream and control SomaFM directly from your Linux system tray — with a clean, declarative, and reusable design powered by `traycore`.

![SomaFM Tray Screenshot](https://github.com/ohbob/somafm-tray-xfce/blob/main/soma.jpg?raw=true)

---

## 🚀 What It Does

- Streams SomaFM radio channels using `mpv`
- Shows current track title
- Lets you:
  - ⏯️ Play / Pause
  - ⏮️ Previous / ⏭️ Next channel
  - 📻 Switch channels via submenu with checkmarks
  - ⬇️ Download current song using `spotdl`
- Runs in the background as a tiny GTK3 AppIndicator tray app

---

## 🧠 What Is `traycore`?

`traycore.py` is a **micro-framework** included in this repo that lets you:

- Define tray apps **declaratively**
- Use a single `state` dictionary to manage app data
- Create UI from a **simple `layout = [...]` list**
- Reuse the framework across any GTK tray project
---

## 💻 Requirements

- Python 3
- GTK 3 (`gi` bindings)
- `mpv`
- `spotdl`
- `requests`
