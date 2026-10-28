' Clawd Mochi: PC locked -> close Mochi's eyes. Runs curl with no visible window.
Const MOCHI_IP = "192.168.137.50"   ' <-- CONFIG: Mochi's address (staBegin() in clawd_mochi.ino)
CreateObject("WScript.Shell").Run "curl.exe -s -m 4 --retry 3 --retry-delay 2 --retry-all-errors ""http://" & MOCHI_IP & "/notify?sleep=1""", 0, False
