# -*- coding: utf-8 -*-
"""
UltraArm P1：绝对定位精度 & 重复定位精度 demo（结果写入 Excel）。

使用接口：set_angles / set_angles + get_angles_info；set_coords / set_coords + get_coords_info。
运动结束后根据控制器反馈计算误差（非外部测量设备）。

运行示例（在项目根目录）::

    python demo/P1_positioning_accuracy_demo.py --port COM10 --baud 1000000

默认会在 demo 目录下生成 ``P1_positioning_accuracy_<时间戳>.xlsx``。
"""

from __future__ import annotations

import argparse
import statistics
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Sequence

from openpyxl import Workbook
from openpyxl.styles import Font
from pymycobot import UltraArmP1

# ---------------------------------------------------------------------------
# 关节 / 笛卡尔限位（按你的规格；请在不确定处与文档/实机核对）
# ---------------------------------------------------------------------------
JOINT_LIMITS_DEG = (
    (-158.0, 158.0),  # J1
    (-18.0, 85.0),  # J2
    (89.0, 190.0),  # J3（与 pymycobot set_angles 校验一致：89 ~ 190）
    (-179.0, 179.0),  # J4
)

# 笛卡尔运动前建议姿态（与 settings.UltraArmP1Base.coords_init_angles、接口测试一致）。
# 若在关节测试后直接 set_coords，易从「奇异/耦合」关节域出发，固件可能返回 LimitError:6。
# pymycobot ultraArmP1._response：LimitError[6] => "J2/J3 joint coupling limit."
COORDS_INIT_ANGLES: list[float] = [0.0, 10.0, 110.0, 0.0]

# [x, y, z, rx] —— P1 示教坐标与仓库用例一致为 4 维
COORD_LIMITS = (
    (-301.7, 360.5),  # X
    (-360.5, 360.5),  # Y
    (-157.0, 91.0),  # Z
    (-180.0, 180.0),  # Rx
)

# 默认测试指令位姿（关节空间）：需在各自限位内且尽量为实机可达姿态，可按现场修改
DEFAULT_ANGLE_TARGETS: list[list[float]] = [
    [0.0, 30.0, 120.0, 0.0],
    [-45.0, 40.0, 150.0, 15.0],
    [60.0, 10.0, 100.0, -30.0],
]

# 默认笛卡尔测试点（需在坐标限位内且可达；若不可达请换成你们标定过的点）
DEFAULT_COORD_TARGETS: list[list[float]] = [
    [250, 20, 30, 10],
    [270.0, 50.0, 40.0, 30.0],
    [230.0, -60.0, 50.0, -45.0],
]


def _in_joint_limits(angles: Sequence[float]) -> bool:
    for v, (lo, hi) in zip(angles, JOINT_LIMITS_DEG):
        if not (lo <= v <= hi):
            return False
    return True


def _in_coord_limits(coords: Sequence[float]) -> bool:
    for v, (lo, hi) in zip(coords, COORD_LIMITS):
        if not (lo <= v <= hi):
            return False
    return True


def move_to_coords_init(mc: UltraArmP1, speed: int) -> None:
    """先回到便于笛卡尔规划的姿态，减轻 J2/J3 耦合触发 LimitError:6。"""
    mc.set_angles(list(COORDS_INIT_ANGLES), speed)
    wait_motion_done(mc)


def wait_motion_done(mc: UltraArmP1, timeout_sec: float = 120.0) -> None:
    deadline = time.monotonic() + float(timeout_sec)
    time.sleep(0.3)
    while mc.get_run_status():
        if time.monotonic() > deadline:
            raise TimeoutError(f"等待运动结束超时（{timeout_sec}s）")
        time.sleep(0.1)
    time.sleep(0.3)


def _float_row(xs: Sequence[Any]) -> list[float]:
    return [float(x) for x in xs]


