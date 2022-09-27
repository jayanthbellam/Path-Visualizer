import pygame as pg
from queue import Queue,LifoQueue
import time
import random
delay=0.0
class node:

    def __init__(self,i,j):
        self.x=i
        self.y=j
        self.f=0
        self.g=0
        self.h=0
        self.distance=999999
        self.neighbours=[]
        self.previous=None
        self.open=False
        self.obs=False
        self.closed=False
        self.value=1
    
    def toggle_obs(self):
        self.obs=not self.obs

class Board:

    def __init__(self,rows,cols):
        self.rows=rows
        self.cols=cols
        self.grid=[[node(i,j) for j in range(self.cols)] for i in range(self.rows)]
        self.randomize()
        self.map_set=True
        self.start_set=False
        self.end_set=False
        self.erase=False
        self.open_set=[]
        self.closed_set=[]
        self.path=[]
        self.start_time=-1
        self.end_time=-1
        self.path_time=-1
    
    def set_end(self,end):
        self.end=end
    
    def set_start(self,start):
        self.start=start
    
    def randomize(self):
        for i in self.grid:
            for j in i:
                if random.random()<=0.35:
                    j.obs=True
        row=random.randint(0,self.rows-1)
        col=random.randint(0,self.cols-1)
        self.start=(row,col)
        self.grid[row][col].obs=False
        row=random.randint(0,self.rows-1)
        col=random.randint(0,self.cols-1)
        self.end=(row,col)
        self.grid[row][col].obs=False
    def toggle(self,pos):
        if self.map_set:
            self.grid[pos[0]][pos[1]].obs=True
        elif self.start_set:
            self.grid[pos[0]][pos[1]].obs=False
            self.start=pos
        elif self.end_set:
            self.grid[pos[0]][pos[1]].obs=False
            self.end=pos
        elif self.erase:
            self.grid[pos[0]][pos[1]].obs=False

    def reset(self):
        self.open_set=[]
        self.closed_set=[]
        for i in range(self.rows):
            for j in range(self.cols):
                self.grid[i][j].f=0
                self.grid[i][j].g=0
                self.grid[i][j].h=0
                self.grid[i][j].previous=None
                self.grid[i][j].open=False
                self.grid[i][j].closed=False        
                self.grid[i][j].distance=999999
        self.grid[self.start[0]][self.start[1]].distance=0

    def add_neighbours(self):
        rows=self.rows
        cols=self.cols
        grid=self.grid
        for i in range(rows):
            for j in range(cols):
                if self.grid[i][j].obs:
                    continue
                node=grid[i][j]
                node.neighbours=[]
                if i<cols-1 and not grid[i+1][j].obs:
                    node.neighbours.append(grid[i+1][j])
                if i>0 and not grid[i-1][j].obs:
                    node.neighbours.append(grid[i-1][j])
                if j<rows-1 and not grid[i][j+1].obs:
                    node.neighbours.append(grid[i][j+1])
                if j>0 and not grid[i][j-1].obs:
                    node.neighbours.append(grid[i][j-1])

    def BFS(self,screen,SIZE,SQ_SIZE,animate=False):
        que=Queue()
        self.grid[self.start[0]][self.start[1]].distance=0
        que.put(self.grid[self.start[0]][self.start[1]])
        notreached=True
        while not que.empty():
            node=que.get()
            if (node.x,node.y)==self.end and notreached:
                self.path_time=time.time()
                notreached=False
                return
            for neighbour in node.neighbours:
                if neighbour.distance>node.distance+1:
                    neighbour.distance=node.distance+1
                    neighbour.open=True
                    neighbour.previous=node
                    que.put(neighbour)
                if animate:
                    start=time.time()
                    while(time.time()-start<=delay):
                        draw_board(self, screen, SIZE, SQ_SIZE)
                        pg.display.flip()
            node.open=False
            node.closed=True
    
    def DFS(self,screen,SIZE,SQ_SIZE,animate=False):
        self.grid[self.start[0]][self.start[1]].distance=0
        stack=LifoQueue()
        stack.put(self.grid[self.start[0]][self.start[1]])
        notreached=True
        while not stack.empty():
            node=stack.get()
            if (node.x,node.y)==self.end and notreached:
                self.path_time=time.time()
                notreached=False
                return
            for neighbour in node.neighbours:
                if neighbour.distance>node.distance+1:
                    neighbour.distance=node.distance+1
                    neighbour.open=True
                    neighbour.previous=node
                    stack.put(neighbour)
                    if animate:
                        start=time.time()
                        while(time.time()-start<=delay):
                            draw_board(self, screen, SIZE, SQ_SIZE)
                            pg.display.flip()
            node.open=False
            node.closed=True
    
    def Dijkstra_helper(self):
        if not self.open_set:
            return 0
        best=self.open_set[0]
        for node in self.open_set:
            if node.distance<best.distance:
                best=node
        return best
    def Dijkstra(self,screen,SIZE,SQ_SIZE,animate=False):
        start_node=self.grid[self.start[0]][self.start[1]]
        start_node.distance=0
        start_node.open=True
        self.open_set=[start_node]
        self.closed_set=[]
        while True:
            node=self.Dijkstra_helper()
            if node==0:
                break
            if (node.x,node.y)==self.end:
                self.path_time=time.time()
                return
            for nbh in node.neighbours:
                if nbh.distance>node.distance+1:
                    nbh.distance=node.distance+1
                    nbh.open=True                        
                    nbh.closed=False
                    nbh.previous=node
                    self.open_set.append(nbh)
                if animate:
                    start=time.time()
                    while(time.time()-start<=delay):
                        draw_board(self, screen, SIZE, SQ_SIZE)
                        pg.display.flip()
            node.open=False
            node.closed=True
            self.open_set.remove(node)

    def Astar_helper(self):
        if not self.open_set:
            return 0
        node=self.open_set[0]
        for i in self.open_set:
            if i.f<node.f:
                node=i
        return node

    def heuristic(self,node):
        horiz=abs(node.x-self.end[0])
        verti=abs(node.y-self.end[1])
        return horiz+verti

    def Astar(self,screen,SIZE,SQ_SIZE,animate=False):
        self.open_set.append(self.grid[self.start[0]][self.start[1]])
        self.closed_set=[]
        while True:
            current_squares=self.Astar_helper()
            if current_squares==0:
                break
            self.open_set.remove(current_squares)
            current_squares.open=False
            current_squares.closed=True
            self.closed_set.append(current_squares)
            for nbh in current_squares.neighbours:
                if nbh.closed==True:
                    continue
                if nbh.open==True:
                    if nbh.g>current_squares.g+1:
                        nbh.previous=current_squares
                        nbh.g=current_squares.g+1
                        nbh.f=nbh.g+nbh.h
                else:
                    self.open_set.append(nbh)
                    nbh.open=True
                    nbh.previous=current_squares
                    nbh.g=current_squares.g+1
                    nbh.h=self.heuristic(nbh)
                    nbh.f=nbh.g+nbh.h
            current_squares.distance=current_squares.g
            if animate:
                start=time.time()
                while(time.time()-start<=delay):
                    draw_board(self, screen, SIZE, SQ_SIZE)
                    pg.display.flip()
            if (current_squares.x,current_squares.y)==self.end:
                self.path_time=time.time()
                return
