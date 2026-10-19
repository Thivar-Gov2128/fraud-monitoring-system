# ================= IMPORTS =================
import sys

from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QTableWidgetItem, QMessageBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QFont

from qfluentwidgets import (
    FluentWindow, TableWidget, LineEdit, ComboBox,
    PrimaryPushButton, CardWidget, ToggleButton,
    setTheme, Theme, FluentIcon as FIF
)

from database import get_transactions


# ================= FRAUD LOGIC =================
def analyze(tx):

    amount = float(tx[5])

    if amount > 30000:
        return "FRAUD", "High Amount"

    elif amount > 20000:
        return "RISK", "Large Transaction"

    return "OK", "Normal Activity"

# ================= LOGIN =================
class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Login")
        self.resize(350, 250)

        layout = QVBoxLayout()

        title = QLabel("🔐 Login")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size:22px; font-weight:bold;")

        self.user = LineEdit()
        self.user.setPlaceholderText("Username")

        self.pwd = LineEdit()
        self.pwd.setPlaceholderText("Password")
        self.pwd.setEchoMode(LineEdit.Password)

        btn = PrimaryPushButton("Login")
        btn.clicked.connect(self.login)

        layout.addStretch()
        layout.addWidget(title)
        layout.addWidget(self.user)
        layout.addWidget(self.pwd)
        layout.addWidget(btn)
        layout.addStretch()

        self.setLayout(layout)

    def login(self):
        if self.user.text() == "admin" and self.pwd.text() == "admin":
            self.dashboard = Dashboard()
            self.dashboard.show()
            self.close()
        else:
            QMessageBox.warning(self, "Error", "Invalid credentials")


