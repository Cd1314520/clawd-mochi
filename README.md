<!-- LOGO -->
<p align="center">
  <img src="pics/clawd_mochi_banner.png" alt="Clawd Mochi Logo" width="700"/>
</p>

# Clawd Mochi: Connected Desk Pet 🦀

A tiny desk companion inspired by **Clawd**, the pixel-crab mascot of Claude Code. An ESP32-C3 drives a 1.54" colour screen,
shows animated faces, and serves a web controller to your phone. This version can also join your Wi-Fi, react to
**Claude Code** (done / failed / waiting for you), fall asleep when your PC locks, and take firmware updates over Wi-Fi.

This is a step-by-step build guide for total beginners, from buying parts to Mochi reacting on your desk.

**Cost: ~$7–8 · Skill level: beginner · No soldering if you buy boards with pins already soldered on**

> This is a personal fork of **[yousifamanuel/clawd-mochi](https://github.com/yousifamanuel/clawd-mochi)** by Yousuf Amanuel.
> The hardware design, the 3D case, the original firmware and all photos are his. Please support the original project:
> [Instagram](https://instagram.com/clawd.mochi) · [case on MakerWorld](https://makerworld.com/en/models/2559505-clawd-mochi-physical-claude-code-mascot#profileId-2820000).

> ⚠️ Independent fan project. Not affiliated with, sponsored by, or endorsed by Anthropic. "Claude" and "Clawd" are trademarks of Anthropic.

<p align="center">
  <img src="pics/clawd_mochi_3_4.jpeg" alt="Assembled Clawd Mochi on a desk" width="420"/>
  &nbsp;
  <img src="pics/clawd_mochi_claude_code.jpeg" alt="Claude Code view" width="420"/>
</p>
<p align="center"><sub>Photos: upstream project.</sub></p>

---

## What's upstream, what's new here

| Upstream (yousifamanuel) | Added in this fork (v0.2.0) |
| ------------------------ | --------------------------- |
| Hardware, wiring, 3D case | Joins your Wi-Fi (STA mode) with fallback to its own hotspot, auto-reconnect, static IP |
| Normal / squish eyes, Claude Code terminal, canvas | 10 faces that rotate on their own, idle blinks and glances, night dimming |
| Web controller over its own hotspot | `/notify` API for scripts: faces, messages, red/green flash, breathing backlight, sleep/wake |
| Flash over USB | Wireless updates over HTTP (`/update`) |
| | Claude Code hooks, Windows lock → sleep sync, hotspot watchdog (`tools/`) |
| | Case with 2.2 mm screw holes (`models/clawd_mochi/…holes_2.2mm`) |
| | These docs |

Full list: [CUSTOM_VERSION.md](CUSTOM_VERSION.md).

## Contents

1. [Buy the parts](#1-buy-the-parts)
2. [Wire it up](#2-wire-it-up)
3. [Install Arduino IDE](#3-install-arduino-ide)
4. [First flash](#4-first-flash)
5. [Connect from your phone](#5-connect-from-your-phone)
6. [(Optional) Join your own Wi-Fi](#6-optional-join-your-own-wi-fi)
7. [(Optional) Wireless updates](#7-optional-wireless-updates)
8. [(Optional) Claude Code integration](#8-optional-claude-code-integration)
9. [(Optional) Windows: sleep when the PC locks](#9-optional-windows-sleep-when-the-pc-locks)
10. [3D case & assembly](#10-3d-case--assembly)

[Known issues](#known-issues) · [Customisation](#customisation) · [Troubleshooting](docs/troubleshooting.md) · [HTTP API](docs/api.md) · [License](#license)

---

## 1. Buy the parts

| Part | Spec | ~Price |
| ---- | ---- | ------ |
| ESP32-C3 **SuperMini** | Wi-Fi microcontroller. Get the version **with pins already soldered** | ~$2.50 |
| **1.54" ST7789 TFT** | **240×240**, SPI, **8 pins** (GND VCC SCL SDA RES DC CS BL) | ~$3.00 |
| 8 jumper wires | **female-to-female** Dupont, 8–10 cm (both boards have male pins) | ~$0.50 |
| 2× M2 × 6 mm screws | | ~$0.10 |
| Glue or foam tape | to hold the boards in the case (see step 10) | ~$0.10 |
| USB-C cable | **must carry data**, not just charge | — |
| 3D-printed case | PLA or PETG, ~30 g | ~$0.50 |

**How not to buy the wrong screen:** many listings sell a **1.8" 128×160 ST7735** and a **1.54" 240×240 ST7789** under one
title, and they look almost the same. Pick the **1.54" / 240×240 / ST7789** option, and choose the 8-pin version
that has a **CS** pin. When it arrives, check that the back of the board says **ST7789**.

**About the USB cable:** many cheap USB-C cables only charge. If your PC doesn't react when you plug the board in, the cable is the
first suspect. Use one you've already used to copy files.

## 2. Wire it up

> ⚠️ **VCC goes to 3V3, never 5V.** 5V can kill the display.

| Display pin | Also labelled | ESP32-C3 pin | Suggested colour |
| ----------- | ------------- | ------------ | ---------------- |
| VCC | VIN, 3.3V | **3V3** | red |
| GND | | GND | black |
| SDA | MOSI, DIN | GPIO 10 | orange |
| SCL | SCK, CLK | GPIO 8 | green |
| RES | RST, RESET | GPIO 2 | purple |
| DC | RS, A0 | GPIO 1 | blue |
| CS | SS | GPIO 4 | white |
| BL | BLK, LED | GPIO 3 | yellow |

GPIO 8 and 10 are the chip's hardware SPI pins (fast). Don't move SPI to GPIO 6/7.

✅ **Check:** 8 wires, each one going from a display pin to the matching GPIO above. Double-check VCC → 3V3.

## 3. Install Arduino IDE

1. Install **[Arduino IDE 2.x](https://www.arduino.cc/en/software)**.
2. **File → Preferences →** *Additional boards manager URLs*, paste:
   ```
   https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json
   ```
3. **Tools → Board → Boards Manager**, search `esp32`, install **esp32 by Espressif Systems**, **version 3.x** (tested: 3.3.10).
4. **Tools → Manage Libraries**, install:
   - `Adafruit GFX Library` (tested: 1.12.6)
   - `Adafruit ST7735 and ST7789 Library` (tested: 1.11.0)
5. Download this repo (**Code → Download ZIP**, then unzip), and open **`clawd_mochi/clawd_mochi.ino`**.
   The folder name must stay `clawd_mochi` (Arduino requires the folder and `.ino` file to share a name).
6. Plug in the board and set **Tools**:

   | Setting | Value |
   | ------- | ----- |
   | Board | **ESP32C3 Dev Module** |
   | USB CDC On Boot | **Enabled** ← important, or you get no serial output over USB |
   | CPU Frequency | 160 MHz |
   | Upload Speed | 921600 |
   | Partition Scheme | leave the default (needed for wireless updates) |
   | Port | the new **COMx** that appeared when you plugged in |

✅ **Check:** Tools → Port lists a COM port. If it's greyed out → [Troubleshooting: Port greyed out](docs/troubleshooting.md#tools--port-is-greyed-out--empty-in-arduino-ide).

## 4. First flash

Leave `STA_SSID` empty for now (it is by default). Click **Upload** (→). It takes about a minute.

✅ **Check:** the IDE ends with `Hard resetting via RTS pin...`, and the screen shows **"Clawd Mochi"**, draws the logo, then shows a
Wi-Fi info screen with `ClaWD-Mochi`, `clawd1234` and `192.168.4.1`.
Nothing on the screen? → [Troubleshooting: screen](docs/troubleshooting.md#screen--first-boot).

## 5. Connect from your phone

1. On your phone (or laptop), join Wi-Fi **`ClaWD-Mochi`**, password **`clawd1234`**. If the phone warns "no internet", stay connected anyway.
2. Open **`http://192.168.4.1`** in a browser.
3. Tap any view, e.g. **Normal eyes**. The screen's *"press any button to start"* means a button on this **web page**.

<img src="pics/clawd_mochi_webpage.jpeg" alt="Web controller" width="320"/>

✅ **Check:** Mochi's eyes wiggle and blink. That's a complete upstream-style Mochi. Everything below is optional.

| Control | What it does |
| ------- | ------------ |
| Normal eyes / Squish eyes | Play the eye animations |
| Claude Code | Title screen + a terminal you type into from the phone |
| Canvas | Draw on the screen with your finger |
| Speed slider | Animation speed |
| Background / Pen colour | Colours for the eyes view and the canvas |
| Display on/off | Backlight |

## 6. (Optional) Join your own Wi-Fi

Then any device on that network can reach Mochi, which you need for steps 7–9.

> **Read this first: the firmware uses a fixed IP for Windows mobile hotspots.** In STA mode Mochi asks for
> **`192.168.137.50`**, the subnet every Windows mobile hotspot uses. That's how this build runs (option A).
> For a normal home router you need one small edit (option B).

**Option A: your PC's Windows mobile hotspot (what this build uses).** Best if your router is far from your desk.
Set up the hotspot at **2.4 GHz** as described in [docs/windows-automation.md](docs/windows-automation.md#1-windows-mobile-hotspot).

**Option B: your home router.** Must be the **2.4 GHz** network (the ESP32-C3 can't do 5 GHz). In `clawd_mochi.ino`, find
`staBegin()` and either delete the `WiFi.config(...)` line (the router assigns an address) or change the four addresses to fit your network.

Then, for either option, fill in near the top of `clawd_mochi.ino`:
```cpp
const char* STA_SSID = "your-2.4GHz-network";
const char* STA_PASS = "your-password";
```
and upload again.

> 🔒 **Never commit or share the file with your password in it.** Put `""` back before you `git commit`.

✅ **Check:** the screen shows `WiFi: <your network>`, `clawdmochi.local` and the IP. Open `http://192.168.137.50`
(option A) or `http://clawdmochi.local` from a device on that network.
If it can't connect within 15 s, Mochi falls back to its own `ClaWD-Mochi` hotspot and keeps retrying in the background →
[Troubleshooting: Wi-Fi](docs/troubleshooting.md#wi-fi).

## 7. (Optional) Wireless updates

Once Mochi is on your network, you never need the USB cable again.

1. Arduino IDE → **Sketch → Export Compiled Binary**. The file lands in
   `clawd_mochi/build/esp32.esp32.esp32c3/clawd_mochi.ino.bin`.
2. Push it (in PowerShell type **`curl.exe`**, not `curl`):
   ```bash
   curl.exe --limit-rate 24k -F "f=@clawd_mochi/build/esp32.esp32.esp32c3/clawd_mochi.ino.bin" http://192.168.137.50/update
   ```
   **Keep `--limit-rate 24k`.** Without it the upload crashes partway.

✅ **Check:** the screen says `updating...`, then Mochi reboots. curl printing **`Empty reply from server`** is normal: Mochi rebooted
before replying. Confirm with `curl.exe http://192.168.137.50/state`.

Command-line alternative to step 1, using the `arduino-cli` that ships inside Arduino IDE:
```bash
arduino-cli compile --fqbn esp32:esp32:esp32c3:CDCOnBoot=cdc --output-dir build clawd_mochi
```

Why not the IDE's network port (ArduinoOTA)? It doesn't get through Windows Firewall. See [Troubleshooting](docs/troubleshooting.md#wireless-updates).

## 8. (Optional) Claude Code integration

Four Claude Code hooks turn Mochi into a status light: **squint** = done, **red flash** = a tool failed, **breathing backlight** = waiting
for you. Copy them from [`tools/claude-code-hooks.example.json`](tools/claude-code-hooks.example.json) into your `~/.claude/settings.json`.

→ Full guide: [docs/claude-code-hooks.md](docs/claude-code-hooks.md). All endpoints: [docs/api.md](docs/api.md).

## 9. (Optional) Windows: sleep when the PC locks

Lock your PC → Mochi closes its eyes. Unlock → it wakes up. Two Scheduled Tasks and two tiny scripts, plus an optional watchdog
that turns the Windows hotspot back on when it drops.

→ How it works: [docs/windows-automation.md](docs/windows-automation.md) · Install / remove: [tools/README.md](tools/README.md)

## 10. 3D case & assembly

Print **[`models/clawd_mochi/clawd_mochi_v1_holes_2.2mm.stl`](models/clawd_mochi/clawd_mochi_v1_holes_2.2mm.stl)**. It's the upstream case with screw holes widened from
1.6 to 2.2 mm. The original is still at `models/clawd_mochi/clawd_mochi_v1.stl`. PLA/PETG, 0.15–0.20 mm layers, 15% gyroid, supports for the display window, face-down.

Short version: test-fit first; all 8 display wires stay inside, and only the USB-C cable uses the back slot; glue the boards (E6000 is permanent; use foam tape if you may want to open it).

→ Full guide, CAD/STEP file and the Fusion 360 "10× too big" fix: [docs/case-and-assembly.md](docs/case-and-assembly.md)

**Just want a figure, no electronics?** Print the 3D Clawd: [`models/clawd_3d/`](models/clawd_3d/) or the squished-eyes version
[`models/clawd_3d_squished_eyes/`](models/clawd_3d_squished_eyes/) ([MakerWorld](https://makerworld.com/en/models/2576503-clawd-claude-code-mascot#profileId-2841183)).

<img src="pics/clawd_3D_squished_eyes_4_3.png" alt="3D printed Clawd with squished eyes" width="420"/>

---

## Known issues

- **The Windows mobile hotspot drops unpredictably.** It always turns off when the PC sleeps, and sometimes within minutes while the PC is
  awake, for no clear reason. Mochi rejoins as soon as the hotspot is back; `tools/mochi_watchdog.py` turns it back on, but only while it's running.
- **The automatic hotspot restart task was never registered.** A Scheduled Task to restart the hotspot at unlock was written but never got
  registered on the original machine, so it isn't included. The watchdog is the working substitute.
- **A "keeps restarting" report was never root-caused.** At one point Mochi was reported as restarting repeatedly over several days. The network was down at
  the time, and the investigation stopped before finding a cause.
- **No authentication.** Anyone on the same network can control Mochi or flash new firmware via `/update`. Keep it on a network you trust.
- **STA mode assumes a Windows hotspot** (static IP `192.168.137.50`). Home routers need the edit in [step 6](#6-optional-join-your-own-wi-fi).
- **Night dimming uses US Central time** and only works when Mochi's network has internet (NTP).
- **Only tested on Windows 11**: the PC-side scripts, the Scheduled Tasks and the Claude Code hooks. The firmware itself doesn't care about your OS.

## Customisation

All in `clawd_mochi/clawd_mochi.ino`, near the top:

| What | Where |
| ---- | ----- |
| Hotspot name / password | `AP_SSID`, `AP_PASS` |
| Your Wi-Fi, join timeout | `STA_SSID`, `STA_PASS`, `STA_TIMEOUT_MS` |
| Static IP | `staBegin()` |
| Face rotation interval | `FACE_MIN_MS`, `FACE_RND_MS` |
| Time zone, night hours, night brightness | `TZ_STRING`, `NIGHT_UNTIL`, `NIGHT_DUTY` |
| Eye size and position | `EYE_W`, `EYE_H`, `EYE_GAP`, `EYE_OX`, `EYE_OY` |

## Repository layout

```
clawd_mochi/clawd_mochi.ino   the firmware (one file, on purpose)
docs/                         API, troubleshooting, Claude Code, Windows, case guides
tools/                        optional PC-side scripts (Windows)
models/                       3D case + 3D Clawd figures (CC BY-NC-SA 4.0)
pics/                         photos (upstream, CC BY-NC-SA 4.0)
```

## Contributing

Fork, change, open a pull request. Please keep the firmware a **single `clawd_mochi.ino` file** (upstream's request) so beginners can flash it in one go.
Generic improvements (STA mode, `/notify`, `/update`, the ESP32-C3 SuperMini Wi-Fi fixes) are good candidates to send upstream too.

## License

- Firmware and scripts: **MIT**. See [LICENSE](LICENSE).
- 3D models and media: **CC BY-NC-SA 4.0**. See [models/LICENSE-models.md](models/LICENSE-models.md). The 2.2 mm case is a modified version of
  Yousuf Amanuel's design and keeps the same license.

---

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=yousifamanuel/clawd-mochi)](https://www.star-history.com/#yousifamanuel/clawd-mochi)
