from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.graphics import Color, Ellipse, Line, Rectangle
from kivy.core.window import Window
from kivy.metrics import dp
import random

TRACK = [
    (6,1),(6,2),(6,3),(6,4),(6,5),(5,6),(4,6),(3,6),(2,6),(1,6),(0,6),
    (0,7),(0,8),(1,8),(2,8),(3,8),(4,8),(5,8),(6,9),(6,10),(6,11),(6,12),
    (6,13),(6,14),(7,14),(8,14),(8,13),(8,12),(8,11),(8,10),(8,9),(9,8),
    (10,8),(11,8),(12,8),(13,8),(14,8),(14,7),(14,6),(13,6),(12,6),(11,6),
    (10,6),(9,6),(8,5),(8,4),(8,3),(8,2),(8,1),(8,0),(7,0),(6,0)
]
START = {"Red":0, "Green":13, "Yellow":26, "Blue":39}
HOME = {
 "Red":[(7,1),(7,2),(7,3),(7,4),(7,5)],
 "Green":[(1,7),(2,7),(3,7),(4,7),(5,7)],
 "Yellow":[(7,13),(7,12),(7,11),(7,10),(7,9)],
 "Blue":[(13,7),(12,7),(11,7),(10,7),(9,7)]
}
SAFE = {0,8,13,21,26,34,39,47}
RGB = {"Red":(0.90,0.16,0.16),"Green":(0.02,0.65,0.40),
       "Yellow":(0.96,0.67,0.08),"Blue":(0.12,0.48,0.90)}
PLAYERS = ["Red","Green","Yellow","Blue"]

class GameBoard(Widget):
    def __init__(self, game, **kwargs):
        super().__init__(**kwargs)
        self.game = game
        self.bind(pos=self.redraw, size=self.redraw)
        self.redraw()

    def cell_center(self, row, col, cell):
        return self.x + (col + .5)*cell, self.y + self.height - (row + .5)*cell

    def redraw(self, *args):
        self.canvas.clear()
        if self.width <= 0 or self.height <= 0:
            return
        cell = min(self.width, self.height) / 15.0
        ox = self.x + (self.width - cell*15)/2
        oy = self.y + (self.height - cell*15)/2
        with self.canvas:
            Color(0.98,0.96,0.91)
            Rectangle(pos=(ox,oy), size=(cell*15,cell*15))
            # Yard blocks
            yards = [("Red",0,0),("Green",0,9),("Blue",9,0),("Yellow",9,9)]
            for name,r,c in yards:
                Color(*RGB[name])
                Rectangle(pos=(ox+c*cell,oy+(15-r-6)*cell),size=(6*cell,6*cell))
                Color(1,1,1)
                Rectangle(pos=(ox+(c+1)*cell,oy+(15-r-5)*cell),size=(4*cell,4*cell))
            # Outer track
            for i,(r,c) in enumerate(TRACK):
                Color(0.88,0.86,0.81)
                Rectangle(pos=(ox+c*cell,oy+(14-r)*cell),size=(cell,cell))
                Color(0.35,0.32,0.28)
                Line(rectangle=(ox+c*cell,oy+(14-r)*cell,cell,cell),width=0.7)
                if i in SAFE:
                    Color(0.55,0.47,0.30)
                    Ellipse(pos=(ox+(c+.3)*cell,oy+(14-r+.3)*cell),size=(.4*cell,.4*cell))
            # Home lanes and starts
            for name, cells in HOME.items():
                for r,c in cells:
                    Color(*RGB[name])
                    Rectangle(pos=(ox+c*cell,oy+(14-r)*cell),size=(cell,cell))
            for name,idx in START.items():
                r,c=TRACK[idx]
                Color(*RGB[name])
                Rectangle(pos=(ox+c*cell,oy+(14-r)*cell),size=(cell,cell))
            Color(1,0.78,0.18)
            Rectangle(pos=(ox+6*cell,oy+6*cell),size=(3*cell,3*cell))
            # Tokens
            for name in PLAYERS:
                for tid,p in enumerate(self.game.tokens[name]):
                    if p == -1:
                        br = 0 if name in ("Red","Green") else 9
                        bc = 0 if name in ("Red","Blue") else 9
                        rr = br + (1.8 if tid<2 else 4.2)
                        cc = bc + (1.8 if tid%2==0 else 4.2)
                    elif p == 56:
                        rr,cc = 7.5,7.5
                    elif p <= 50:
                        rr,cc = TRACK[(START[name]+p)%52]
                        rr += .5; cc += .5
                    else:
                        rr,cc = HOME[name][p-51]
                        rr += .5; cc += .5
                    cx=ox+cc*cell
                    cy=oy+(14.5-rr)*cell
                    Color(*RGB[name])
                    Ellipse(pos=(cx-cell*.30,cy-cell*.30),size=(cell*.60,cell*.60))
                    Color(1,1,1)
                    Line(circle=(cx,cy,cell*.30),width=1.2)
                    if name == self.game.current and tid in self.game.legal:
                        Color(1,1,1)
                        Line(circle=(cx,cy,cell*.39),width=2)

    def on_touch_down(self, touch):
        if not self.collide_point(*touch.pos) or not self.game.waiting:
            return super().on_touch_down(touch)
        cell=min(self.width,self.height)/15.0
        ox=self.x+(self.width-cell*15)/2
        oy=self.y+(self.height-cell*15)/2
        name=self.game.current
        for tid in self.game.legal:
            p=self.game.tokens[name][tid]
            if p==-1:
                br=0 if name in ("Red","Green") else 9
                bc=0 if name in ("Red","Blue") else 9
                rr=br+(1.8 if tid<2 else 4.2)
                cc=bc+(1.8 if tid%2==0 else 4.2)
            elif p==56:
                rr,cc=7.5,7.5
            elif p<=50:
                rr,cc=TRACK[(START[name]+p)%52]; rr+=.5; cc+=.5
            else:
                rr,cc=HOME[name][p-51]; rr+=.5; cc+=.5
            cx=ox+cc*cell; cy=oy+(14.5-rr)*cell
            if (touch.x-cx)**2+(touch.y-cy)**2 < (cell*.55)**2:
                self.game.move(tid)
                return True
        return True

