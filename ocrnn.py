# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ocrnnui.ui'
#
# Created by: PyQt5 UI code generator 5.10.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets
from keras.models import Sequential
from keras.layers import Dense, Dropout, Flatten
#from keras.layers import BatchNormalization
from keras.layers import Conv2D, MaxPooling2D
import cv2
import numpy as np
import os.path, sys

class Point:
    x, y = 0, 0
    def __init__(self, nx=0, ny=0): 
        self.x = nx
        self.y = ny
        
class Shape:
    location = Point()
    number = 0
    def __init__(self, L, S):
        self.location = L
        self.number = S

class Shapes:
    shapes = []
    def __init__(self):
        self.shapes = []
    def NumberOfShapes(self):
        return len(self.shapes)
    def NewShape(self, L, S):
        shape = Shape(L,S)
        self.shapes.append(shape)
    def GetShape(self, Index):
        return self.shapes[Index]

class Painter(QtWidgets.QWidget):
    ParentLink = 0
    MouseLoc = Point(0,0)  
    LastPos = Point(0,0)  
    def __init__(self, parent):
        super(Painter, self).__init__()
        self.ParentLink = parent
        self.MouseLoc = Point(0,0)
        self.LastPos = Point(0,0) 
    def mousePressEvent(self, event): 
        self.ParentLink.IsPainting = True
        self.ParentLink.ShapeNum += 1
        self.LastPos = Point(0,0)    
    def mouseMoveEvent(self, event):
        if(self.ParentLink.IsPainting == True):
            self.MouseLoc = Point(event.x(),event.y())
            if((self.LastPos.x != self.MouseLoc.x) and (self.LastPos.y != self.MouseLoc.y)):
                self.LastPos =  Point(event.x(),event.y())
                self.ParentLink.DrawingShapes.NewShape(self.LastPos, self.ParentLink.ShapeNum)
            self.repaint()             
             
    def mouseReleaseEvent(self, event):
        if(self.ParentLink.IsPainting == True):
            self.ParentLink.IsPainting = False
    def paintEvent(self,event):
        painter = QtGui.QPainter()
        painter.begin(self)
        self.drawLines(event, painter)
        painter.end()
    def drawLines(self, event, painter):   
        for i in range(self.ParentLink.DrawingShapes.NumberOfShapes()-1):     
            T = self.ParentLink.DrawingShapes.GetShape(i)
            T1 = self.ParentLink.DrawingShapes.GetShape(i+1) 
            if(T.number== T1.number):
                pen = QtGui.QPen(QtGui.QColor(0, 0, 0), 12, QtCore.Qt.SolidLine)
                painter.setPen(pen)
                painter.drawLine(T.location.x, T.location.y, T1.location.x, T1.location.y)
        
        



image_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir) + '/Images/'

