# Windows automation

How this Mochi lives on a Windows 11 desk: the PC's own hotspot is its network, Mochi sleeps when the PC locks, and a watchdog
brings the hotspot back when it drops. Install and remove commands for the scripts are in [`tools/README.md`](../tools/README.md).

## 1. Windows mobile hotspot

**Why:** the ESP32-C3 has a small antenna. If your router is far away (here: downstairs, RSSI -92 dBm), Mochi can't hold a connection.
The PC on the same desk is a few centimetres away, so its hotspot is a solid link, and it shares the PC's internet so the night-dimming clock (NTP) still works.

**Set it up:**

1. **Settings → Network & internet → Mobile hotspot.**
2. *Share my internet connection from*: your normal Wi-Fi or Ethernet.
3. **Properties → Edit**: pick a network name and password, and set **Network band = 2.4 GHz** (Mochi can't use 5 GHz).
4. Turn **Power saving** ("when no devices are connected, turn off mobile hotspot") **off**.
5. Turn the hotspot **on**.
6. In `clawd_mochi.ino`, set `STA_SSID` / `STA_PASS` to that name and password and re-flash. Keep these local and never commit them.

✅ After boot the screen shows `WiFi: <your hotspot name>`, and Windows' hotspot page lists one connected device.
Mochi is at **`http://192.168.137.50`**. Windows hotspots always use `192.168.137.x`, and the firmware asks for `.50` so
scripts always know where to find it.

If you need to find it another way:
```powershell
arp -a | findstr 192.168.137
```

**Limits (be aware):**

- The hotspot goes off whenever the PC sleeps. Mochi falls back and rejoins on its own once the hotspot is back.
- It also turns itself off now and then **while the PC is awake**, with no clear cause. That's what the watchdog (section 3) is for.

## 2. Sleep when the PC locks

Two Scheduled Tasks listen for Windows' **SessionLock** / **SessionUnlock** events and run a tiny VBScript each.
The VBScript calls `curl.exe` with the window hidden (Task Scheduler would otherwise flash a console every time you lock):

| Event | Script | Request | Mochi |
| ----- | ------ | ------- | ----- |
| Lock (Win + L, screen timeout) | `mochi_lock.vbs` | `/notify?sleep=1` (3 retries) | eyes shut, faint slow pulse |
| Unlock | `mochi_unlock.vbs` | `/notify?sleep=0` (6 retries, 3 s apart) | wake-up wiggle |

Unlock retries more because after a real PC sleep, the hotspot needs a few seconds to come back.
Any button on the web page also wakes Mochi. If it is asleep and the network stays gone for 10+ minutes, it wakes itself up.

→ Install / remove: [`tools/README.md#lock--unlock-sync`](../tools/README.md#lock--unlock-sync)

## 3. Hotspot watchdog

`tools/mochi_watchdog.py` checks `http://192.168.137.50/state` every 10 s. When Mochi stops answering, it runs a PowerShell snippet
that calls the WinRT `NetworkOperatorTetheringManager.StartTetheringAsync()`. That's the same thing as clicking the hotspot toggle.
When Mochi answers again, the watchdog sends `/cmd?k=w` so it comes back to its normal face.

It runs only while its window is open. It isn't installed as a service or task.

→ Run / stop: [`tools/README.md#hotspot-watchdog`](../tools/README.md#hotspot-watchdog)
