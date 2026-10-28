# HTTP API

Mochi runs a plain HTTP server on port 80. Everything the web page does, a script can do with `curl`.

| Mochi is on… | Base URL |
| ------------ | -------- |
| its own hotspot `ClaWD-Mochi` | `http://192.168.4.1` |
| your network (STA mode) | `http://192.168.137.50` (static IP in `staBegin()`), or `http://clawdmochi.local` |

> **On Windows PowerShell 5.1, type `curl.exe`, not `curl`.** There, `curl` is an alias for `Invoke-WebRequest` and takes different arguments.
> The examples below use `curl.exe`. In Git Bash, macOS, or Linux, plain `curl` is fine.

> ⚠️ **No authentication.** Anyone on the same network can call every endpoint, including `/update`, which replaces the firmware.
> Keep Mochi on a network you trust (your PC's hotspot, or its own password-protected hotspot).

Unless noted otherwise, every endpoint replies `{"ok":1}` **before** it runs its animation, so the call returns right away.

---

## `/notify` — for scripts and hooks

`GET` or `POST`. This is the endpoint the Claude Code hooks and Windows scripts use.

| Parameter | Values | Effect |
| --------- | ------ | ------ |
| `view` | `w` · `s` · `d` | `w` normal eyes (wiggle + blink), `s` squish eyes `> <`, `d` the "Claude Code" title screen |
| `msg` | text | Opens the terminal view and types the text out. 15 columns × 8 rows, scrolls. Printable ASCII only; URL-encode spaces (`%20`) |
| `alert` | `good` · `bad` | Flashes the whole screen green (`good`) or red (`bad`) three times, then redraws the current view. Any other value counts as `good` |
| `breathe` | `1` · `0` | `1` pulses the backlight until the next interaction. `0` stops it |
| `sleep` | `1` · `0` | `1`: eyes shut, backlight fades to a slow, faint pulse. `0`: wake-up wiggle |
| `face` | `0`–`9` | Jump to one of the ten faces (values outside the range are clamped) |
| `bg` | `RRGGBB` | Background colour, hex **without** `#`. Applied first and combines with any other parameter |

**What wins when you send several at once** (straight from `routeNotify()`):

1. `bg` is always applied. `breathe` is set next.
2. If `sleep` is present, only the sleep/wake runs. Everything else except `bg`/`breathe` is ignored.
3. Else if `face` is present, only the face change runs.
4. Else **one** of `alert` › `msg` › `view` runs, in that order.
5. `alert`, `msg`, `view` and `face` all cancel breathing and sleep. So `breathe=1&view=s` ends up **not** breathing.

The ten faces:

| `face` | Look | `face` | Look |
| ------ | ---- | ------ | ---- |
| 0 | normal square eyes (blinks, glances) | 5 | heart eyes |
| 1 | squish `> <` (blinks) | 6 | dizzy `X X` |
| 2 | sleepy, half-lidded | 7 | angry slanted brows |
| 3 | surprised round eyes with a glint | 8 | suspicious side-eye |
| 4 | wink | 9 | content `∩ ∩` |

Examples:

```bash
curl.exe "http://192.168.137.50/notify?alert=good"
curl.exe "http://192.168.137.50/notify?msg=build%20passed"
curl.exe "http://192.168.137.50/notify?face=5&bg=1e3a8a"
curl.exe "http://192.168.137.50/notify?sleep=1"
```

---

## `/state`

`GET` → current state as JSON:

```json
{"view":0,"busy":false,"term":false,"bl":true,"speed":1}
```

| Field | Meaning |
| ----- | ------- |
| `view` | `0` eyes, `1` squish eyes, `2` Claude Code / terminal, `3` canvas |
| `busy` | an animation is running |
| `term` | terminal mode is on |
| `bl` | backlight on/off (the web page's display toggle) |
| `speed` | animation speed, `1` slow · `2` normal · `3` fast |

It does **not** report the IP address, the face number, or whether Mochi is asleep or breathing.
To find the IP, read it off the boot screen or the serial monitor. `/state` is a cheap "are you alive?" check, and the watchdog uses it for exactly that.

---

## `/update` — wireless firmware update

`POST`, multipart form, one file field (any name). The file is the compiled `.bin`.

```bash
curl.exe --limit-rate 24k -F "f=@clawd_mochi.ino.bin" http://192.168.137.50/update
```

- **`--limit-rate 24k` is required.** Without it, flash writes block the Wi-Fi stack and the upload dies around 100–200 KB.
- The screen shows `updating...`. On success Mochi reboots right away.
- **`curl: (52) Empty reply from server` usually means it worked**: Mochi rebooted before finishing the reply. Wait ~10 s and run `curl.exe http://<ip>/state`. If you get JSON back, you're on the new firmware.
- If the upload breaks halfway, the firmware aborts the update and redraws the screen. Just run the command again.

How to get the `.bin`: see [README step 7](../README.md#7-optional-wireless-updates).

---

## Endpoints the web page uses

You can call these too.

| Endpoint | Parameters | Effect |
| -------- | ---------- | ------ |
| `GET /` | — | The web controller page |
| `GET /cmd` | `k=w` · `s` · `d` · `a` · `q` | `w` normal eyes, `s` squish eyes, `d` Claude Code view + terminal mode, `a` replay the logo animation, `q` leave terminal mode. In terminal mode only `q` does anything. Any `/cmd` also stops breathing and wakes Mochi. Missing `k` → `400 {"e":1}` |
| `GET /char` | `c=<one char>` | Types one character in terminal mode (ignored otherwise). `%0A` newline, `%08` backspace |
| `GET /speed` | `v=1` · `2` · `3` | Animation speed slow / normal / fast |
| `GET /redraw` | `bg=<hex>` | Sets the background colour and redraws the current view. `#` is optional; send it as `%23` |
| `GET /canvas` | `on=1` | Enters canvas mode (fills the screen with the canvas colour). `on=0` does nothing on the device |
| `GET /draw/clear` | `bg=<hex>` (default `#aa4818`) | Clears the canvas to that colour |
| `GET /draw/stroke` | `pen=RRGGBB`, `pts=x,y;x,y;…` | Draws a polyline in screen pixels (0–239) |
| `GET /backlight` | `on=1` · `0` | Backlight on / off |

Colours that aren't 6 hex digits are drawn as white. Unknown paths return `404 not found`.

---

## Things the firmware does on its own

- **Idle life:** on the eye views, Mochi blinks or glances every 2.5–7 s, and switches to a random face every 2–6 min (`FACE_MIN_MS`, `FACE_RND_MS`). Not while in the terminal, canvas, or asleep.
- **Night dimming:** from 00:00 to 08:00 the backlight drops to 25/255 (`NIGHT_UNTIL`, `NIGHT_DUTY`). This needs the clock, which comes from NTP, so it only works when Mochi's network has internet. On its own hotspot it never dims. Time zone is US Central (`TZ_STRING`); change it for yours.
- **Wi-Fi self-heal (STA mode):** checks every 10 s and rejoins when the network comes back. If it had fallen back to its own hotspot at boot, it keeps that hotspot up while it retries.
- **Self-wake:** if Mochi is asleep and the network has been gone for 10+ minutes, it wakes up by itself, so it doesn't sit there looking dead when the "wake" command can't reach it.
