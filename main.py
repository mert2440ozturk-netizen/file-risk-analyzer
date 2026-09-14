import sys

from pathlib import Path
from PySide6.QtCore import QThread, Signal, Slot, Qt
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

class DropArea(QLabel):
    file_dropped = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setAcceptDrops(True)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setMinimumHeight(130)
        self.setWordWrap(True)
        self.set_busy(False)

    def set_busy(self, busy):
        self.busy = busy
        self.setAcceptDrops(not busy)

        if busy:
            self.setText("Analysis in progress...")
        else:
            self.setText(
                "Drop one file here\n"
                "or use the button below"
            )

        self.update_appearance()

    def update_appearance(self, highlighted=False):
        border_color = "#60A5FA" if highlighted else "#475569"
        background = "#172554" if highlighted else "#1F2937"

        self.setStyleSheet(f"""
            QLabel {{
                background-color: {background};
                color: #CBD5E1;
                border: 2px dashed {border_color};
                border-radius: 12px;
                padding: 20px;
                font-size: 16px;
            }}
        """)

    def get_file_path(self, event):
        if self.busy or not event.mimeData().hasUrls():
            return None

        urls = event.mimeData().urls()

        if len(urls) != 1 or not urls[0].isLocalFile():
            return None

        file_path = urls[0].toLocalFile()

        try:
            if Path(file_path).is_file():
                return file_path
        except OSError:
            pass

        return None

    def dragEnterEvent(self, event):
        file_path = self.get_file_path(event)

        if file_path and (
            event.possibleActions() & Qt.DropAction.CopyAction
        ):
            event.setDropAction(Qt.DropAction.CopyAction)
            event.accept()
            self.update_appearance(highlighted=True)
        else:
            event.ignore()

    def dragLeaveEvent(self, event):
        self.update_appearance()
        event.accept()

    def dropEvent(self, event):
        file_path = self.get_file_path(event)
        self.update_appearance()

        if file_path and (
            event.possibleActions() & Qt.DropAction.CopyAction
        ):
            event.setDropAction(Qt.DropAction.CopyAction)
            event.accept()
            self.file_dropped.emit(file_path)
        else:
            event.ignore()

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

        self.drop_area = DropArea()
        self.drop_area.file_dropped.connect(self.start_analysis)

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
        layout.addWidget(self.drop_area)
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

        self.start_analysis(file_path)

    @Slot(str)
    def start_analysis(self, file_path):
        if self.worker is not None:
            return

        self.result_box.clear()
        self.select_button.setEnabled(False)
        self.drop_area.set_busy(True)
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
        self.drop_area.set_busy(False)

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