; ==========================================================================
; Хоткеи для двух ламп "Main" - версия с логом в файл
; ==========================================================================

PythonPath := "C:\Users\kakty\IdeaProjects\yandex_smart_house\.venv\Scripts\python.exe"
ScriptPath := "C:\Users\kakty\IdeaProjects\yandex_smart_house\toggle_light.py"

Main1 := "173b5445-ad1f-430c-8149-1902c0500f92"
Main2 := "6df3e8cb-b479-425a-864c-336654bf0d6f"

RunLight(cmd, id) {
    global PythonPath, ScriptPath
    logFile := "C:\Users\kakty\IdeaProjects\yandex_smart_house\hotkey_log.txt"
    RunWait('cmd /c ""' PythonPath '" "' ScriptPath '" ' cmd ' "' id '" >> "' logFile '" 2>&1"',, "Hide")
}

^!l::{
    RunLight("toggle", Main1)
    RunLight("toggle", Main2)
}

^!o::{
    RunLight("on", Main1)
    RunLight("on", Main2)
}

^!p::{
    RunLight("off", Main1)
    RunLight("off", Main2)
}