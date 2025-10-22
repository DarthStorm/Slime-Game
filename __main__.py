from types import UnionType
import pygame, sys, random, json
from io import TextIOWrapper
from textwrap import wrap as strwrap
from math import sin, cos

s = random.randint(1, 100)
displaysize = width, height = (640, 480)
bg_color = (69, 69, 69)

pygame.init()
SCREEN = pygame.display.set_mode(displaysize, pygame.RESIZABLE)  # global
pygame.display.set_caption("platformer v2")
clock = pygame.time.Clock()
# camera
CAMX = 0
CAMY = 0
FPS = 60

# init imgs
from constants import (
    tiletemplates,
    TileTemplate,
    img,
    DEATHS,
    TILES,
    TILESIZE,
    order,
    keys_dict,
)


# functions
def match_tiletemplate(type_: TILES) -> TileTemplate:
    try:
        tt = tiletemplates[type_]
    except KeyError:
        tt = tiletemplates[TILES.NULL]
    return tt


def generatelevel(width, height):
    # fix
    return ("001" * width + "\n") * height


# actual classes
class Particle(pygame.sprite.Sprite):
    def __init__(
        self,
        image: pygame.Surface,
        x: int | float,
        y: int | float,
        xv: int | float,
        yv: int | float,
        angle: int | float,
        ticks: int,
        gravity=True,
    ):
        pygame.sprite.Sprite.__init__(self)
        self.image = image
        self.xv = xv
        self.yv = yv
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.angle = angle
        self.ticks = ticks
        self.gravity = gravity

    def update(self):
        self.ticks -= 1
        if self.gravity:
            self.yv += 1
        if self.ticks <= 0:
            self.kill()
            del self
            return
        rotated_image = pygame.transform.rotate(self.image, self.angle)
        new_rect = rotated_image.get_rect(
            center=self.image.get_rect(
                center=(self.rect.centerx, self.rect.centery)
            ).center
        )
        self.image, self.rect = rotated_image, new_rect
        self.rect.x += self.xv
        self.rect.y += self.yv


class Level:
    """
    wrong place, check the docs at Level.__init__()
    """

    def __init__(self, level: str):
        """
        A level.
        Creates a level. Does not automatically add a player for you though: you HAVE to place it in the level.
        Inputs:
            Level(level:str)

            level is the string (JSON data) passed it to create a level. for example:

            [
                {
                    "x": 32,
                    "y": 96,
                    "type":"platform_1",
                    "width":32,
                    "height":32,
                    "data":""
                },
                {
                    "x": 32,
                    "y": 32,
                    "type": "spawn_point",
                    "width": 32,
                    "height": 32,
                    "data": ""
                }
            ]

            will create a level that looks a bit like this:
            🟩

            ⬜
            where 🟩 is the player and ⬜ is the platform.


        """
        self.levelstr = level

        # self.level = [strwrap(y,3) for y in level.split("\n")]#trust me bro
        # if self.level[-1] == "\n":
        #     #gets rid of the excess \n
        #     self.level.pop()

        self.players = pygame.sprite.Group()
        self.tiles = pygame.sprite.Group()
        self.particles = pygame.sprite.Group()

        # reads level from string
        for i in json.loads(self.levelstr):
            # loops over level tiles.
            # {"x": 32, "y": 0, "type": "003", "width": 32, "height": 32, "data": ""}

            # handle special cases
            match i["type"]:
                case TILES.SPAWN_POINT.value:
                    self.players.add(Player(x=i["x"], y=i["y"]))

            # add the tile, even when handled by special case
            sprite = Tile(
                i["x"],
                i["y"],
                type_=TILES(i["type"]),
                width=i["width"],
                height=i["height"],
                data=i["data"],
            )
            self.tiles.add(sprite)

        # editor-exclusive
        self.editortile = EditorTile()
        self.editor = False

        self.delta = 1000 / FPS  # will change btw

        if len(self.players) == 0:
            tmpplayer = Player(x=0, y=0)
            self.players.add(tmpplayer)
            self.toggle_editor()

    def save(self, file: TextIOWrapper):
        try:
            alltiledata = []
            for tile in self.tiles:
                # changes tiles to just tile id, x,y, and data
                if isinstance(tile, Tile):
                    if tile.type == TILES.AIR or tile.type == TILES.NULL:
                        continue
                    tiledata = {
                        "x": tile.x,
                        "y": tile.y,
                        "type": tile.type.value,
                        "width": tile.width,
                        "height": tile.height,
                        "data": tile.data,
                    }
                    alltiledata.append(tiledata)
            json.dump(alltiledata, file, indent=4)
        except Exception as e:
            print(e)

    def toggle_editor(self):
        """Toggles the editor."""
        for i in self.players:
            i.godmode = not i.godmode
        self.editor = not self.editor

    def tick(self):
        """Tick function: runs every frame."""
        global CAMX, CAMY, width, height
        width, height = SCREEN.get_size()
        # rezero CAMX and CAMY for players (yea, plural form) to add
        CAMX = 0
        CAMY = 0
        self.tiles.update(self.editor)
        self.players.update(self)
        CAMX /= len(self.players)
        CAMY /= len(self.players)
        self.particles.update()
        self.editortile.update(self)

    def draw(self):
        """Draw function: runs every frame."""
        for i in self.tiles:
            SCREEN.blit(i.image, i.rect.move(CAMX, CAMY))
        for i in self.players:
            SCREEN.blit(i.image, i.rect.move(CAMX, CAMY))
        for i in self.particles:
            SCREEN.blit(i.image, i.rect.move(CAMX, CAMY))
        if self.editor:
            self.editortile.draw(SCREEN)


