import urllib.request

import time
from bs4 import BeautifulSoup

from Task1_2.MatrixTools import MatrixTools

if __name__ == '__main__':
    start_time = time.time()
    tools = MatrixTools("http://en.wikipedia.org/", 100)
    tools.makeMatrix()
    tools.countPagerank()
    print(time.time()-start_time, "sec")
