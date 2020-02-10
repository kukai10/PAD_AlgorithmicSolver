import sys
from PyQt5.QtWidgets import QWidget, QMessageBox, QApplication, QPushButton


class Example(QWidget):
    
    def __init__(self):
        super().__init__()
        
        self.initUI()
        
        
    def initUI(self):   
        b1 = QPushButton(self)
        b1.setText("Start Solver")
        b1.clicked.connect(self.start_looking)
        self.setGeometry(300, 300, 250, 150)        
        self.setWindowTitle('PAD test') 
        self.show()
        
        
    def closeEvent(self, event):
        
        reply = QMessageBox.question(self, 'Message',
            "Are you sure to quit?", QMessageBox.Yes | 
            QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()        

    def start_looking(self):
        ask = QMessageBox.question(self, "Message", "is PAD opened?", QMessageBox.Yes|QMessageBox.No, QMessageBox.No)
        if ask == QMessageBox.Yes:
            print("button pressed")
        else:
            print("not accept")

        
if __name__ == '__main__':
    
    app = QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())