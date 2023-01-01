#SETUP FOR CONSTANTS
import pygame as _pg
import os as _os
from enum import Enum as _enum
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
    def __init__(self,type_:str,imgs:list[_pg.Surface]=[img["empty"]],editorimgs:list[_pg.Surface]|None = None,randomtexture:bool=False,collidable:bool=False,width:int=32,height:int = 32,deadly:bool=False,key: int | None = None):
        self.type = type_
        self.imgs = imgs
        self.editorimgs = editorimgs if editorimgs is not None else imgs
        self.randomtexture = randomtexture
        self.collidable = collidable
        self.width = width
        self.height = height
        self.deadly = deadly
        self.key = _keys_dict[key]
    def get_texture(self,seed:int|None=None,editor:bool=False,variant = 0):
        imgl = self.editorimgs if editor else self.imgs#switch between editor and normal, so some textures only show in editor
        if seed is not None:#lemme just inform you that if a list has only one value, you are FORCED to pick the value.
            return imgl[seed %len(imgl)]
        else:
            return imgl[variant]
#To add a new tile, this is the only file you need to change if other effects are not required.
tiletemplates = {
    "000":TileTemplate(type_="000",imgs=[img["empty"]],key=None),
    "001":TileTemplate(type_="001",imgs=[img["empty"]],key=2),
    "002":TileTemplate(type_="002",imgs=[img["tiles/platform"]],collidable=True,key=1),
    "003":TileTemplate(type_="003",imgs=[img["empty"]],editorimgs=[img["player/player_idle"]],key=2),
    "004":TileTemplate(type_="004",imgs=[img["tiles/bounce_pad"]],key=3),
    "005":TileTemplate(type_="005",imgs=[img["tiles/platform_straight"]],collidable=True,key=2),
    "006":TileTemplate(type_="006",imgs=[img["tiles/grass_1"],img["tiles/grass_2"],img["tiles/grass_3"]],collidable=True,key=2),
    "007":TileTemplate(type_="007",imgs=[img["tiles/spike"]],deadly=True,key=4),
}

class DEATHS(_enum):
    SPIKE = "spike"
    UNKNOWN = "unknown"


del _pg,_getListOfFiles,_i,_loadimg,_os,_keys_dict