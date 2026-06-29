# -*- coding: utf-8 -*-
"""实机测试人员交互：TTY input / tkinter 确定·取消 / 倒计时（默认 3s）。"""
from __future__ import annotations

import os
import sys
import time

import allure
import pytest

from common1 import logger

_DEFAULT_WAIT_SEC = 3.0
_DEFAULT_DIALOG_TITLE = "实机测试确认"


def _env_truthy(name: str) -> bool:
    return os.environ.get(name, "").strip().lower() in ("1", "true", "yes")


def _wait_seconds() -> float:
    raw = os.environ.get("ELEPHANT_OPERATOR_WAIT_SEC", "").strip()
    if not raw:
        return _DEFAULT_WAIT_SEC
    try:
        return float(raw)
    except ValueError:
        return _DEFAULT_WAIT_SEC


def _gui_enabled() -> bool:
    return not _env_truthy("ELEPHANT_OPERATOR_NO_GUI")


def _has_tty() -> bool:
    return sys.stdin is not None and sys.stdin.isatty()


def _ask_ok_cancel(message: str, title: str) -> bool | None:
    """True=确定, False=取消, None=GUI 不可用。"""
    try:
        import tkinter as tk
        from tkinter import messagebox
    except Exception as e:
        logger.debug("tkinter 未可用: %s", e)
        return None
    root = tk.Tk()
    root.withdraw()
    try:
        return bool(messagebox.askokcancel(title, message))
    except Exception as e:
        logger.debug("无法显示确认对话框: %s", e)
        return None
    finally:
        try:
            root.destroy()
        except Exception:
            pass


def prompt_continue(
    message: str,
    *,
    title: str = _DEFAULT_DIALOG_TITLE,
    allow_skip: bool = True,
) -> None:
    """等待测试人员确认继续。TTY：input；无 TTY：确定/取消弹窗；再否则倒计时。"""
    if _has_tty():
        input(message)
        return

    if _gui_enabled():
        with allure.step("无 TTY：弹出确定/取消"):
            ok = _ask_ok_cancel(message, title)
        if ok is True:
            return
        if ok is False:
            if allow_skip:
                pytest.skip("用户点击取消")
            return

    sec = _wait_seconds()
    with allure.step(f"非 TTY：等待 {sec:g} 秒后继续"):
        logger.info(
            "未检测到 TTY 且 GUI 不可用/已禁用，将等待 %.1f 秒后自动继续。"
            "可设 ELEPHANT_OPERATOR_NO_GUI=0 尝试弹窗，或 ELEPHANT_OPERATOR_WAIT_SEC 调整等待。",
            sec,
        )
        if sec > 0:
            time.sleep(sec)


def prompt_text(
    message: str,
    *,
    title: str = _DEFAULT_DIALOG_TITLE,
    default: str = "",
) -> str:
    """
    替代 input()。TTY：原生 input；无 TTY：确定→default（通常通过），取消→\"0\"（失败）；
    倒计时后返回 default。
    """
    if _has_tty():
        return input(message).strip()

    if _gui_enabled():
        with allure.step("无 TTY：弹出确定/取消（确定=通过，取消=失败）"):
            ok = _ask_ok_cancel(
                message + "\n\n点击「确定」表示通过；点击「取消」表示失败(0)。",
                title,
            )
        if ok is True:
            return default
        if ok is False:
            return "0"

    sec = _wait_seconds()
    with allure.step(f"非 TTY：等待 {sec:g} 秒后默认通过"):
        logger.info(
            "未检测到 TTY，%.1f 秒后返回默认值 %r。"
            "需人工判失败请在终端运行或启用弹窗后点取消。",
            sec,
            default,
        )
        if sec > 0:
            time.sleep(sec)
        return default
