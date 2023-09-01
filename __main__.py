import pygame,sys,random
from textwrap import wrap as strwrap
from math import sin,cos
s = random.randint(1,100)
displaysize = width,height = (640,480)
bg_color = (69,69,69)

pygame.init()
SCREEN = pygame.display.set_mode(displaysize,pygame.RESIZABLE)#global
pygame.display.set_caption("platformer v2")
clock = pygame.time.Clock()
#camera
CAMX = 0
CAMY = 0
FPS = 30

#init imgs
from constants import tiletemplates,TileTemplate,img,DEATHS
#functions
def match_tiletemplate(type_:str) -> TileTemplate:
    try:
        tt = tiletemplates[type_]
    except KeyError:
        tt = tiletemplates["000"]
    return tt     

def generatelevel(width,height):
    return(("001"*width+"\n")*height)

#actuual classes
class Particle(pygame.sprite.Sprite):
    def __init__(self,image:pygame.Surface,x:int|float,y:int|float,xv:int|float,yv:int|float,angle:int|float,ticks:int,gravity=True):
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
        if self.gravity:self.yv += 1
        if self.ticks <= 0:
            self.kill()
            del self
            return
        rotated_image = pygame.transform.rotate(self.image,self.angle)
        new_rect = rotated_image.get_rect(center = self.image.get_rect(center = (self.rect.centerx,self.rect.centery)).center)
        self.image,self.rect = rotated_image, new_rect
        self.rect.x += self.xv
        self.rect.y += self.yv
        
class Level():
    """
    A level.
    Creates a level. Does not automatically add a player for you though: you HAVE to place it in the level.
    Inputs:    
        Level(level:str)
        
        level is the string passed it to create a level. for example:
        \"\"\"001003001
        001001001
        001002001
        \"\"\"
        will create a level that looks a bit like this:
          🟩

          ⬜
        where 🟩 is the player and ⬜ is the platform.

        
    """
    def __init__(self,level:str):
        """Initialises the level. See class Level."""
        self.levelstr = level

        self.level = [strwrap(y,3) for y in level.split("\n")]#trust me bro
        self.level.pop()#gets rid of the excess \n

        self.players = pygame.sprite.Group()
        self.tiles = pygame.sprite.Group()

        #reads level from string
        for y,row in enumerate(self.level):
            for x,tiletype in enumerate(row):
                match tiletype:
                    case "003":#player
                        sprite = Player(x,y)
                        self.players.add(sprite)
                sprite = Tile(x,y,type_ = tiletype)
                self.tiles.add(sprite)

        self.particles = pygame.sprite.Group()

        #editor-exclusive
        self.et = EditorTile()
        self.editor = False

    def toggle_editor(self):
        """Toggles the editor."""
        for i in self.players:
            i.godmode = not i.godmode
        self.editor = not self.editor

    def tick(self):
        
        """Tick function: runs every frame."""
        global CAMX,CAMY,width,height
        width,height=SCREEN.get_size()
        #rezero CAMX and CAMY for players (yea, plural form) to add
        CAMX = 0
        CAMY = 0
        self.tiles.update(self.editor)
        self.players.update(self)
        CAMX /= len(self.players)
        CAMY /= len(self.players)
        self.particles.update()
        self.et.update(self)

    def draw(self):
        """Draw function: runs every frame."""
        for i in self.tiles:SCREEN.blit(i.image,i.rect.move(CAMX,CAMY))
        for i in self.players:SCREEN.blit(i.image,i.rect.move(CAMX,CAMY))
        for i in self.particles:SCREEN.blit(i.image,i.rect.move(CAMX,CAMY))
        if self.editor:self.et.draw(SCREEN)

class Tile(pygame.sprite.Sprite):
    """A tile in the level."""
    def __init__(self,x,y,type_ = "001",width=32,height=32):
        """Initialises the tile. See class Tile."""
        pygame.sprite.Sprite.__init__(self)
        self.x,self.y = (x*32,y*32)
        self.tgx,self.tgy = x,y
        self.width,self.height = (width,height)
        self.type = type_

        self.seed = random.randint(1,100)
        self.image = match_tiletemplate(self.type).get_texture()
        self.rect = self.image.get_rect(topleft=(self.x,self.y))
    def update(self,editor:bool=False):
        """Updates the tile."""
        self.image = match_tiletemplate(self.type).get_texture(seed=self.seed + s,editor = editor)
        self.rect.x,self.rect.y = self.x,self.y
    
