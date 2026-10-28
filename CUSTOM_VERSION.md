# v0.2.0: Connected Desk Pet

Chris Dong's fork of [yousifamanuel/clawd-mochi](https://github.com/yousifamanuel/clawd-mochi), based on upstream `main` at
commit `0a8e9f6` (2026-06-28). Everything below is added on top of upstream. Hardware, wiring, original firmware, case and photos are upstream's.

## Firmware (`clawd_mochi/clawd_mochi.ino`, still one file)

- **STA mode:** joins your Wi-Fi when `STA_SSID` is set; after 15 s without a connection it falls back to the classic `ClaWD-Mochi` hotspot.
- **Static IP** `192.168.137.50` (Windows mobile hotspot subnet), re-applied on every reconnect. mDNS name `clawdmochi.local`.
- **Self-healing Wi-Fi:** checks every 10 s and rejoins after the network drops.
- **ESP32-C3 SuperMini fixes:** `WiFi.setTxPower(WIFI_POWER_8_5dBm)` (antenna quirk) and `WiFi.setSleep(false)` (modem sleep broke uploads).
- **`/notify` API:** `view`, `msg`, `alert=good|bad`, `breathe`, `sleep`, `face`, `bg`. See [docs/api.md](docs/api.md).
- **`/update`:** firmware upload over plain HTTP. Replaces ArduinoOTA/espota, which Windows Firewall blocked.
- **Backlight on PWM:** breathing pulse, faint sleep pulse, night dimming 00:00–08:00 (NTP, US Central).
- **Life:** 10 faces rotating every 2–6 min, random blinks and glances.
- **Sleep sync:** `sleep=1|0`; wakes itself after 10 min asleep with no network.

## PC side (`tools/`, Windows 11)

- Claude Code hooks example: squint on done, red flash on tool failure, breathing while waiting.
- Lock/unlock → sleep/wake: two VBScripts + two Task Scheduler XMLs.
- `mochi_watchdog.py`: restarts the Windows mobile hotspot when Mochi goes unreachable.

## Case (`models/clawd_mochi/`)

- `clawd_mochi_v1_holes_2.2mm.stl` / `.step`: screw holes widened 1.6 → 2.2 mm, rebuilt by `enlarge_screw_holes.py`. CC BY-NC-SA 4.0, derived from Yousuf Amanuel's design.

## Docs

- README rewritten as a beginner tutorial; `docs/` for API, troubleshooting, Claude Code, Windows automation, case & assembly.
