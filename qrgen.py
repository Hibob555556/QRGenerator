import pyqrcode
import png
from pyqrcode import QRCode

link = input("Please Input URL: ")
url = pyqrcode.create(link)
url.png('qr.png', scale = 15)
