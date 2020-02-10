# MIT License
# 
# Copyright (c) [2020] [Antonio Domènech, Daniela Tarzia]
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import win32api
import win32con
import pyautogui
from pynput.mouse import Button, Controller
from Ratio import *

########################################################################################################################
########################################################################################################################
##################################################### Cursor ###########################################################

#La clase Cursor determina el movimiento del raton segun el movimiento de la cara.
class Cursor:

    #Genera el objeto ratio y los contadores de los clicks.
    def __init__(self):
        self.r = Ratio()    #Clase Ratio.
        self.count = 0      #Contador para el click.
        self.count1 = 0     #Contador para el doble click.

    #Llamar a las funciones de la clase Ratio.
    def ratios(self, grayimage):
        self.r.extraer_puntos(grayimage)
        self.horizontal = self.r.ratio_horizontal()
        self.vertical = self.r.ratio_vertical()
        self.ojo_derecho = self.r.ratio_ojo_derecho()
        self.ojo_izquierdo = self.r.ratio_ojo_izquierdo()
        #self.labios = self.r.ratio_labios()

        return(self.horizontal, self.vertical, self.ojo_derecho, self.ojo_izquierdo)

    #Determina la posicion del cursor.
    def position(self):
        mous = win32api.GetCursorPos()
        self.mouseX = mous[0]
        self.mouseY = mous[1]

########################################################################################################################
############################################## Click y doble click #####################################################
########################################################################################################################

    #Acción de click y doble click.
    def click_doubleclick(self, ratio_R, ratio_L):
        #Solo activo mientras el cursor no está en movimiento:
        if(self.mouse_act == 1):
            #Si el ratio del ojo es superior a un determinado valor, suma el contador:
            if (ratio_R > ratio_L):
                self.count = self.count + 1

                #Con el siguiente if evitamos la posibilidad de hacer click y doble click a la vez:
                if (self.count1 > 0):
                    self.count1 = self.count1 - 1

            #Cuando el contador llega a 15 se realiza un click:
            if ((self.count == 5) and (self.clk == 0)):
                #Instrucciones para hacer un click:
                win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, self.mouseX, self.mouseY, 0, 0)
                win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, self.mouseX, self.mouseY, 0, 0)
                self.clk = 1 #Variable para distinguir entre un click y un doble clik.

            #Cuando el contador és más grande que 15 però los ojos están abiertos, se resetea el contador:
            if ((self.count > 5) and (ratio_R < ratio_L)):
                self.clk = 0
                self.count = 0

            #Si el ojo sigue cerrado después de hacer click, el contador sigue y se hace doble clic:
            if (self.count == 30):
                #Instrucciones para hacer doble click:
                win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, self.mouseX, self.mouseY, 0, 0)
                win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, self.mouseX, self.mouseY, 0, 0)
                win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, self.mouseX, self.mouseY, 0, 0)
                win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, self.mouseX, self.mouseY, 0, 0)
                self.count = 0
                self.clk = 0

            #Si se abre el ojo el contador se resta:
            #Esto se hace con tal de no acumular tiempos en donde detecte parpadeo sin intencion de click.
            if ((ratio_R < ratio_L) and (self.count > 0)):
                self.count = self.count - 1

    #Acción de click derecho.
    def right_click(self, ratio_R, ratio_L):
        #Solo activo mientras el cursor no está en movimiento:
        if(self.mouse_act == 1):
            #Si el ratio del ojo es superior a un determinado valor, suma el contador:
            if (ratio_R > ratio_L):
                self.count1 = self.count1 + 1

            #Cuando el contador llega a 15 se realiza un click derecho:
            if ((self.count1 == 15)):
                # instrucciones para hacer clic derecho con esta libreria:
                win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTDOWN, self.mouseX, self.mouseY, 0, 0)
                win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTUP, self.mouseX, self.mouseY, 0, 0)
                self.count1 = 0

            #Si se abre el ojo, el contador se resta:
            #Esto se hace con tal de no acumular tiempos en donde detecte parpadeo sin intencion de click.
            if ((ratio_R < ratio_L) and (self.count1 > 0)):
                self.count1 = self.count1 - 1

########################################################################################################################
############################################# Movimiento del cursor ####################################################
########################################################################################################################

    #Realización de un movimiento vertical.
    def move_vertical(self, FU, FD, velocidad):
        #Si el ratio vertical de la cara es superior a un determinado valor, el raton se mueve hacia abajo.
        if(self.vertical > FD):
            win32api.SetCursorPos((self.mouseX, self.mouseY + velocidad))

            #Las siguientes instrucciones impiden un click mientras el cursor se mueve:
            self.mouse_act = 0
            self.count = 0
            self.clk = 0
            self.count1 = 0

        #Si el ratio vertical de la cara es inferior a un determinado valor, el raton se mueve hacia arriba.
        elif(self.vertical < FU):
            win32api.SetCursorPos((self.mouseX, self.mouseY - velocidad))

            #Las siguientes instrucciones impiden un click mientras el cursor se mueve:
            self.mouse_act = 0
            self.count = 0
            self.clk = 0
            self.count1 = 0

        #Si el ratio vertical de la cara esta entre estos dos valores, el raton no se mueve.
        else:
            win32api.SetCursorPos((self.mouseX, self.mouseY))

            #Activamos la posibilidad de clicar:
            self.mouse_act = 1

    #Realización de un movimiento horizontal.
    def move_horizontal(self, FR, FL, velocidad):
        #Si el ratio horizontal de la cara es superior a un determinado valor, el raton se mueve a la izquierda.
        if (self.horizontal > FL):
            win32api.SetCursorPos((self.mouseX - velocidad, self.mouseY))

            #Las siguientes instrucciones impiden un click mientras el cursor se mueve:
            self.mouse_act = 0
            self.count = 0
            self.count1 = 0
        #Si el ratio horizontal de la cara es inferior a un determinado valor, el raton se mueve a la derecha.
        elif (self.horizontal < FR):
            win32api.SetCursorPos((self.mouseX + velocidad, self.mouseY))

            #Las siguientes instrucciones impiden un click mientras el cursor se mueve:
            self.mouse_act = 0
            self.count = 0
            self.count1 = 0

        #Si el ratio horizontal de la cara esta entre estos valores, el raton no se mueve.
        else:
            win32api.SetCursorPos((self.mouseX, self.mouseY))

            #Activamos la posibilidad de clicar:
            self.mouse_act = 1

##################################################### FIN ##############################################################
########################################################################################################################
########################################################################################################################

if __name__ == '__main__':
    import cv2
    from Ratio import *

    capture = cv2.VideoCapture(0)

    _, frame = capture.read()  # obtenermos la captura
    grayimage = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  # Escala de grises

    count = 0

    while(1):
        _, frame = capture.read()  # obtenermos la captura
        grayimage = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  # Escala de grises
        cv2.imshow('video', frame)
        c = Cursor()
        #c.position()
        ratio = c.ratios(grayimage)
        print(ratio)

        if (ratio[2] > 3.8):
            count = count + 1
        if (count == 5):
            c.click()
            count = 0
        if ((ratio[2] < 3.8) and (count > 0)):
            count = count - 1