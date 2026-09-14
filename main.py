import sys

from PySide6.QtWidgets import QApplication, QWidget


class FileRiskAnalyzer(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("File Risk Analyzer")
        self.resize(900,600)
        self.setMinimumSize(700,450)

        self.setStyleSheet("""
            QWidget {
                background-color: #111827;
                color: #F9FAFB;
                font-family: "Segoe UI";
                font-size: 14px;
            }
        """)

if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = FileRiskAnalyzer()
    window.show()

    sys.exit(app.exec_())