#!/usr/bin/env python3
import subprocess, requests, os, signal
import traycore

API_URL = "https://api.somafm.com/channels.json"
PID_FILE = "/tmp/somafm_tray.pid"

state = {
    "song": "",
    "playing": False,
    "tray_label": "🎵 SomaFM",
    "channels": {},          # id → title
    "channel_ids": [],       # [id1, id2, ...]
    "current_channel": "groovesalad",
}

def get_stream_url():
    return f"https://ice.somafm.com/{state['current_channel']}"

def start():
    stop()
    proc = subprocess.Popen(["mpv", "--no-video", "--ao=pulse", "--quiet", get_stream_url()],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    with open(PID_FILE, "w") as f:
        f.write(str(proc.pid))
    state["playing"] = True
    app.update_ui()

def stop():
    try:
        with open(PID_FILE) as f:
            os.kill(int(f.read().strip()), signal.SIGTERM)
        os.remove(PID_FILE)
    except:
        pass
    state["playing"] = False
    app.update_ui()

def download():
    subprocess.Popen(["spotdl", state["song"]],
                     cwd=os.path.expanduser("~/Music"),
                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def quit_app():
    stop()
    app.quit()

def switch_channel(channel_id):
    state["current_channel"] = channel_id
    start()
    app.update_ui()

def next_channel():
    ids = state["channel_ids"]
    cur = state["current_channel"]
    idx = (ids.index(cur) + 1) % len(ids)
    switch_channel(ids[idx])

def prev_channel():
    ids = state["channel_ids"]
    cur = state["current_channel"]
    idx = (ids.index(cur) - 1) % len(ids)
    switch_channel(ids[idx])

def fetch_song():
    try:
        data = requests.get(API_URL, timeout=5).json()
        for c in data["channels"]:
            if c["id"] == state["current_channel"]:
                state["song"] = c["lastPlaying"]
                state["tray_label"] = f"🎵 {state['song']}"
                break
    except:
        state["song"] = "(error)"
    app.update_ui()
    return True

def fetch_channels():
    try:
        data = requests.get(API_URL, timeout=5).json()
        channels = {c["id"]: c["title"] for c in data["channels"]}
        state["channels"] = channels
        state["channel_ids"] = list(channels.keys())
        if state["current_channel"] not in state["channels"]:
            state["current_channel"] = state["channel_ids"][0]
    except:
        state["channels"] = {"groovesalad": "Groove Salad"}
        state["channel_ids"] = ["groovesalad"]
    app.rebuild_submenu("channel_list", build_channel_submenu)
    app.update_ui()

def build_channel_submenu():
    menu = []
    for cid, title in state["channels"].items():
        menu.append({
            "type": "radio",
            "label": title,
            "active": (cid == state["current_channel"]),
            "action": lambda c=cid: switch_channel(c)
        })
    return menu

layout = [
    # {"type": "text", "id": "song_line", "bind": "song"},
    {"type": "dynamic", "id": "download", "template": "⬇️ Download {song}", "action": download},
      {"type": "submenu", "id": "channel_list", "label": "🎚️ Change Channel", "build": build_channel_submenu},
        {
        "type": "toggle",
        "id": "play_button",
        "state": "playing",
        "states": [
            {"label": "▶️ Play", "action": start},
            {"label": "⏸️ Pause", "action": stop}
        ]
    },
    {"type": "button", "label": "⏮️ Previous Channel", "action": prev_channel},
    {"type": "button", "label": "⏭️ Next Channel", "action": next_channel},
  
    {"type": "separator"},
    {"type": "button", "label": "Quit", "action": quit_app}
]

app = traycore.TrayApp(
    "somafm",
    state,
    layout,
    icon="audio-x-generic"  # or provide your own icon path
)
fetch_channels()
start()
app.run(update_fn=fetch_song, interval=10)
