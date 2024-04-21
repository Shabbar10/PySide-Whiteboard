from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QLineEdit,
    QPushButton)

from PySide6.QtGui import (
    QPalette,
    QColor,
    QLinearGradient)

from PySide6.QtGui import QFont

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Login")

        # Setting window size
        self.setFixedSize(450, 275)

        # Setting the gradient
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0.0, QColor(135, 206, 235))  # Light blue color at the top
        gradient.setColorAt(1.0, QColor(65, 105, 225))  # Royal blue color at the bottom

        # Set the gradient as the background
        palette = self.palette()
        palette.setBrush(QPalette.Window, gradient)
        self.setPalette(palette)


        layout = QVBoxLayout()

        # Username Section
        self.username_input = QLineEdit()
        self.username_input.setFixedHeight(50)
        self.username_input.setPlaceholderText("Username")  # Set placeholder text for username input box
        self.username_input.setFont(QFont("Arial", 12))  # Set custom font for the input text
        self.username_input.setStyleSheet("QLineEdit { padding: 10px 20px; margin-left: 30px; margin-right: 30px;}") # Set margin and padding
        layout.addWidget(self.username_input)

        # Password Section
        self.password_input = QLineEdit()
        self.password_input.setFixedHeight(50)
        self.password_input.setPlaceholderText("Password")  # Set placeholder text for password input box
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password) # Setting to password mode to display dots
        self.password_input.setFont(QFont("Arial", 12))  # Set custom font for the input text
        self.password_input.setStyleSheet("QLineEdit { padding: 10px 20px; margin-left: 30px; margin-right: 30px;}") # Set margin and padding
        layout.addWidget(self.password_input)

        # Login Button
        self.login_button = QPushButton("LOGIN")
        self.login_button.setFixedHeight(50)
        self.login_button.clicked.connect(self.login) # Connecting it to login function
        self.login_button.setStyleSheet(
            "QPushButton { background-color: #4CAF50; color: white; padding: 10px 20px; font-size: 20px; margin-left: 30px; margin-right: 30px; font-weight: bold;}" )# Styling the button
        layout.addWidget(self.login_button)

        self.setLayout(layout)

    def login(self):
        username = self.username_input.text()
        password = self.password_input.text()
        print("Username:", username)
        print("Password:", password)
        self.close()


if __name__ == "__main__":
    app = QApplication([])
    login_window = LoginWindow()
    login_window.show()
    app.exec()