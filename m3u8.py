import os
import urllib3
import shutil
from traceback import print_exc
from pathlib import Path
from urllib import parse
from concurrent.futures import ThreadPoolExecutor

import requests
from tqdm import tqdm
from faker import Faker
from retry import retry
from ffmpy import FFmpeg

urllib3.disable_warnings()


class Downloader():
    def __init__(self, url, dst=None, filename=None):
        """
        :param url: m3u8 文件下载地址
        :param dst: 指定下载视频文件输出目录，不指定则为当前目录
        :param filename: 下载视频文件名
        """
        self.url = url
        self.dst = dst or os.getcwd()
        self.filename = filename or 'output.mp4'

        self.session = requests.Session()
        self.session.headers.update({'User-Agent': Faker().user_agent()})
        self.session.verify = False

        self.proxies = {}

    def parse_m3u8_url(self):
        """
        获取m3u8文件 并解析文件获取ts视频文件地址
        :return: ts文件下载地址
        """
        text = self.session.get(self.url).text

        return [parse.urljoin(self.url, row.strip()) for row in text.split('\n') if not row.startswith('#')]

    def check_save_folder(self):
        """
        检测视频输出目录是否正确，并创建temp目录用于临时存储ts文件
        :return: ts文件保存目录 (Path对象)
        """
        dst_folder = Path(self.dst)
        if not dst_folder.is_dir():
            raise Exception(f'{self.dst} is not a dir!')

        # 如果temp目录不存在便创建
        save_folder = dst_folder / 'temp'
        if not save_folder.exists():
            save_folder.mkdir()

        return save_folder

    def download(self, ts_url, save_folder):
        """
        根据ts文件地址下载视频文件并保存到指定目录
        * 当前处理递归下载！！！
        :param ts_url: ts文件下载地址
        :param save_folder: ts文件保存目录
        :return: ts文件保存路径
        """
        try:
            # ts_url 可能有参数
            filename = parse.urlparse(ts_url).path.split('/')[-1]

            filepath = save_folder / filename
            if filepath.exists():
                # 文件已存在 跳过
                return str(filepath)

            res = self.session.get(ts_url)

            if not (200 <= res.status_code < 400):
                print(f'{ts_url}, status_code: {res.status_code}')
                raise Exception('Bad request!')

            with filepath.open('wb') as fp:
                fp.write(res.content)

            print(ts_url)
        except Exception as e:
            print_exc()
            return self.download(ts_url, save_folder)

        return str(filepath)

    def merge(self, ts_file_paths):
        """
        ts文件合成
        :return:
        """
        join_path = '|'.join(ts_file_paths)
        command = f'ffmpeg -i "concat:{join_path}" -acodec copy -vcodec copy -absf aac_adtstoasc {self.filename}'
        print(len(command))
        print(command)
        os.system(command)

    def run(self, max_workers=None):
        """
        任务主函数
        :param max_workers: 线程池最大线程数
        """
        # 获取ts文件地址列表
        ts_urls = self.parse_m3u8_url()
        print(f'ts file nums: {len(ts_urls)}')

        # 获取ts文件保存目录
        save_folder = self.check_save_folder()

        # 创建线程池，将ts文件下载任务推入线程池
        pool = ThreadPoolExecutor(max_workers=max_workers)
        ret = [pool.submit(self.download, url, save_folder) for url in ts_urls]
        ts_file_paths = ['temp/' + task.result().split('/')[-1] for task in ret]

        # 合并ts文件
        self.merge(ts_file_paths)

        # 删除临时目录以及ts文件
        # shutil.rmtree(save_folder)


if __name__ == '__main__':
    pass
    # https://www.cnblogs.com/faberbeta/p/ffmpeg001.html
    # 直接从网络m3u8文件下载视频  不确定能否多线程
    # ffmpeg -i https://ip182.com/media=hlsA/ssd2/21/8/184547828.m3u8 -acodec copy -vcodec copy output.mp4

    # 命令行合并ts文件 亲测OK
    # ffmpeg -i "concat:file001.ts|file002.ts|file003.ts|file004.ts......n.ts" -acodec copy -vcodec copy out.mp4

    # url = 'https://youku.cdn4-okzy.com/20191217/3440_29f38847/1000k/hls/index.m3u8'
    Downloader(url, filename='out2.mp4').run(max_workers=3)
