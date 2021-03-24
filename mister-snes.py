#!/usr/bin/env python3
"""
MiSTer SNES Controller display based on retrospy

(c) 2021 Ryad-Marcel El-Dajani

License: MIT

To be honest, this script is really shitty and I just did it quick and
dirty on a free afternoon to simply show inputs on my SNES compatible
controller from my MiSTer FPGA. The client viewer from the
suggested application retrospy does not work properly on Linux based
operating systems to my knowledge.

Perhaps this script is useful for anybody out there, yet I cannot
imagine somebody would like to use it without a lot of refactoring etc.

However, this script requires a working SSH connection to the MiSTer and
the retrospy binary for MiSTer found at:

https://github.com/retrospy/RetroSpy/releases/latest/download/retrospy
Put this binary to: /media/fat/retrospy/retrospy
Just as you would with the retrospy installer.

This script will simply run the retrospy binary on the device using
a SSH subprocess to fetch the button state information. I suggest using
key-file authentication and the SSH agent to simplify the fetching
process.

Please run the retrospy binary directly on your device to test which
bits are switched depending on your controller. Most probably you will
have to adapt the self.buttons object in the MisterClient class based
on that information.
"""

import sys
import subprocess
import threading
from PyQt5.QtWidgets import QApplication, QWidget, QLabel
from PyQt5.QtGui import QIcon, QPixmap

# adapt following parameters if needed
ssh_host = "mister"
ssh_port = 22
username = "root"
command = "/media/fat/retrospy/retrospy /dev/input/js0"


class MisterClient(threading.Thread):
    def __init__(self, app):
        threading.Thread.__init__(self)
        self.killed = False
        # mapping of bit from retrospy to button in the gui
        # adapt according to your output in retrospy
        self.buttons = {
            16: app.a,
            17: app.b,
            19: app.x,
            20: app.y,
            22: app.l1,
            23: app.r1,
            26: app.select,
            27: app.start,
            160: app.r,
            174: app.l,
            192: app.d,
            206: app.u,
        }
        self.p = None

    def run(self):
        self.p = subprocess.Popen(
            ["ssh", "%s" % ssh_host, command],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        while self.p.poll() is None:
            for line_raw in self.p.stdout:
                line = line_raw.decode("ascii")
                for key, label in self.buttons.items():
                    if len(line) < 224: continue
                    label.setHidden(line[key] == "0")
    
    def kill(self):
        self.p.kill()

class App(QWidget):

    def __init__(self):
        super().__init__()
        self.title = "Mister SNES Controller"
        self.left = 10
        self.top = 10
        self.width = 640
        self.height = 480
        self.setStyleSheet("background-color: #00ffff;")
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        bgLabel = QLabel(self)
        bgImage = QPixmap("images/snes_controller.png")
        bgLabel.setPixmap(bgImage)

        aImg = QPixmap("images/a_pressed.png")
        self.a = QLabel(self)
        self.a.move(810, 209)
        self.a.setPixmap(aImg)
        self.a.setHidden(True)

        bImg = QPixmap("images/b_pressed.png")
        self.b = QLabel(self)
        self.b.move(718, 282)
        self.b.setPixmap(bImg)
        self.b.setHidden(True)

        xImg = QPixmap("images/x_pressed.png")
        self.x = QLabel(self)
        self.x.move(718, 139)
        self.x.setPixmap(xImg)
        self.x.setHidden(True)

        yImg = QPixmap("images/y_pressed.png")
        self.y = QLabel(self)
        self.y.move(625, 211)
        self.y.setPixmap(yImg)
        self.y.setHidden(True)

        startImg = QPixmap("images/s_pressed.png")
        self.start = QLabel(self)
        self.start.move(461, 247)
        self.start.setPixmap(startImg)
        self.start.setHidden(True)

        selectImg = QPixmap("images/s_pressed.png")
        self.select = QLabel(self)
        self.select.move(355, 246)
        self.select.setPixmap(selectImg)
        self.select.setHidden(True)

        l1Img = QPixmap("images/l_pressed.png")
        self.l1 = QLabel(self)
        self.l1.move(102, 31)
        self.l1.setPixmap(l1Img)
        self.l1.setHidden(True)

        r1Img = QPixmap("images/r_pressed.png")
        self.r1 = QLabel(self)
        self.r1.move(648, 31)
        self.r1.setPixmap(r1Img)
        self.r1.setHidden(True)

        uImg = QPixmap("images/up_pressed.png")
        self.u = QLabel(self)
        self.u.move(174, 164)
        self.u.setPixmap(uImg)
        self.u.setHidden(True)

        dImg = QPixmap("images/down_pressed.png")
        self.d = QLabel(self)
        self.d.move(174, 277)
        self.d.setPixmap(dImg)
        self.d.setHidden(True)

        lImg = QPixmap("images/left_pressed.png")
        self.l = QLabel(self)
        self.l.move(120, 219)
        self.l.setPixmap(lImg)
        self.l.setHidden(True)

        rImg = QPixmap("images/right_pressed.png")
        self.r = QLabel(self)
        self.r.move(232, 219)
        self.r.setPixmap(rImg)
        self.r.setHidden(True)

        self.resize(bgImage.width(), bgImage.height())
        self.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = App()
    client = MisterClient(ex)
    client.start()
    app.exec_()
    client.kill()
    sys.exit()
