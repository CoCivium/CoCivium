#Requires AutoHotkey v2.0
#SingleInstance Force
; This is OFF until manually launched, and handles only the explicit key chord.
; A Logitech gesture may later be mapped to Ctrl+Alt+Shift+F12 in Options+.
; Do not uncomment XButton bindings until the physical input is identified.
; No silent clipboard capture, no synthetic paste, no provider calls.

^!+F12::{
    path := FileSelect(1, , "Choose one file for a LOCAL CoThumb capsule", "All files (*.*)")
    if !path
        return
    script := A_ScriptDir "\cothumb.py"
    output := A_ScriptDir "\capsules"
    ; Windows filenames cannot contain double quotes. A user-selected file is
    ; an explicit, bounded input. The local file is NOT transmitted.
    command := 'py -3 "' script '" capture --file "' path '" --output-dir "' output '" --origin EXPLICIT_FILE_SELECTION --verify-local'
    try {
        exitCode := RunWait(command, A_ScriptDir)
        if (exitCode = 0)
            MsgBox("Local capsule created and locally checked. Check `n" output "`nNo information was sent.", "CoThumb: local proof")
        else
            MsgBox("Capture held; exit " exitCode ". Check the local console for details.", "CoThumb: HOLD")
    } catch as err {
        MsgBox("Could not invoke Python 3. No device binding has been made. " err.Message, "CoThumb: HOLD")
    }
}
; For verified hardware configuration only, add an OPTIONAL *different* hotkey
; after confirming the precise emitted event, collision and rollback behavior.
