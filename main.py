from pywinauto import application
from cproto import CProto
import re


def activate_or_open_tab(url, url_regex):
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


def foreground_training_chrome():
    app = application.Application(backend="uia")
    app.connect(title_re=".*(AWS Training).*")
    app.top_window().set_focus()
    activate_or_open_tab("https://google.com", ".*google.com.*")