# ================= DASHBOARD =================
class Dashboard(FluentWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Quantum Fraud Monitor")
        self.resize(1400, 800)

        self.transactions = []
        self.filtered = []
        self.alerts = []
        self.incidents = []

        self.dark_mode = True
        setTheme(Theme.DARK)

        self.init_ui()
        self.load_data()

    def init_ui(self):

        self.dashboard_page = QWidget()
        self.dashboard_page.setObjectName("dashboard_page")
        layout = QVBoxLayout(self.dashboard_page)

        # ===== HEADER =====
        top = QHBoxLayout()

        title = QLabel("⚡ Quantum Fraud Monitor")
        title.setStyleSheet("font-size:26px; font-weight:bold; color:#38bdf8;")

        self.toggle = ToggleButton()
        self.toggle.setChecked(True)
        self.toggle.clicked.connect(self.toggle_theme)

        top.addWidget(title)
        top.addStretch()
        top.addWidget(QLabel("Dark Mode"))
        top.addWidget(self.toggle)

        layout.addLayout(top)

        # ===== FILTERS =====
        fl = QHBoxLayout()

        icon = QLabel()
        icon.setPixmap(FIF.SEARCH.icon().pixmap(16, 16))

        self.search = LineEdit()
        self.search.setPlaceholderText("Search")
        self.search.textChanged.connect(self.apply_filters)

        self.status = ComboBox()
        self.status.addItems(["ALL", "FRAUD", "RISK", "OK"])
        self.status.currentIndexChanged.connect(self.apply_filters)

        self.limit = ComboBox()
        self.limit.addItems(["10", "50", "100", "500", "1000", "ALL"])
        self.limit.currentIndexChanged.connect(self.apply_filters)

        fl.addWidget(icon)
        fl.addWidget(self.search)
        fl.addWidget(self.status)
        fl.addWidget(self.limit)

        layout.addLayout(fl)

        # ===== KPI =====
        k = QHBoxLayout()

        def card(title, color):
            c = CardWidget()
            l = QLabel(f"{title}\n0")
            l.setAlignment(Qt.AlignCenter)
            l.setStyleSheet(f"color:{color}; font-weight:bold;")
            QVBoxLayout(c).addWidget(l)
            return c, l

        self.tot, self.kt = card("TOTAL", "#38bdf8")
        self.fr, self.kf = card("FRAUD", "#ef4444")
        self.rs, self.kr = card("RISK", "#f59e0b")
        self.ok, self.ko = card("SAFE", "#10b981")

        for c in [self.tot, self.fr, self.rs, self.ok]:
            k.addWidget(c)

        layout.addLayout(k)

        # ===== TABLE =====
        self.table = TableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(
            ["ID", "Customer", "Amount", "Type", "Status", "Reason"]
        )

        layout.addWidget(self.table)

        self.addSubInterface(self.dashboard_page, "dashboard", "Dashboard")

        # ===== ALERTS =====
        self.alerts_page = QWidget()
        self.alerts_page.setObjectName("alerts_page")
        al = QVBoxLayout(self.alerts_page)

        al_title = QLabel("🚨 Alerts")
        al_title.setStyleSheet("font-size:20px; font-weight:bold;")

        self.alert_table = TableWidget()
        self.alert_table.setColumnCount(3)
        self.alert_table.setHorizontalHeaderLabels(
            ["ID", "Customer", "Amount"]
        )

        al.addWidget(al_title)
        al.addWidget(self.alert_table)

        self.addSubInterface(self.alerts_page, "alerts", "Alerts")

        # ===== INCIDENTS =====
        self.inc_page = QWidget()
        self.inc_page.setObjectName("inc_page")
        il = QVBoxLayout(self.inc_page)

        inc_title = QLabel("🛠 Incidents")
        inc_title.setStyleSheet("font-size:20px; font-weight:bold;")

        self.inc_table = TableWidget()
        self.inc_table.setColumnCount(5)
        self.inc_table.setHorizontalHeaderLabels(
            ["ID", "Customer", "Amount", "Status", "Owner"]
        )

        self.stat = ComboBox()
        self.stat.addItems(["OPEN", "INVESTIGATING", "RESOLVED"])

        self.owner = LineEdit()

        btn = PrimaryPushButton("Update")
        btn.clicked.connect(self.update_inc)

        il.addWidget(inc_title)
        il.addWidget(self.inc_table)
        il.addWidget(self.stat)
        il.addWidget(self.owner)
        il.addWidget(btn)

        self.addSubInterface(self.inc_page, "inc", "Incidents")

        # ===== AUDIT LOGS =====

        self.audit_page = QWidget()
        self.audit_page.setObjectName("audit_page")

        audit_layout = QVBoxLayout(self.audit_page)

        audit_title = QLabel("📋 Audit Logs")
        audit_title.setStyleSheet("font-size:20px; font-weight:bold;")

        self.audit_table = TableWidget()

        self.audit_table.setColumnCount(1)

        self.audit_table.setHorizontalHeaderLabels(["Log Entry"])

        self.audit_table.setColumnWidth(0, 1200)

        audit_layout.addWidget(audit_title)
        audit_layout.addWidget(self.audit_table)

        self.addSubInterface(self.audit_page, "audit", "Audit Logs")


    def toggle_theme(self):
        self.dark_mode = not self.dark_mode
        setTheme(Theme.DARK if self.dark_mode else Theme.LIGHT)

    def load_data(self):
        self.transactions = get_transactions()
        self.apply_filters()
        self.load_audit_logs()

    def apply_filters(self):
        s = self.search.text().lower()
        f = self.status.currentText()
        lim = self.limit.currentText()

        max_r = len(self.transactions) if lim == "ALL" else int(lim)

        self.filtered = []
        self.alerts = []

        for tx in self.transactions:
            lvl, reason = analyze(tx)

            if s and s not in str(tx[0]).lower() and s not in str(tx[2]).lower():
                continue

            if f != "ALL" and lvl != f:
                continue

            self.filtered.append((tx, lvl, reason))

            if lvl == "FRAUD":
                self.alerts.append(tx)

                if not any(i["id"] == tx[0] for i in self.incidents):
                    self.incidents.append({
                        "id": tx[0],
                        "customer": tx[2],
                        "amount": tx[5],
                        "status": "OPEN",
                        "owner": ""
                    })

        self.filtered = self.filtered[:max_r]
        self.update_ui()

    def update_ui(self):

        self.table.setRowCount(len(self.filtered))

        for r, (tx, lvl, reason) in enumerate(self.filtered):

            self.table.setItem(r, 0, QTableWidgetItem(str(tx[0])))
            self.table.setItem(r, 1, QTableWidgetItem(str(tx[2])))
            self.table.setItem(r, 2, QTableWidgetItem(str(tx[5])))
            self.table.setItem(r, 3, QTableWidgetItem(str(tx[4])))

            st = QTableWidgetItem(f"● {lvl}")

            if lvl == "FRAUD":
                st.setForeground(QColor("#ef4444"))
                bg = QColor(50, 20, 20)
            elif lvl == "RISK":
                st.setForeground(QColor("#f59e0b"))
                bg = QColor(50, 40, 10)
            else:
                st.setForeground(QColor("#10b981"))
                bg = QColor(20, 50, 40)

            self.table.setItem(r, 4, st)

            self.table.setItem(r, 5, QTableWidgetItem(reason))

            for c in range(6):
                it = self.table.item(r, c)
                if it:
                    it.setBackground(bg)

        # KPI
        self.kt.setText(f"TOTAL\n{len(self.filtered)}")
        self.kf.setText(f"FRAUD\n{len(self.alerts)}")
        self.kf.setText(f"FRAUD\n{sum(1 for _, lvl, _ in self.filtered if lvl == 'FRAUD')}")
        self.kr.setText(f"RISK\n{sum(1 for _, lvl, _ in self.filtered if lvl == 'RISK')}")
        self.ko.setText(f"SAFE\n{sum(1 for _, lvl, _ in self.filtered if lvl == 'OK')}")

        # Alerts
        self.alert_table.setRowCount(len(self.alerts))
        for i, tx in enumerate(self.alerts):
            self.alert_table.setItem(i, 0, QTableWidgetItem(str(tx[0])))
            self.alert_table.setItem(i, 1, QTableWidgetItem(str(tx[2])))
            self.alert_table.setItem(i, 2, QTableWidgetItem(str(tx[5])))

        # Incidents
        self.inc_table.setRowCount(len(self.incidents))
        for i, inc in enumerate(self.incidents):
            self.inc_table.setItem(i, 0, QTableWidgetItem(str(inc["id"])))
            self.inc_table.setItem(i, 1, QTableWidgetItem(inc["customer"]))
            self.inc_table.setItem(i, 2, QTableWidgetItem(str(inc["amount"])))
            self.inc_table.setItem(i, 3, QTableWidgetItem(inc["status"]))
            self.inc_table.setItem(i, 4, QTableWidgetItem(inc["owner"]))

            #self.load_audit_logs()


    def load_audit_logs(self):

        try:

            with open("audit_log.txt", "r", encoding="utf-8") as f:

                logs = f.readlines()

            self.audit_table.clearContents()

            self.audit_table.setRowCount(len(logs))

            for r, line in enumerate(logs):

                item = QTableWidgetItem(line.strip())

                self.audit_table.setItem(r, 0, item)

            self.audit_table.resizeColumnsToContents()

        except Exception as e:

            print("AUDIT ERROR:", e)

    def update_inc(self):

        r = self.inc_table.currentRow()

        if r >= 0:

            self.incidents[r]["status"] = self.stat.currentText()
            self.incidents[r]["owner"] = self.owner.text()

            try:
                with open(
                    "audit_log.txt",
                    "a",
                    encoding="utf-8"
                ) as f:

                    f.write(
                        f"Incident {self.incidents[r]['id']} "
                        f"updated to {self.stat.currentText()} "
                        f"by {self.owner.text()}\n"
                    )

            except Exception:
                pass

        self.update_ui()
        


# ================= RUN =================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    login = LoginWindow()
    login.show()
    sys.exit(app.exec_())