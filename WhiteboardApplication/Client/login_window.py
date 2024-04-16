import sys
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton

from PySide6.QtGui import QFont


class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Login")

        # Set the initial size of the window
        self.resize(400, 200)  # Adjust the width and height as needed

        main_layout = QVBoxLayout()

        # Username Label and Input
        username_layout = QHBoxLayout()
        self.username_label = QLabel("Username:")
        username_font = QFont()  # Create a QFont object
        username_font.setPointSize(14)  # Set the font size
        self.username_label.setFont(username_font)  # Apply the font to the label
        self.username_input = QLineEdit()
        self.username_input.setFixedHeight(30)  # Set the height of the input box
        username_layout.addWidget(self.username_label)
        username_layout.addWidget(self.username_input)

        # Password Label and Input
        password_layout = QHBoxLayout()
        self.password_label = QLabel("Password:")
        password_font = QFont()  # Create a QFont object
        password_font.setPointSize(14)  # Set the font size
        self.password_label.setFont(password_font)  # Apply the font to the label
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setFixedHeight(30)  # Set the height of the input box
        password_layout.addWidget(self.password_label)
        password_layout.addSpacing(5)
        password_layout.addWidget(self.password_input)

        main_layout.addLayout(username_layout)
        main_layout.addLayout(password_layout)

        # Login Button
        self.login_button = QPushButton("Login")
        self.login_button.clicked.connect(self.login)
        self.login_button.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; padding: 10px 20px; font-size: 16px; }")

        main_layout.addWidget(self.login_button)

        self.setLayout(main_layout)

    def login(self):
        username = self.username_input.text()
        password = self.password_input.text()
        # You can add your login authentication logic here
        print("Username:", username)
        print("Password:", password)
        # For simplicity, let's close the window after login attempt
        self.close()

    def login(self):
        username = self.username_input.text()
        password = self.password_input.text()
        # You can add your login authentication logic here
        print("Username:", username)
        print("Password:", password)
        # For simplicity, let's close the window after login attempt
        self.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    login_window = LoginWindow()
    login_window.show()
    sys.exit(app.exec())