def run_absolute_angles(
    mc: UltraArmP1, speed: int, targets: list[list[float]]
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for i, cmd in enumerate(targets):
        cmdf = _float_row(cmd)
        if not _in_joint_limits(cmdf):
            raise ValueError(f"关节目标 {i} 超出限位: {cmdf}")
        mc.set_angles(cmdf, speed)
        wait_motion_done(mc)
        act = _float_row(mc.get_angles_info())
        err = [a - c for a, c in zip(act, cmdf)]
        rows.append(
            {
                "目标点序号": i + 1,
                "J1指令(°)": cmdf[0],
                "J2指令(°)": cmdf[1],
                "J3指令(°)": cmdf[2],
                "J4指令(°)": cmdf[3],
                "J1反馈(°)": act[0],
                "J2反馈(°)": act[1],
                "J3反馈(°)": act[2],
                "J4反馈(°)": act[3],
                "J1误差(°)": err[0],
                "J2误差(°)": err[1],
                "J3误差(°)": err[2],
                "J4误差(°)": err[3],
                "四轴最大绝对误差(°)": max(abs(x) for x in err),
            }
        )
    return rows


def run_repeat_angles(
    mc: UltraArmP1, speed: int, targets: list[list[float]], repeat_n: int
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    detail: list[dict[str, Any]] = []
    summary: list[dict[str, Any]] = []

    for pi, cmd in enumerate(targets):
        cmdf = _float_row(cmd)
        if not _in_joint_limits(cmdf):
            raise ValueError(f"关节目标 {pi} 超出限位: {cmdf}")
        samples: list[list[float]] = []
        for k in range(repeat_n):
            mc.set_angles(cmdf, speed)
            wait_motion_done(mc)
            act = _float_row(mc.get_angles_info())
            samples.append(act)
            detail.append(
                {
                    "目标点序号": pi + 1,
                    "重复序号": k + 1,
                    "J1反馈(°)": act[0],
                    "J2反馈(°)": act[1],
                    "J3反馈(°)": act[2],
                    "J4反馈(°)": act[3],
                }
            )

        for j, name in enumerate(("J1", "J2", "J3", "J4")):
            col = [s[j] for s in samples]
            mu = statistics.fmean(col)
            sigma = statistics.pstdev(col) if len(col) > 1 else 0.0
            rng = max(col) - min(col)
            summary.append(
                {
                    "目标点序号": pi + 1,
                    "关节": name,
                    "均值(°)": mu,
                    "总体标准差(°)": sigma,
                    "最小值(°)": min(col),
                    "最大值(°)": max(col),
                    "极差(°)": rng,
                    "相对均值最大偏差(°)": max(abs(x - mu) for x in col),
                }
            )

    return detail, summary


def run_absolute_coords(
    mc: UltraArmP1, speed: int, targets: list[list[float]]
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for i, cmd in enumerate(targets):
        cmdf = _float_row(cmd)
        if not _in_coord_limits(cmdf):
            raise ValueError(f"坐标目标 {i} 超出限位: {cmdf}")
        move_to_coords_init(mc, speed)
        mc.set_coords(cmdf, speed)
        wait_motion_done(mc)
        act = _float_row(mc.get_coords_info())
        err = [a - c for a, c in zip(act, cmdf)]
        rows.append(
            {
                "目标点序号": i + 1,
                "X指令(mm)": cmdf[0],
                "Y指令(mm)": cmdf[1],
                "Z指令(mm)": cmdf[2],
                "Rx指令(°)": cmdf[3],
                "X反馈(mm)": act[0],
                "Y反馈(mm)": act[1],
                "Z反馈(mm)": act[2],
                "Rx反馈(°)": act[3],
                "X误差(mm)": err[0],
                "Y误差(mm)": err[1],
                "Z误差(mm)": err[2],
                "Rx误差(°)": err[3],
                "四项最大绝对误差": max(abs(err[0]), abs(err[1]), abs(err[2]), abs(err[3])),
            }
        )
    return rows


def run_repeat_coords(
    mc: UltraArmP1, speed: int, targets: list[list[float]], repeat_n: int 
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    detail: list[dict[str, Any]] = []
    summary: list[dict[str, Any]] = []

    axis_labels = ("X(mm)", "Y(mm)", "Z(mm)", "Rx(°)")

    for pi, cmd in enumerate(targets):
        cmdf = _float_row(cmd)
        if not _in_coord_limits(cmdf):
            raise ValueError(f"坐标目标 {pi} 超出限位: {cmdf}")
        move_to_coords_init(mc, speed)
        samples: list[list[float]] = []
        for k in range(repeat_n):
            mc.set_coords(cmdf, speed)
            wait_motion_done(mc)
            act = _float_row(mc.get_coords_info())
            samples.append(act)
            detail.append(
                {
                    "目标点序号": pi + 1,
                    "重复序号": k + 1,
                    "X反馈(mm)": act[0],
                    "Y反馈(mm)": act[1],
                    "Z反馈(mm)": act[2],
                    "Rx反馈(°)": act[3],
                }
            )

        for j, name in enumerate(axis_labels):
            col = [s[j] for s in samples]
            mu = statistics.fmean(col)
            sigma = statistics.pstdev(col) if len(col) > 1 else 0.0
            summary.append(
                {
                    "目标点序号": pi + 1,
                    "坐标轴": name,
                    "均值": mu,
                    "总体标准差": sigma,
                    "最小值": min(col),
                    "最大值": max(col),
                    "极差": max(col) - min(col),
                    "相对均值最大偏差": max(abs(x - mu) for x in col),
                }
            )

    return detail, summary


def _autosize_columns(ws: Any) -> None:
    for col in ws.columns:
        letter = col[0].column_letter
        maxlen = max(len(str(c.value)) if c.value is not None else 0 for c in col)
        ws.column_dimensions[letter].width = min(maxlen + 2, 48)


def write_workbook(
    path: Path,
    meta: dict[str, Any],
    absolute_angles: list[dict[str, Any]],
    repeat_angle_detail: list[dict[str, Any]],
    repeat_angle_summary: list[dict[str, Any]],
    absolute_coords: list[dict[str, Any]],
    repeat_coord_detail: list[dict[str, Any]],
    repeat_coord_summary: list[dict[str, Any]],
) -> None:
    wb = Workbook()
    ws0 = wb.active
    ws0.title = "测试说明与参数"
    ws0.append(["项目", "内容"])
    for k, v in meta.items():
        ws0.append([k, str(v)])
    ws0["A1"].font = Font(bold=True)
    ws0["B1"].font = Font(bold=True)
    _autosize_columns(ws0)

    def sheet_from_dicts(name: str, rows: list[dict[str, Any]]) -> None:
        ws = wb.create_sheet(name)
        if not rows:
            ws.append(["本表无数据"])
            return
        headers = list(rows[0].keys())
        ws.append(headers)
        for h in ws[1]:
            h.font = Font(bold=True)
        for row in rows:
            ws.append([row[k] for k in headers])
        _autosize_columns(ws)

    sheet_from_dicts("关节绝对精度", absolute_angles)
    sheet_from_dicts("关节重复精度_明细", repeat_angle_detail)
    sheet_from_dicts("关节重复精度_汇总", repeat_angle_summary)
    sheet_from_dicts("笛卡尔绝对精度", absolute_coords)
    sheet_from_dicts("笛卡尔重复精度_明细", repeat_coord_detail)
    sheet_from_dicts("笛卡尔重复精度_汇总", repeat_coord_summary)

    wb.save(path)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="UltraArm P1 定位精度 demo → Excel")
    p.add_argument("--port", default="COM11", help="串口，如 COM10")
    p.add_argument("--baud", type=int, default=1_000_000, help="波特率")
    p.add_argument("--speed", type=int, default=50, help="set_angles / set_coords 速度参数")
    p.add_argument(
        "--repeat",
        type=int,
        default=10,
        help="每个目标点的重复次数（重复定位精度）",
    )
    p.add_argument(
        "--skip-coords",
        action="store_true",
        help="仅测关节空间，跳过笛卡尔段（若逆解不可达可开此项）",
    )
    p.add_argument(
        "--out",
        type=str,
        default="",
        help="输出 xlsx 路径；默认写入 demo/P1_positioning_accuracy_<时间戳>.xlsx",
    )
    return p.parse_args()


def main() -> None:
    args = parse_args()
    demo_dir = Path(__file__).resolve().parent
    out_path = (
        Path(args.out)
        if args.out.strip()
        else demo_dir / f"P1_positioning_accuracy_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    )

    mc = UltraArmP1(args.port, args.baud, debug=1)
    try:
        angle_targets = [list(map(float, x)) for x in DEFAULT_ANGLE_TARGETS]
        coord_targets = [list(map(float, x)) for x in DEFAULT_COORD_TARGETS]

        absolute_angles = run_absolute_angles(mc, args.speed, angle_targets)
        rad, ras = run_repeat_angles(mc, args.speed, angle_targets, args.repeat)

        if args.skip_coords:
            absolute_coords: list[dict[str, Any]] = []
            rcd: list[dict[str, Any]] = []
            rcs: list[dict[str, Any]] = []
        else:
            absolute_coords = run_absolute_coords(mc, args.speed, coord_targets)
            rcd, rcs = run_repeat_coords(mc, args.speed, coord_targets, args.repeat)

        meta = {
            "生成时间": datetime.now().isoformat(timespec="seconds"),
            "串口": args.port,
            "波特率": args.baud,
            "运动速度参数": args.speed,
            "每目标点重复次数": args.repeat,
            "关节限位J1~J4(°)": str(JOINT_LIMITS_DEG),
            "坐标限位(XYZ/Rx)": str(COORD_LIMITS),
            "备注": "误差来自控制器反馈(get_angles_info/get_coords_info)，非外部激光跟踪仪测量",
            "笛卡尔前置关节角(coords_init)": str(COORDS_INIT_ANGLES),
            "LimitError说明": "固件 LimitError:6 为 J2/J3 耦合限位；笛卡尔段已在每次 set_coords 前回到 coords_init",
            "关节测试指令列表": str(angle_targets),
            "笛卡尔测试指令列表": str(coord_targets),
        }
        write_workbook(
            out_path,
            meta,
            absolute_angles,
            rad,
            ras,
            absolute_coords,
            rcd,
            rcs,
        )
        print(f"已保存: {out_path}")
    finally:
        mc.close()


if __name__ == "__main__":
    main()
