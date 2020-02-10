import sys
from PyQt5.QtWidgets import (QWidget, QToolTip, QPushButton, QApplication,  QMessageBox)
from PyQt5.QtGui import QFont    

class Example(QWidget):
    
    def __init__(self):
        super().__init__()
        self.initUI()
    
    def initUI(self):
        #####################Buttons #################################
        QToolTip.setFont(QFont('SansSerif', 10))
        self.setToolTip("This is a <b>QWidget</b> widget")
        btn = QPushButton('Button', self)
        btn.setToolTip('This is a <b>QPushButton</b> widget')
        btn.resize(btn.sizeHint())
        btn.move(50, 50)       
        #self.setWindowTitle('Tooltips')    
        #######################Quit buttons ############################       
        
        qbtn = QPushButton('Quit', self)
        qbtn.clicked.connect(QApplication.instance().quit)
        qbtn.resize(qbtn.sizeHint())
        qbtn.move(150,50)       
        #self.setWindowTitle('Quit button')    
        ################################################################
        self.setGeometry(300, 300, 250, 200)        
        self.setWindowTitle('Message box')    
        self.show()
           
    def closeEvent(self, event):
        reply = QMessageBox.question(self, 'Message', "Are you sure to quit?",
         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes: event.accept()
        else:event.ignore()        
        
        
if __name__ == '__main__':
    
    app = QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())