class LudoGame(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation="vertical",padding=dp(8),spacing=dp(6),**kwargs)
        self.tokens={p:[-1,-1,-1,-1] for p in PLAYERS}
        self.turn=0; self.die=None; self.legal=[]; self.waiting=False
        self.sixes=0; self.winners=[]
        self.status=Label(text="RED: Tap Roll Dice",size_hint_y=None,height=dp(42),font_size="18sp")
        self.add_widget(self.status)
        self.board=GameBoard(self,size_hint=(1,1))
        self.add_widget(self.board)
        controls=BoxLayout(size_hint_y=None,height=dp(54),spacing=dp(8))
        self.roll_btn=Button(text="ROLL DICE",font_size="18sp",background_color=(1,.75,.15,1),color=(.08,.1,.15,1))
        self.roll_btn.bind(on_release=self.roll)
        controls.add_widget(self.roll_btn)
        reset=Button(text="NEW MATCH",font_size="16sp")
        reset.bind(on_release=self.reset)
        controls.add_widget(reset)
        self.add_widget(controls)

    @property
    def current(self):
        return PLAYERS[self.turn]

    def legal_moves(self, name, die):
        return [i for i,p in enumerate(self.tokens[name]) if p!=56 and
                ((p==-1 and die==6) or (p>=0 and p+die<=56))]

    def roll(self,*args):
        if self.waiting or self.winners: return
        name=self.current
        self.die=random.randint(1,6)
        self.sixes=self.sixes+1 if self.die==6 else 0
        if self.sixes>=3:
            self.sixes=0
            self.status.text=f"{name} rolled three 6s. Turn lost."
            self.next_turn(); self.ai_if_needed(); return
        self.legal=self.legal_moves(name,self.die)
        if not self.legal:
            self.status.text=f"{name} rolled {self.die}: no move."
            self.sixes=0; self.next_turn(); self.ai_if_needed(); return
        self.waiting=True
        self.status.text=f"{name} rolled {self.die}. Choose a highlighted token."
        self.board.redraw()
        if name!="Red":
            self.ai_move()

    def ai_move(self):
        name=self.current
        def score(i):
            p=self.tokens[name][i]; n=0 if p==-1 else p+self.die
            val=n*3 + (1000 if n==56 else 0) + (400 if p==-1 else 0)
            if 0<=n<=50:
                dest=(START[name]+n)%52
                if dest in SAFE: val+=150
                else:
                    for opp in PLAYERS:
                        if opp!=name:
                            for op in self.tokens[opp]:
                                if op>=0 and op<=50 and (START[opp]+op)%52==dest:
                                    val+=800
            return val
        self.move(max(self.legal,key=score))

    def move(self,tid):
        if not self.waiting: return
        name=self.current; old=self.tokens[name][tid]
        new=0 if old==-1 else old+self.die
        self.tokens[name][tid]=new
        captured=False
        if 0<=new<=50:
            dest=(START[name]+new)%52
            if dest not in SAFE:
                for opp in PLAYERS:
                    if opp!=name:
                        for j,p in enumerate(self.tokens[opp]):
                            if 0<=p<=50 and (START[opp]+p)%52==dest:
                                self.tokens[opp][j]=-1; captured=True
        if all(p==56 for p in self.tokens[name]):
            self.winners.append(name)
            self.status.text=f"{name} WINS!"
            self.waiting=False; self.board.redraw(); return
        bonus=self.die==6 or captured or new==56
        self.waiting=False; self.legal=[]
        if not bonus:
            self.sixes=0; self.next_turn()
        else:
            self.status.text=f"{name} gets another turn!"
        self.board.redraw()
        if self.current!="Red":
            self.roll()

    def next_turn(self):
        for _ in range(4):
            self.turn=(self.turn+1)%4
            if self.current not in self.winners: break
        self.status.text=f"{self.current}: Tap Roll Dice"
        self.board.redraw()

    def reset(self,*args):
        self.tokens={p:[-1,-1,-1,-1] for p in PLAYERS}
        self.turn=0; self.die=None; self.legal=[]; self.waiting=False
        self.sixes=0; self.winners=[]
        self.status.text="RED: Tap Roll Dice"
        self.board.redraw()

class LudoArenaApp(App):
    def build(self):
        self.title="Ludo Arena"
        Window.clearcolor=(.06,.08,.13,1)
        return LudoGame()

if __name__=="__main__":
    LudoArenaApp().run()
