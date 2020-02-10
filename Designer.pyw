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

import sys
from PyQt5 import QtCore, QtGui, uic, QtWidgets
from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5.QtWidgets import (QApplication, QDialog, QFileDialog, QInputDialog, QMessageBox)
import time
import dlib
import cv2
import win32api
import win32con
import numpy as np
import pandas as pd
from math import hypot
from Cursor import *

########################################################################################################################
########################################################################################################################
################################################### Designer ###########################################################

#Esta es la clase principal del programa.
#Esta clase controla el funcionamiento del programa. La programación de cada botón del formulario está aquí.

#Cargar nuestro formulario *.ui.
form_class = uic.loadUiType("Iridis.ui")[0]

#Crear la Clase MyWindowClass con el formulario cargado.
class MyWindowClass(QMainWindow, form_class):

    calibra = ''
    calibra1 = 'Calibrando, espere unos segundos...'
    calibra2 = 'Calibración terminada correctamente!'

    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        self.setupUi(self)
        self.pantallas.setCurrentIndex(0) #Empezamos en la pantalla 1 por defecto, la de activacion de la aplicación.

        #Pantalla configuración:
        self.rb2.setChecked(True)               #Click izquierdo con ojo derecho por defecto.
        self.velocidades.clear()
        distrolist = ['1','2','3','4','5','6','7','8','9','10']
        self.velocidades.addItems(distrolist)
        self.velocidades.setCurrentIndex(3)     #Velocidad 4 por defecto.
        self.act = 0                            #Variable que indica que la aplicacion empieza desactivada.
        self.estado.setText('Desactivado')      #Texto que indica que la aplicación está desactivada.

        #Base datos calibraciones
        self.namelist = []
        self.base_datos = pd.read_csv('calibraciones.txt')
        self.columnaName = int(self.base_datos.shape[0])
        for i in range(0,self.columnaName):
            cada_nombre = self.base_datos.loc[i,'Name']
            self.namelist.append(cada_nombre)
        self.nombres.addItems(self.namelist)
        self.nombres.setCurrentIndex(0)

        #Pantallas calibracion:
        self.calibracion2.setText(self.calibra) #Todas empiezan con texto vacio.
        self.calibracion3.setText(self.calibra)
        self.calibracion4.setText(self.calibra)

        self.cali2.setText(self.calibra)
        self.cali3.setText(self.calibra)
        self.cali4.setText(self.calibra)
        self.cali5.setText(self.calibra)
        self.cali6.setText(self.calibra)

        self.pushButton_8.setEnabled(False)     #Todos los botones 'siguiente' empiezan deshabilitados
        self.pushButton_10.setEnabled(False)
        self.pushButton_12.setEnabled(False)
        self.pushButton_24.setEnabled(False)
        self.pushButton_27.setEnabled(False)
        self.pushButton_30.setEnabled(False)
        self.pushButton_33.setEnabled(False)
        self.pushButton_36.setEnabled(False)

        self.nombre = self.lineEdit.setText('')

        #Las variable inferiores activan/desactivan las cámaras para la calibración de ojos y cara.
        #Iniciamos en modo desactivado:
        self.cam_calibracion = 0
        self.cam_calibracion_cara = 0

        #Definición de variables usadas posteriormente:
        self.capture = cv2.VideoCapture(0)  #Captura de la imagen de la webcam.
        self.R = Ratio()                    #Clase Ratio.
        self.C = Cursor()                   #Clase Cursor.

        self.ojoClick = 0                   #Selección de ojo
        self.velocidad = 4                  #Velocidad por defecto.
        self.RDerecho = 4.5                 #Ratio ojo derecho por defecto.
        self.RIzquierdo = 4.5               #Ratio ojo izquierdo por defecto.
        self.Rup = 0.6                      #Ratio hacia arriba por defecto.
        self.Rdown = 1.3                    #Ratio hacia abajo por defecto.
        self.Rright = 0.7                   #Ratio hacia la derecha por defecto.
        self.Rleft = 1.3                    #Ratio hacia la izquierda por defecto.

