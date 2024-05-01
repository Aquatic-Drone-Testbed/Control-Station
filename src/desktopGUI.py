import sys

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QLineEdit, QMessageBox, QSplitter, QWidget, QLabel, QTableWidget, QTableWidgetItem, QHeaderView, QHBoxLayout, QFormLayout, QFileDialog
from PyQt6.QtGui import QIcon, QAction

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Capstone Project")
        # self.setFixedSize(QSize(1080, 720)) # width, height
        self.setup_ui()

    def setup_ui(self):
        # Setup UI elements
        # self.setWindowIcon(QIcon('./images/')) # TODO:later
        self.setGeometry(0, 0, 1080, 720)
        self.setup_menu_bar()
        self.setup_splitter_section()

    def setup_menu_bar(self):
        menu_bar = self.menuBar()
        # just showing how to add feature to menu bar
        # file_menu = menu_bar.addMenu("&File")
        # open_clicked = QAction("&Open", self)
        # open_clicked.triggered.connect(self.open_clicked)
        # open_clicked.setShortcut('Ctrl+O')

        # download_clicked = QAction("&Download CSV", self)
        # download_clicked.triggered.connect(self.download_clicked)
        # add_new_row = QAction("&New Row", self)
        # file_menu.addAction(open_clicked)
        # file_menu.addAction(download_clicked)
        # file_menu.addAction(add_new_row)

        setting_menu = menu_bar.addMenu("&Setting")
        more_setting = QAction("More Setting coming soon", self)
        more_setting.triggered.connect(self.more_setting_clicked)
        about_action = QAction("About", self)
        about_action.triggered.connect(self.about_clicked)
        setting_menu.addAction(more_setting)
        setting_menu.addAction(about_action)

    def setup_splitter_section(self):
        splitter = QSplitter(Qt.Orientation.Horizontal, self)
        self.setCentralWidget(splitter)
        
        # initial right widget
        self.table_widget = QTableWidget(splitter)        

        # initial left widget
        self.left_widget = QWidget(splitter)
        self.left_layout = QFormLayout(self.left_widget)
    
        splitter.addWidget(self.left_widget)
        splitter.addWidget(self.table_widget)
        
        # set initial size for left and right widget
        splitter.setSizes([200, 800])

   
    def open_clicked(self):
        print("Open clicked")

    def more_setting_clicked(self):
        print("More Setting clicked")

    def about_clicked(self):
        print("About clicked")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())