class Ui_MainWindow(object):
    DrawingShapes = Shapes()
    PaintPanel = 0
    IsPainting = False
    ShapeNum = 0
    def __init__(self):
        super(Ui_MainWindow,self).__init__()
        
        self.mappings=self.load_char_mappings('emnist-balanced-mapping.txt')
        self.file_name=" "
        self.predict_Svalue="predict...."
        self.cnn_model = Sequential()
        self.cnn_model.add(Conv2D(filters=32, kernel_size=3, padding='same', activation='relu', 
                        input_shape=(28, 28, 1)))
        self.cnn_model.add(MaxPooling2D(pool_size=2))
        
        self.cnn_model.add(Dropout(0.5))
        self.cnn_model.add(Conv2D(filters=64,kernel_size=3,padding="same",activation="relu"))
        self.cnn_model.add(MaxPooling2D(pool_size=2))
        self.cnn_model.add(Dropout(0.3))
        self.cnn_model.add(Flatten())
        self.cnn_model.add(Dense(512, activation='relu'))
        self.cnn_model.add(Dropout(0.2))

        self.cnn_model.add(Dense(47, activation='softmax')) 
        self.cnn_model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
        self.cnn_model.load_weights('weights.best.CNN.hdf5')
        
        #self.setupUi(self)
        #self.setObjectName('Rig Helper')

        
    def ClearSlate(self):
        self.DrawingShapes = Shapes()
        self.PaintPanel.repaint()  
        self.pixmap = QtGui.QPixmap(image_path + str(-1) +".png")
        #self.label.setPixmap(self.pixmap)
    
    
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.setEnabled(True)
        MainWindow.resize(800, 600)
        MainWindow.setDocumentMode(False)
        MainWindow.setDockOptions(QtWidgets.QMainWindow.AllowTabbedDocks|QtWidgets.QMainWindow.AnimatedDocks)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.Main_label = QtWidgets.QLabel(self.centralwidget)
        self.Main_label.setGeometry(QtCore.QRect(0, 0, 801, 571))
        self.Main_label.setObjectName("Main_label")
        self.load_img_btn = QtWidgets.QPushButton(self.centralwidget)
        self.load_img_btn.setGeometry(QtCore.QRect(640, 50, 111, 31))
        self.load_img_btn.setObjectName("load_img_btn")
        
        self.widget_scribble = QtWidgets.QWidget(self.centralwidget)
        self.widget_scribble.setGeometry(QtCore.QRect(0, 280, 400, 400))
        self.widget_scribble.setObjectName("widget_scribble")
        
        self.load_img_btn.clicked.connect(self.set_img)
        
        self.predict_btn = QtWidgets.QPushButton(self.centralwidget)
        self.predict_btn.setGeometry(QtCore.QRect(640, 140, 111, 31))
        self.predict_btn.setObjectName("predict_btn")
        
        self.predict_btn.clicked.connect(self.cnn_predict)
        
                
        self.predict_btn2 = QtWidgets.QPushButton(self.centralwidget)
        self.predict_btn2.setGeometry(QtCore.QRect(640, 300, 111, 31))
        self.predict_btn2.setObjectName("predict_drawing_btn")
        
        self.predict_btn2.clicked.connect(self.cnn_predict2)
        
        self.predict_label = QtWidgets.QLabel(self.centralwidget)
        self.predict_label.setGeometry(QtCore.QRect(640, 460, 111, 41))
        self.predict_label.setFrameShape(QtWidgets.QFrame.Box)
        
        
        #    
        self.DrawingFrame = QtWidgets.QStackedWidget(self.centralwidget)
        self.DrawingFrame.setGeometry(QtCore.QRect(40, 351, 201, 201))
        self.DrawingFrame.setFrameShape(QtWidgets.QFrame.Box)
        self.DrawingFrame.setFrameShadow(QtWidgets.QFrame.Plain)
        self.DrawingFrame.setObjectName("DrawingFrame")
        self.page = QtWidgets.QWidget()
        self.page.setObjectName("page")
        self.DrawingFrame.addWidget(self.page)
        self.page_2 = QtWidgets.QWidget()
        self.page_2.setObjectName("page_2")
        self.DrawingFrame.addWidget(self.page_2)
        self.Clear_Button = QtWidgets.QPushButton(self.centralwidget)
        self.Clear_Button.setGeometry(QtCore.QRect(80, 551, 111, 31))
        self.Clear_Button.setObjectName("Clear_Button")
        self.PaintPanel = Painter(self)
        self.PaintPanel.close()
        self.DrawingFrame.insertWidget(0,self.PaintPanel)
        self.DrawingFrame.setCurrentWidget(self.PaintPanel)
        #self.label = QtWidgets.QLabel(self)
        #self.label.setGeometry(QtCore.QRect(460, 70, 280, 280))
        self.pixmap = QtGui.QPixmap(image_path + str(-1) +".png")
        #self.label.setPixmap(self.pixmap)
        self.Clear_Button.clicked.connect(self.ClearSlate)
        #
        
        
        #
        
        font = QtGui.QFont()
        font.setPointSize(20)
        font.setBold(True)
        font.setItalic(True)
        font.setWeight(85)
        self.predict_label.setFont(font)
        self.predict_label.setMouseTracking(False)

        ##new
        self.predict_label.setStyleSheet("color: rgb(0, 0, 0);\n"
"background-color: rgb(255, 255, 255);\n"
"font: 75 10pt \"Arial\";")
        self.predict_label.setObjectName("predict_label")
        self.loadedImg_lab = QtWidgets.QLabel(self.centralwidget)
        self.loadedImg_lab.setGeometry(QtCore.QRect(30, 20, 200, 200))
        self.loadedImg_lab.setFrameShape(QtWidgets.QFrame.Box)
        self.loadedImg_lab.setObjectName("loadedImg_lab")
        #self.processedImg_view = QtWidgets.QLabel(self.centralwidget)
        #self.processedImg_view.setGeometry(QtCore.QRect(40, 330, 311, 191))
        #self.processedImg_view.setFrameShape(QtWidgets.QFrame.Box)
        #self.processedImg_view.setObjectName("processedImg_view")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 21))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "OCR"))
        self.Main_label.setText(_translate("MainWindow", ""))
        
        self.load_img_btn.setText(_translate("MainWindow", "Load img"))
        self.predict_btn.setText(_translate("MainWindow", "predict"))
        self.predict_btn2.setText(_translate("MainWindow", "predict from drawing"))
        self.predict_label.setText(_translate("MainWindow", "predict...."))
        self.loadedImg_lab.setText(_translate("MainWindow", ""))
        #self.processedImg_view.setText(_translate("MainWindow", ""))
        self.Clear_Button.setText(_translate("MainWindow", "Clear"))
    
    def set_img(self):
        self.file_name,_=QtWidgets.QFileDialog.getOpenFileName(None,'Select Image','',"Image Files (*.png *.jpg *jpeg *.bmp)")
        print(self.file_name)
        if self.file_name:
            pixmap = QtGui.QPixmap(self.file_name) # Setup pixmap with the provided image
            pixmap = pixmap.scaled(self.loadedImg_lab.width(), self.loadedImg_lab.height(), QtCore.Qt.KeepAspectRatio)
            self.loadedImg_lab.setPixmap(pixmap)
            self.loadedImg_lab.setAlignment(QtCore.Qt.AlignCenter) # Align the label to center
            
    def get_image(self,DrawingFrame):
        pixmap = DrawingFrame.grab()
        pixmap.save("image", "jpg")
        print(pixmap.save("image", "jpg"))
        image = self.preprocessing_drowing("image")
        return image
    

        
    def cnn_predict(self):
        print('cnn predict ')

        
        print(self.file_name)

        predict_vec=self.cnn_model.predict(self.preprocessing(self.file_name))
        self.predict_value=self.mappings[np.argmax(predict_vec)]
        value=self.predict_Svalue+self.predict_value
        self.predict_label.setText(value)
        print(self.predict_value)
        #return predict_value
       # image = self.get_image(self.DrawingFrame)
        
        '''predict_vec=self.cnn_model.predict(self.get_image(self.DrawingFrame))
        self.predict_value=self.mappings[np.argmax(predict_vec)]
        value=self.predict_Svalue+self.predict_value
        self.predict_label.setText(value)
        print(self.predict_value)'''
        #image=np.round(image)
        #image=image.reshape((28,28))
        #image=image.transpose()
        #image=image.reshape((1,1,28,28))
        #predi = clf.predict(np.array(image).reshape(1,-1))
        #probs = clf.predict(image)
        #prediction = probs.argmax(axis=1)
        #pred=prediction[0]
        #[pred]=[predi]
        #print(pred)
        #print(image_path + str(int(pred)) +".png")
        #self.pixmap = QtGui.QPixmap(image_path + str(int(pred)) +".png")

    def cnn_predict2(self):
                
        predict_vec=self.cnn_model.predict(self.get_image(self.DrawingFrame))
        self.predict_value=self.mappings[np.argmax(predict_vec)]
        value=self.predict_Svalue+self.predict_value
        self.predict_label.setText(value)
        print(self.predict_value)
        
        
        
    def load_char_mappings(self,mapping_path):
    #"""
    #load EMNIST character mappings. This maps a label to the correspondent byte value of the given character
   # return: the dictionary of label mappings
   # """
     mappings = []
     with open(mapping_path) as f:
         for line in f:
            (key, val) = line.split()
            temp= chr(int(val))
            mappings.append(temp)

     return mappings
 
    def preprocessing_drowing(self,img_path):
        import PIL.ImageOps
        size=32,32
        from PIL import Image
        img=Image.open(img_path)
        inverted_image = PIL.ImageOps.invert(img)
        inverted_image.thumbnail(size)

        inverted_image.save('new_name.jpg')
        
        
        img=cv2.imread('new_name.jpg',0) # RGB to gray
        img= cv2.resize(img, (28, 28))
        
        kernel = np.ones((2,2),np.uint8)
        retval, img = cv2.threshold(img, 100, 255, cv2.THRESH_BINARY) # gray to binary
        imgB=img
        img = cv2.Canny(img,2,2) # edge dectiction
        img = cv2.morphologyEx(img, cv2.MORPH_CLOSE, kernel)
        h, w = img.shape[:2]
        mask = np.zeros((h+2, w+2), np.uint8)
    # Floodfill from point (0, 0)
        cv2.floodFill(img, mask, (0,0), 255);
    # Invert floodfilled image
        im_floodfill_inv = cv2.bitwise_not(img)
    # Combine the two images to get the foreground.
        im_out = imgB | im_floodfill_inv
        #print(im_out.shape)
        #plt.imshow(im_out/255)
        #plt.show()
        im_out=im_out.reshape([1,28,28,1])
        return im_out/255
        
        
        
        
    def preprocessing(self,img_path):
        print("processing image....")
        print(img_path)

        img=cv2.imread(img_path,0) # RGB to gray
        img= cv2.resize(img, (28, 28))
        
        kernel = np.ones((2,2),np.uint8)
        retval, img = cv2.threshold(img, 100, 255, cv2.THRESH_BINARY) # gray to binary
        imgB=img
        img = cv2.Canny(img,2,2) # edge dectiction
        img = cv2.morphologyEx(img, cv2.MORPH_CLOSE, kernel)
        h, w = img.shape[:2]
        mask = np.zeros((h+2, w+2), np.uint8)
    # Floodfill from point (0, 0)
        cv2.floodFill(img, mask, (0,0), 255);
    # Invert floodfilled image
        im_floodfill_inv = cv2.bitwise_not(img)
    # Combine the two images to get the foreground.
        im_out = imgB | im_floodfill_inv
        #print(im_out.shape)
        #plt.imshow(im_out/255)
        #plt.show()
        im_out=im_out.reshape([1,28,28,1])
        return im_out/255

        
        
        
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    #app.setStyleSheet("object { border-image: url(ocr-to-word.png) 0 0 0 0 stretch stretch; }")
    MainWindow = QtWidgets.QMainWindow()
    #app.setStyle('Fusion')
    MainWindow.setStyleSheet("QMainWindow { border-image: url(ocr-to-word.png) 0 0 0 0 stretch stretch; }")
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
    