class Tile(pygame.sprite.Sprite):
    """A tile in the level."""

    def __init__(self, x, y, type_=TILES.AIR, width=32, height=32, data=""):
        """A tile in the level."""
        pygame.sprite.Sprite.__init__(self)
        self.x, self.y = x, y
        self.width, self.height = (width, height)
        self.type = type_
        self.data = data

        self.seed = random.randint(1, 100)
        self.image = match_tiletemplate(self.type).get_texture()
        self.rect = self.image.get_rect(topleft=(self.x, self.y))

    def eq(self, other):
        return (
            True
            if (
                self.type == other.type
                and self.x == other.x
                and self.y == other.y
                and self.width == other.width
                and self.height == other.height
                and self.data == other.data
            )
            else False
        )

    def update(self, editor: bool = False):
        """Updates the tile."""
        self.image = match_tiletemplate(self.type).get_texture(
            seed=self.seed + s, editor=editor
        )
        self.rect.x, self.rect.y = self.x, self.y


class ControlVariable:
    """A `ControlVariable` increments by 1 when a (predetermined) key is pressed.
    Thus,\n
    `var = 0` = not pressed at all\n
    `var = 1` = just pressed\n
    `var > 1` = held\n
    `var >= 0` = key down\n"""

    def __init__(self, value: int = 0) -> None:
        self.value = value

    def __int__(self) -> int:
        return self.value

    def __bool__(self) -> bool:
        return False if self.value <= 0 else True

    def __eq__(self, value: object) -> bool:
        return self.__int__() == value

    def __ne__(self, value: object) -> bool:
        return self.__int__() != value

    def __ge__(self, value: object) -> bool:
        return self.__int__() >= value

    def __le__(self, value: object) -> bool:
        return self.__int__() <= value

    def __gt__(self, value: object) -> bool:
        return self.__int__() > value

    def __lt__(self, value: object) -> bool:
        return self.__int__() < value

    def __iadd__(self, value: object):
        if type(value) is type(self):  # is type ControlVariable
            self.value += value.value
        else:
            self.value += value
        return self

    def __isub__(self, value: object):
        if type(value) is type(self):  # is type ControlVariable
            self.value -= value.value
        else:
            self.value -= value
        return self

    def __imul__(self, value: object):
        if type(value) is type(self):  # is type ControlVariable
            self.value *= value.value
        else:
            self.value *= value
        return self

    def __itruediv__(self, value: object):
        if type(value) is type(self):  # is type ControlVariable
            self.value /= value.value
        else:
            self.value /= value
        return self

    def __repr__(self) -> str:
        return str(self.__int__())

    def __str__(self) -> str:
        return str(self.__int__())

    def calcvar(self, pressed: bool) -> int:
        """
        Updates the `ControlVariable`.

        `pressed`: whether or not the key is pressed.

        See class `ControlVariable` for how it works.
        """

        if pressed:
            self.value += 1
        else:
            self.value = 0
        return self.value


class Controls:
    """`this.controls.up` is a lot more readable than `this.controls["up"]`

    Storage container for ControlVariables. See class `ControlVariable` for how they work.
    """

    def __init__(self) -> None:
        self.up = ControlVariable()
        self.down = ControlVariable()
        self.left = ControlVariable()
        self.right = ControlVariable()

    def __repr__(self) -> str:
        return f"<Controls {self.__dict__}>"


