#SETUP FOR CONSTANTS
import pygame as _pg
import os as _os
import random as _rnd
if __name__ == "__main__":
    _pg.init()
    _pg.display.set_mode((1,1))
_keys_dict = {1:_pg.K_1,2:_pg.K_2,3:_pg.K_3,4:_pg.K_4,5:_pg.K_5,6:_pg.K_6,7:_pg.K_7,8:_pg.K_8,9:_pg.K_9,None:None}

def _loadimg(fp):
    "load img:autoapply 'textures\\'"
    return _pg.image.load("textures\\" + fp).convert_alpha()
def _getListOfFiles(dirName):
    listOfFile = _os.listdir(dirName)
    allFiles = []
    for entry in listOfFile:
        fullPath = _os.path.join(dirName, entry)
        if _os.path.isdir(fullPath):allFiles = allFiles + _getListOfFiles(fullPath)
        else:allFiles.append(fullPath)
    return allFiles


#CONSTANTS
img:dict[str:_pg.Surface] = {}
for _i in [x.removeprefix("textures\\") for x in _getListOfFiles("textures")]:
    img[_i.removesuffix(".png").replace("\\","/")] = _loadimg(_i)

class TileTemplate():
    def __init__(self,type_,imgs=[img["empty"]],randomtexture=False,collidable=False,width=32,height=32,key: int | None = None):
        self.type = type_
        self.imgs = imgs
        self.randomtexture = randomtexture
        self.collidable = collidable
        self.width = width
        self.height = height
        self.key = _keys_dict[key]
    def get_texture(self,seed:int|None=None,variant = 0):
        if seed is not None:#lemme just inform you that if a list has only one value, you are FORCED to pick the value.
            return self.imgs[seed %len(self.imgs)]
        else:
            return self.imgs[variant]
#To add a new tile, this is the only file you need to change if other effects are not required.
tiletemplates = {
    "000":TileTemplate(type_="000",imgs=[img["empty"]],key=None),
    "001":TileTemplate(type_="001",imgs=[img["empty"]],key=2),
    "002":TileTemplate(type_="002",imgs=[img["tiles/platform"]],collidable=True,key=1),
    "003":TileTemplate(type_="003",imgs=[img["empty"]],key=2),
    "004":TileTemplate(type_="004",imgs=[img["tiles/bounce_pad"]],key=3),
    "005":TileTemplate(type_="005",imgs=[img["tiles/platform_straight"]],collidable=True,key=2),
    "006":TileTemplate(type_="006",imgs=[img["tiles/grass_1"],img["tiles/grass_2"],img["tiles/grass_3"]],collidable=True,key=2),
}



del _pg,_getListOfFiles,_i,_loadimg,_os,_keys_dict