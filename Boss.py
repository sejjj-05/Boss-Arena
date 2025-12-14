import pygame, sys, math, random
pygame.init()
W,H=800,600
S=pygame.display.set_mode((W,H))
pygame.display.set_caption("Boss Arena")
C=pygame.time.Clock()
F=60
FONT=pygame.font.SysFont(None,36)
SMALL=pygame.font.SysFont(None,24)

class Player:
    def __init__(self):
        self.x=W*0.2
        self.y=H*0.5
        self.r=18
        self.sp=3.2
        self.hp=100
        self.max_hp=100
        self.ifr=0
        self.dodge_cd=0
        self.shoot_cd=0
        self.color=(50,180,255)
    def rect(self):
        return pygame.Rect(int(self.x-self.r),int(self.y-self.r),self.r*2,self.r*2)
    def update(self,keys,mouse):
        vx=(keys[pygame.K_d]-keys[pygame.K_a])
        vy=(keys[pygame.K_s]-keys[pygame.K_w])
        m=math.hypot(vx,vy)
        if m>0:
            vx/=m; vy/=m
        sp=self.sp
        if self.ifr>0: sp=self.sp*1.2
        self.x+=vx*sp
        self.y+=vy*sp
        self.x=max(40,min(W-40,self.x))
        self.y=max(60,min(H-40,self.y))
        if self.ifr>0: self.ifr-=1
        if self.dodge_cd>0: self.dodge_cd-=1
        if self.shoot_cd>0: self.shoot_cd-=1
    def dodge(self,dirx,diry):
        if self.dodge_cd==0:
            m=math.hypot(dirx,diry)
            if m==0: dirx,diry=1,0
            else: dirx/=m; diry/=m
            self.x+=dirx*80
            self.y+=diry*80
            self.ifr=24
            self.dodge_cd=60
    def shoot(self,tx,ty):
        if self.shoot_cd==0:
            dx=tx-self.x; dy=ty-self.y
            m=math.hypot(dx,dy)
            if m==0: dx,dy=1,0
            else: dx/=m; dy/=m
            self.shoot_cd=12
            return Bullet(self.x,self.y,dx*6,dy*6,8,(255,255,80),False)
        return None
    def draw(self):
        pygame.draw.circle(S,self.color,(int(self.x),int(self.y)),self.r)

class Boss:
    def __init__(self):
        self.x=W*0.7
        self.y=H*0.5
        self.r=26
        self.hp=220
        self.max_hp=220
        self.color=(255,80,80)
        self.pattern_cd=90
        self.charge_cd=240
        self.charge_windup=0
        self.vx=0; self.vy=0
        self.base_sp=1.4
        self.flash=0
    def rect(self):
        return pygame.Rect(int(self.x-self.r),int(self.y-self.r),self.r*2,self.r*2)
    def update(self,player):
        if self.flash>0: self.flash-=1
        self.pattern_cd-=1
        self.charge_cd-=1
        if self.charge_windup>0:
            self.charge_windup-=1
            if self.charge_windup==0:
                dx=player.x-self.x; dy=player.y-self.y
                m=math.hypot(dx,dy)
                if m==0: dx,dy=1,0
                else: dx/=m; dy/=m
                self.vx=dx*7; self.vy=dy*7
        else:
            if abs(self.vx)>0.1 or abs(self.vy)>0.1:
                self.x+=self.vx; self.y+=self.vy
                self.vx*=0.95; self.vy*=0.95
            else:
                dx=player.x-self.x; dy=player.y-self.y
                m=math.hypot(dx,dy)
                if m>0:
                    dx/=m; dy/=m
                self.x+=dx*self.base_sp*0.8
                self.y+=dy*self.base_sp*0.8
        self.x=max(60,min(W-60,self.x))
        self.y=max(80,min(H-60,self.y))
    def take_hit(self,dmg):
        self.hp=max(0,self.hp-dmg); self.flash=6
    def draw(self):
        c=self.color if self.flash%2==0 else (255,200,200)
        pygame.draw.circle(S,c,(int(self.x),int(self.y)),self.r)
    def maybe_pattern(self,bullets):
        out=[]
        if self.pattern_cd<=0:
            self.pattern_cd=90
            n=18
            sp=3.2
            for i in range(n):
                ang=2*math.pi*i/n
                out.append(Bullet(self.x,self.y,math.cos(ang)*sp,math.sin(ang)*sp,6,(255,140,0),True))
        if self.charge_cd<=0 and self.charge_windup==0:
            self.charge_cd=240
            self.charge_windup=45
        return out

