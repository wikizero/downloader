import requests
import os


class Downloader():
    def __init__(self, url):
        self.url = url
        self.chunk_size = 1024 * 5000  # 设置为100KB

        self.filename = 'download.mp4'
        self.file_size = 0
        self.file_type = None

    def check_url(self):
        """
        判断url是否支持断点续传功能
        :return:
        """
        res = requests.head(self.url)
        if res.status_code != 200:
            raise Exception('...')
        headers = res.headers
        self.file_size = int(headers.get('Content-Length'))
        self.file_type = headers.get('Content-Type')
        print(self.file_size, self.file_type)
        return headers.get('Accept-Ranges') == 'bytes'

    def get_range(self):
        lst = list(range(0, self.file_size, self.chunk_size))
        end_range = [lst[-1], self.file_size]
        _range = list(zip(lst[:-1], [i - 1 for i in lst[1:]]))  # [i - 1 for i in lst[1:]]
        _range.append(end_range)
        print(_range)
        return _range

    def download(self):
        # res = requests.get(self.url)
        self.check_url()
        # count = 0
        tempf = open(self.filename, 'w')  # 清空并生成文件
        with open(self.filename, 'rb+') as f:
            fileno = f.fileno()
            dup = os.dup(fileno)
            fd = os.fdopen(dup, 'rb+', -1)
            for row in self.get_range():
                header = {"Range": f"bytes={row[0]}-{row[1]}"}
                res = requests.get(self.url, headers=header)
                print(res.headers['Content-Length'], res.headers['Content-Range'])
                fd.seek(row[0])
                print(row[0])
                fd.write(res.content)
            # print(res.status_code)
            # for k, v in res.headers.items():
            #     print(k, ':', v)
            # print('-' * 100)
            # count += 1
            # if count > 5:
            #     break


if __name__ == '__main__':
    url = "https://pic.ibaotu.com/00/51/34/88a888piCbRB.mp4"
    # url = 'http://192.168.10.7/a.jpg'
    d = Downloader(url)
    # print(d.check_url())
    d.download()
    # TODO du -h