########################################################################################################################
######################################## Botones de la pantalla principal ##############################################
########################################################################################################################

    #Cambiamos a la pantalla 1, principal.
    def des_activar(self):
        self.pantallas.setCurrentIndex(0)

    #Cambiamos a la pantalla 2, de configuracion.
    def configurar(self):
        self.pantallas.setCurrentIndex(1)

    #Cambiamos a la pantalla 3, de instrucciones.
    def instrucciones(self):
        self.pantallas.setCurrentIndex(2)

########################################################################################################################
########################################## Pantalla de activar/desactivar ##############################################
########################################################################################################################

    #Activa el programa para controlar el ratón del ordenador con la cara.
    def activar(self):
        cv2.destroyAllWindows()
        self.capture = cv2.VideoCapture(0)
        self.cam_calibracion = 0
        self.cam_calibracion_cara = 0
        self.act = 1
        self.estado.setText('Activado')
        ratio = [1, 1, 3, 3]                    #Ratio predefinido en caso de fallo.

        while(self.act == 1):
            _, frame = self.capture.read()      #Obtenermos la captura.
            self.grayimage = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  #Escala de grises.

            self.C.position()                   #Obtenemos la posicion del cursor.

            for t in range(0, self.columnaName):
                if (self.nombres.currentIndex() == t):
                    self.velocidad = self.base_datos.loc[t, 'velocidad']
                    self.ojoClick = self.base_datos.loc[t, 'ojo_click']
                    self.Rright = self.base_datos.loc[t, 'lim_derecho']
                    self.Rleft = self.base_datos.loc[t, 'lim_izquierdo']
                    self.Rup = self.base_datos.loc[t, 'lim_arriba']
                    self.Rdown = self.base_datos.loc[t, 'lim_abajo']
                    self.RDerecho = self.base_datos.loc[t, 'lim_ojo_derecho']
                    self.RIzquierdo = self.base_datos.loc[t, 'lim_ojo_izquierdo']
            try:


                #Si el ratio cambia, el cursor se mueve:
                ratio = self.C.ratios(self.grayimage)
                self.C.move_vertical(self.Rup, self.Rdown, self.velocidad)
                self.C.position()
                self.C.move_horizontal(self.Rright, self.Rleft, self.velocidad)


                #Llamamos a las funciones para hacerClick y DobleClick en función de la configuración escogida:
                if (self.rb2.isChecked()):
                    self.C.click_doubleclick(ratio[2], self.RDerecho)
                    self.C.right_click(ratio[3], self.RIzquierdo)
                    self.ojoClick = 0
                if (self.rb1.isChecked()):
                    self.C.click_doubleclick(ratio[3], self.RIzquierdo)
                    self.C.right_click(ratio[2], self.RDerecho)
                    self.ojoClick = 1

                #Variamos la velocidad en función de la configuración escogida:
                if (self.velocidades.currentIndex() == 0):
                    self.velocidad = 1
                if (self.velocidades.currentIndex() == 1):
                    self.velocidad = 2
                if (self.velocidades.currentIndex() == 2):
                    self.velocidad = 3
                if (self.velocidades.currentIndex() == 3):
                    self.velocidad = 4
                if (self.velocidades.currentIndex() == 4):
                    self.velocidad = 5
                if (self.velocidades.currentIndex() == 5):
                    self.velocidad = 6
                if (self.velocidades.currentIndex() == 6):
                    self.velocidad = 7
                if (self.velocidades.currentIndex() == 7):
                    self.velocidad = 8
                if (self.velocidades.currentIndex() == 8):
                    self.velocidad = 9
                if (self.velocidades.currentIndex() == 9):
                    self.velocidad = 10

            except:
                #Si falla no hace nada.
                pass

            #cv2.imshow('video', self.grayimage)  #se abre una ventana con la camara

            #Esperamos la tecla "esc" para cerrar:
            key = cv2.waitKey(1)
            if key == 27:
                break

    #Desactiva el programa para controlar el ratón del ordenador con la cara
    def desactivar(self):
        self.act = 0
        self.estado.setText('Desactivado')
        self.capture.release()
        cv2.destroyAllWindows()
        self.cam_calibracion = 0
        self.cam_calibracion_cara = 0