class Bullet:
    def __init__(self,x,y,vx,vy,r,color,enemy):
        self.x=x; self.y=y
        self.vx=vx; self.vy=vy
        self.r=r
        self.color=color
        self.enemy=enemy
        self.alive=True
        self.dmg=10 if enemy else 14
    def update(self):
        self.x+=self.vx; self.y+=self.vy
        if self.x<-20 or self.x>W+20 or self.y<-20 or self.y>H+20:
            self.alive=False
    def draw(self):
        pygame.draw.circle(S,self.color,(int(self.x),int(self.y)),self.r)
    def collide_rect(self,rect):
        cx=max(rect.left,min(self.x,rect.right))
        cy=max(rect.top,min(self.y,rect.bottom))
        return (self.x-cx)**2+(self.y-cy)**2<=self.r**2

def draw_bar(x,y,w,h,val,max_val,fg,bg):
    pygame.draw.rect(S,bg,(x,y,w,h))
    rw=int(w*(val/max_val))
    pygame.draw.rect(S,fg,(x,y,rw,h))
    pygame.draw.rect(S,(20,20,20),(x,y,w,h),2)

def text_center(t,y,size=FONT,color=(240,240,240)):
    s=size.render(t,True,color)
    S.blit(s,(W//2-s.get_width()//2,y))

def start_screen():
    t=0
    while True:
        for e in pygame.event.get():
            if e.type==pygame.QUIT: pygame.quit(); sys.exit()
            if e.type==pygame.KEYDOWN and e.key==pygame.K_RETURN: return
        S.fill((16,18,24))
        pygame.draw.rect(S,(30,35,48),(30,50,W-60,H-100))
        text_center("Boss Arena",110)
        text_center("W/A/S/D: Move | Space: Shoot toward mouse | Shift: Dodge",180,SMALL)
        text_center("Press Enter to Start",260)
        t+=1
        pygame.display.flip()
        C.tick(F)

def end_screen(win):
    t=0
    while True:
        for e in pygame.event.get():
            if e.type==pygame.QUIT: pygame.quit(); sys.exit()
            if e.type==pygame.KEYDOWN and e.key==pygame.K_RETURN: return
        S.fill((16,18,24))
        pygame.draw.rect(S,(30,35,48),(30,50,W-60,H-100))
        text_center("Victory!" if win else "Defeat",140)
        text_center("Press Enter to return to Start",220,SMALL)
        t+=1
        pygame.display.flip()
        C.tick(F)

def game():
    player=Player()
    boss=Boss()
    bullets=[]
    t=0
    while True:
        keys=pygame.key.get_pressed()
        for e in pygame.event.get():
            if e.type==pygame.QUIT: pygame.quit(); sys.exit()
            if e.type==pygame.KEYDOWN:
                if e.key==pygame.K_SPACE:
                    b=player.shoot(*pygame.mouse.get_pos())
                    if b: bullets.append(b)
                if e.key==pygame.K_LSHIFT:
                    vx=(keys[pygame.K_d]-keys[pygame.K_a])
                    vy=(keys[pygame.K_s]-keys[pygame.K_w])
                    player.dodge(vx,vy)
        player.update(keys,pygame.mouse.get_pos())
        boss.update(player)
        bullets.extend(boss.maybe_pattern(bullets))
        for b in bullets: b.update()
        bullets=[b for b in bullets if b.alive]
        if boss.charge_windup>0:
            pygame.draw.circle(S,(255,200,200),(int(boss.x),int(boss.y)),boss.r+8,2)
        pr=player.rect(); br=boss.rect()
        for b in bullets:
            if b.enemy:
                if player.ifr==0 and b.collide_rect(pr):
                    player.hp=max(0,player.hp-b.dmg); b.alive=False
            else:
                if b.collide_rect(br):
                    boss.take_hit(b.dmg); b.alive=False
        if boss.charge_windup==0 and (abs(boss.vx)>0.1 or abs(boss.vy)>0.1):
            if br.colliderect(pr) and player.ifr==0:
                player.hp=max(0,player.hp-18)
                boss.vx*=0.7; boss.vy*=0.7
        S.fill((16,18,24))
        pygame.draw.rect(S,(50,55,70),(20,40,W-40,H-80))
        player.draw()
        boss.draw()
        for b in bullets: b.draw()
        draw_bar(20,10,300,16,player.hp,player.max_hp,(80,200,255),(30,60,80))
        draw_bar(W-320,10,300,16,boss.hp,boss.max_hp,(255,120,120),(80,30,30))
        text_center("Boss Arena",560,SMALL)
        pygame.display.flip()
        C.tick(F)
        if player.hp<=0:
            return False
        if boss.hp<=0:
            return True

def main():
    while True:
        start_screen()
        win=game()
        end_screen(win)

if __name__=="__main__":
    main()