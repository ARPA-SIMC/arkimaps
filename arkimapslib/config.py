# from __future__ import annotations

import os


class Config:
    """
    Runtime configuration for an arkimaps run
    """
    def __init__(self):
        # Number of orders to bundle in a render script
        self.orders_per_script = 16
        # Width of tile-of-tiles grouped rendering (in number of tiles)
        self.tile_group_width = 8
        # Height of tile-of-tiles grouped rendering (in number of tiles)
        self.tile_group_height = 8
        # Directories where static files are looked up
        self.static_dir = [os.path.abspath(os.path.join(os.path.dirname(__file__), "static"))]
