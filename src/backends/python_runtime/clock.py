from __future__ import annotations


class SimulationClock:
    """仮想シミュレーションクロック。実時間ではなく仮想時間を管理する。"""

    def __init__(self) -> None:
        self._sim_time: float = 0.0
        self._block_start: float = 0.0

    def start_block(self) -> None:
        self._block_start = self._sim_time

    def tick(self, delta: float) -> None:
        self._sim_time += delta

    def simulation_time(self) -> float:
        return self._sim_time

    def elapsed_block_time(self) -> float:
        return self._sim_time - self._block_start
