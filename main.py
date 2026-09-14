import sys

from PySide6.QtCore import QThread, Signal, Slot
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QFileDialog,
    QPlainTextEdit,
)

from analyzer import analyze_file


class AnalysisWorker(QThread):
    result_ready = Signal(dict)
    analysis_failed = Signal(str)

    def __init__(self, file_path, parent=None):
        super().__init__(parent)
        self.file_path = file_path

    def run(self):
        try:
            result = analyze_file(self.file_path)
            self.result_ready.emit(result)
        except Exception as error:
            self.analysis_failed.emit(
                f"{type(error).__name__}: {error}"
            )


class FileRiskAnalyzer(QWidget):
    def __init__(self):
        super().__init__()

        self.worker = None

        self.setWindowTitle("File Risk Analyzer")
        self.resize(900, 600)
        self.setMinimumSize(700, 450)

        self.setStyleSheet("""
            QWidget {
                background-color: #111827;
                color: #F9FAFB;
                font-family: "Segoe UI";
                font-size: 14px;
            }

            QLabel#title {
                font-size: 28px;
                font-weight: bold;
            }

            QPushButton {
                background-color: #2563EB;
                border: none;
                border-radius: 8px;
                padding: 12px 20px;
            }

            QPushButton:hover {
                background-color: #1D4ED8;
            }

            QPushButton:disabled {
                background-color: #374151;
                color: #9CA3AF;
            }

            QPlainTextEdit {
                background-color: #1F2937;
                border: 1px solid #374151;
                border-radius: 8px;
                padding: 12px;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(16)

        title = QLabel("File Risk Analyzer")
        title.setObjectName("title")

        description = QLabel(
            "Basic file checks. A low score does not guarantee safety."
        )
        description.setWordWrap(True)

        self.select_button = QPushButton("Select file and analyze")
        self.select_button.clicked.connect(self.select_file)

        self.status_label = QLabel("Ready.")

        self.result_box = QPlainTextEdit()
        self.result_box.setReadOnly(True)
        self.result_box.setPlaceholderText(
            "Analysis results will appear here."
        )

        layout.addWidget(title)
        layout.addWidget(description)
        layout.addWidget(self.select_button)
        layout.addWidget(self.status_label)
        layout.addWidget(self.result_box, 1)

    @Slot()
    def select_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select a file to analyze",
        )

        if not file_path:
            return

        self.result_box.clear()
        self.select_button.setEnabled(False)
        self.status_label.setText("Analyzing...")

        self.worker = AnalysisWorker(file_path, self)
        self.worker.result_ready.connect(self.show_result)
        self.worker.analysis_failed.connect(self.show_error)
        self.worker.finished.connect(self.analysis_finished)
        self.worker.start()

    @Slot(dict)
    def show_result(self, result):
        score = result["risk_score"]
        score_text = "Not scored" if score is None else f"{score}/5"

        status_labels = {
            "basic_checks_only": "Basic checks only",
            "limited": "Limited assessment",
        }

        assessment = status_labels.get(
            result["assessment_status"],
            result["assessment_status"],
        )

        lines = [
            f"Name: {result['name']}",
            f"Extension: {result['extension'] or '(none)'}",
            f"Size: {result['size_bytes']:,} bytes",
            f"Detected type (signature): {result['detected_type']}",
            f"SHA-256: {result['sha256']}",
            "",
            f"Rule-based risk score: {score_text}",
            f"Assessment: {assessment}",
            "",
            "Findings:",
        ]

        if result["findings"]:
            for finding in result["findings"]:
                lines.append(
                    f"- [{finding['severity']}] {finding['message']}"
                )
        else:
            lines.append("- No findings under the applied rules.")

        self.result_box.setPlainText("\n".join(lines))
        self.status_label.setText("Analysis completed.")

    @Slot(str)
    def show_error(self, message):
        self.result_box.setPlainText(
            f"Analysis could not be completed:\n{message}"
        )
        self.status_label.setText("Analysis failed.")

    @Slot()
    def analysis_finished(self):
        self.worker.deleteLater()
        self.worker = None
        self.select_button.setEnabled(True)

    def closeEvent(self, event):
        if self.worker is not None:
            self.status_label.setText(
                "Analysis is finishing. Please close the window afterward."
            )
            event.ignore()
        else:
            event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = FileRiskAnalyzer()
    window.show()

    sys.exit(app.exec())