class Player(pygame.sprite.Sprite):
    """
    A player.

    Used by the level to spawn a player.
    Inputs:
        Player(x,y,width=32,height=32,accel=1.5,jumpheight=-15,airres=0.85)
        NOTE: All of these are passed in from the level.

        x,y:The absolute position of the player in-game. These are NOT passed to rect.x and rect.y.
        width,height: The size of the player, normally 32*32.
        accel:Acceleration, a multiplier.
        jumpheight:How high the player can jump:keep in mind it is NEGATIVE due to how pygame's display works.
        airres:Air resistance to slow the player down, a multiplier.
        
    """
    def __init__(self,x,y,basewidth=32,baseheight=32,accel=1.5,jumpheight=-15,airres=0.85):
        """Initialises the player. See class Player."""
        pygame.sprite.Sprite.__init__(self)
        self.spawnx,self.spawny = x*32,y*32
        self.accel = accel
        self.jumpheight = jumpheight
        self.airres = airres
        self.godmode = False
        self.basewidth = basewidth
        self.baseheight = baseheight
        self.respawn()
        self.movecam()
    def respawn(self):
        self.respawntimer = -1 #not dead
        self.x,self.y = self.spawnx,self.spawny
        self.width,self.height = self.basewidth,self.baseheight
        self.xv = 0
        self.yv = 0
        self.airtime = 999
        self.frame = 0
        self.imgname = "player/player_idle"
        self.image = img[self.imgname]
        self.rect = self.image.get_rect(topleft=(self.x,self.y))
        
    def movecam(self):
        """Moves the camara."""
        global CAMX,CAMY
        CAMX += -self.rect.centerx + width/2
        CAMY += -self.rect.centery + height/2

    def switch_texture(self):
        """
        Updates player.image for animation.
        If the animation needs to be changed, ig you fix this function? also constants
        """
        #if player dead:
        if self.respawntimer > 0:
            self.image = img["empty"]
            return

        self.frame += 1
        if self.airtime > 3:
            if self.airtime < 5:self.imgname = "player/player_blob_3"
            elif 5 <= self.airtime and self.airtime < 7:self.imgname = "player/player_blob_4"
            else:self.imgname = "player/player_blob_5"
            self.image = img[self.imgname]
            if self.xv < 0:self.image = pygame.transform.flip(self.image,True,False)
        elif abs(self.xv) > 1:
            self.imgname = "player/player_blob_" + str(int((self.frame) % 10))
            self.image = img[self.imgname]
            if self.xv < 0:self.image = pygame.transform.flip(self.image,True,False)
        else:
            if "player/player_blob_" in self.imgname:
                if int(self.imgname[-1]) < 9:#conversion to int error cannot happen
                    self.imgname = self.imgname[:-1] + str(int(self.imgname[-1]) + 1)
                else:self.imgname = "player/player_idle"
            else:self.imgname = "player/player_idle"
                        
            self.image = img[self.imgname]
            self.frame = 0

    def update(self,level:Level):
        """Updates the player."""
        keys = pygame.key.get_pressed()
        if self.godmode:
            self.xv += ((keys[pygame.K_RIGHT] or keys[pygame.K_d])-(keys[pygame.K_LEFT] or keys[pygame.K_a])) * self.accel * 1.5
            self.xv *= self.airres
            self.yv += ((keys[pygame.K_s] or keys[pygame.K_DOWN])-(keys[pygame.K_w] or keys[pygame.K_UP])) * self.accel * 1.5
            self.yv *= self.airres
            self.x += self.xv
            self.y += self.yv
            self.rect.x = self.x
            self.rect.y = self.y
        elif self.respawntimer > 0:
            self.respawntimer -= 1
            if self.respawntimer == 0:
                self.respawn()
        else:
            #player is still alive
            self.yv += 1
            self.airtime += 1

            #xv
            self.xv += ((keys[pygame.K_RIGHT] or keys[pygame.K_d])-(keys[pygame.K_LEFT] or keys[pygame.K_a])) * self.accel
            self.xv *= 0.85
            
            #yv
            if self.airtime < 3 and (keys[pygame.K_w] or keys[pygame.K_UP]):
                self.yv = self.jumpheight

            #update x & y
            self.x += self.xv
            self.y += self.yv

            #really update the position and also add collision

            #collision x:
            self.rect.x = self.x
            for i in level.tiles:
                if self.rect.colliderect(i) and match_tiletemplate(i.type).collidable:
                    if self.xv > 0:
                        for _ in range(100):
                            self.rect.x -= 1
                            if not self.rect.colliderect(i):break
                    elif self.xv < 0:
                        for _ in range(100):
                            self.rect.x += 1
                            if not self.rect.colliderect(i):break
                    self.xv = 0
                    self.x = self.rect.x
            #collision y:
            self.rect.y = self.y
            for i in level.tiles:
                if self.rect.colliderect(i) and match_tiletemplate(i.type).collidable:
                    if self.yv > 0:
                        for _ in range(100):
                            self.rect.y -= 1
                            if not self.rect.colliderect(i):break
                        self.airtime = 0
                    elif self.yv < 0:
                        for _ in range(100):
                            self.rect.y += 1
                            if not self.rect.colliderect(i):break
                    self.yv = 0
                    self.y = self.rect.y

            #trigger effects of special tiles
            for i in pygame.sprite.spritecollide(self,level.tiles,False):
                if match_tiletemplate(i.type).deadly:
                    self.triggerdeath(level,cause=DEATHS.SPIKE)
                if i.type == "004":#bounce pad
                    self.yv = -20
            
                
        self.switch_texture()
        self.movecam()

    def triggerdeath(self,level:Level,cause=DEATHS.UNKNOWN):
        """Triggers the death of the player."""
        match cause:
            case DEATHS.SPIKE:
                for _ in range(5):
                    _x = random.random() * 2 + 5
                    ps = pygame.Surface(size=(_x,_x),flags=pygame.SRCALPHA)
                    ps.fill((109,231,117))
                    particle = Particle(ps,self.x+self.width/2,self.y+self.height/2,random.random() * 12 - 6,random.random() * 16 - 10,0,30)
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
    def __init__(self,width=32,height=32):
        """Initialises the EditorTile. See class EditorTile."""
        pygame.sprite.Sprite.__init__(self)
        self.width,self.height = (width,height)
        self.brush = "002"

        self.image = match_tiletemplate(self.brush).get_texture(editor=True)
        self.rect = self.image.get_rect()
        #ok remember to blit the IMAGE and not the sprite
    def update(self,lvl:Level):
        """Updates the EditorTile."""
        if lvl.editor == False:return
        mouse = pygame.mouse
        mp = mouse.get_pos()#mp means mouse pos
        self.rect.x,self.rect.y = ((mp[0]) // 32)*32 + CAMX%32,((mp[1]) // 32)*32 + CAMY%32
        self.image = match_tiletemplate(self.brush).get_texture(editor=True)
        #now mp means mouse pressed
        #0 = left click
        #don't worry, these are just temp vars, not using them outside this func
        mp = mouse.get_pressed()

        tgx = int((self.rect.x - CAMX)//32)
        tgy = int((self.rect.y - CAMY)//32)
        if mp[0]:
            try:
                lvl.level[tgy][tgx] = self.brush
                #a rather long winded solution
                for i in lvl.tiles:
                    if i.tgx == tgx and i.tgy == tgy:
                        i.type=self.brush
                        break#reduce lag?

            except IndexError:pass
        if mp[1]:
            try:
                self.brush = lvl.level[tgy][tgx]
            except IndexError:pass

    def nextkey(self):
        print(str(int(self.brush)+1).zfill(3),int(self.brush)+1,"001",sep="\n")
        self.brush = str(int(self.brush)+1).zfill(3) if int(self.brush)+1 < len(tiletemplates) else "001"
        print(self.brush)

    def prevkey(self):
        print(str(int(self.brush)-1).zfill(3),int(self.brush)-1,str(len(tiletemplates)-1).zfill(3),sep="\n")
        self.brush = str(int(self.brush)-1).zfill(3) if int(self.brush)-1 > 1 else str(len(tiletemplates)-1).zfill(3)
        print(self.brush)

    def draw(self,surf:pygame.surface.Surface):
        """A custom draw method for the EditorTile to support alpha."""
        _tmpimg = self.image.copy()
        _tmpimg.set_alpha(56)
        surf.blit(_tmpimg,(self.rect.x,self.rect.y))

#init before game:
def runlevel(lvlname):
    """Runs the level."""
    ls = ""#level string
    with open(lvlname,"r") as f:
        ls = f.read()

    level = Level(ls)
    running = True
    #main game loop
    while running:
        #handle events
        for event in pygame.event.get():
            #check if user wants to quit
            if event.type == pygame.QUIT:
                #save level
                with open("level.txt","w") as f:
                    f.writelines(["".join(i) + "\n" for i in level.level])
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_0:level.toggle_editor()
                elif event.key == pygame.K_MINUS:level.et.prevkey()
                elif event.key == pygame.K_EQUALS:level.et.nextkey()
                elif event.key == pygame.K_r:[p.respawn() for p in level.players]
            #elif event.type == pygame.KEYDOWN and event.key in [pygame.K_1,pygame.K_2,pygame.K_3,pygame.K_4,pygame.K_5,pygame.K_6,pygame.K_7,pygame.K_8,pygame.K_9]:
                #level.et.next_key(event.key)
            
        #tick can be here or with draw
        SCREEN.fill(bg_color)
        level.tick()
        level.draw()
        pygame.display.update()
        clock.tick(FPS)

runlevel("level.txt")

pygame.quit()
sys.exit()