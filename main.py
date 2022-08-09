from pywinauto import application, ElementNotFoundError, Desktop, keyboard
from cproto import CProto
import time
import re


aws_training_chrome_command = "\"C:\Program Files\Google\Chrome\Application\chrome.exe\" --remote-debugging-port=9222 --profile-directory=\"Profile 1\""
aws_training_chrome_title_re = ".*- Google Chrome"



# Break time!
start_break_time = 10


def add_to_break_time(diff):
    global start_break_time
    start_break_time += diff
    state.set_named_buttons_up_face("break_time_100", {'label': f"{int(start_break_time / 100)}"})
    state.set_named_buttons_up_face("break_time_10", {'label': f"{int(start_break_time/10) % 10}"})
    state.set_named_buttons_up_face("break_time_1", {'label': f"{int(start_break_time/100) % 10}"})


def goto_break_page():
    state.load_page("break_page")


def get_window_titles():
    windows = Desktop(backend="uia").windows()
    return [w.window_text() for w in windows]


def chrome_activate_or_open_tab(url, url_regex):
    # foreground or start chrome!
    foreground_or_start_by_title(aws_training_chrome_title_re, aws_training_chrome_command)

    # activate the tab
    cp = CProto(host="127.0.0.1", port=9222)
    try:
        pages = list(filter(lambda t: t['type'] == "page", cp.Target.getTargets()['result']['targetInfos']))
        for page in pages:
            if re.match(url_regex, page['url']) is not None:
                cp.Target.activateTarget(targetId=page['targetId'])
                print("Page found and activated")
                return
        # open new page
        print("Open new tab")
        cp.Target.createTarget(url=url)
    finally:
        cp.close()


def foreground_or_start_by_title(title_re: str, command: str):
    # Try to connect!
    try:
        app = application.Application(backend="uia")
        app.connect(title_re=title_re)
        app.top_window().set_focus()
    except ElementNotFoundError:
        app = application.Application(backend="uia")
        app.start(command)
        app.top_window().set_focus()


def set_zoomit_timer(seconds):
    # Close zoom it if open
    try:
        app = application.Application(backend="uia")
        app.connect(title_re="Zoomit.*")
        window = app.top_window()
        window.click_input()
        keyboard.send_keys("{VK_ESCAPE}")
    except ElementNotFoundError:
        pass

    # Open it from the tray
    app = application.Application(backend="uia").connect(path="explorer.exe")
    sys_tray = app.window(class_name="Shell_TrayWnd")
    sys_tray.child_window(title="ZoomIt").click()
    time.sleep(0.25)
    keyboard.send_keys("o")
    time.sleep(0.25)

    app = application.Application(backend="uia")
    app.connect(title_re="ZoomIt.*")
    app.Dialog.BreakTabItem.click_input()
    app.Dialog['Timer:Edit'].set_text(f"{seconds}")
    app.Dialog.Ok.click()
    keyboard.send_keys("^3")
