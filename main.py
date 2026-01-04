from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
import sys, os

sys.path.insert(0, os.path.join(os.getcwd(), "Everything_else"))

from ui.login_window import LoginWindow
from ui.main_window import GhostDriveMainWindow

# Global reference to prevent garbage collection
main_window = None

def launch_main(username, passphrase, fernet):
    global main_window
    main_window = GhostDriveMainWindow(username, passphrase, fernet)
    main_window.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)

    app.setWindowIcon(QIcon("Everything_else/viking.png"))

    login = LoginWindow(on_login_success=launch_main)
    login.show()
    sys.exit(app.exec())