########################################################################################################################
############################################ Pantalla de Configuración #################################################
########################################################################################################################

    #Guarda la calibración y los datos de configuración deseados.
    def aceptar(self):
        self.pantallas.setCurrentIndex(15)
        self.nombre = self.lineEdit.setText('')

        # Llamamos a las funciones para hacerClick y DobleClick en función de la configuración escogida:
        if (self.rb2.isChecked()):
            self.ojoClick = 0
        if (self.rb1.isChecked()):
            self.ojoClick = 1

        # Variamos la velocidad en función de la configuración escogida:
        if (self.velocidades.currentIndex() == 0):
            self.velocidad = 1
        if (self.velocidades.currentIndex() == 1):
            self.velocidad = 2
        if (self.velocidades.currentIndex() == 2):
            self.velocidad = 3
        if (self.velocidades.currentIndex() == 3):
            self.velocidad = 4
        if (self.velocidades.currentIndex() == 4):
            self.velocidad = 5
        if (self.velocidades.currentIndex() == 5):
            self.velocidad = 6
        if (self.velocidades.currentIndex() == 6):
            self.velocidad = 7
        if (self.velocidades.currentIndex() == 7):
            self.velocidad = 8
        if (self.velocidades.currentIndex() == 8):
            self.velocidad = 9
        if (self.velocidades.currentIndex() == 9):
            self.velocidad = 10

    def guardar(self):
        self.pantallas.setCurrentIndex(1)
        self.nombre = self.lineEdit.text()
        #Guardamos las calibraciones tomadas en un documento de texto
        calibraciones = 'calibraciones.txt'
        with open(calibraciones, 'a') as file:
            file.write(str(self.nombre))
            file.write(',')
            file.write(str(self.velocidad))
            file.write(',')
            file.write(str(self.ojoClick))
            file.write(',')
            file.write(str(self.Rright))
            file.write(',')
            file.write(str(self.Rleft))
            file.write(',')
            file.write(str(self.Rup))
            file.write(',')
            file.write(str(self.Rdown))
            file.write(',')
            file.write(str(self.RDerecho))
            file.write(',')
            file.write(str(self.RIzquierdo))
            file.write('\n')

        self.namelist.append(self.nombre)
        self.nombres.addItem(self.nombre)

    #Se va a la pantalla principal de calibracion de ojos.
    def calibrar(self):
        self.pantallas.setCurrentIndex(3)

    #Se va a la pantalla principal de calibracion de cara.
    def calibrar_cara(self):
        self.pantallas.setCurrentIndex(8)

