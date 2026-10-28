# Troubleshooting

Each problem below actually happened while building this Mochi, except a few general tips marked *(general)*.
Find the symptom, then read the cause and the fix.

- [USB & flashing](#usb--flashing)
- [Screen & first boot](#screen--first-boot)
- [Wi-Fi](#wi-fi)
- [Wireless updates](#wireless-updates)
- [Windows automation](#windows-automation)
- [3D case](#3d-case)

---

## USB & flashing

### Nothing shows up in Device Manager when I plug the board in
**Cause:** a **charge-only USB-C cable**. Lots of cheap cables have no data wires. Board, driver, and port are all fine.
**Fix:** use a cable you know can transfer files (for example, one that has moved photos off a phone). A working board appears as
**USB Serial Device (COMx)**. To check from PowerShell (`VID_303A` is Espressif's USB vendor ID):
```powershell
Get-PnpDevice -PresentOnly | Where-Object InstanceId -like '*VID_303A*'
```

### Tools → Port is greyed out / empty in Arduino IDE
**Cause:** same as above. Windows doesn't see the board, so there's no COM port to pick.
**Fix:** swap the cable first. *(general)* If the port still doesn't appear, hold the **BOOT** button on the
board while plugging it in. That forces download mode. Release BOOT, then click Upload.

### Windows keeps playing the device connect / disconnect sound
**Cause:** not root-caused. On this build it stopped after reseating the cable. Most likely a flaky contact in the cable or port.
**Fix:** test one change at a time: unplug the display wires, try another cable, try another USB port. If the sound stops, the last thing you changed was the problem.

### Compile error about `ledcAttach`
**Cause:** ESP32 board package older than 3.0. The firmware uses the 3.x backlight PWM API.
**Fix:** Tools → Board → Boards Manager → update **esp32 by Espressif Systems** to 3.x (tested with 3.3.10).

---

## Screen & first boot

### The screen says "press any button to start" and I'm pressing the board
That means a button **on the web page**, not on the board. Connect to Mochi's Wi-Fi, open the address shown on the screen, and tap any view (e.g. *Normal eyes*).
The info screen stays up until the first web command arrives.

### Screen stays black or white after a successful upload *(general)*
Check the wiring table again, especially **VCC on 3V3** (never 5 V), **BL → GPIO 3** (no BL = black screen), and that SDA/SCL aren't swapped.
Also check the display is a **240×240 ST7789** (printed on the back of the board). A 128×160 ST7735 looks almost identical but won't work with this firmware.

---

## Wi-Fi

### I can't find / can't join my Wi-Fi with Mochi
**Cause:** the ESP32-C3 only supports **2.4 GHz**. It can't see 5 GHz networks at all.
**Fix:** if your router broadcasts two names (e.g. `MyWiFi` and `MyWiFi-5G`), put the 2.4 GHz one in `STA_SSID`.

### Serial monitor shows `[STA] FAILED — falling back to AP`
**Cause on this build:** the home router was downstairs and the signal at the desk was too weak (RSSI around **-92 dBm**; anything below about -80 is unreliable).
**Fix:** move Mochi closer, or do what this build does: turn on **Windows mobile hotspot** on the PC sitting next to it.
Setup: [windows-automation.md → Mobile hotspot](windows-automation.md#1-windows-mobile-hotspot).
Mochi still works in the meantime. It falls back to its own `ClaWD-Mochi` hotspot and keeps retrying your network every 10 s.

### Mochi joins Wi-Fi (screen shows the network name) but I can't open its page
**Cause:** the firmware sets a **static IP of `192.168.137.50`**, which only fits a Windows mobile hotspot (`192.168.137.x`).
On a home router that uses e.g. `192.168.1.x`, Mochi joins but sits on the wrong subnet.
**Fix:** edit `staBegin()` in `clawd_mochi.ino`. Either change the four addresses to match your network, or delete the
`WiFi.config(...)` line to let your router assign an address (then find it on the boot screen or at `http://clawdmochi.local`). See [README step 6](../README.md#6-optional-join-your-own-wi-fi).

### Joining fails even right next to the router (ESP32-C3 SuperMini)
**Cause:** a known SuperMini antenna problem. At full transmit power the signal distorts and the router never finishes the handshake.
**Fix:** already in the firmware: `WiFi.setTxPower(WIFI_POWER_8_5dBm);` before `WiFi.begin`. Copy that line into any other sketch you write for this board.

### Ping to Mochi jumps around ~200 ms; uploads drop halfway
**Cause:** Wi-Fi *modem sleep*. The radio naps between beacons.
**Fix:** already in the firmware: `WiFi.setSleep(false);` after connecting. With it, ping is around 16 ms.

### Mochi went offline / stopped reacting
Almost always the network, not Mochi:
1. Is the Windows mobile hotspot still on? It turns itself off sometimes, and always when the PC sleeps. Turn it back on. Mochi rejoins within ~10 s.
2. Run [`tools/mochi_watchdog.py`](../tools/README.md#hotspot-watchdog) to do that automatically.
3. Check with `curl.exe http://192.168.137.50/state`.
4. If Mochi was asleep (eyes shut) when the network vanished, it wakes up by itself after 10 minutes.

---

## Wireless updates

### Arduino IDE's network port / ArduinoOTA / espota doesn't work
**Cause:** espota needs Mochi to open a connection *back* to the PC, and Windows Firewall blocks it. It failed 4 out of 4 times here, so ArduinoOTA was removed from the firmware.
**Fix:** use the HTTP `/update` endpoint instead. Your PC pushes the file, so there's no connection back for the firewall to block. [README step 7](../README.md#7-optional-wireless-updates).

### `curl` upload dies at around 100–200 KB
**Cause:** writing flash blocks the Wi-Fi stack, and a fast upload overflows it.
**Fix:** always add `--limit-rate 24k`.

### `curl: (52) Empty reply from server` after the upload
**That's success.** Mochi finished writing, rebooted right away, and cut the connection. Wait ~10 s, then run `curl.exe http://<ip>/state`. If JSON comes back, the update worked.

### `/update` replies `FAILED`
*(general)* Check that you uploaded the **`clawd_mochi.ino.bin`** file (not `.bootloader.bin`, `.partitions.bin` or `.merged.bin`), and that
**Tools → Partition Scheme** is still the default. "No OTA" / "Huge APP" schemes leave no room for an update.

### In PowerShell, `curl -F ...` errors out with something about parameters
Windows PowerShell 5.1 maps `curl` to `Invoke-WebRequest`. Type **`curl.exe`**.

---

## Windows automation

### Registering a Scheduled Task fails with `Access is denied`
Open PowerShell **as Administrator** and run the command there. On this build, that was the only way that worked.

### The lock/unlock task runs, but Mochi doesn't react
1. Run the script by hand: `wscript "$env:LOCALAPPDATA\ClawdMochi\mochi_lock.vbs"`. If that doesn't work, fix `MOCHI_IP` in the `.vbs`.
2. If the script works by hand but not from the task, open Task Scheduler → the task → Actions and replace `%LOCALAPPDATA%` with the full path.
3. Waking after the PC slept: the hotspot takes a few seconds to come back. `mochi_unlock.vbs` already retries 6 times, 3 s apart.

---

## 3D case

### Fusion 360 imports the STL 10× too big
**Cause:** STL files carry no units, and Fusion assumes centimetres.
**Fix:** in the *Insert Mesh* dialog, set units to **Millimeter**. Or open the `.step` version instead
(`models/clawd_mochi/clawd_mochi_v1_holes_2.2mm.step`), which has millimetres built in.

### The screws don't fit the case holes
The original case has 1.6 mm holes. Print **`clawd_mochi_v1_holes_2.2mm.stl`** instead, which has 2.2 mm holes and is otherwise identical.
[case-and-assembly.md](case-and-assembly.md).
