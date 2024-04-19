# from __future__ import annotations

from pathlib import Path
from typing import List


class Config:
    """
    Runtime configuration for an arkimaps run
    """

    def __init__(self) -> None:
        # Number of orders to bundle in a render script
        self.orders_per_script: int = 16
        # Width of tile-of-tiles grouped rendering (in number of tiles)
        self.tile_group_width: int = 8
        # Height of tile-of-tiles grouped rendering (in number of tiles)
        self.tile_group_height: int = 8
        # Directories where static files are looked up
        self.static_dir: List[Path] = [(Path(__file__).parent / "static").absolute()]