########################################################################################################################
############################################ Pantallas de calibracion ojos #############################################
########################################################################################################################

    #Boton de paso siguiente + encender cámara.
    def next_0(self):
        self.pantallas.setCurrentIndex(4)
        self.capture = cv2.VideoCapture(0)
        self.cam_calibracion = 1                #Se activa la variable que comienza con la calibración.
        while(self.cam_calibracion == 1):
            try:
                _, frame = self.capture.read()  #Obtenemos la captura.
                self.grayimage = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) #Escala de grises.
                cv2.imshow('Video calibracion', self.grayimage) #Activa la camara para que la persona se vea mientras calibra.
                cv2.moveWindow('Video calibracion', 0, 0)

                #Esperamos la tecla "esc" para cerrar:
                key = cv2.waitKey(1)
                if key == 27:
                    break
            except:
                #Si falla no hace nada.
                pass

    #Volvemos a la pantalla de configuracion.
    def atras_0(self):
        self.pantallas.setCurrentIndex(1)

    #Vamos a la pantalla de calibracion de ojos abiertos.
    def next_1(self):
        self.pantallas.setCurrentIndex(5)

    #Volvemos a la pantalla prinicipal de calibracion + cerrar cámara.
    def atras_1(self):
        self.pantallas.setCurrentIndex(3)
        self.capture.release()
        self.cam_calibracion = 0
        cv2.destroyWindow('Video calibracion')

    #Se inicia la calibracion de los ojo abiertos.
    def cuenta_atras_2(self):
        self.calibracion2.setText(self.calibra1)    #Se indica en texto que la calibracion ha empezado.
        self.cam_calibracion = 1

        #Se inicializan las variables a 0:
        ODA = 0     #Variable de ratio de ojo derecho abierto.
        OIA = 0     #Variable de ratio de ojo izquierdo abierto.
        cont = 0

        #Adquisición de 100 valores para cada dato:
        while (cont < 100):
            try:
                self.pushButton_8.setEnabled(False)                         #Siguiente bloqueado.
                self.pushButton_15.setEnabled(False)                        #Atras bloqueado.
                _, frame = self.capture.read()                              #Obtenermos la captura.
                self.grayimage = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)    #Escala de grises.
                cv2.imshow('Video calibracion', self.grayimage)
                cv2.moveWindow('Video calibracion', 0, 0)
                self.R.extraer_puntos(self.grayimage)
                ODA = ODA + self.R.ratio_ojo_derecho()
                OIA = OIA + self.R.ratio_ojo_izquierdo()
                cont = cont + 1

                #Esperamos la tecla "esc" para cerrar.
                key = cv2.waitKey(1)
                if key == 27:
                    break
            except:
                #Si falla no hace nada.
                pass

        #Se hace la media de los ratios calculados para los dos ojos:
        self.media_ODA = ODA / cont
        self.media_OIA = OIA / cont
        print(self.media_ODA, self.media_OIA)

        self.calibracion2.setText(self.calibra2)    #Se indica por pantalla que la calibracion a terminado.
        self.pushButton_8.setEnabled(True)          #Siguiente habilitado.
        self.pushButton_15.setEnabled(True)         #Atras habilitado.

    #Se pasa a la pantalla de calibracion del ojo derecho cerrado.
    def next_2(self):
        self.pantallas.setCurrentIndex(6)

    #Se vuelve a la pantalla de calibracion de ojos abiertos.
    def atras_2(self):
        self.pantallas.setCurrentIndex(4)

    #Se inicia la calibracion del ojo derecho cerrado.
    def cuenta_atras_3(self):
        self.calibracion3.setText(self.calibra1) #Se indica en texto que la calibracion ha empezado.
        self.cam_calibracion = 1  #Se activa la variable de calibracion.

        #Se inicializan las variables a 0:
        ODC = 0 #Variable del ratio de ojo derecho cerrado.
        cont = 0

        #Adquisición de 100 valores para ODC:
        while (cont < 100):
            try:
                self.pushButton_10.setEnabled(False)                        #Siguiente.
                self.pushButton_16.setEnabled(False)                        #Atras.
                _, frame = self.capture.read()                              #Obtenermos la captura.
                self.grayimage = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)    #Escala de grises.
                cv2.imshow('Video calibracion', self.grayimage)
                cv2.moveWindow('Video calibracion', 0, 0)
                self.R.extraer_puntos(self.grayimage)
                ODC = ODC + self.R.ratio_ojo_derecho()
                cont = cont + 1

                #Esperamos la tecla "esc" para cerrar:
                key = cv2.waitKey(1)
                if key == 27:
                    break
            except:
                #Si falla no hace nada.
                pass

        #Se hace la media de los ratios calculados para el ojo derecho cerrado:
        self.media_ODC = ODC / cont
        print(self.media_ODC)

        self.calibracion3.setText(self.calibra2)    #Se indica por pantalla que la calibracion a terminado.
        self.pushButton_10.setEnabled(True)         #Siguiente.
        self.pushButton_16.setEnabled(True)         #Atras.

    #Se pasa a la pantalla de calibración del ojo izquierdo cerrado.
    def next_3(self):
        self.pantallas.setCurrentIndex(7)

    #Se vuelve a la pantalla de calibracion de los dos ojos abiertos.
    def atras_3(self):
        self.pantallas.setCurrentIndex(5)

    #Se inicia la calibracion del ojo izquierdo cerrado.
    def cuenta_atras_4(self):
        self.calibracion4.setText(self.calibra1)        #Se indica en texto que la calibracion ha empezado.
        self.cam_calibracion = 1

        #Se inicializan las variables a 0:
        OIC = 0     #Variable del ratio de ojo izquierdo cerrado.
        cont = 0

        #Adquisición de 100 valores para OIC:
        while (cont < 100):
            try:
                self.pushButton_12.setEnabled(False)    #Siguiente.
                self.pushButton_17.setEnabled(False)    #Atras.
                _, frame = self.capture.read()                              #Obtenermos la captura.
                self.grayimage = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)    #Escala de grises.
                cv2.imshow('Video calibracion', self.grayimage)
                cv2.moveWindow('Video calibracion', 0, 0)
                self.R.extraer_puntos(self.grayimage)
                OIC = OIC + self.R.ratio_ojo_izquierdo()
                cont = cont + 1

                #Esperamos la tecla "esc" para cerrar:
                key = cv2.waitKey(1)
                if key == 27:
                    break
            except:
                #Si falla no hace nada.
                pass
        #Se hace la media de los ratios calculados para el ojo izquierdo cerrado:
        self.media_OIC = OIC / cont
        print(self.media_OIC)

        self.calibracion4.setText(self.calibra2)  #Se indica por pantalla que la calibracion a terminado.
        self.pushButton_12.setEnabled(True)  #Siguiente.
        self.pushButton_17.setEnabled(True)  #Atras.

    #Se establecen los ratios límite calibrados y se va a la pantalla de inicio de activar/desactivar.
    def finalizar(self):
        self.pantallas.setCurrentIndex(1)
        self.capture.release()
        self.cam_calibracion = 0
        cv2.destroyWindow('Video calibracion')  #Se saca la camara de calibracion.
        self.RDerecho = self.R.calibracion_ojo(self.media_ODA, self.media_ODC)
        self.RIzquierdo = self.R.calibracion_ojo(self.media_OIA, self.media_OIC)
        print(self.RDerecho, self.RIzquierdo)

    #Se vuelve a la pantalla de calibracion del ojo izquierdo cerrado.
    def atras_4(self):
        self.pantallas.setCurrentIndex(6)

