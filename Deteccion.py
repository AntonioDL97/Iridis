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

import dlib
from math import hypot

########################################################################################################################
########################################################################################################################
################################################### Deteccion ##########################################################

#La clase Deteccion sirve para detectar la cara y puntos de la cara.
class Deteccion:

    #Creamos los objetos detector de caras y puntos de la cara.
    def __init__(self):
        self.detector = dlib.get_frontal_face_detector()  #Detección de la cara con dlib.

        #Cargamos el archivo para detectar los puntos de la cara:
        self.pointdetector = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

    #Detecta las caras en una imagen y devuelve la que esté más centrada.
    def detect_face(self, grayimage):
        facelist = []
        faces = self.detector(grayimage)    #Crea un rectangulo para cada cara que encuentra.
        for face in faces:
            self.x1 = face.left()           #Limite izquierdo de la cara.
            self.y1 = face.top()            #Limite superior de la cara.
            self.x2 = face.right()          #Limite derecho de la cara.
            self.y2 = face.bottom()         #Limite inferior de la cara.

            #Guardamos los límites en una lista:
            pointlist = []
            pointlist.append(self.x1)
            pointlist.append(self.y1)
            pointlist.append(self.x2)
            pointlist.append(self.y2)

            #Añadimos todas las caras en una lista:
            facelist.append(pointlist)

        #Seleccionamos la cara que esté más centrada a partir del límite izquierdo de la cara:
        distance = []
        distance_2 = []
        for i in facelist:
            x1 = i[0] - 272
            p = abs(x1)
            distance.append(p)
            distance_2.append(p)

        #Añadimos un valor final por conveniencia:
        distance.append(500)
        distance_2.append(500)

        #Encontramos el valor más cercano al centro para seleccionar la cara:
        length = len(distance) - 1
        faceSelect = 0
        for j in range(0, length):
            if(distance[j] < distance[j + 1]):
                distance[j + 1] = distance[j]

        for l in range(0, length):
            if(distance_2[l] == distance[length]):
                faceSelect = l

        #Retornamos unicamente la cara que está más centrada:
        return(faces[faceSelect])

    #Detección de los puntos faciales a partir de una cara dada.
    def detect_landmarks(self, grayimage, points):
        faces = Deteccion.detect_face(self, grayimage)           #Extraemos la cara.

        #Extraemos los puntos seleccionados y añadimos las coordenadas en una lista:
        list = []
        for p in points:
            landmarks = self.pointdetector(grayimage, faces)     #Usamos el archivo de deteccion de puntos.
            x = landmarks.part(p).x                              #Coordenada x del punto.
            y = landmarks.part(p).y                              #Coordenada y del punto.

            #Creamos una lista para poner las dos coordenadas y las agregamos en la lista list[]:
            listxy = []
            listxy.append(x)
            listxy.append(y)
            list.extend(listxy)

        #Retornamos la lista con las cordenadas de todos los puntos deseados:
        return(list)

##################################################### FIN ##############################################################
########################################################################################################################
########################################################################################################################

if __name__ == '__main__':
    import cv2
    capture = cv2.VideoCapture(0)

    _, frame = capture.read()  # obtenermos la captura
    grayimage = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  # Escala de grises

    d = Deteccion()
    p = [30]
    x = d.detect_landmarks(grayimage, p)
    #print(x)