class Player(pygame.sprite.Sprite):
    """
    A player.

    Used by the level to spawn a player.
    Parameters:
        Player(x,y,width=32,height=32,accel=1.5,jumpheight=-15,airres=0.85)
        NOTE: All of these are passed in from the level.

        x,y:The absolute position of the player in-game.
        width,height: The size of the player, normally 32*32.
        accel:Acceleration, a multiplier.
        jumpheight:How high the player can jump:keep in mind it is NEGATIVE due to how pygame's display works.
        airres:Air resistance to slow the player down, a multiplier.

    """

    def __init__(
        self,
        x,
        y,
        basewidth=32,
        baseheight=32,
        accel=15,
        jumpheight=-12,
        gravity=0.8,
        airres=0.8,
    ):
        """Initialises the player. See class Player."""
        pygame.sprite.Sprite.__init__(self)
        # set base attrs
        self.spawnx, self.spawny = x, y
        self.accel = accel
        self.jumpheight = jumpheight
        self.airres = airres
        self.basewidth = basewidth
        self.baseheight = baseheight
        self.gravity = gravity
        self.godmode = False  # start with editor off
        self.controls = Controls()

        self.respawn()
        self.movecam()

    def respawn(self):
        """Respawns the player."""

        self.respawntimer = -1  # player alive when respawntimer <= 0

        # controls (see getControls for details)
        self.up = 0
        self.down = 0
        self.left = 0
        self.right = 0

        # x, y, width, height
        self.x, self.y = self.spawnx, self.spawny
        self.width, self.height = (
            self.basewidth,
            self.baseheight,
        )  # ok why did i do this

        # set velocities
        self.xv = 0
        self.yv = 0

        # player cannot jump when just spawned, must be greater than coyote threshold
        self.airtime = 999

        # walljump
        self.hanging = 0
        self.lostcontrol = 0
        self.enterdirection = 0

        # textures
        self.frame = 0  # chooses which blob stage to use
        self.imgname = "player/player_idle"
        self.image = img[self.imgname]

        # rect
        self.rect = self.image.get_rect(topleft=(self.x, self.y))

    def movecam(self):
        """Moves the camera."""
        global CAMX, CAMY  # this will bite me back
        CAMX += -self.rect.centerx + width / 2
        CAMY += -self.rect.centery + height / 2

    def switch_texture(self):
        """
        Updates player.image for animation.
        If the animation needs to be changed, ig you fix this function? also constants
        """
        # if player dead:
        if self.respawntimer > 0:
            self.image = img["empty"]
            return

        self.frame += 1

        # special cases (not walking, jumping, falling, or doing nothing)
        # wallhanging
        if self.hanging > 0:
            self.imgname = "player/player_wallhang"
            self.image = img[self.imgname]
            if self.enterdirection < 0:
                self.image = pygame.transform.flip(self.image, True, False)

        else:
            # in air
            if self.airtime > 3:
                if self.airtime < 5:
                    self.imgname = "player/player_blob_3"
                elif (
                    5 <= self.airtime and self.airtime < 7
                ):  # python needs to add 5 <= self.airtime < 7
                    self.imgname = "player/player_blob_4"
                else:
                    self.imgname = "player/player_blob_5"
                self.image = img[self.imgname]
                if self.xv < 0:
                    self.image = pygame.transform.flip(self.image, True, False)
            # not in air
            # walking
            elif abs(self.xv) > 1:
                self.imgname = "player/player_blob_" + str(int((self.frame) % 10))
                self.image = img[self.imgname]
                if self.xv < 0:  # flip if turning left
                    self.image = pygame.transform.flip(self.image, True, False)
            # not walking
            else:
                if "player/player_blob_" in self.imgname:
                    # round off blob animation, so it ends smoothly
                    if (
                        int(self.imgname[-1]) < 9
                    ):  # conversion to int error cannot happen
                        self.imgname = self.imgname[:-1] + str(
                            int(self.imgname[-1]) + 1
                        )
                    else:
                        self.imgname = "player/player_idle"
                else:
                    self.imgname = "player/player_idle"

                self.image = img[self.imgname]
                self.frame = 0

    def get_controls(self):
        """Gets the controls. See class `Controls` for how the variables work.

        TODO: when i get internet search up getters and setters to make this better"""

        keys = pygame.key.get_pressed()

        self.controls.up.calcvar(keys[pygame.K_w] or keys[pygame.K_UP])
        self.controls.down.calcvar(keys[pygame.K_s] or keys[pygame.K_DOWN])
        self.controls.left.calcvar(keys[pygame.K_a] or keys[pygame.K_LEFT])
        self.controls.right.calcvar(keys[pygame.K_RIGHT] or keys[pygame.K_d])

    def update(self, level: Level):
        """Updates the player."""
        keys = pygame.key.get_pressed()
        self.get_controls()
        if self.godmode:
            self.airtime = 0
            self.xv += (
                ((self.controls.right > 0) - (self.controls.left > 0))
                * self.accel
                * 1.4
                * level.delta
            )
            self.xv *= self.airres
            self.yv += (
                ((self.controls.down > 0) - (self.controls.up > 0))
                * self.accel
                * 1.4
                * level.delta
            )
            self.yv *= self.airres
            self.x += self.xv
            self.y += self.yv
            self.rect.x = self.x
            self.rect.y = self.y
        elif self.respawntimer > 0:  # player dead
            self.respawntimer -= 1
            if self.respawntimer == 0:
                self.respawn()
        else:
            # player is still alive

            self.hanging -= 1
            self.lostcontrol -= 1
            # check if player is hanging from a wall, if not, then continue as normal.

            if self.hanging > 0:
                # launch player from wall
                self.airtime = 999
                self.yv = 0
                if keys[pygame.K_w] or keys[pygame.K_UP]:
                    self.xv = self.enterdirection * self.jumpheight * 1.4 * level.delta
                    self.yv = self.jumpheight * 1.4 * level.delta
                    self.hanging = 0
                    self.lostcontrol = 5
            else:
                # fall as normal
                self.yv += self.gravity * level.delta
                self.airtime += 30 * level.delta

                # handle controls
                if self.lostcontrol < 0:  # block if player just jumped from a wall
                    # xv
                    self.xv += (
                        (
                            (keys[pygame.K_RIGHT] or keys[pygame.K_d])
                            - (keys[pygame.K_LEFT] or keys[pygame.K_a])
                        )
                        * self.accel
                        * level.delta
                    )
                    # yv
                    if self.airtime < 3 and (keys[pygame.K_w] or keys[pygame.K_UP]):
                        self.yv = self.jumpheight * level.delta
                    self.xv *= self.airres
                else:
                    self.xv *= self.airres * 1.1 if self.airres * 1.1 < 1 else 0.99

                # update x & y
                self.x += self.xv
                self.y += self.yv

                # really update the position and also add collision

                # collision x:
                self.rect.x = self.x
                for i in level.tiles:
                    if (
                        self.rect.colliderect(i)
                        and match_tiletemplate(i.type).collidable
                    ):
                        if self.xv > 0:
                            for _ in range(100):
                                self.rect.x -= 1
                                if not self.rect.colliderect(i):
                                    break
                        elif self.xv < 0:
                            for _ in range(100):
                                self.rect.x += 1
                                if not self.rect.colliderect(i):
                                    break
                        if abs(self.xv) > 3 and self.yv != 1:
                            self.hanging = 60
                            self.enterdirection = self.xv / abs(self.xv)
                        self.xv = 0
                        self.x = self.rect.x
                # collision y:
                self.rect.y = self.y
                for i in level.tiles:
                    if (
                        self.rect.colliderect(i)
                        and match_tiletemplate(i.type).collidable
                    ):
                        if self.yv > 0:
                            for _ in range(100):
                                self.rect.y -= 1
                                if not self.rect.colliderect(i):
                                    break
                            self.airtime = 0
                        elif self.yv < 0:
                            for _ in range(100):
                                self.rect.y += 1
                                if not self.rect.colliderect(i):
                                    break
                        self.yv = 0
                        self.y = self.rect.y

            # trigger effects of special tiles
            for i in pygame.sprite.spritecollide(self, level.tiles, False):
                if match_tiletemplate(i.type).deadly:
                    self.triggerdeath(level, cause=DEATHS.SPIKE)
                if i.type == TILES.BOUNCE_PAD:  # bounce pad
                    self.yv = -600 * level.delta

        print(self.x, self.y, self.xv, self.yv)
        self.switch_texture()
        self.movecam()

    def triggerdeath(self, level: Level, cause=DEATHS.UNKNOWN):
        """Triggers the death of the player."""
        match cause:
            case DEATHS.SPIKE:
                for _ in range(5):
                    _x = random.random() * 2 + 5
                    ps = pygame.Surface(size=(_x, _x), flags=pygame.SRCALPHA)
                    ps.fill((109, 231, 117))
                    particle = Particle(
                        ps,
                        self.x + self.width / 2,
                        self.y + self.height / 2,
                        random.random() * 12 - 6,
                        random.random() * 16 - 10,
                        0,
                        30,
                    )
                    level.particles.add(particle)
                self.respawntimer = 50
            case _:
                self.respawn()


