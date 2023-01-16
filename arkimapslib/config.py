# from __future__ import annotations

class Config:
    def __init__(self):
        # Number of orders to bundle in a render script
        self.orders_per_script = 16
        # Width of tile-of-tiles grouped rendering (in number of tiles)
        self.tile_group_width = 8
        # Height of tile-of-tiles grouped rendering (in number of tiles)
        self.tile_group_height = 8
