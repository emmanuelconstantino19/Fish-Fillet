from scipy import interpolate
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import time  # to be used in timer
import pygame
import numpy as np
import random
from random import randint
from sys import exit
import ast 
pygame.init()
import socket
import threading
import globals 

# Possible levels ==> [Score to pass, maximum time]
levels = [[40,30],[60,40],[80,50],[90,60],[100,70]]   # 5 levels
level = 1  # initial level,


seconds = 0   # the actual timer of every level
time_start = 0  # just for calculating tome
######## Control the Small Fishes Motion ###########

x_ax = 50        #'INCREASING'  = increasing number of curve points which means'MORE' curve resolution(integer)
patterns_num=5   # Number of Available patterns (integer)

vertical_displacement = 5    #'DECREASING'  = decreasing vertical motion which means 'MORE STABLE' Motion
x_displacement = 0.2            # Speed of small fish
##################################################


score=0
big_fish_size=2.2
texture=()
mouse_dir=1
photos=['Fishleft1.png','Fishright1.png','Fishleft2.png','Fishright2.png','Fishleft3.png','Fishright3.png','Fishleft4.png','Fishright4.png','Fishleft5.png','Fishright5.png','Fishleft6.png','Fishright6.png','Fishleft7.png','Fishright7.png','Fishleft8.png','Fishright8.png','Fishleft9.png','Fishright9.png','Fishleft10.png','Fishright10.png','Fishleft11.png','Fishright11.png','background.jpg','menu.png']


current_x = 200
current_y = 200

global_coordinates = {}

