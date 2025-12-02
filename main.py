# main.py
import sys
from SerialInputDialog import SerialInputDialog
from PyQt6.QtWidgets import QApplication

app = QApplication(sys.argv)

dlg = SerialInputDialog()  
result = dlg.exec_and_get()

if result == 0:
    print(f'Returned value: {result}')
else:
    print(f'Serial Number: {result}')

sys.exit(0)
