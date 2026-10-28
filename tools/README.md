# tools/

Optional PC-side helpers. Mochi works without any of them. All of them were written and used on **Windows 11** only.

Every file has Mochi's address hard-coded as `192.168.137.50`, marked with `CONFIG`.
That is the static IP the firmware takes when it joins a Windows mobile hotspot
(`staBegin()` in [`clawd_mochi.ino`](../clawd_mochi/clawd_mochi.ino)). If yours is different, change it in every file you use.

| File | What it does | Guide |
| ---- | ------------ | ----- |
| `claude-code-hooks.example.json` | Makes Mochi react to Claude Code: squint when done, red flash on a failed tool, breathing backlight while waiting for you | [docs/claude-code-hooks.md](../docs/claude-code-hooks.md) |
| `mochi_lock.vbs`, `mochi_unlock.vbs` | Send `sleep=1` / `sleep=0` to Mochi without flashing a console window | below |
| `task_sleep.xml`, `task_wake.xml` | Task Scheduler definitions that run the two scripts when you lock / unlock Windows | below |
| `mochi_watchdog.py` | Polls Mochi every 10 s; if it's unreachable, turns the Windows mobile hotspot back on and wakes Mochi | below |

---

## Lock / unlock sync

**What it does:** you lock the PC (Win + L), Mochi closes its eyes and its backlight fades into a slow, faint pulse. You unlock it, Mochi wiggles awake.

**Install** (PowerShell, from the repo root):

1. Open both `.vbs` files and set `MOCHI_IP` if yours isn't `192.168.137.50`.
2. Copy the scripts to the folder the tasks expect:
   ```powershell
   New-Item -ItemType Directory -Force "$env:LOCALAPPDATA\ClawdMochi"
   Copy-Item tools\mochi_lock.vbs, tools\mochi_unlock.vbs "$env:LOCALAPPDATA\ClawdMochi\"
   ```
3. Test a script by hand. Mochi should close its eyes:
   ```powershell
   wscript "$env:LOCALAPPDATA\ClawdMochi\mochi_lock.vbs"
   ```
4. Register the tasks. **Use an Administrator PowerShell window.** A normal window got `Access is denied` on the original build:
   ```powershell
   Register-ScheduledTask -TaskName "ClawdMochi Sleep" -Xml (Get-Content -Raw tools\task_sleep.xml)
   Register-ScheduledTask -TaskName "ClawdMochi Wake"  -Xml (Get-Content -Raw tools\task_wake.xml)
   ```
5. Press Win + L. Mochi should fall asleep. Log back in and it wakes up.

> The original tasks were registered through the Task Scheduler COM API with absolute paths. The `%LOCALAPPDATA%` paths and the
> `Register-ScheduledTask` commands above do the same thing but were not re-run on the original machine. If a task runs and nothing
> happens, open Task Scheduler → the task → Actions and replace `%LOCALAPPDATA%` with the full path
> (`C:\Users\<you>\AppData\Local`).

**Remove:**
```powershell
Unregister-ScheduledTask -TaskName "ClawdMochi Sleep" -Confirm:$false
Unregister-ScheduledTask -TaskName "ClawdMochi Wake"  -Confirm:$false
Remove-Item -Recurse "$env:LOCALAPPDATA\ClawdMochi"
```

---

## Hotspot watchdog

**What it does:** Windows mobile hotspot sometimes switches itself off (see [Known issues](../README.md#known-issues)), and Mochi
drops off the network with it. While this script is running, it checks `http://<MOCHI_IP>/state` every 10 seconds. If Mochi doesn't answer, the script
restarts the hotspot through the WinRT tethering API and sends Mochi back to its normal face once it's reachable again.

Only useful if Mochi is connected to your **PC's mobile hotspot**. It does nothing for a home router.

**Install:** needs Python 3. Standard library only, no `pip install`.
```powershell
python tools\mochi_watchdog.py
```
Leave the window open. It prints `mochi unreachable, restarting hotspot...` / `recovered` as it works.
The hotspot restart needs the PC itself to have an internet connection, since Windows shares that connection.

**Remove:** Ctrl + C or close the window. Nothing is installed.

> It is not started automatically. A Scheduled Task to auto-restart the hotspot at unlock was drafted but never registered,
> so it isn't included here.
