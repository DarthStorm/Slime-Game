# SETUP FOR CONSTANTS
import pygame as _pg
import os as _os
from enum import Enum as _enum

if __name__ == "__main__":
    _pg.init()
    _pg.display.set_mode((1, 1))
keys_dict = {
    1: _pg.K_1,
    2: _pg.K_2,
    3: _pg.K_3,
    4: _pg.K_4,
    5: _pg.K_5,
    6: _pg.K_6,
    7: _pg.K_7,
    8: _pg.K_8,
    9: _pg.K_9,
    None: None,
}


def _loadimg(fp):
    "load img:autoapply 'textures\\'"
    return _pg.image.load("textures\\" + fp).convert_alpha()


def _getListOfFiles(dirName):
    listOfFile = _os.listdir(dirName)
    allFiles = []
    for entry in listOfFile:
        fullPath = _os.path.join(dirName, entry)
        if _os.path.isdir(fullPath):
            allFiles = allFiles + _getListOfFiles(fullPath)
        else:
            allFiles.append(fullPath)
    return allFiles


# CONSTANTS

# img:list of images
img: dict[str : _pg.Surface] = {}
for _i in [x.removeprefix("textures\\") for x in _getListOfFiles("textures")]:
    img[_i.removesuffix(".png").replace("\\", "/")] = _loadimg(_i)
# tile:
TILESIZE = 32


class TileTemplate:
    def __init__(
        self,
        type_: str,
        imgs: list[_pg.Surface] = [img["empty"]],
        editorimgs: list[_pg.Surface] | None = None,
        randomtexture: bool = False,
        collidable: bool = False,
        width: int = 32,
        height: int = 32,
        deadly: bool = False,
        key: int | None = None,
    ):
        self.type = type_
        self.imgs = imgs
        self.editorimgs = editorimgs if editorimgs is not None else imgs
        self.randomtexture = randomtexture
        self.collidable = collidable
        self.width = width
        self.height = height
        self.deadly = deadly
        self.key = keys_dict[key]

    def get_texture(self, seed: int | None = None, editor: bool = False, variant=0):
        imgl = (
            self.editorimgs if editor else self.imgs
        )  # switch between editor and normal, so some textures only show in editor
        if (
            seed is not None
        ):  # lemme just inform you that if a list has only one value, you are FORCED to pick the value.
            return imgl[seed % len(imgl)]
        else:
            return imgl[variant]


# To add a new tile, this is the only file you need to change if other effects are not required.


class TILES(_enum):
    NULL = "null"
    AIR = "air"
    PLATFORM_1 = "platform_1"
    SPAWN_POINT = "spawn_point"
    BOUNCE_PAD = "bounce_pad"
    PLATFORM_2 = "platform_2"
    PLATFORM_MIDDLE = "platform_middle"
    GRASS = "grass"
    SPIKE = "spike"
    CRYSTAL = "crystal"
    PLATFORM_TOP = "platform_top"
    PLATFORM_TOPLEFT = "platform_topleft"
    PLATFORM_LEFT = "platform_left"
    PLATFORM_BOTTOMLEFT = "platform_bottomleft"
    PLATFORM_BOTTOM = "platform_bottom"
    PLATFORM_BOTTOMRIGHT = "platform_bottomright"
    PLATFORM_RIGHT = "platform_right"
    PLATFORM_TOPRIGHT = "platform_topright"


# fmt:off

# None: inaccessible through the editor
# 1: platform
# 2: air (bad idea, but not like you have a better one)
# 3: special tiles that affect the gameplay
# 4: D E A T H

tiletemplates = {
    TILES.NULL: TileTemplate(type_=TILES.NULL, imgs=[img["empty"]], key=None),
    TILES.AIR: TileTemplate(type_=TILES.AIR, imgs=[img["empty"]], key=2),
    TILES.PLATFORM_1: TileTemplate(type_=TILES.PLATFORM_1, imgs=[img["tiles/platform"]], collidable=True, key=1),
    
    
    TILES.PLATFORM_TOP: TileTemplate(type_=TILES.PLATFORM_TOP, imgs=[img["tiles/platform_edge_top"]], collidable=True, key=1),
    TILES.PLATFORM_TOPLEFT: TileTemplate(type_=TILES.PLATFORM_TOPLEFT, imgs=[img["tiles/platform_edge_topleft"]], collidable=True, key=1),
    TILES.PLATFORM_LEFT: TileTemplate(type_=TILES.PLATFORM_LEFT, imgs=[img["tiles/platform_edge_left"]], collidable=True, key=1),
    TILES.PLATFORM_BOTTOMLEFT: TileTemplate(type_=TILES.PLATFORM_BOTTOMLEFT, imgs=[img["tiles/platform_edge_bottomleft"]], collidable=True, key=1),
    TILES.PLATFORM_BOTTOM: TileTemplate(type_=TILES.PLATFORM_BOTTOM, imgs=[img["tiles/platform_edge_bottom"]], collidable=True, key=1),
    TILES.PLATFORM_BOTTOMRIGHT: TileTemplate(type_=TILES.PLATFORM_BOTTOMRIGHT, imgs=[img["tiles/platform_edge_bottomright"]], collidable=True, key=1),
    TILES.PLATFORM_RIGHT: TileTemplate(type_=TILES.PLATFORM_RIGHT, imgs=[img["tiles/platform_edge_right"]], collidable=True, key=1),
    TILES.PLATFORM_TOPRIGHT: TileTemplate(type_=TILES.PLATFORM_TOPRIGHT, imgs=[img["tiles/platform_edge_topright"]], collidable=True, key=1),


    TILES.PLATFORM_MIDDLE: TileTemplate(type_=TILES.PLATFORM_MIDDLE, imgs=[img["tiles/platform_middle"]], key=1),
    TILES.SPAWN_POINT: TileTemplate(type_=TILES.SPAWN_POINT,imgs=[img["empty"]],editorimgs=[img["player/player_idle"]],key=3),
    TILES.BOUNCE_PAD: TileTemplate(type_=TILES.BOUNCE_PAD, imgs=[img["tiles/bounce_pad"]], key=3),
    TILES.PLATFORM_2: TileTemplate(type_=TILES.PLATFORM_2,imgs=[img["tiles/platform_straight"]],collidable=True,key=1),
    TILES.GRASS: TileTemplate(type_=TILES.GRASS,imgs=[img["tiles/grass_1"], img["tiles/grass_2"], img["tiles/grass_3"]],collidable=True,key=1),
    TILES.SPIKE: TileTemplate(type_=TILES.SPIKE, imgs=[img["tiles/spike"]], deadly=True, key=4),
    TILES.CRYSTAL: TileTemplate(type_=TILES.CRYSTAL,imgs=[img["tiles/crystal"]],key=3)
}
# fmt:on

# this will be revamped when we add more tiles
order = {
    _pg.K_1: [],
    _pg.K_2: [],
    _pg.K_3: [],
    _pg.K_4: [],
    _pg.K_5: [],
    _pg.K_6: [],
    _pg.K_7: [],
    _pg.K_8: [],
    _pg.K_9: [],
}
for k, v in tiletemplates.items():
    try:
        order[v.key].append(k)
    except KeyError:
        pass


class DEATHS(_enum):
    SPIKE = "spike"
    UNKNOWN = "unknown"


del _pg, _getListOfFiles, _i, _loadimg, _os, _enum
