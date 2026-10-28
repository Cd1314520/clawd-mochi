' Clawd Mochi: PC unlocked -> wake Mochi up. More retries than lock: after the PC
' wakes from sleep the Windows hotspot can take several seconds to come back.
Const MOCHI_IP = "192.168.137.50"   ' <-- CONFIG: Mochi's address (staBegin() in clawd_mochi.ino)
CreateObject("WScript.Shell").Run "curl.exe -s -m 4 --retry 6 --retry-delay 3 --retry-all-errors ""http://" & MOCHI_IP & "/notify?sleep=0""", 0, False
