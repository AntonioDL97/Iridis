# MIT License
#
# Copyright (c) [2020] [Antonio Domènech L., Daniela Tarzia]
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

from math import hypot
from Deteccion import *

########################################################################################################################
########################################################################################################################
##################################################### Ratio ############################################################

#La clase Ratio es para determinar los movimientos que hace la cara, los ojos y la boca.
class Ratio:

    #Crea el objeto detección
    def __init__(self):
        self.t = Deteccion()

    #Retorna el punto medio entre dos puntos
    def midpoint(self, point1, point2):
        mp = int((point1[0] + point2[0]) / 2), int((point1[1] + point2[1]) / 2)
        return(mp)

    #Retorna la distancia en valor absoluto entre dos puntos
    def distance(self, point1, point2):
        d = abs(hypot((point2[0] - point1[0]), (point2[1] - point1[1])))
        return(d)

    #Extrae puntos de interes a partir de una imagen
    def extraer_puntos(self, grayimage):
        # lista de puntos utiles
        points = [30,33,29,17,26,45,42,43,47,39,36,38,40,62,66,48,54,44,46,37,41]
        puntos = self.t.detect_landmarks(grayimage, points) #Obtenemos las coordenadas de cada punto

        #Puntos de la nariz
        self.nariz = puntos[0:2] #Punto 30
        self.nariz_inf = puntos[2:4] #Punto 33
        self.nariz_sup = puntos[4:6] #Punto 29
        self.nariz_derecha = puntos[6:8] #Punto 17
        self.nariz_izquierda = puntos[8:10] #Punto 26

        #Punto del ojo izquierdo
        self.ojo_izquierdo_izquierda = puntos[10:12] #Punto 45
        self.ojo_izquierdo_derecha = puntos[12:14] #Punto 42
        self.ojo_izquierdo_arriba1 = puntos[14:16] #Punto 43
        self.ojo_izquierdo_arriba2 = puntos[34:36] #Punto 44
        self.ojo_izquierdo_abajo1 = puntos[16:18] #Punto 47
        self.ojo_izquierdo_abajo2 = puntos[36:38] #Punto 46

        #Puntos del ojo derecho
        self.ojo_derecho_izquierda = puntos[18:20] #Punto 39
        self.ojo_derecho_derecha = puntos[20:22] #Punto 36
        self.ojo_derecho_arriba1 = puntos[22:24] #Punto 38
        self.ojo_derecho_arriba2 = puntos[38:40] #Punto 37
        self.ojo_derecho_abajo1 = puntos[24:26] #Punto 40
        self.ojo_derecho_abajo2 = puntos[40:] #Punto 41

        #Puntos de la boca
        self.labio_superior = puntos[26:28] #Punto 62
        self.labio_inferior = puntos[28:30] #Punto 66
        self.labio_derecha = puntos[30:32] #Punto 48
        self.labio_izquierda = puntos[32:34] #Punto 54