class Game:

    def __init__(self):

        #self.sock = sock

        receiveThread = threading.Thread(target=self.receive_data)
        receiveThread.daemon = True
        receiveThread.start()

        self.x_points = [i for i in range(-50,750,x_ax)]
        self.num_points = len(self.x_points)

        #A[0_X_pos, 1_Y_pos, 2_Scale, 3_dir_X, 4_pattern_num, 5_y_offset, 6 Shape ]

        #The 7th dimension refers to the vertical offset
        self.A =      [[0, 120 , 1.5, 1, 0, self.random_offset(), 1],
                 [0  , 240, 3  , 1, 1, self.random_offset(), 3],
                 [0  , 360, 1.5, 1, 2, self.random_offset(), 5],
                 [0  , 480, 3  , 1, 3, self.random_offset(), 7],
                 [0  , 600, 1.5, 1, 4, self.random_offset(), 9],
                 [600, 120, 3  , -1, 4, self.random_offset(), 0],
                 [600, 240, 1.5, -1, 3, self.random_offset(), 2],
                 [600, 360, 3  , -1, 2, self.random_offset(), 4],
                 [600, 480, 1.5, -1, 1, self.random_offset(), 6],
                 [600, 600, 3  , -1, 0, self.random_offset(), 8]]
        self.count =len(self.A)

        self.paths = []
        self.lost_flag=0



        glutInit()                                  # Initialize Glut Features
        glutInitDisplayMode(GLUT_SINGLE | GLUT_RGBA)    # Initialize Window Options
        glutInitWindowSize(600,600)
        glutCreateWindow(b"Fish Fillet")
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)   # Blend
        glEnable(GL_BLEND)

        self.myint()
        glutKeyboardFunc(self.keyboard)
        glutIdleFunc(self.menu)
        glutPassiveMotionFunc(self.mouse)
        glutDisplayFunc(self.menu)
        glutMainLoop()

    #Small Function to generate the vertical offset
    def random_offset(self):
        return randint(vertical_displacement+10,600-vertical_displacement-10)



    def generate_patterns(self):
        global paths, patterns_num, vertical_displacement
        paths = [] # clear paths
        for j in range(patterns_num):
            new_path = []
            for i in range(self.num_points):
                new_path.append(randint(300-vertical_displacement , 300+vertical_displacement))

            paths.append(interpolate.splrep(self.x_points, new_path))   # tck


    def f(self, i):
        global paths

        if self.A[i][3] == 1:
            f_x = interpolate.splev(self.A[i][0],paths[self.A[i][4]])
        else:
            f_x = 600 - interpolate.splev(self.A[i][0],paths[self.A[i][4]])

        if self.A[i][0] > 650:
            self.A[i][3] = -self.A[i][3]
            self.A[i][6]=self.A[i][6]-1 #look at

        elif self.A[i][0]< -50:
            self.A[i][3] = -self.A[i][3]
            self.A[i][6]=self.A[i][6]+1



        return f_x + self.A[i][5] - 300

    def drawText(self, string, x, y):
        glLineWidth(4)
        glColor(1, 1, 0)  # Yellow Color
        glLoadIdentity()
        glTranslate(x, y, 0)
        glRotate(180,1,0,0)
        glScale(.20, .20, 1)
        string = string.encode()  # conversion from Unicode string to byte string
        for c in string:
            glutStrokeCharacter(GLUT_STROKE_ROMAN, c)

    def drawName(self, string, x, y):
        glLineWidth(2)
        glColor(1, 1, 0)  # Yellow Color
        glLoadIdentity()
        glTranslate(x-60, y-40, 0)
        glRotate(180,1,0,0)
        glScale(.10, .10, .26)
        string = string.encode()  # conversion from Unicode string to byte string
        for c in string:
            glutStrokeCharacter(GLUT_STROKE_ROMAN, c)


    def add_small_fish(self):
        self.count += 1

        new_rand_x = random.choice([-50, 650])

        new_rand_pattern = randint(0, patterns_num - 1)
        if score <= 30:
            scale = 1.5
        else:
            scale = random.choice([1.5, 3])
        if new_rand_x == 0:
            new_fish_shape=random.choice([1,3,5,7,9,11,13,15,17,19])
            direction = 1
        else:
            new_fish_shape = random.choice([0, 2, 4, 6, 8, 10, 12, 14, 16, 18])
            direction = -1
        self.A.append(list((new_rand_x, 0, scale, direction, new_rand_pattern, self.random_offset(),new_fish_shape)))

    def remove_small_fish(self, i):
        del self.A[i]
        self.count-=1

    def remove_big_fish_lost(self):
        self.lost_flag=1


    def increase_score(self):
        global score
        score +=1

    def eating_sound(self):
        s_file = pygame.mixer.Sound("eating.wav")
        s_file.play()

    def game_over_sound(self):
        s_file = pygame.mixer.Sound("gameover.wav")
        s_file.play()



    def collision (self, i):
        global current_x,current_y,score,patterns_num,big_fish_size,seconds
        x=self.A[i][0]
        y=self.A[i][1]
        if abs(current_x -x) <30 and abs(current_y-y)<30 and self.A[i][2] > big_fish_size :

            self.remove_big_fish_lost()
            self.game_over_sound()


        elif abs(current_x -x) <30 and abs(current_y-y)<30 and self.A[i][2] < big_fish_size :
            self.remove_small_fish(i)
            self.increase_score()
            self.add_small_fish()
            self.eating_sound()










    def load_texture(self):
        global texture,photos
        texture=glGenTextures(24)
        for i in range(24):
            imgload = pygame.image.load(photos[i])
            img = pygame.image.tostring(imgload, "RGBA", 1)
            width = imgload.get_width()
            height = imgload.get_height()
            glBindTexture(GL_TEXTURE_2D, texture[i])  # Set this image in images array
            glTexParameter(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
            glTexParameter(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
            glTexParameter(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
            glTexParameter(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
            glTexImage2D(GL_TEXTURE_2D, 0, 4, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, img)
            glEnable(GL_TEXTURE_2D)
            glBindTexture(GL_TEXTURE_2D, texture[i])




    def myint(self):

        s_file = pygame.mixer.Sound("feeding-frenzy.wav")
        s_file.play()

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0,600,600,0,0,600)
        self.load_texture()
        #gluLookAt(0,0,1,0,0,0,0,1,0) #eye, look at, up vector
        glClearColor(1,1,1,.5)
        self.generate_patterns()


    def start_again(self):
        global score,big_fish_size,score,time_start

        self.A = [[0, 120 , 1.5, 1, 0, self.random_offset(), 1],
             [0  , 240, 3  , 1, 1, self.random_offset(), 3],
             [0  , 360, 1.5, 1, 2, self.random_offset(), 5],
             [0  , 480, 3  , 1, 3, self.random_offset(), 7],
             [0  , 600, 1.5, 1, 4, self.random_offset(), 9],
             [600, 120, 3  , -1, 4, self.random_offset(), 0],
             [600, 240, 1.5, -1, 3, self.random_offset(), 2],
             [600, 360, 3  , -1, 2, self.random_offset(), 4],
             [600, 480, 1.5, -1, 1, self.random_offset(), 6],
             [600, 600, 3  , -1, 0, self.random_offset(), 8]]
        score = 0
        big_fish_size = 2.2
        self.lost_flag = 0

        time_start = time.time()

    def start_time(self):
        big_fish_size = 2.2
        self.lost_flag = 0
        global time_start
        time_start = time.time()


    ###########################################################
    def menu (self):
        global texture
        glBindTexture(GL_TEXTURE_2D, texture[-1])
        glColor(1,1,1)
        glBegin(GL_QUADS)
        glTexCoord(1,1)
        glVertex3f(0,0, 0)
        glTexCoord(0,1)
        glVertex3f(600,0 , 0)
        glTexCoord(0,0)
        glVertex3f(600,600, 0)
        glTexCoord(1,0)
        glVertex3f(0,600, 0)
        glEnd()

        glFlush()


    def keyboard(self,key,x,y):
        global level
        if key == b"x":
            exit("Exit !")
        if key == b"a": #play
            self.start_time()
            glutIdleFunc(self.main_scene)

        # if key == b"r":#statr again
        #     self.start_again()
        #     glutIdleFunc(self.main_scene)




    ##########################################################################################

    def receive_data(self):
        global global_coordinates
        while True:
            try:
                peersCoordinates = globals.sock.recv(1024)
                res = ast.literal_eval(str(peersCoordinates,'utf-8')) 
                global_coordinates = res
            except:
                pass

    def main_scene (self):
        global texture,current_x,current_y , current_z ,big_fish_size,mouse_dir,score,levels,level
        if self.lost_flag == 1:
            glutIdleFunc(self.menu)



        if score >=20 :
            big_fish_size= 5



        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glClear(GL_COLOR_BUFFER_BIT) #| GL_DEPTH_BUFFER_BIT)
        if self.lost_flag!=1: #plar the game


            glBindTexture(GL_TEXTURE_2D, texture[22]) #background

            glBegin(GL_QUADS)
            glTexCoord(0, 0)
            glVertex3f(600,600 , 0)
            glTexCoord(0, 1)
            glVertex3f(600,0 , 0)
            glTexCoord(1, 1)
            glVertex3f(0,0 , 0)
            glTexCoord(1, 0)
            glVertex3f(0,600, 0)
            glEnd()


     #Texture Added
            string = "Score:" + str(score)

            self.drawText(string, 20,40 )
            glLoadIdentity()

            #Texture Added
            string = "Timer:" + str(levels[level-1][1]-seconds)

            self.drawText(string, 20, 100)
            glLoadIdentity()

            #Texture Added
            string = "Level:" + str(level)

            self.drawText(string, 20, 70)
            glLoadIdentity()


            for key in global_coordinates.keys():
                #threading.Thread(target=self.render_players, args=(int(global_coordinates[key][0]), int(global_coordinates[key][1]),)).start()
                # renderThread.daemon = True
                # renderThread.start()
                string = str(key)

                self.drawName(string,int(global_coordinates[key][0]), int(global_coordinates[key][1]))
                glLoadIdentity()

                glTranslate(int(global_coordinates[key][0]), int(global_coordinates[key][1]),0)
                glColor4f(1, 1, 1, 1)
                if mouse_dir==1:
                    glBindTexture(GL_TEXTURE_2D, texture[21])
                else:
                    glBindTexture(GL_TEXTURE_2D, texture[20])

                glBegin(GL_QUADS)
                glTexCoord(0, 0)
                glVertex3f(-10 * big_fish_size, 10 * big_fish_size, 0)
                glTexCoord(0, 1)
                glVertex3f(-10 * big_fish_size, -10 * big_fish_size, 0)
                glTexCoord(1, 1)
                glVertex3f(10 * big_fish_size, -10 * big_fish_size, 0)
                glTexCoord(1, 0)
                glVertex3f(10 * big_fish_size, 10 * big_fish_size, 0)
                glEnd()
                glLoadIdentity()


        if self.lost_flag != 1:

            for i in range(self.count):
                glLoadIdentity()
                self.A[i][1]=self.f(i)
                glTranslate(self.A[i][0],self.A[i][1],0)

                self.A[i][0] += (self.A[i][3] * x_displacement)


                if self.A[i][3]==1:
                    glBindTexture(GL_TEXTURE_2D, texture[self.A[i][6]])
                if self.A[i][3] == -1:
                    glBindTexture(GL_TEXTURE_2D, texture[self.A[i][6]])



                glBegin(GL_QUADS)
                glTexCoord(0,0)
                glVertex3f(-10 *self.A[i][2], 10 *self.A[i][2], 0)
                glTexCoord(0,1)
                glVertex3f(-10*self.A[i][2], -10*self.A[i][2], 0)
                glTexCoord(1,1)
                glVertex3f(10 *self.A[i][2], -10 *self.A[i][2], 0)
                glTexCoord(1,0)
                glVertex3f(10*self.A[i][2], 10 *self.A[i][2], 0)
                glEnd()
                self.collision(i)


        glFlush()

        ###################### Levels ###########################################
        # Check for the Level

        if score >= levels[level-1][0]:    # Only 5 levels then get Error
            self.next_level(level)
            glutIdleFunc(self.main_scene)


        # continue timer
        self.game_timer()


    def game_timer(self):
        global seconds,time_start,levels,level


        seconds = int(time.time() - time_start)
        if seconds >= levels[level-1][1]:
            self.lost_flag = 1

    def next_level(self, i):

        global x_displacement,patterns_num,vertical_displacement,level,levels
        x_displacement = 0.2 + (i*0.05)
        vertical_displacement  = 5 + (i*2)
        patterns_num += 5 + (i*1)
        self.generate_patterns()
        level += 1
        if level >len(levels) :
            exit("Thanks, I was hungry !")
            # End of the game
        else:
            self.start_again()

    def mouse(self, new_x, new_y):
        global current_x, current_y,mouse_dir
        if new_x >current_x :
            mouse_dir = 1
        else:
            mouse_dir = -1
        current_x = new_x
        current_y = new_y
        try:
            globals.sock.send(bytes(str('CURRENT_COORDINATES:' + str(current_x) + ',' + str(current_y)), 'utf-8'))
        except:
            pass
