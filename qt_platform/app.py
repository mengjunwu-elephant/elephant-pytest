# -*- coding: utf-8 -*-
"""PyQt6 测试平台：选臂 → IP/串口连接 → 勾选单元测试与 test_type → 跑 pytest → Allure 报告。"""
from __future__ import annotations

import importlib.util
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from qt_platform.test_discovery import TestModuleRow

from PyQt6 import uic
from PyQt6.QtCore import QProcess, QProcessEnvironment, Qt, QUrl
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QApplication,
    QComboBox,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QStackedWidget,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

_ROOT = Path(__file__).resolve().parents[1]
_UI_FILE = Path(__file__).resolve().parent / "ui" / "main_window.ui"
ALLURE_RESULTS = _ROOT / "reports" / "qt_allure" / "allure-results"
ALLURE_REPORT = _ROOT / "reports" / "qt_allure" / "allure-report"

# 最近一次 pytest 对该 (文件, 测试项选择) 全部通过时，下拉框高亮
_STYLE_COMBO_ALL_PASSED = """
QComboBox {
    background-color: #dcfce7;
    border: 2px solid #22c55e;
    border-radius: 6px;
    padding: 4px 8px;
    min-height: 22px;
}
"""

# 与 arms.json 中 testcase_roots 最后一级目录对应，便于界面展示
_TESTCASE_GROUP_LABELS: dict[str, str] = {
    "mycobot_450": "Mycobot Pro450",
    "mycobot450_pro_gripper": "mycobot Pro 450 夹爪",
    "mercury": "Mercury X1 双臂",
    "mercury_pro_gripper": "Mercury X1 夹爪",
    "mercury_my_hand": "Mercury X1 三指",
    "mercury_e1": "Mercury E1",
    "mercury_e1_pro_gripper": "Mercury E1 夹爪",
    "mycobot_280": "Mycobot 280",
    "UltraArm_P1": "UltraArm P1",
    "UltraArm_P1_Attachments": "UltraArm P1 附件",
}


def _group_title_for_testcase_root(testcase_root: str) -> str:
    key = Path(testcase_root).name
    if key in _TESTCASE_GROUP_LABELS:
        return _TESTCASE_GROUP_LABELS[key]
    return key.replace("_", " ")