########################################################################################################################
################################################# Ratios ###############################################################
########################################################################################################################

    #Calcula un ratio que define la apertura de la boca
    def ratio_labios(self):
        # medimos la distancia entre puntos en horizontal y en vertical
        ver = Ratio.distance(self, self.labio_superior, self.labio_inferior)
        hor = Ratio.distance(self, self.labio_izquierda, self.labio_derecha)

        #Evitamos valores negativos para la distancia vertical
        if(ver < 0):
            ver = 0

        #Se dividen las distancias y obtenemos un ratio que nos indica la apertura de la boca
        ratio = (hor/ver)
        return(ratio)

    #Calcula el ratio horizontal de la cara
    def ratio_horizontal(self):
        #Medimos las distancias entre centro - derecha y centro - izquierda
        derecha = Ratio.distance(self, self.nariz, self.nariz_derecha)
        izquierda = Ratio.distance(self, self.nariz, self.nariz_izquierda)

        #Se dividen las distancias y obtenemos un ratio que nos indica el movimiento horizontal de la cara
        ratio = (derecha/izquierda)
        return(ratio)

    #Calcula el ratio vertical de la cara
    def ratio_vertical(self):
        #Medimos las distancias entre centro - arriba y centro - abajo
        arriba = Ratio.distance(self, self.nariz, self.nariz_sup)
        abajo = Ratio.distance(self, self.nariz, self.nariz_inf)

        #Se dividen las distancias y obtenemos un ratio que nos indica el movimiento vertical de la cara
        ratio = (arriba / abajo)
        return (ratio)

    #Calcula el ratio de apertura/cierre del ojo derecho
    def ratio_ojo_derecho(self):
        #Medimos la media entre los dos puntos superiores e inferiores del ojo
        centro_arriba = Ratio.midpoint(self, self.ojo_derecho_arriba1, self.ojo_derecho_arriba2)
        centro_abajo = Ratio.midpoint(self, self.ojo_derecho_abajo1, self.ojo_derecho_abajo2)

        #Medimos la distancia media superior - media inferior y derecha - izquierda
        horizontal = Ratio.distance(self, self.ojo_derecho_derecha, self.ojo_derecho_izquierda)
        vertical = Ratio.distance(self, centro_arriba, centro_abajo)

        #Se dividen las distancias y obtenemos un ratio que nos indica la apertura/cierre del ojo derecho
        ratio = (horizontal / vertical)
        return(ratio)

    #Calcula el ratio de apertura/cierre del ojo izquierdo
    def ratio_ojo_izquierdo(self):
        #Medimos la media entre los dos puntos superiores e inferiores del ojo
        centro_arriba = Ratio.midpoint(self, self.ojo_izquierdo_arriba1, self.ojo_izquierdo_arriba2)
        centro_abajo = Ratio.midpoint(self, self.ojo_izquierdo_abajo1, self.ojo_izquierdo_abajo2)

        #Medimos la distancia media superior - media inferior y derecha - izquierda
        horizontal = Ratio.distance(self, self.ojo_izquierdo_derecha, self.ojo_izquierdo_izquierda)
        vertical = Ratio.distance(self, centro_arriba, centro_abajo)

        #Se dividen las distancias y obtenemos un ratio que nos indica la apertura/cierre del ojo izquierdo
        ratio = (horizontal / vertical)
        return (ratio)

########################################################################################################################
############################################### Calibración ############################################################
########################################################################################################################

    #Calcula el valor exacto del ratio donde el ojo pasa de abierto a cerrado y viceversa
    def calibracion_ojo(self, lim_abierto, lim_cerrado):
        RatioOjo = (lim_cerrado + lim_abierto) / 2
        return(RatioOjo)

    #Calcula los valores del ratio que separan los estados de subir, bajar, o qudarse centrado
    def calibracion_cara_vertical(self, lim_up, lim_down, center):
        media_up = (lim_up + center) / 2
        media_down = (center + lim_down) / 2
        return(media_up, media_down)

    #Calcula los valores del ratio que separan los estados de derecha, izquierda o centro
    def calibracion_cara_horizontal(self, lim_right, lim_left, center):
        media_right = (center + lim_right) / 2
        media_left = (center + lim_left) / 2
        return (media_right, media_left)

##################################################### FIN ##############################################################
########################################################################################################################
########################################################################################################################

if __name__ == '__main__':
    import cv2
    from Deteccion import *
    capture = cv2.VideoCapture(0)

    _, frame = capture.read()  # obtenermos la captura
    grayimage = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  # Escala de grises

    r = Ratio()
    r.extraer_puntos(grayimage)
    a = r.ratio_vertical()
    b = r.ratio_horizontal()
    c = r.ratio_ojo_derecho()
    e = r.ratio_ojo_izquierdo()

    print(a)
    print(b)
    print(c)
    print(e)