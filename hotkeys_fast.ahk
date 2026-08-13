; ==========================================================================
; Хоткеи для двух ламп "Main" - ОДИН запуск python на обе лампы (без задержки)
; ==========================================================================

BatPath := "C:\Users\kakty\IdeaProjects\yandex_smart_house\run_toggle.bat"

Main1 := "173b5445-ad1f-430c-8149-1902c0500f92"
Main2 := "6df3e8cb-b479-425a-864c-336654bf0d6f"

RunLightBoth(cmd) {
    global BatPath, Main1, Main2
    RunWait('"' BatPath '" ' cmd ' "' Main1 '" "' Main2 '"',, "Hide")
}

^!l::RunLightBoth("toggle")
^!o::RunLightBoth("on")
^!p::RunLightBoth("off")
