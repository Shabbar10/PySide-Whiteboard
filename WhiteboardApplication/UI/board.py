# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'board.ui'
##
## Created by: Qt User Interface Compiler version 6.6.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QAction, QBrush, QColor, QConicalGradient,
    QCursor, QFont, QFontDatabase, QGradient,
    QIcon, QImage, QKeySequence, QLinearGradient,
    QPainter, QPalette, QPixmap, QRadialGradient,
    QTransform)
from PySide6.QtWidgets import (QApplication, QDial, QGraphicsView, QGridLayout,
    QMainWindow, QMenu, QMenuBar, QPushButton,
    QSizePolicy, QSpacerItem, QStatusBar, QWidget)
import Icons_rc

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1172, 656)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        self.actionHello = QAction(MainWindow)
        self.actionHello.setObjectName(u"actionHello")
        self.actionSomething = QAction(MainWindow)
        self.actionSomething.setObjectName(u"actionSomething")
        self.actionSomething_again = QAction(MainWindow)
        self.actionSomething_again.setObjectName(u"actionSomething_again")
        self.actionNew = QAction(MainWindow)
        self.actionNew.setObjectName(u"actionNew")
        self.actionNew_2 = QAction(MainWindow)
        self.actionNew_2.setObjectName(u"actionNew_2")
        self.actionOpen = QAction(MainWindow)
        self.actionOpen.setObjectName(u"actionOpen")
        self.actionSave = QAction(MainWindow)
        self.actionSave.setObjectName(u"actionSave")
        self.actionOpen_2 = QAction(MainWindow)
        self.actionOpen_2.setObjectName(u"actionOpen_2")
        self.actionSave_2 = QAction(MainWindow)
        self.actionSave_2.setObjectName(u"actionSave_2")
        self.actionSave_As = QAction(MainWindow)
        self.actionSave_As.setObjectName(u"actionSave_As")
        self.actionClear = QAction(MainWindow)
        self.actionClear.setObjectName(u"actionClear")
        self.actionCoolDude = QAction(MainWindow)
        self.actionCoolDude.setObjectName(u"actionCoolDude")
        self.actionClose = QAction(MainWindow)
        self.actionClose.setObjectName(u"actionClose")
        self.actionNew_4 = QAction(MainWindow)
        self.actionNew_4.setObjectName(u"actionNew_4")
        self.actionNew_3 = QAction(MainWindow)
        self.actionNew_3.setObjectName(u"actionNew_3")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.gridLayout = QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName(u"gridLayout")
        self.pb_Redo = QPushButton(self.centralwidget)
        self.pb_Redo.setObjectName(u"pb_Redo")
        icon = QIcon()
        icon.addFile(u":/Tools/redo.png", QSize(), QIcon.Normal, QIcon.Off)
        self.pb_Redo.setIcon(icon)
        self.pb_Redo.setCheckable(False)

        self.gridLayout.addWidget(self.pb_Redo, 10, 0, 1, 1)

        self.pb_Eraser = QPushButton(self.centralwidget)
        self.pb_Eraser.setObjectName(u"pb_Eraser")
        icon1 = QIcon()
        icon1.addFile(u":/Tools/eraser.png", QSize(), QIcon.Normal, QIcon.Off)
        self.pb_Eraser.setIcon(icon1)
        self.pb_Eraser.setCheckable(True)

        self.gridLayout.addWidget(self.pb_Eraser, 1, 0, 1, 1)

        self.pb_Color = QPushButton(self.centralwidget)
        self.pb_Color.setObjectName(u"pb_Color")
        self.pb_Color.setCheckable(False)

        self.gridLayout.addWidget(self.pb_Color, 7, 0, 1, 1)

        self.pb_Rectangle = QPushButton(self.centralwidget)
        self.pb_Rectangle.setObjectName(u"pb_Rectangle")
        icon2 = QIcon()
        icon2.addFile(u":/Tools/rect.png", QSize(), QIcon.Normal, QIcon.Off)
        self.pb_Rectangle.setIcon(icon2)
        self.pb_Rectangle.setCheckable(True)

        self.gridLayout.addWidget(self.pb_Rectangle, 3, 0, 1, 1)

        self.pb_Pen = QPushButton(self.centralwidget)
        self.pb_Pen.setObjectName(u"pb_Pen")
        icon3 = QIcon()
        icon3.addFile(u":/Tools/pen.png", QSize(), QIcon.Normal, QIcon.Off)
        self.pb_Pen.setIcon(icon3)
        self.pb_Pen.setCheckable(True)

        self.gridLayout.addWidget(self.pb_Pen, 0, 0, 1, 1)

        self.dial = QDial(self.centralwidget)
        self.dial.setObjectName(u"dial")

        self.gridLayout.addWidget(self.dial, 6, 0, 1, 1)

        self.pb_Undo = QPushButton(self.centralwidget)
        self.pb_Undo.setObjectName(u"pb_Undo")
        icon4 = QIcon()
        icon4.addFile(u":/Tools/undo.png", QSize(), QIcon.Normal, QIcon.Off)
        self.pb_Undo.setIcon(icon4)
        self.pb_Undo.setCheckable(False)

        self.gridLayout.addWidget(self.pb_Undo, 9, 0, 1, 1)

        self.gv_Canvas = QGraphicsView(self.centralwidget)
        self.gv_Canvas.setObjectName(u"gv_Canvas")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.gv_Canvas.sizePolicy().hasHeightForWidth())
        self.gv_Canvas.setSizePolicy(sizePolicy1)

        self.gridLayout.addWidget(self.gv_Canvas, 0, 1, 11, 1)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout.addItem(self.verticalSpacer, 8, 0, 1, 1)

        self.pb_Line = QPushButton(self.centralwidget)
        self.pb_Line.setObjectName(u"pb_Line")
        icon5 = QIcon()
        icon5.addFile(u":/Tools/line.png", QSize(), QIcon.Normal, QIcon.Off)
        self.pb_Line.setIcon(icon5)
        self.pb_Line.setCheckable(True)

        self.gridLayout.addWidget(self.pb_Line, 2, 0, 1, 1)

        self.verticalSpacer_2 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout.addItem(self.verticalSpacer_2, 5, 0, 1, 1)

        self.pb_Ellipse = QPushButton(self.centralwidget)
        self.pb_Ellipse.setObjectName(u"pb_Ellipse")
        icon6 = QIcon()
        icon6.addFile(u":/Tools/ellipse.png", QSize(), QIcon.Normal, QIcon.Off)
        self.pb_Ellipse.setIcon(icon6)
        self.pb_Ellipse.setCheckable(True)

        self.gridLayout.addWidget(self.pb_Ellipse, 4, 0, 1, 1)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 1172, 22))
        self.menuFile = QMenu(self.menubar)
        self.menuFile.setObjectName(u"menuFile")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.menubar.addAction(self.menuFile.menuAction())
        self.menuFile.addAction(self.actionNew_3)
        self.menuFile.addAction(self.actionOpen_2)
        self.menuFile.addAction(self.actionSave_2)
        self.menuFile.addAction(self.actionSave_As)
        self.menuFile.addAction(self.actionClear)
        self.menuFile.addAction(self.actionClose)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.actionHello.setText(QCoreApplication.translate("MainWindow", u"Hello", None))
        self.actionSomething.setText(QCoreApplication.translate("MainWindow", u"Something", None))
        self.actionSomething_again.setText(QCoreApplication.translate("MainWindow", u"Something again", None))
        self.actionNew.setText(QCoreApplication.translate("MainWindow", u"New", None))
        self.actionNew_2.setText(QCoreApplication.translate("MainWindow", u"New", None))
        self.actionOpen.setText(QCoreApplication.translate("MainWindow", u"Open", None))
        self.actionSave.setText(QCoreApplication.translate("MainWindow", u"Save", None))
        self.actionOpen_2.setText(QCoreApplication.translate("MainWindow", u"Open", None))
        self.actionSave_2.setText(QCoreApplication.translate("MainWindow", u"Save", None))
        self.actionSave_As.setText(QCoreApplication.translate("MainWindow", u"Save As", None))
        self.actionClear.setText(QCoreApplication.translate("MainWindow", u"Clear", None))
        self.actionCoolDude.setText(QCoreApplication.translate("MainWindow", u"CoolDude", None))
        self.actionClose.setText(QCoreApplication.translate("MainWindow", u"Close", None))
        self.actionNew_4.setText(QCoreApplication.translate("MainWindow", u"New", None))
        self.actionNew_3.setText(QCoreApplication.translate("MainWindow", u"New", None))
#if QT_CONFIG(tooltip)
        self.pb_Redo.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Redo</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.pb_Redo.setText("")
#if QT_CONFIG(tooltip)
        self.pb_Eraser.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Eraser</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.pb_Eraser.setText("")
        self.pb_Color.setText(QCoreApplication.translate("MainWindow", u"Color", None))
        self.pb_Rectangle.setText("")
#if QT_CONFIG(tooltip)
        self.pb_Pen.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Pen</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.pb_Pen.setText("")
#if QT_CONFIG(tooltip)
        self.pb_Undo.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Undo</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(whatsthis)
        self.pb_Undo.setWhatsThis(QCoreApplication.translate("MainWindow", u"<html><head/><body><p><br/></p></body></html>", None))
#endif // QT_CONFIG(whatsthis)
        self.pb_Undo.setText("")
        self.pb_Line.setText("")
        self.pb_Ellipse.setText("")
        self.menuFile.setTitle(QCoreApplication.translate("MainWindow", u"File", None))
    # retranslateUi

