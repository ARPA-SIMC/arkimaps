from contextlib import contextmanager
from pathlib import Path
from typing import List, Generator


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

    @contextmanager
    def preserve(self) -> Generator[None, None, None]:
        old_orders_per_script = self.orders_per_script
        old_tile_group_width = self.tile_group_width
        old_tile_group_height = self.tile_group_height
        old_static_dir = self.static_dir
        try:
            self.static_dir = list(self.static_dir)
            yield
        finally:
            self.orders_per_script = old_orders_per_script
            self.tile_group_width = old_tile_group_width
            self.tile_group_height = old_tile_group_height
            self.static_dir = old_static_dir
