import urllib

import time

import numpy
from bs4 import BeautifulSoup
from urllib.parse import urlparse


class MatrixTools():
    def __init__(self, init_site, size):
        self.d = 0.85
        self.size = size
        self.matrix = numpy.array([])
        self.list_links = [init_site]
        self.links_and_size = []

    def makeMatrix(self):
        print("Собираем список ссылок...")
        start_time = time.time()
        for l in self.list_links:
            if len(self.list_links) == self.size:
                break

            list_link_cur = self.getListLinks(l)
            if len(self.list_links) + len(list_link_cur) > self.size:
                k = self.size - len(list_link_cur)
                list_link_cur = list_link_cur[0:k]

            for link in list_link_cur:
                link_href = str(link.get('href'))
                self.setLinkInList(link_href, l)
        print("Ok!", time.time() - start_time)

        print("Создаем матрицу смежности...")
        start_time = time.time()
        list_matrix = []
        download = -1
        for l in self.list_links:

            list_row = []
            links = self.purifyListSite(l, self.getListLinks(l))
            size = len(links)
            self.links_and_size.append([l, size])
            for l1 in self.list_links:
                f = False
                if l != l1:

                    for l2 in links:

                        if l2 == l1:
                            f = True
                        else:
                            f = f or False

                if f:
                    list_row.append(1)
                else:
                    list_row.append(0)

            list_matrix.append(list_row)
            try:
                download_now = int(round((self.list_links.index(l) / (len(self.list_links) - 1)) * 100))
            except ZeroDivisionError:
                pass
            if download != download_now:
                print("Загрузка", str(download_now) + "%")
                download = download_now

        self.matrix = numpy.asarray(list_matrix)
        print("Ok!", time.time() - start_time)

        print("Записываем список ссылок в файл...")
        start_time = time.time()
        f = open("lists.txt", "w")
        for l in self.links_and_size:
            f.write(l[0] + "    " + str(l[1]) + " \r")
        f.close()
        print("Ok!", time.time() - start_time)

        print("Записываем матрицу в файл...")
        start_time = time.time()
        f = open("matrix.txt", "w")
        for row in self.matrix:
            for num in row:
                f.write(str(num) + " ")
            f.write("\r")
        f.close()
        print("Ok!", time.time() - start_time)

    def checkLink(self, string):
        return string.startswith('/') or string.startswith('http') or string.startswith('www')

    def setLinkInList(self, link_href, init_site):
        init_site.encode('utf-8')
        link_href.encode('utf-8')
        f = True
        if len(self.list_links) < self.size:
            if self.checkLink(link_href):
                init_site = '{uri.scheme}://{uri.netloc}/'.format(uri=urlparse(init_site))
                if link_href.startswith("//"):
                    f = False

                if link_href.startswith("https"):
                    link_href = link_href.replace("https", "http")

                if link_href.startswith("http://www"):
                    link_href = link_href.replace("http://www.", "http://")

                if init_site.endswith("/"):
                    init_site = init_site[0:-1]

                if link_href.startswith("/"):
                    link_href = init_site + link_href

                if not link_href.endswith("/"):
                    link_href += "/"

                if link_href not in self.list_links and f:
                    self.list_links.append(link_href)

    def getListLinks(self, url):
        req = urllib.request.Request(
            url[:-1],
            data=None,
            headers={
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, '
                              'like Gecko) Chrome/35.0.1916.47 Safari/537.36 '
            }
        )
        soup = BeautifulSoup("", "html.parser")
        try:
            f = urllib.request.urlopen(req)
            soup = BeautifulSoup(f.read(), "html.parser")
        except (urllib.error.HTTPError, urllib.error.URLError, UnicodeEncodeError):
            return []
        return soup.findAll('a')

    def purifyListSite(self, init_site, list_links):
        li = []
        init_site = '{uri.scheme}://{uri.netloc}/'.format(uri=urlparse(init_site))
        if init_site.endswith("/"):
            init_site = init_site[0:-1]
        for l in list_links:
            l = l.get('href')
            if l is None:
                pass
            else:
                if self.checkLink(l):

                    if l.startswith("https"):
                        l = l.replace("https", "http")

                    if l.startswith("http://www"):
                        l = l.replace("http://www.", "http://")

                    if l.startswith("/"):
                        l = init_site + l

                    if not l.endswith("/"):
                        l += "/"
                    li.append(l)

        return li

    def countPagerank(self):
        print("Считываем матрицу из файла...")
        start_time = time.time()
        f = open("matrix.txt", "r")
        matrix = []
        for line in f:
            list_number_row_str = line.split(" ")
            list_number_row = []
            for l in list_number_row_str:
                try:
                    list_number_row.append(int(l))
                except ValueError:
                    pass
            matrix.append(list_number_row)
        f.close()
        matrix = numpy.asarray(matrix)
        print("Ok!", time.time() - start_time)

        print("Считываем список ссылок из файла...")
        start_time = time.time()
        f = open("lists.txt", "r")
        links_and_amount = []
        for line in f:
            line_elements = line.split("    ")
            l = [line_elements[0], int(line_elements[1])]
            links_and_amount.append(l)
        print("Ok!", time.time() - start_time)

        print("Формируем начальный список...")
        start_time = time.time()
        pr_list = []
        for l in links_and_amount:
            pr_list.append(1 / len(links_and_amount))
        print("Ok!", time.time() - start_time)

        print("Собираем входящие ссылки...")
        start_time = time.time()
        list_m = []
        for i in range(0, len(pr_list)):
            row = matrix[:, i]
            row_m = []
            for r in range(0, len(row)):
                if row[r] == 0:
                    pass
                elif row[r] == 1:
                    row_m.append(r)
            list_m.append(row_m)
        print("Ok!", time.time() - start_time)

        print("Считаем PageRank...")
        start_time = time.time()
        for j in range(0, 30):
            for i in range(0, len(pr_list)):
                s = 0
                for l_m in list_m[i]:
                    s += (pr_list[l_m] / links_and_amount[l_m][1])
                pr_list[i] = (1 - self.d) / len(pr_list) + self.d * s
        print("Ok!", time.time() - start_time)

        print("Создаем соответствия PageRank и сайтов...")
        start_time = time.time()
        pr_links = []
        for l in range(0, len(links_and_amount)):
            pr_round = round(pr_list[l] * 100, 4)
            pr_links.append([links_and_amount[l], pr_round])
        print("Ok!", time.time() - start_time)

        print("Сортируем список")
        start_time = time.time()
        pr_links = sorted(pr_links, key=sort_col, reverse=True)
        print("Ok!", time.time() - start_time)

        print("Записываем PageRank сайтов в файл...")
        start_time = time.time()
        f = open("pagerank.txt", "w")
        for l in pr_links:
            f.write(str(l[1]) + " " + l[0][0] + " \r")
        f.close()
        print("Ok!", time.time() - start_time)

        print("Done!")


def sort_col(i):
    return i[1]