def _app_stylesheet() -> str:
    """浅色工业风 QSS，与 Fusion 搭配。"""
    return """
    QWidget { font-size: 13px; color: #1e293b; }
    QMainWindow, QWidget#centralwidget { background-color: #f1f5f9; }
    QGroupBox {
        font-weight: 600;
        border: 1px solid #cbd5e1;
        border-radius: 8px;
        margin-top: 10px;
        padding-top: 8px;
        background-color: #ffffff;
    }
    QGroupBox::title {
        subcontrol-origin: margin;
        left: 12px;
        padding: 0 6px;
        color: #0f172a;
    }
    QPushButton {
        color: #ffffff;
        border: none;
        border-radius: 6px;
        padding: 6px 14px;
        min-height: 22px;
    }
    /* 绿：连接、运行、生成报告 */
    QPushButton#btn_connect,
    QPushButton#btn_run_selected,
    QPushButton#btn_run_all,
    QPushButton#btn_gen_report {
        background-color: #16a34a;
    }
    QPushButton#btn_connect:hover,
    QPushButton#btn_run_selected:hover,
    QPushButton#btn_run_all:hover,
    QPushButton#btn_gen_report:hover { background-color: #15803d; }
    QPushButton#btn_connect:pressed,
    QPushButton#btn_run_selected:pressed,
    QPushButton#btn_run_all:pressed,
    QPushButton#btn_gen_report:pressed { background-color: #166534; }
    /* 红：断开、停止 */
    QPushButton#btn_disconnect,
    QPushButton#btn_stop {
        background-color: #dc2626;
    }
    QPushButton#btn_disconnect:hover,
    QPushButton#btn_stop:hover { background-color: #b91c1c; }
    QPushButton#btn_disconnect:pressed,
    QPushButton#btn_stop:pressed { background-color: #991b1b; }
    /* 黄：勾选、清空、刷新串口 */
    QPushButton#btn_check_all,
    QPushButton#btn_uncheck_all,
    QPushButton#btn_clear_allure,
    QPushButton#btn_refresh_serial {
        background-color: #ca8a04;
        color: #1c1917;
    }
    QPushButton#btn_check_all:hover,
    QPushButton#btn_uncheck_all:hover,
    QPushButton#btn_clear_allure:hover,
    QPushButton#btn_refresh_serial:hover { background-color: #a16207; color: #1c1917; }
    QPushButton#btn_check_all:pressed,
    QPushButton#btn_uncheck_all:pressed,
    QPushButton#btn_clear_allure:pressed,
    QPushButton#btn_refresh_serial:pressed { background-color: #854d0e; color: #fafaf9; }
    QPushButton:disabled { background-color: #94a3b8 !important; color: #e2e8f0 !important; }
    QComboBox, QLineEdit {
        border: 1px solid #cbd5e1;
        border-radius: 6px;
        padding: 4px 8px;
        background: #ffffff;
        min-height: 22px;
    }
    QComboBox:focus, QLineEdit:focus { border-color: #2563eb; }
    QScrollArea { border: 1px solid #cbd5e1; border-radius: 8px; background: #f8fafc; }
    QTableWidget {
        gridline-color: #e2e8f0;
        background: #ffffff;
        alternate-background-color: #f8fafc;
        border: none;
        border-radius: 4px;
    }
    QHeaderView::section {
        background-color: #e2e8f0;
        color: #334155;
        padding: 6px;
        border: none;
        font-weight: 600;
    }
    QPlainTextEdit#log {
        border: 1px solid #64748b;
        border-radius: 8px;
        background-color: #0f172a;
        color: #e2e8f0;
        font-family: Consolas, "Cascadia Mono", monospace;
        font-size: 12px;
        padding: 10px;
    }
    QLabel#label_conn_status { color: #475569; }
    """


def _force_child_stdio_utf8(env: QProcessEnvironment) -> None:
    """避免 Windows 下子进程中文日志被当成系统代码页，Qt 侧按 UTF-8 解码乱码。"""
    env.insert("PYTHONUTF8", "1")
    env.insert("PYTHONIOENCODING", "utf-8")


def _allure_pytest_available() -> bool:
    """--alluredir 由 allure-pytest 注册；未安装时不能传该参数。"""
    return importlib.util.find_spec("allure_pytest") is not None


def _ensure_project_path() -> None:
    os.chdir(_ROOT)
    if str(_ROOT) not in sys.path:
        sys.path.insert(0, str(_ROOT))


def _list_serial_ports() -> list[str]:
    try:
        from serial.tools import list_ports

        return [p.device for p in list_ports.comports()]
    except Exception:
        return []


