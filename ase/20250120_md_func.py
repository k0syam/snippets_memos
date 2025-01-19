#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
ase_utils.py
------------
Collection of utility functions for ASE-based workflows:
 - random structure generation
 - energy minimization (BFGS)
 - MD simulation in various ensembles (NVE, NVT, NPT)
 - quenching with adjustable cooling rate
"""

import os
import numpy as np

from ase import Atoms
from ase.calculators.emt import EMT
from ase.optimize import BFGS
from ase.io import write
from ase.md.velocitydistribution import (MaxwellBoltzmannDistribution,
                                         Stationary)
from ase.md.verlet import VelocityVerlet
from ase.md.langevin import Langevin
from ase.md.nosehoover import NoseHoover
from ase.md.npt import NPT
from ase import units
from ase.io.trajectory import Trajectory


# -------------------------------------------------------------------------
# (1) Random Structure Generation
# -------------------------------------------------------------------------
def generate_random_structure_multi(
    element_ratios,
    total_atoms=100,
    box_size=10.0,
    min_distance=2.0,
    max_attempts=10000,
    pbc=True
):
    """
    複数元素のランダム配置アモルファス初期構造を生成する関数。

    Parameters
    ----------
    element_ratios : dict
        { "Si": 0.5, "O": 0.5 } のように、各元素の比率を指定する辞書。
        合計が1.0になるようにしてください（誤差があれば正規化）。
    total_atoms : int
        配置する総原子数
    box_size : float
        立方体セルの一辺の長さ (Å)
    min_distance : float
        原子間の最小距離(Å)。この距離より近い配置が起きないようにする。
    max_attempts : int
        各原子配置時の最大試行回数。
    pbc : bool or list of bool
        周期境界条件を適用するかどうか。

    Returns
    -------
    atoms : ase.Atoms
        生成されたランダムアトム構造 (周期境界条件つき)。
    """
    # 合計比率が1.0でない場合は正規化
    ratio_sum = sum(element_ratios.values())
    if abs(ratio_sum - 1.0) > 1e-8:
        for k in element_ratios:
            element_ratios[k] = element_ratios[k] / ratio_sum

    # 各元素の個数を計算
    element_counts = {}
    accumulated = 0
    items = list(element_ratios.items())
    for i, (elem, ratio) in enumerate(items):
        if i < len(items) - 1:
            count = int(round(ratio * total_atoms))
        else:
            # 最後の要素は端数をすべて引き受ける
            count = total_atoms - accumulated
        element_counts[elem] = count
        accumulated += count

    # ランダムに配置するためのシンボルリストを作成
    symbols_list = []
    for elem, count in element_counts.items():
        symbols_list.extend([elem]*count)
    np.random.shuffle(symbols_list)

    positions = []
    for symbol in symbols_list:
        attempt = 0
        while True:
            attempt += 1
            if attempt > max_attempts:
                raise RuntimeError(
                    f"Cannot place atom '{symbol}' without violating min_distance={min_distance} "
                    f"after {max_attempts} attempts. Increase box_size or reduce total_atoms."
                )
            x = np.random.rand() * box_size
            y = np.random.rand() * box_size
            z = np.random.rand() * box_size
            new_pos = np.array([x, y, z])

            # 最小距離チェック (PBC考慮)
            too_close = False
            for pos in positions:
                dist_vec = new_pos - pos
                # PBCが有効なら最小イメージで距離を計算
                if pbc is True or (isinstance(pbc, (list, tuple)) and any(pbc)):
                    for i in range(3):
                        if pbc is True or (isinstance(pbc, (list, tuple)) and pbc[i]):
                            if dist_vec[i] > box_size/2:
                                dist_vec[i] -= box_size
                            elif dist_vec[i] < -box_size/2:
                                dist_vec[i] += box_size

                dist = np.linalg.norm(dist_vec)
                if dist < min_distance:
                    too_close = True
                    break

            if not too_close:
                positions.append(new_pos)
                break

    atoms = Atoms(
        symbols=symbols_list,
        positions=positions,
        cell=[box_size]*3,
        pbc=pbc
    )

    return atoms


# -------------------------------------------------------------------------
# (2) Energy Minimization
# -------------------------------------------------------------------------
def energy_minimize(
    atoms,
    calculator=None,
    fmax=0.05,
    max_steps=500,
    logfile="opt.log",
    restart_file="opt_bfgs.pkl"
):
    """
    汎用的なエネルギー最小化関数 (BFGS, リスタート対応)

    Parameters
    ----------
    atoms : ase.Atoms
        対象構造
    calculator : ase.calculators.Calculator or None
        ASEの計算器(EMT, LAMMPS, VASPなど)
        Noneの場合はEMTを使用
    fmax : float
        最大力の収束閾値 (eV/Å)
    max_steps : int
        最大反復ステップ数
    logfile : str
        BFGSのログファイル名
    restart_file : str
        リスタート用のファイル名。存在すれば再開し、なければ新規作成

    Returns
    -------
    float
        最終構造のポテンシャルエネルギー (eV)
    """
    if calculator is None:
        calculator = EMT()
    atoms.calc = calculator

    dyn = BFGS(atoms, logfile=logfile, restart=restart_file)
    dyn.run(fmax=fmax, steps=max_steps)

    return atoms.get_potential_energy()


# -------------------------------------------------------------------------
# (3) Run MD (NVE, NVT, NPT)
# -------------------------------------------------------------------------
def run_md(
    atoms,
    ensemble="NVE",           # "NVE", "NVT", "NPT"
    thermostat="Langevin",    # NVT時のみ使用 ("Langevin" or "NoseHoover")
    temperature=300.0,        # ターゲット温度
    pressure=1.0,             # ターゲット圧力(bar) (NPT時のみ)
    timestep=1.0,             # タイムステップ(fs)
    steps=5000,               # MDステップ数
    friction=0.02,            # ランジュバン法用 摩擦係数(1/fs)
    ttime=25.0,               # 温度ゆらぎ特性時間(fs) (Nosé-Hoover, NPT)
    ptime=100.0,              # 圧力ゆらぎ特性時間(fs) (NPT)
    trajectory="md.traj",
    logfile="md.log",
    calculator=None,
    init_velocities=True,
    remove_translation=True
):
    """
    MDを実行する汎用関数。NVE / NVT(Langevin or Nosé-Hoover) / NPT を切り替え可能。

    Parameters
    ----------
    atoms : ase.Atoms
        MDシミュレーション対象
    ensemble : str
        "NVE", "NVT", or "NPT"
    thermostat : str
        NVT時のサーモスタット: "Langevin" or "NoseHoover"
    temperature : float
        ターゲット温度 (K)
    pressure : float
        ターゲット圧力 (bar) (NPT使用時のみ)
    timestep : float
        タイムステップ (fs)
    steps : int
        総MDステップ数
    friction : float
        ランジュバンの摩擦係数 (1/fs 程度)
    ttime : float
        Nosé-Hoover・NPTの温度制御特性時間 (fs)
    ptime : float
        NPTの圧力制御特性時間 (fs)
    trajectory : str
        トラジェクトリファイル名
    logfile : str
        MDログファイル名
    calculator : ase.calculators.Calculator or None
        使用する計算器(NoneならEMT)
    init_velocities : bool
        Trueなら初期Maxwell-Boltzmann分布を付与
    remove_translation : bool
        Trueなら系全体の並進運動を打ち消す
    """
    if calculator is None:
        calculator = EMT()
    atoms.calc = calculator

    # 初期速度の設定
    if init_velocities:
        MaxwellBoltzmannDistribution(atoms, temperature * units.kB)
    if remove_translation:
        Stationary(atoms)

    dt_ps = timestep / 1000.0  # fs -> ps

    # アンサンブルによる切り替え
    if ensemble.upper() == "NVE":
        dyn = VelocityVerlet(
            atoms,
            dt_ps * units.fs,
            logfile=logfile,
            trajectory=trajectory
        )
    elif ensemble.upper() == "NVT":
        if thermostat.lower() == "langevin":
            dyn = Langevin(
                atoms,
                dt_ps * units.fs,
                temperature * units.kB,
                friction=friction,
                logfile=logfile,
                trajectory=trajectory
            )
        elif thermostat.lower() == "nosehoover":
            dyn = NoseHoover(
                atoms,
                dt_ps * units.fs,
                temperature * units.kB,
                ttime=ttime * units.fs,
                logfile=logfile,
                trajectory=trajectory
            )
        else:
            raise ValueError("Unknown thermostat for NVT: choose 'Langevin' or 'NoseHoover'.")
    elif ensemble.upper() == "NPT":
        # externalstress はスカラーで等方圧指定 (bar単位)
        dyn = NPT(
            atoms,
            dt_ps * units.fs,
            temperature * units.kB,
            externalstress=pressure,  # bar
            ttime=ttime * units.fs,
            ptime=ptime * units.fs,
            logfile=logfile,
            trajectory=trajectory
        )
    else:
        raise ValueError("Invalid ensemble. Must be 'NVE', 'NVT', or 'NPT'.")

    dyn.run(steps)


# -------------------------------------------------------------------------
# (4) Quenching (linearly decrease temperature in NVT)
# -------------------------------------------------------------------------
def quench_structure(
    atoms,
    start_temp=3000.0,
    end_temp=300.0,
    total_steps=5000,
    timestep_fs=1.0,
    thermostat="Langevin",    # or "NoseHoover"
    friction=0.02,
    ttime=25.0,
    calculator=None,
    init_velocity=True,
    remove_translation=True,
    logfile="quench.log",
    trajectory="quench.traj"
):
    """
    指定ステップ数(total_steps)かけて温度を線形に下げるクエンチ (NVT)。
    ThermostatはLangevinまたはNosé-Hooverを選択可能。

    Parameters
    ----------
    atoms : ase.Atoms
        対象構造
    start_temp : float
        開始温度 (K)
    end_temp : float
        終了温度 (K)
    total_steps : int
        MDステップ数 (これだけの間にstart->endへ線形に冷却)
    timestep_fs : float
        タイムステップ (fs)
    thermostat : str
        "Langevin" or "NoseHoover"
    friction : float
        Langevinの摩擦係数 (1/fs)
    ttime : float
        Nosé-Hooverの温度特性時間 (fs)
    calculator : ase.calculators.Calculator or None
        ASE計算器。NoneならEMT
    init_velocity : bool
        Trueならstart_tempで初期速度を付与
    remove_translation : bool
        Trueなら系全体の並進運動を除去
    logfile : str
        MDログ出力ファイル
    trajectory : str
        トラジェクトリ保存ファイル名
    """
    if calculator is None:
        calculator = EMT()
    atoms.calc = calculator

    if init_velocity:
        MaxwellBoltzmannDistribution(atoms, start_temp * units.kB)
    if remove_translation:
        Stationary(atoms)

    dt_ps = timestep_fs / 1000.0

    if thermostat.lower() == "langevin":
        dyn = Langevin(
            atoms,
            dt_ps * units.fs,
            start_temp * units.kB,
            friction=friction,
            logfile=logfile,
            trajectory=None
        )
        # temperature更新は set_temperature()
        def set_temp_func(new_temp):
            dyn.set_temperature(new_temp * units.kB)

    elif thermostat.lower() == "nosehoover":
        dyn = NoseHoover(
            atoms,
            dt_ps * units.fs,
            temperature=start_temp * units.kB,
            ttime=ttime * units.fs,
            logfile=logfile,
            trajectory=None
        )
        # NoseHooverの場合は set_temeq() が温度設定関数
        def set_temp_func(new_temp):
            dyn.set_temeq(new_temp * units.kB)

    else:
        raise ValueError("thermostat must be 'Langevin' or 'NoseHoover'.")

    # Trajectoryを手動管理
    traj = Trajectory(trajectory, 'w', atoms)

    for step in range(total_steps):
        # 線形で温度を下げる
        current_temp = start_temp + (end_temp - start_temp) * (step / total_steps)
        set_temp_func(current_temp)
        dyn.run(1)
        traj.write()

    # 最終時の温度はおおよそ end_temp になる

# -------------------------------------------------------------------------
# もし、このファイルを直接実行した場合のサンプルテスト (main)
# -------------------------------------------------------------------------
def main():
    """
    Example usage of these functions.
    """
    # (A) ランダム構造生成
    element_ratios = {"Si": 0.5, "O": 0.5}
    atoms = generate_random_structure_multi(element_ratios, total_atoms=30, box_size=10.0)

    # (B) エネルギー緩和
    final_e = energy_minimize(atoms, fmax=0.1, max_steps=100)
    print(f"Energy after minimization: {final_e} eV")

    # (C) MD (NVE)
    run_md(
        atoms,
        ensemble="NVE",
        temperature=2000.0,
        timestep=1.0,
        steps=2000,
        trajectory="nve.traj",
        logfile="nve.log"
    )

    # (D) Quench (3000K -> 300K)
    quench_structure(
        atoms,
        start_temp=3000.0,
        end_temp=300.0,
        total_steps=3000,
        thermostat="Langevin",
        friction=0.02,
        trajectory="quench.traj",
        logfile="quench.log"
    )
    print("Done. Quench completed.")


if __name__ == "__main__":
    main()