def print_neighbours(node):
    for i in node.neighbours:
        print(i.x,i.y)
def print_distance(grid):
    arr=[]
    for i in range(len(grid)):
        temp=[]
        for j in range(len(grid[i])):
            temp.append(grid[i][j].distance)
        arr.append(temp)
    return arr
def draw_board(board,screen,SIZE,SQ_SIZE):
    if type(board)!=Board:
        print("Object does not not belong to Board Class")
        return None
    draw_nodes(screen, board, SQ_SIZE)
    draw_path(screen,board,SQ_SIZE)
    draw_gridlines(screen, board, SIZE, SQ_SIZE)
    #draw_distance(screen,board,SQ_SIZE)
def draw_path(screen,board,SQ_SIZE):
    end=board.end
    if board.grid[end[0]][end[1]].distance==999999:
        return
    node=board.grid[end[0]][end[1]]
    surface=pg.Surface((SQ_SIZE,SQ_SIZE))
    surface.fill((255,255,0))
    while node:
        i=node.x
        j=node.y
        screen.blit(surface,(j*SQ_SIZE,i*SQ_SIZE))
        node=node.previous
def draw_distance(screen,board,SQ_SIZE):
    rows=board.rows
    cols=board.cols
    grid=board.grid
    font=pg.font.SysFont("Helvitca",SQ_SIZE//2,True,False)
    for i in range(rows):
        for j in range(cols):
            distance=grid[i][j].distance
            if distance!=999999:
                textobject=font.render(str(distance),0,(0,0,0))
                screen.blit(textobject,(j*SQ_SIZE,i*SQ_SIZE))
def draw_nodes(screen,board,SQ_SIZE):
    rows,cols=board.rows,board.cols
    grid=board.grid
    for i in range(rows):
        for j in range(cols):
            surface=pg.Surface((SQ_SIZE,SQ_SIZE))
            if grid[i][j].obs:
                surface.fill((0,0,0))
            else:
                if grid[i][j].open:
                    surface.fill((0,255,255))
                elif grid[i][j].closed:
                    surface.fill((255,0,0))
                else:
                    surface.fill((255,255,255))
            screen.blit(surface,(j*SQ_SIZE,i*SQ_SIZE))
    surface=pg.Surface((SQ_SIZE,SQ_SIZE))
    start=board.start
    start=(start[1]*SQ_SIZE,start[0]*SQ_SIZE)
    surface.fill((0,255,0))
    screen.blit(surface,start)
    end=board.end
    end=(end[1]*SQ_SIZE,end[0]*SQ_SIZE)
    surface.fill((0,0,255))
    screen.blit(surface,end)
def draw_gridlines(screen,board,SIZE,SQ_SIZE):
    rows=board.rows
    cols=board.cols
    for i in range(1,rows+1):
        pg.draw.line(screen,(0,0,0),(i*SQ_SIZE,0),(i*SQ_SIZE,cols*SQ_SIZE))
    for i in range(1,cols+1):
        pg.draw.line(screen,(0,0,0),(0,i*SQ_SIZE),(rows*SQ_SIZE,i*SQ_SIZE))
def main():
    pg.init()
    rows=cols=800
    new=Board(rows,cols)
    SIZE=800
    SQ_SIZE=SIZE//rows
    screen=pg.display.set_mode((SIZE,SIZE))
    screen.fill((255,255,255))
    sq_selected=()
    running=True
    obs_drawing=False
    animate=False
    while running:
        draw_board(new,screen,(SIZE,SIZE),SQ_SIZE)
        pg.display.flip()
        for e in pg.event.get():
            if e.type==pg.MOUSEBUTTONDOWN:
                pos=pg.mouse.get_pos()
                sq_selected=(pos[1]//SQ_SIZE,pos[0]//SQ_SIZE)
                new.toggle(sq_selected)
                obs_drawing=True
            elif e.type==pg.MOUSEBUTTONUP:
                obs_drawing=False
            elif e.type==pg.MOUSEMOTION and obs_drawing:
                pos=pg.mouse.get_pos()
                sq_selected=(pos[1]//SQ_SIZE,pos[0]//SQ_SIZE)
                new.toggle(sq_selected)
            elif e.type==pg.KEYDOWN:
                if e.key==pg.K_m:
                    new.start_set=False
                    new.map_set=True
                    new.end_set=False
                    new.erase=False
                elif e.key==pg.K_s:
                    new.map_set=False
                    new.start_set=True
                    new.end_set=False
                    new.erase=False
                elif e.key==pg.K_e:
                    new.map_set=False
                    new.start_set=False
                    new.end_set=True
                    new.erase=False
                elif e.key==pg.K_w:
                    new.map_set=False
                    new.start_set=False
                    new.end_set=False
                    new.erase=True
                elif e.key==pg.K_q:
                    new.map_set=False
                    new.start_set=False
                    new.end_set=False
                    new.erase=False
                elif e.key==pg.K_r:
                    new.reset()
                    new.add_neighbours()
                elif e.key==pg.K_t:
                    new.start_time=time.time()
                    new.BFS(screen,SIZE,SQ_SIZE,animate)
                    new.end_time=time.time()
                    print(new.end_time-new.start_time,new.path_time-new.start_time)
                elif e.key==pg.K_y:
                    new.start_time=time.time()
                    new.DFS(screen, SIZE, SQ_SIZE,animate)
                    new.end_time=time.time()
                    print(new.end_time-new.start_time,new.path_time-new.start_time)
                elif e.key==pg.K_u:
                    animate=not animate
                elif e.key==pg.K_n:
                    new=Board(rows,cols)
                elif e.key==pg.K_a:
                    new.start_time=time.time()
                    new.Astar(screen, SIZE, SQ_SIZE,animate)
                    new.end_time=time.time()
                    print(new.end_time-new.start_time,new.path_time-new.start_time)
                elif e.key==pg.K_d:
                    new.start_time=time.time()
                    new.Dijkstra(screen, SIZE, SQ_SIZE,animate)
                    new.end_time=time.time()
                    print(new.end_time-new.start_time,new.path_time-new.start_time)
            elif e.type==pg.QUIT:
                pg.quit()
                running=False
main()