class EditorTile(pygame.sprite.Sprite):
    """
    Sprite that does all the actual editing.

    Inputs:
        EditorTile(width=32,height=32)
        width,height:Self-explanatory.
    """

    def __init__(self, width=32, height=32):
        """Initialises the EditorTile. See class EditorTile."""
        pygame.sprite.Sprite.__init__(self)
        self.width, self.height = (width, height)
        self.brush = TILES.PLATFORM_1

        self.image = match_tiletemplate(self.brush).get_texture(editor=True)
        self.rect = self.image.get_rect()
        # ok remember to blit the IMAGE and not the sprite

    def update(self, lvl: Level):
        """Updates the EditorTile."""
        if lvl.editor == False:
            return
        mouse = pygame.mouse
        mousepos = mouse.get_pos()  # mp means mouse pos
        self.rect.x, self.rect.y = ((mousepos[0]) // 32) * 32 + CAMX % 32, (
            (mousepos[1]) // 32
        ) * 32 + CAMY % 32
        self.image = match_tiletemplate(self.brush).get_texture(editor=True)

        # 0 = left click
        mousepressed = mouse.get_pressed()

        tgx = int((self.rect.x - CAMX) // 32)
        tgy = int((self.rect.y - CAMY) // 32)
        if mousepressed[0]:
            if isinstance(lvl, Level):
                # check if air is selected, and if it is, activate delete mode
                # should be fixed
                if self.brush == TILES.AIR:
                    # delete stuff

                    # get tile touching editor mouse
                    # (closest)
                    # tile to delete is the tile to delete
                    # istg this can certainly be made WAYYYYYY easier
                    tiletodelete = Tile(0, 0)
                    for i in lvl.tiles:
                        if isinstance(i, Tile):
                            if (
                                mousepos[0] - CAMX > i.x
                                and mousepos[0] - CAMX < i.x + i.width
                                and mousepos[1] - CAMY > i.y
                                and mousepos[1] - CAMY < i.y + i.height
                            ):
                                tiletodelete = i
                    tiletodelete.kill()

                else:
                    # avoid holding down placing multiple tiles at once
                    newtile = Tile(self.rect.x - CAMX, self.rect.y - CAMY, self.brush)

                    for tile in lvl.tiles:
                        if newtile.eq(tile):
                            break
                    else:
                        lvl.tiles.add(newtile)

        if mousepressed[1]:
            tile = Tile(0, 0)
            for i in lvl.tiles:
                if isinstance(i, Tile):
                    if (
                        mousepos[0] - CAMX > i.x
                        and mousepos[0] - CAMX < i.x + i.width
                        and mousepos[1] - CAMY > i.y
                        and mousepos[1] - CAMY < i.y + i.height
                    ):
                        tile = i
            self.brush = tile.type

    def nexttile(self, key):
        """
        Gets the next tile for the key.
        key: the keycode
        """

        # gets the index of the key
        try:
            idx = order[key].index(self.brush)
            self.brush = order[key][idx + 1]
        except (ValueError, IndexError):
            # IndexError: list index out of range, set back to 0
            # ValueError: if we are not on the key group, jump to the first key
            try:
                idx = 0
                self.brush = order[key][idx]
            except IndexError:
                # we get another error: the key group has nothing in it
                # don't touch the brush in this case, the key should not work
                # will be useless when all key groups are filled, but by then maybe i have a better editor system
                pass

    def draw(self, surf: pygame.surface.Surface):
        """A custom draw method for the EditorTile to support alpha."""
        _tmpimg = self.image.copy()
        _tmpimg.set_alpha(56)
        surf.blit(_tmpimg, (self.rect.x, self.rect.y))


# init before game:
def runlevel(lvlname):
    """Runs the level."""
    ls = ""  # level string
    with open(lvlname, "r") as f:
        ls = f.read()

    level = Level(ls)
    running = True
    # main game loop
    while running:
        # handle events
        for event in pygame.event.get():
            # check if user wants to quit
            if event.type == pygame.QUIT:
                # save level
                with open(lvlname, "w") as f:
                    level.save(f)
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_0:
                    level.toggle_editor()
                elif event.key in order.keys():
                    level.editortile.nexttile(event.key)
                elif event.key == pygame.K_r:
                    [p.respawn() for p in level.players]
            # elif event.type == pygame.KEYDOWN and event.key in [pygame.K_1,pygame.K_2,pygame.K_3,pygame.K_4,pygame.K_5,pygame.K_6,pygame.K_7,pygame.K_8,pygame.K_9]:
            # level.et.next_key(event.key)
        level.delta = clock.tick(FPS) / 1000

        # tick can be here or with draw
        SCREEN.fill(bg_color)
        level.tick()
        level.draw()
        pygame.display.update()


runlevel("level.json")

pygame.quit()
sys.exit()
