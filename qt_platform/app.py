# -*- coding: utf-8 -*-
"""PyQt6 壳：选择 arms.json 中的机械臂，子进程跑 pytest 并显示控制台输出。"""
from __future__ import annotations

import os
import sys
from pathlib import Path

from PyQt6.QtCore import QProcess, QProcessEnvironment, Qt
from PyQt6.QtWidgets import (
    QApplication,
    QComboBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QWidget,
)

# 项目根（含 pytest.ini）
_ROOT = Path(__file__).resolve().parents[1]


def _load_arm_registry():
    os.chdir(_ROOT)
    if str(_ROOT) not in sys.path:
        sys.path.insert(0, str(_ROOT))
    from arm_registry import (  # noqa: WPS433
        connection_env_var_for_arm,
        get_arm_entry,
        list_arm_ids,
        get_testcase_roots,
    )

    return connection_env_var_for_arm, get_arm_entry, list_arm_ids, get_testcase_roots


class ElephantQtRunner(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("elephant-pytest 启动器 (PyQt6)")
        self.resize(900, 560)

        conn_fn, get_entry, list_ids, roots_fn = _load_arm_registry()

        self._connection_env_var_for_arm = conn_fn
        self._get_arm_entry = get_entry
        self._get_testcase_roots = roots_fn

        central = QWidget()
        self.setCentralWidget(central)
        layout = QFormLayout(central)

        self.combo_arm = QComboBox()
        for aid in list_ids():
            entry = get_entry(aid)
            label = entry.get("label", aid)
            self.combo_arm.addItem(f"{label} ({aid})", aid)
        layout.addRow("机械臂", self.combo_arm)

        self.edit_conn = QLineEdit()
        self.edit_conn.setPlaceholderText("留空则使用环境变量 / 各产品线默认")
        layout.addRow("连接参数", self.edit_conn)

        self.hint = QLabel()
        self.hint.setWordWrap(True)
        self.hint.setTextFormat(Qt.TextFormat.PlainText)
        layout.addRow(self.hint)

        self.combo_arm.currentIndexChanged.connect(self._update_hint)
        self._update_hint()

        btn_row = QHBoxLayout()
        self.btn_run = QPushButton("运行 pytest（当前臂全部用例根）")
        self.btn_stop = QPushButton("停止")
        self.btn_stop.setEnabled(False)
        btn_row.addWidget(self.btn_run)
        btn_row.addWidget(self.btn_stop)
        layout.addRow(btn_row)

        self.log = QPlainTextEdit()
        self.log.setReadOnly(True)
        self.log.setMaximumBlockCount(5000)
        layout.addRow(self.log)

        self.proc: QProcess | None = None

        self.btn_run.clicked.connect(self._run_pytest)
        self.btn_stop.clicked.connect(self._stop_pytest)

    def _update_hint(self) -> None:
        aid = self.combo_arm.currentData()
        if not aid:
            return
        envn = self._connection_env_var_for_arm(aid)
        if envn:
            self.hint.setText(f"非空时启动前会设置环境变量 {envn}；Pro450 亦支持命令行 --elephant-ip。")
        else:
            self.hint.setText(
                "Mercury 双臂请事先设置 MERCURY_LEFT_PORT、MERCURY_RIGHT_PORT（或代码默认 Linux 设备路径）。"
            )

    def _append_log(self, text: str) -> None:
        self.log.appendPlainText(text.rstrip("\n"))

    def _run_pytest(self) -> None:
        if self.proc is not None and self.proc.state() != QProcess.ProcessState.NotRunning:
            return

        aid = self.combo_arm.currentData()
        roots = self._get_testcase_roots(aid)
        args = ["-m", "pytest", "-v", "--tb=short", f"--elephant-arm={aid}", *roots]

        self.proc = QProcess(self)
        self.proc.setProgram(sys.executable)
        self.proc.setArguments(args)
        self.proc.setWorkingDirectory(str(_ROOT))

        env = QProcessEnvironment.systemEnvironment()
        env.insert("ELEPHANT_ARM", aid)
        conn = self.edit_conn.text().strip()
        envn = self._connection_env_var_for_arm(aid)
        if conn and envn:
            env.insert(envn, conn)
        self.proc.setProcessEnvironment(env)

        self.proc.readyReadStandardOutput.connect(self._read_stdout)
        self.proc.readyReadStandardError.connect(self._read_stderr)
        self.proc.finished.connect(self._on_finished)

        self._append_log(f"$ python {' '.join(args)}")
        self.proc.start()
        self.btn_run.setEnabled(False)
        self.btn_stop.setEnabled(True)

    def _read_stdout(self) -> None:
        if self.proc:
            self._append_log(bytes(self.proc.readAllStandardOutput()).decode("utf-8", errors="replace"))

    def _read_stderr(self) -> None:
        if self.proc:
            self._append_log(bytes(self.proc.readAllStandardError()).decode("utf-8", errors="replace"))

    def _stop_pytest(self) -> None:
        if self.proc and self.proc.state() != QProcess.ProcessState.NotRunning:
            self.proc.kill()

    def _on_finished(self, code: int, status: QProcess.ExitStatus) -> None:
        self._append_log(f"\n[进程结束 exit={code} status={status}]")
        self.btn_run.setEnabled(True)
        self.btn_stop.setEnabled(False)
        self.proc = None


def main() -> None:
    app = QApplication(sys.argv)
    w = ElephantQtRunner()
    w.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
