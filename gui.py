# gui.py - PyQt5 UI for QuietPatch outputs
import json
import sys

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QApplication,
    QComboBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from src.config.encryptor_new import decrypt_file

SEVERITY_ORDER = {"critical": 4, "high": 3, "medium": 2, "low": 1, "none": 0, "unknown": -1}


class QuietPatchGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("QuietPatch – CVE Viewer")
        self.resize(1100, 680)
        self.data = []
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Controls
        top = QHBoxLayout()
        self.open_btn = QPushButton("Open vuln_log.json.enc")
        self.search = QLineEdit()
        self.search.setPlaceholderText("Search app or CVE...")
        self.sev = QComboBox()
        self.sev.addItems(["all", "critical", "high", "medium", "low", "none", "unknown"])
        self.export_btn = QPushButton("Export CSV")

        top.addWidget(self.open_btn)
        top.addWidget(QLabel("Filter:"))
        top.addWidget(self.search)
        top.addWidget(QLabel("Severity ≥"))
        top.addWidget(self.sev)
        top.addWidget(self.export_btn)
        layout.addLayout(top)

        # Table
        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(
            ["App", "Version", "CVE", "CVSS", "Severity", "Summary"]
        )
        self.table.setSortingEnabled(True)
        layout.addWidget(self.table)

        # Events
        self.open_btn.clicked.connect(self.load_file)
        self.search.textChanged.connect(self.refresh)
        self.sev.currentTextChanged.connect(self.refresh)
        self.export_btn.clicked.connect(self.export_csv)

    def load_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select encrypted vuln file", "", "Encrypted JSON (*.enc);;All Files (*)"
        )
        if not path:
            return
        raw = decrypt_file(path)
        try:
            self.data = json.loads(raw.decode())
        except Exception:
            self.data = []
        self.refresh()

    def passes_filters(self, app_row, sev_min):
        # app_row is dict with vulnerabilities list
        q = self.search.text().lower().strip()
        if q and q not in app_row["app"].lower():
            # also search inside CVE ids and summaries
            if not any(
                q in (v.get("cve_id", "") or "").lower()
                or q in (v.get("summary", "") or "").lower()
                for v in app_row["vulnerabilities"]
            ):
                return False
        if sev_min == "all":
            return True
        min_rank = SEVERITY_ORDER[sev_min]
        # keep rows that have any vuln >= min
        for v in app_row["vulnerabilities"]:
            if SEVERITY_ORDER.get(v.get("severity", "unknown"), -1) >= min_rank:
                return True
        return False

    def refresh(self):
        sev_min = self.sev.currentText()
        rows = []
        for app in self.data:
            if not self.passes_filters(app, sev_min):
                continue
            for v in app.get("vulnerabilities", []):
                rows.append(
                    [
                        app.get("app", ""),
                        app.get("version", ""),
                        v.get("cve_id", ""),
                        str(v.get("cvss", "")),
                        v.get("severity", ""),
                        (v.get("summary", "") or "")[:300],
                    ]
                )

        # sort by severity then cvss descending by default
        def sort_key(r):
            sev = r[4]
            try:
                cvss = float(r[3])
            except Exception:
                cvss = -1
            return (SEVERITY_ORDER.get(sev, -1), cvss)

        rows.sort(key=sort_key, reverse=True)

        self.table.setRowCount(0)
        for r in rows:
            i = self.table.rowCount()
            self.table.insertRow(i)
            for c, val in enumerate(r):
                item = QTableWidgetItem(val)
                if c in (3, 4):  # center cvss and severity
                    item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(i, c, item)

    def export_csv(self):
        if self.table.rowCount() == 0:
            return
        path, _ = QFileDialog.getSaveFileName(
            self, "Export CSV", "quietpatch_vulns.csv", "CSV Files (*.csv)"
        )
        if not path:
            return
        import csv

        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            headers = [
                self.table.horizontalHeaderItem(i).text() for i in range(self.table.columnCount())
            ]
            w.writerow(headers)
            for r in range(self.table.rowCount()):
                w.writerow(
                    [
                        self.table.item(r, c).text() if self.table.item(r, c) else ""
                        for c in range(self.table.columnCount())
                    ]
                )


def main():
    app = QApplication(sys.argv)
    gui = QuietPatchGUI()
    gui.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
