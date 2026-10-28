"""Watches the mochi. If it goes unreachable, restarts the Windows mobile
hotspot (WinRT tethering) and wakes the device back to normal view.

ponytail: stdlib only (urllib + subprocess), no pip installs needed.
Run it, leave the window open while you want mochi alive; Ctrl+C or close
the window to stop (which also lets you kill the hotspot to save bandwidth
again without me babysitting it).
"""
import subprocess
import time
import urllib.request

IP = "192.168.137.50"  # <-- CONFIG: Mochi's address (staBegin() in clawd_mochi.ino)
POLL_SEC = 10
TIMEOUT = 3

HOTSPOT_PS = r"""
Add-Type -AssemblyName System.Runtime.WindowsRuntime
$m = ([System.WindowsRuntimeSystemExtensions].GetMethods() | Where-Object { $_.Name -eq 'AsTask' -and $_.GetParameters().Count -eq 1 -and $_.GetParameters()[0].ParameterType.Name -eq 'IAsyncOperation`1' })[0]
function Await($t, $r) {
    $task = $m.MakeGenericMethod($r).Invoke($null, @($t))
    $task.Wait(-1) | Out-Null
    $task.Result
}
[Windows.Networking.Connectivity.NetworkInformation,Windows.Networking.Connectivity,ContentType=WindowsRuntime] | Out-Null
[Windows.Networking.NetworkOperators.NetworkOperatorTetheringManager,Windows.Networking.NetworkOperators,ContentType=WindowsRuntime] | Out-Null
$profile = [Windows.Networking.Connectivity.NetworkInformation]::GetInternetConnectionProfile()
$manager = [Windows.Networking.NetworkOperators.NetworkOperatorTetheringManager]::CreateFromConnectionProfile($profile)
if ($manager.TetheringOperationalState -ne 'On') {
    $op = $manager.StartTetheringAsync()
    Await $op ([Windows.Networking.NetworkOperators.NetworkOperatorTetheringOperationResult]) | Out-Null
}
"""


def alive():
    try:
        urllib.request.urlopen(f"http://{IP}/state", timeout=TIMEOUT)
        return True
    except Exception:
        return False


def start_hotspot():
    subprocess.run(["powershell", "-NoProfile", "-Command", HOTSPOT_PS], capture_output=True)


def wake():
    try:
        urllib.request.urlopen(f"http://{IP}/cmd?k=w", timeout=TIMEOUT)
    except Exception:
        pass


def main():
    was_down = False
    print(f"watching {IP} every {POLL_SEC}s... (Ctrl+C to stop)")
    while True:
        if alive():
            if was_down:
                wake()
                print("mochi back online, woken")
                was_down = False
        else:
            was_down = True
            print("mochi unreachable, restarting hotspot...")
            start_hotspot()
            time.sleep(5)
            if alive():
                wake()
                print("recovered")
            else:
                print("still down, will retry")
        time.sleep(POLL_SEC)


if __name__ == "__main__":
    main()
