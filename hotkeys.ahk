; ==========================================================================
; Глобальные хоткеи для управления лампочкой Яндекс
;
; 1. Поставь AutoHotkey (https://www.autohotkey.com/) - бесплатно, 1 минута
; 2. Отредактируй пути ниже (PYTHON_PATH и SCRIPT_PATH) под свою систему
; 3. Дважды кликни по этому файлу, чтобы хоткеи заработали
;    (можно закинуть ярлык в папку автозагрузки, чтобы работало всегда)
; ==========================================================================

PYTHON_PATH := "python"  ; если python не в PATH, укажи полный путь, например C:\Python312\python.exe
SCRIPT_PATH := "C:\Users\ИМЯ\yandex-light-control\toggle_light.py"  ; поменяй на свой путь
LIGHT_NAME  := "Лампочка"  ; часть названия устройства, как в приложении Яндекса

; Ctrl+Alt+L -> переключить лампочку (toggle)
^!l::
    RunWait, %PYTHON_PATH% "%SCRIPT_PATH%" toggle "%LIGHT_NAME%",, Hide
return

; Ctrl+Alt+O -> включить
^!o::
    RunWait, %PYTHON_PATH% "%SCRIPT_PATH%" on "%LIGHT_NAME%",, Hide
return

; Ctrl+Alt+P -> выключить
^!p::
    RunWait, %PYTHON_PATH% "%SCRIPT_PATH%" off "%LIGHT_NAME%",, Hide
return