########################################################################################################################
############################################ Pantallas de calibracion cara #############################################
########################################################################################################################

    #Volvemos a la pantalla de configuracion.
    def atras_c0(self):
        self.pantallas.setCurrentIndex(1)

    #Se va a la primera pantalla de calibracion + activación de la cámara.
    def next_c0(self):
        self.pantallas.setCurrentIndex(9)
        self.capture = cv2.VideoCapture(0)
        self.cam_calibracion_cara = 1
        while (self.cam_calibracion_cara == 1):
            try:
                _, frame = self.capture.read()                              #Obtenemos la captura.
                self.grayimage = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)    #Escala de grises.
                cv2.imshow('Video calibracion cara', self.grayimage)
                cv2.moveWindow('Video calibracion cara', 0, 0)

                #Esperamos la tecla "esc" para cerrar:
                key = cv2.waitKey(1)
                if key == 27:
                    break
            except:
                #Si falla no hace nada.
                pass

    #Volvemos a la pantalla inicial de calibración + desactivación de la cámara.
    def atras_c1(self):
        self.pantallas.setCurrentIndex(8)
        self.capture.release()
        self.cam_calibracion_cara = 0
        cv2.destroyWindow('Video calibracion cara')

    #Se va a la pantalle de calibración de la cara hacia arriba.
    def next_c1(self):
        self.pantallas.setCurrentIndex(10)

    #Se vuelve a la pantalla de calibración de la cara hacia arriba.
    def atras_c2(self):
        self.pantallas.setCurrentIndex(9)

    #Se inicia la calibración de la cara hacia arriba.
    def ini_cali_2(self):
        self.cali2.setText(self.calibra1)  #Se indica en texto que la calibracion ha empezado.
        self.cam_calibracion_cara = 1

        #Inicializamos las variables:
        FU = 0 #Variable del ratio de cara hacia arriba.
        cont = 0

        #Adquisición de 100 valores para FU:
        while (cont < 100):
            try:
                self.pushButton_24.setEnabled(False)                        #Siguiente.
                self.pushButton_23.setEnabled(False)                        #Atras.
                _, frame = self.capture.read()                              #Obtenemos la captura.
                self.grayimage = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)    #Escala de grises.
                cv2.imshow('Video calibracion cara', self.grayimage)
                cv2.moveWindow('Video calibracion cara', 0, 0)
                self.R.extraer_puntos(self.grayimage)
                FU = FU + self.R.ratio_vertical()
                cont = cont + 1

                #Esperamos la tecla "esc" para cerrar:
                key = cv2.waitKey(1)
                if key == 27:
                    break
            except:
                #Si falla no hace nada.
                pass

        #Se hace la media de los ratios calculados para la cara hacia arriba.
        self.media_FU = FU / cont
        self.cali2.setText(self.calibra2)
        print(self.media_FU)

        self.pushButton_24.setEnabled(True)  #Siguiente.
        self.pushButton_23.setEnabled(True)  #Atras.

    #Se va a la pantalla de calibración de la cara hacia abajo.
    def next_c2(self):
        self.pantallas.setCurrentIndex(11)

    #Se vuelve a la pantalla de calibración de la cara hacia arriba.
    def atras_c3(self):
        self.pantallas.setCurrentIndex(10)

    #Se inicia la calibración de la cara hacia abajo.
    def ini_cali_3(self):
        self.cali3.setText(self.calibra1)  #Se indica en texto que la calibracion ha empezado.
        self.cam_calibracion_cara = 1

        #Inicializamos las variables:
        FD = 0 #Variable del ratio de la cara hacia abajo.
        cont = 0

        #Adquisición de 100 valores para FD:
        while (cont < 100):
            try:
                self.pushButton_27.setEnabled(False)                        #Siguiente.
                self.pushButton_26.setEnabled(False)                        #Atras.
                _, frame = self.capture.read()                              #Obtenemos la captura.
                self.grayimage = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)    #Escala de grises.
                cv2.imshow('Video calibracion cara', self.grayimage)
                cv2.moveWindow('Video calibracion cara', 0, 0)
                self.R.extraer_puntos(self.grayimage)
                FD = FD + self.R.ratio_vertical()
                cont = cont + 1

                #Esperamos la tecla "esc" para cerrar:
                key = cv2.waitKey(1)
                if key == 27:
                    break
            except:
                #Si falla no hace nada.
                pass

        #Se hace la media de los ratios calculados para la cara hacia abajo.
        self.media_FD = FD / cont
        print(self.media_FD)

        self.cali3.setText(self.calibra2)
        self.pushButton_27.setEnabled(True)  #Siguiente.
        self.pushButton_26.setEnabled(True)  #Atras.

    #Se va a la pantalla de calibración de la cara hacia la derecha.
    def next_c3(self):
        self.pantallas.setCurrentIndex(12)

    #Se vuelve a la pantalla de calibración de la cara hacia abajo.
    def atras_c4(self):
        self.pantallas.setCurrentIndex(11)

    #Se inicia la calibración de la cara hacia la derecha.
    def ini_cali_4(self):
        self.cali4.setText(self.calibra1)  #Se indica en texto que la calibracion ha empezado.
        self.cam_calibracion_cara = 1

        #Se inicializan las variables:
        FR = 0  #Variable del ratio de la cara hacia la derecha.
        cont = 0

        #Adquisición de 100 valores para FR:
        while (cont < 100):
            try:
                self.pushButton_30.setEnabled(False)                        #Siguiente.
                self.pushButton_29.setEnabled(False)                        #Atras.
                _, frame = self.capture.read()                              #Obtenemos la captura.
                self.grayimage = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)    #Escala de grises.
                cv2.imshow('Video calibracion cara', self.grayimage)
                cv2.moveWindow('Video calibracion cara', 0, 0)
                self.R.extraer_puntos(self.grayimage)
                FR = FR + self.R.ratio_horizontal()
                cont = cont + 1

                #Esperamos la tecla "esc" para cerrar:
                key = cv2.waitKey(1)
                if key == 27:
                    break
            except:
                #Si falla no hace nada.
                pass

        #Se hace la media de los ratios calculados para la cara hacia la derecha.
        self.media_FR = FR / cont
        print(self.media_FR)

        self.cali4.setText(self.calibra2)
        self.pushButton_30.setEnabled(True)  #Siguiente.
        self.pushButton_29.setEnabled(True)  #Atras.

    #Se va a la pantalla de calibración de la cara hacia la izquierda.
    def next_c4(self):
        self.pantallas.setCurrentIndex(13)

    #Se vuelve a la pantalla de calibración de la cara hacia la derecha.
    def atras_c5(self):
        self.pantallas.setCurrentIndex(12)

    #Se inicia la calibración de la cara hacia la izquierda.
    def ini_cali_5(self):
        self.cali5.setText(self.calibra1)  #Se indica en texto que la calibracion ha empezado.
        self.cam_calibracion_cara = 1

        #Inicializamos las variables:
        FL = 0  #Variable del ratio de la cara hacia la izquierda.
        cont = 0

        #Adquisición de 100 valores para FL:
        while (cont < 100):
            try:
                self.pushButton_33.setEnabled(False)  #Siguiente.
                self.pushButton_32.setEnabled(False)  #Atras.
                _, frame = self.capture.read()  #Obtenemos la captura.
                self.grayimage = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  #Escala de grises.
                cv2.imshow('Video calibracion cara', self.grayimage)
                cv2.moveWindow('Video calibracion cara', 0, 0)
                self.R.extraer_puntos(self.grayimage)
                FL = FL + self.R.ratio_horizontal()
                cont = cont + 1

                #Esperamos la tecla "esc" para cerrar:
                key = cv2.waitKey(1)
                if key == 27:
                    break
            except:
                #Si falla no hace nada.
                pass

        #Se hace la media de los ratios calculados para la cara hacia la izquierda.
        self.media_FL = FL / cont
        print(self.media_FL)

        self.cali5.setText(self.calibra2)
        self.pushButton_33.setEnabled(True)  #Siguiente.
        self.pushButton_32.setEnabled(True)  #Atras.

    #Se va la pantalla de calibración de la cara centrada.
    def next_c5(self):
        self.pantallas.setCurrentIndex(14)

    #Se vuelve a la pantalla de calibración de la cara hacia la izquierda.
    def atras_c6(self):
        self.pantallas.setCurrentIndex(13)

    #Se inicia la calibración de la cara centrada.
    def ini_cali_c6(self):
        self.cali6.setText(self.calibra1)
        self.cam_calibracion_cara = 1

        #Se inicializan las variables:
        FCH = 0     #Variable del ratio de la cara horizontal.
        FCV = 0     #Variable del ratio de la cara vertical.
        cont = 0

        #Adquisición de 100 valores de FCH y FCV:
        while (cont < 100):
            try:
                self.pushButton_36.setEnabled(False)                        #Finalizar calibracion cara.
                self.pushButton_35.setEnabled(False)                        #Atras.
                _, frame = self.capture.read()                              #Obtenemos la captura.
                self.grayimage = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)    #Escala de grises.
                cv2.imshow('Video calibracion cara', self.grayimage)
                cv2.moveWindow('Video calibracion cara', 0, 0)
                self.R.extraer_puntos(self.grayimage)
                FCH = FCH + self.R.ratio_horizontal()
                FCV = FCV + self.R.ratio_vertical()
                cont = cont + 1

                #Esperamos la tecla "esc" para cerrar:
                key = cv2.waitKey(1)
                if key == 27:
                    break
            except:
                #Si falla no hace nada.
                pass

        #Se hace la media de los ratios calculados para la cara centrada.
        self.media_FCH = FCH / cont
        self.media_FCV = FCV / cont
        print(self.media_FCH, self.media_FCV)

        self.cali6.setText(self.calibra2)
        self.pushButton_36.setEnabled(True)  #Siguiente.
        self.pushButton_35.setEnabled(True)  #Atras.

    #Se establecen los ratios límite calibrados y se va a la pantalla de inicio de activar/desactivar.
    def finalizar_c(self):
        self.pantallas.setCurrentIndex(1)
        self.capture.release()
        self.cam_calibracion_cara = 0

        cv2.destroyWindow('Video calibracion cara')

        self.Rup = self.R.calibracion_cara_vertical(self.media_FU, self.media_FD, self.media_FCV)[0]
        self.Rdown = self.R.calibracion_cara_vertical(self.media_FU, self.media_FD, self.media_FCV)[1]
        self.Rright = self.R.calibracion_cara_horizontal(self.media_FR, self.media_FL, self.media_FCH)[0]
        self.Rleft = self.R.calibracion_cara_horizontal(self.media_FR, self.media_FL, self.media_FCH)[1]
        print(self.Rup, self.Rdown, self.Rright, self.Rleft)

##################################################### FIN ##############################################################
########################################################################################################################
########################################################################################################################

if __name__ == '__main__':
    app = QApplication(sys.argv)
    MyWindow = MyWindowClass(None)
    MyWindow.show()
    app.exec_()