class ElephantQtRunner(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        if not _UI_FILE.is_file():
            raise FileNotFoundError(f"未找到界面文件: {_UI_FILE}")
        uic.loadUi(str(_UI_FILE), self)

        _ensure_project_path()
        from arm_registry import (  # noqa: WPS433
            connection_env_var_for_arm,
            get_arm_entry,
            get_connection_mode,
            get_testcase_roots,
            list_arm_ids,
        )

        self._get_connection_mode = get_connection_mode
        self._get_testcase_roots = get_testcase_roots
        self._get_arm_entry = get_arm_entry
        self._connection_env_var_for_arm = connection_env_var_for_arm

        self._connected = False
        self._session_ip: str = ""
        self._session_serial: str = ""
        self._session_left: str = ""
        self._session_right: str = ""

        self._pytest_proc: Optional[QProcess] = None
        # (相对路径, pytest -k 表达式, 下拉当前 data：__ALL__ 或函数名)
        self._pytest_queue: list[tuple[str, str, str]] = []
        self._pytest_active: Optional[tuple[str, str]] = None
        self._pass_state: dict[tuple[str, str], bool] = {}

        self._test_tables: list[tuple[QTableWidget, list[TestModuleRow]]] = []
        self._logged_missing_allure = False

        self._build_connection_stack()
        ly = self.conn_host.layout()
        if ly is not None:
            ly.addWidget(self.stack_conn)

        self.combo_arm.clear()
        for aid in list_arm_ids():
            entry = get_arm_entry(aid)
            label = entry.get("label", aid)
            self.combo_arm.addItem(f"{label} ({aid})", aid)

        ly_host = self.tests_host.layout()
        if ly_host is None:
            raise RuntimeError("tests_host 缺少布局，请检查 main_window.ui")
        self._tests_layout: QVBoxLayout = ly_host

        self.combo_arm.currentIndexChanged.connect(self._on_arm_changed)
        self.btn_connect.clicked.connect(self._on_connect)
        self.btn_disconnect.clicked.connect(self._on_disconnect)
        self.btn_check_all.clicked.connect(self._check_all)
        self.btn_uncheck_all.clicked.connect(self._uncheck_all)
        self.btn_run_selected.clicked.connect(self._on_run_selected)
        self.btn_run_all.clicked.connect(self._on_run_all)
        self.btn_stop.clicked.connect(self._on_stop_pytest)
        self.btn_clear_allure.clicked.connect(self._on_clear_allure)
        self.btn_gen_report.clicked.connect(self._on_gen_report)

        self._on_arm_changed()

    def _configure_test_table(self, tbl: QTableWidget) -> None:
        tbl.setColumnCount(4)
        tbl.setHorizontalHeaderLabels(["运行", "接口/表名", "测试项", "文件"])
        hh = tbl.horizontalHeader()
        hh.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        hh.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        hh.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        hh.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        tbl.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        tbl.setAlternatingRowColors(True)
        tbl.verticalHeader().setVisible(False)
        tbl.setMinimumHeight(120)

    def _clear_tests_panel(self) -> None:
        self._pass_state.clear()
        while self._tests_layout.count():
            item = self._tests_layout.takeAt(0)
            w = item.widget()
            if w is not None:
                w.setParent(None)
                w.deleteLater()
        self._test_tables.clear()

    def _find_row_by_rel(self, rel_path: str) -> Optional[TestModuleRow]:
        for _, rows in self._test_tables:
            for row in rows:
                if row.rel_path == rel_path:
                    return row
        return None

    def _apply_combo_pass_style(self, cb: QComboBox, rel_path: str) -> None:
        choice = cb.currentData()
        if not isinstance(choice, str) or not choice:
            cb.setStyleSheet("")
            return
        if self._pass_state.get((rel_path, choice)) is True:
            cb.setStyleSheet(_STYLE_COMBO_ALL_PASSED)
        else:
            cb.setStyleSheet("")

    def _refresh_combo_style_for_rel(self, rel_path: str) -> None:
        for tbl, rows in self._test_tables:
            for r, row in enumerate(rows):
                if row.rel_path != rel_path:
                    continue
                w = tbl.cellWidget(r, 2)
                if isinstance(w, QComboBox):
                    self._apply_combo_pass_style(w, rel_path)

    def _build_connection_stack(self) -> None:
        self.stack_conn = QStackedWidget()

        page_ip = QWidget()
        h_ip = QHBoxLayout(page_ip)
        h_ip.addWidget(QLabel("IP"))
        self.edit_ip = QLineEdit()
        self.edit_ip.setPlaceholderText("控制器 IP，如 192.168.0.232")
        h_ip.addWidget(self.edit_ip, 1)

        page_serial = QWidget()
        h_s = QHBoxLayout(page_serial)
        h_s.addWidget(QLabel("串口"))
        self.combo_serial = QComboBox()
        self.combo_serial.setEditable(True)
        self.combo_serial.setMinimumWidth(160)
        h_s.addWidget(self.combo_serial, 1)
        self.btn_refresh_serial = QPushButton("刷新串口")
        self.btn_refresh_serial.setObjectName("btn_refresh_serial")
        self.btn_refresh_serial.clicked.connect(self._refresh_serial_ports)
        h_s.addWidget(self.btn_refresh_serial)

        page_dual = QWidget()
        h_d = QHBoxLayout(page_dual)
        h_d.addWidget(QLabel("左臂"))
        self.edit_m_left = QLineEdit()
        self.edit_m_left.setPlaceholderText("如 COM3 或 /dev/ttyUSB0")
        h_d.addWidget(self.edit_m_left, 1)
        h_d.addWidget(QLabel("右臂"))
        self.edit_m_right = QLineEdit()
        self.edit_m_right.setPlaceholderText("如 COM4")
        h_d.addWidget(self.edit_m_right, 1)

        self.stack_conn.addWidget(page_ip)
        self.stack_conn.addWidget(page_serial)
        self.stack_conn.addWidget(page_dual)

    def _append_log(self, text: str) -> None:
        self.log.appendPlainText(text.rstrip("\n"))

    def _on_arm_changed(self) -> None:
        aid = self.combo_arm.currentData()
        if not aid:
            return
        mode = self._get_connection_mode(aid)
        idx = {"ip": 0, "serial": 1, "dual_serial": 2}.get(mode, 0)
        self.stack_conn.setCurrentIndex(idx)
        entry = self._get_arm_entry(aid)
        dip = str(entry.get("default_ip", "") or "").strip()
        if mode == "ip" and dip:
            self.edit_ip.setText(dip)
        self._connected = False
        self._refresh_test_table()
        self._update_run_enabled()
        self.label_conn_status.setText("状态：未连接（请先连接再运行测试）")

    def _refresh_serial_ports(self) -> None:
        self.combo_serial.clear()
        for p in _list_serial_ports():
            self.combo_serial.addItem(p)

    def _refresh_test_table(self) -> None:
        from qt_platform.test_discovery import discover_grouped_for_arm

        self._clear_tests_panel()
        aid = self.combo_arm.currentData()
        if not aid:
            return
        roots = self._get_testcase_roots(aid)
        grouped = discover_grouped_for_arm(_ROOT, roots)
        for testcase_root, rows in grouped:
            title = _group_title_for_testcase_root(testcase_root)
            grp = QGroupBox(title)
            v = QVBoxLayout(grp)
            v.setContentsMargins(8, 12, 8, 8)
            tbl = QTableWidget()
            self._configure_test_table(tbl)
            tbl.setRowCount(len(rows))
            for i, row in enumerate(rows):
                ck = QTableWidgetItem()
                ck.setFlags(
                    Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled
                )
                ck.setCheckState(Qt.CheckState.Unchecked)
                tbl.setItem(i, 0, ck)
                tbl.setItem(i, 1, QTableWidgetItem(row.display_name))
                cb = QComboBox()
                if len(row.items) > 1:
                    cb.addItem("全部（本文件）", "__ALL__")
                for it in row.items:
                    cb.addItem(it.label, it.func_name)
                if cb.count() == 0:
                    cb.addItem("(无测试函数)", "")
                rp = row.rel_path
                cb.currentIndexChanged.connect(
                    lambda _idx, c=cb, rel_p=rp: self._apply_combo_pass_style(c, rel_p),
                )
                self._apply_combo_pass_style(cb, rp)
                tbl.setCellWidget(i, 2, cb)
                tbl.setItem(i, 3, QTableWidgetItem(row.rel_path))
            v.addWidget(tbl)
            self._tests_layout.addWidget(grp)
            self._test_tables.append((tbl, rows))
        self._tests_layout.addStretch(1)

    def _serial_text(self) -> str:
        return self.combo_serial.currentText().strip()

    def _on_connect(self) -> None:
        aid = self.combo_arm.currentData()
        if not aid:
            return
        mode = self._get_connection_mode(aid)
        argv = ["-m", "qt_platform.probe", aid]
        if mode == "ip":
            ip = self.edit_ip.text().strip()
            if not ip:
                QMessageBox.warning(self, "连接", "请输入 IP")
                return
            argv += ["--ip", ip]
        elif mode == "serial":
            s = self._serial_text()
            if not s:
                QMessageBox.warning(self, "连接", "请选择或输入串口")
                return
            argv += ["--serial", s]
        else:
            l = self.edit_m_left.text().strip()
            r = self.edit_m_right.text().strip()
            if not l or not r:
                QMessageBox.warning(self, "连接", "请填写左、右臂串口")
                return
            argv += ["--left", l, "--right", r]

        proc = QProcess(self)
        proc.setProgram(sys.executable)
        proc.setArguments(argv)
        proc.setWorkingDirectory(str(_ROOT))
        env = QProcessEnvironment.systemEnvironment()
        _force_child_stdio_utf8(env)
        proc.setProcessEnvironment(env)
        self._append_log(f"$ {sys.executable} {' '.join(argv)}")
        proc.start()
        proc.waitForFinished(120_000)
        out = bytes(proc.readAllStandardOutput()).decode("utf-8", errors="replace")
        err = bytes(proc.readAllStandardError()).decode("utf-8", errors="replace")
        if out.strip():
            self._append_log(out)
        if err.strip():
            self._append_log(err)
        if proc.exitCode() != 0:
            self.label_conn_status.setText("状态：连接失败（见日志）")
            self._connected = False
            QMessageBox.warning(self, "连接", "探测失败，请检查参数与硬件。")
            return

        self._connected = True
        if mode == "ip":
            self._session_ip = self.edit_ip.text().strip()
        elif mode == "serial":
            self._session_serial = self._serial_text()
        else:
            self._session_left = self.edit_m_left.text().strip()
            self._session_right = self.edit_m_right.text().strip()
        self.label_conn_status.setText("状态：已连接，可运行测试")
        self._update_run_enabled()

    def _on_disconnect(self) -> None:
        self._connected = False
        self._session_ip = ""
        self._session_serial = ""
        self._session_left = ""
        self._session_right = ""
        self.label_conn_status.setText("状态：已断开")
        self._update_run_enabled()

    def _update_run_enabled(self) -> None:
        busy = self._pytest_proc is not None and self._pytest_proc.state() != QProcess.ProcessState.NotRunning
        en = self._connected and not busy
        self.btn_run_selected.setEnabled(en)
        self.btn_run_all.setEnabled(en)
        self.btn_connect.setEnabled(not busy)
        self.btn_disconnect.setEnabled(not busy)

    def _pytest_environment(self) -> QProcessEnvironment:
        env = QProcessEnvironment.systemEnvironment()
        _force_child_stdio_utf8(env)
        aid = self.combo_arm.currentData()
        env.insert("ELEPHANT_ARM", aid)
        mode = self._get_connection_mode(aid)
        if mode == "ip" and self._session_ip:
            env.insert("MYCOBOT450_IP", self._session_ip)
        elif mode == "serial" and self._session_serial:
            ev = self._connection_env_var_for_arm(aid)
            if ev:
                env.insert(ev, self._session_serial)
        elif mode == "dual_serial":
            env.insert("MERCURY_LEFT_PORT", self._session_left)
            env.insert("MERCURY_RIGHT_PORT", self._session_right)
        return env

    def _check_all(self) -> None:
        for tbl, _ in self._test_tables:
            for r in range(tbl.rowCount()):
                it = tbl.item(r, 0)
                if it:
                    it.setCheckState(Qt.CheckState.Checked)

    def _uncheck_all(self) -> None:
        for tbl, _ in self._test_tables:
            for r in range(tbl.rowCount()):
                it = tbl.item(r, 0)
                if it:
                    it.setCheckState(Qt.CheckState.Unchecked)

    def _collect_tasks(self, all_rows: bool) -> list[tuple[str, str, str]]:
        tasks: list[tuple[str, str, str]] = []
        for tbl, rows in self._test_tables:
            for r in range(tbl.rowCount()):
                if not all_rows:
                    it = tbl.item(r, 0)
                    if not it or it.checkState() != Qt.CheckState.Checked:
                        continue
                row = rows[r]
                w = tbl.cellWidget(r, 2)
                if not isinstance(w, QComboBox):
                    continue
                choice = w.currentData()
                if not choice or not isinstance(choice, str):
                    continue
                k_expr = row.pytest_k_expr_for(choice)
                if not k_expr:
                    self._append_log(f"[跳过] {row.rel_path} 无有效测试项")
                    continue
                tasks.append((row.rel_path, k_expr, choice))
        return tasks

    def _on_run_selected(self) -> None:
        if not self._connected:
            return
        self._pytest_queue = self._collect_tasks(all_rows=False)
        if not self._pytest_queue:
            QMessageBox.information(self, "运行", "请勾选至少一行，并选择有效的测试项。")
            return
        self._start_next_pytest()

    def _on_run_all(self) -> None:
        if not self._connected:
            return
        self._pytest_queue = self._collect_tasks(all_rows=True)
        if not self._pytest_queue:
            QMessageBox.information(self, "运行", "未发现可运行的测试行。")
            return
        self._start_next_pytest()

    def _start_next_pytest(self) -> None:
        if not self._pytest_queue:
            self._pytest_proc = None
            self._pytest_active = None
            self._append_log("\n[队列执行完毕]")
            self._update_run_enabled()
            self.btn_stop.setEnabled(False)
            return

        rel, k_expr, choice = self._pytest_queue.pop(0)
        row_meta = self._find_row_by_rel(rel)
        if row_meta is not None and row_meta.choice_uses_input(choice):
            ans = QMessageBox.question(
                self,
                "需人工交互（input）",
                "当前选择的测试代码中包含人工交互（input / prompt_continue / prompt_text），"
                "执行时会在控制台等待输入或弹出确认窗。\n\n"
                "从本界面启动的子进程通常没有可用的交互式标准输入，用例容易卡住；"
                "请优先在系统终端中复制日志里的完整命令执行，或确保测试机为 pytest 提供可用控制台。\n\n"
                "将自动添加 pytest 参数 -s（不捕获输出），便于对照终端提示。\n\n"
                "是否仍在本界面尝试运行本段？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            if ans != QMessageBox.StandardButton.Yes:
                self._append_log(f"[跳过] {rel}（含人工交互，已取消）")
                self._start_next_pytest()
                return

        aid = self.combo_arm.currentData()
        ALLURE_RESULTS.mkdir(parents=True, exist_ok=True)

        args: list[str] = [
            "-m",
            "pytest",
            "-v",
            "--tb=short",
            f"--elephant-arm={aid}",
        ]
        if row_meta is not None and row_meta.choice_uses_input(choice):
            args.append("-s")
        if _allure_pytest_available():
            args.append(f"--alluredir={ALLURE_RESULTS.as_posix()}")
        elif not self._logged_missing_allure:
            self._logged_missing_allure = True
            self._append_log(
                "[提示] 当前环境未安装 allure-pytest，已省略 --alluredir；"
                "请执行: pip install allure-pytest"
            )
        args.extend([rel, "-k", k_expr])
        self._pytest_active = (rel, choice)
        self._pytest_proc = QProcess(self)
        self._pytest_proc.setProgram(sys.executable)
        self._pytest_proc.setArguments(args)
        self._pytest_proc.setWorkingDirectory(str(_ROOT))
        self._pytest_proc.setProcessEnvironment(self._pytest_environment())
        self._pytest_proc.readyReadStandardOutput.connect(self._read_out)
        self._pytest_proc.readyReadStandardError.connect(self._read_err)
        self._pytest_proc.finished.connect(self._on_pytest_finished)

        self._append_log(f"$ python {' '.join(args)}")
        self._pytest_proc.start()
        self._update_run_enabled()
        self.btn_stop.setEnabled(True)

    def _read_out(self) -> None:
        if self._pytest_proc:
            self._append_log(
                bytes(self._pytest_proc.readAllStandardOutput()).decode(
                    "utf-8", errors="replace"
                )
            )

    def _read_err(self) -> None:
        if self._pytest_proc:
            self._append_log(
                bytes(self._pytest_proc.readAllStandardError()).decode(
                    "utf-8", errors="replace"
                )
            )

    def _on_pytest_finished(self, code: int, status: QProcess.ExitStatus) -> None:
        self._append_log(f"\n[本段结束 exit={code} status={status}]")
        active = self._pytest_active
        self._pytest_active = None
        if active is not None:
            rel_path, choice = active
            if status == QProcess.ExitStatus.NormalExit:
                self._pass_state[(rel_path, choice)] = code == 0
                self._refresh_combo_style_for_rel(rel_path)
        self._start_next_pytest()

    def _on_stop_pytest(self) -> None:
        self._pytest_queue.clear()
        self._pytest_active = None
        if self._pytest_proc and self._pytest_proc.state() != QProcess.ProcessState.NotRunning:
            self._pytest_proc.kill()
        self._pytest_proc = None
        self._append_log("\n[已停止]")
        self._update_run_enabled()
        self.btn_stop.setEnabled(False)

    def _on_clear_allure(self) -> None:
        if ALLURE_RESULTS.exists():
            for p in ALLURE_RESULTS.iterdir():
                if p.is_file():
                    p.unlink()
                elif p.is_dir():
                    shutil.rmtree(p)
        ALLURE_RESULTS.mkdir(parents=True, exist_ok=True)
        self._append_log(f"已清空: {ALLURE_RESULTS}")
        QMessageBox.information(self, "Allure", "已清空原始结果目录。")

    def _on_gen_report(self) -> None:
        exe = shutil.which("allure")
        if not exe:
            QMessageBox.warning(
                self,
                "Allure",
                "未在 PATH 中找到 allure 命令。\n"
                "请安装 Allure CLI 后重试，或手动执行：\n"
                f'allure generate "{ALLURE_RESULTS}" -o "{ALLURE_REPORT}" --clean',
            )
            return
        if not ALLURE_RESULTS.is_dir() or not any(ALLURE_RESULTS.iterdir()):
            QMessageBox.warning(
                self,
                "Allure",
                "allure-results 目录为空。\n请先运行测试（需已安装 allure-pytest），再生成报告。",
            )
            return
        proc = QProcess(self)
        proc.setProgram(exe)
        proc.setArguments(
            [
                "generate",
                str(ALLURE_RESULTS),
                "-o",
                str(ALLURE_REPORT),
                "--clean",
            ]
        )
        proc.setWorkingDirectory(str(_ROOT))
        proc.start()
        proc.waitForFinished(180_000)
        err = bytes(proc.readAllStandardError()).decode("utf-8", errors="replace")
        out = bytes(proc.readAllStandardOutput()).decode("utf-8", errors="replace")
        if out.strip():
            self._append_log(out)
        if err.strip():
            self._append_log(err)
        if proc.exitCode() != 0:
            QMessageBox.warning(self, "Allure", "生成失败，见日志。")
            return
        idx = ALLURE_REPORT / "index.html"
        if not idx.is_file():
            QMessageBox.warning(
                self,
                "Allure",
                f"未找到 index.html，请检查生成输出：\n{ALLURE_REPORT}",
            )
            return
        # 直接 file:// 打开时，部分 Allure 版本会因前端路由/资源路径出现 404；用内置 HTTP 打开更稳
        opened = False
        try:
            popen_kw: dict = {
                "cwd": str(_ROOT),
                "stdout": subprocess.DEVNULL,
                "stderr": subprocess.DEVNULL,
            }
            if sys.platform == "win32":
                popen_kw["creationflags"] = getattr(subprocess, "CREATE_NO_WINDOW", 0)
            else:
                popen_kw["start_new_session"] = True
            subprocess.Popen([exe, "open", str(ALLURE_REPORT)], **popen_kw)
            opened = True
            self._append_log(f"[Allure] 已启动本地服务打开报告: {ALLURE_REPORT}")
        except OSError as e:
            self._append_log(f"[Allure] allure open 失败 ({e})，改用语系默认方式打开 index.html")
        if not opened:
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(idx.resolve())))
        QMessageBox.information(
            self,
            "Allure",
            "报告已生成。\n"
            "若未自动弹出浏览器，请查看日志中的 Allure 本地地址，或手动打开：\n"
            f"{idx}",
        )


def main() -> None:
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setStyleSheet(_app_stylesheet())
    w = ElephantQtRunner()
    w.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
