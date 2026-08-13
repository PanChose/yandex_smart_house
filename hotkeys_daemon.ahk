; ==========================================================================
; Хоткеи для ламп "Main" через фоновый демон (daemon.py) - минимальная задержка.
; Требует, чтобы daemon.py уже был запущен (см. run_daemon.bat).
; ==========================================================================

CallDaemon(cmd) {
    http := ComObject("WinHttp.WinHttpRequest.5.1")
    try {
        http.Open("GET", "http://127.0.0.1:8765/" cmd, false)
        http.Send()
    } catch as e {
        MsgBox("Демон не отвечает. Убедись, что daemon.py запущен.`n" e.Message)
    }
}

^!l::CallDaemon("toggle")
^!o::CallDaemon("on")
^!p::CallDaemon("off")
