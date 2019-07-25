import requests

url = "https://pic.ibaotu.com/00/51/34/88a888piCbRB.mp4"
# url = 'https://www.cnblogs.com/duanxz/p/5126637.html'
#
# res = requests.head(url)
# print(res.status_code)
# for k, v in res.headers.items():
#     print(k, v)

# headers = {'Range': 'bytes=200-299'}
# res = requests.get(url, headers=headers)
# print(res.status_code)
# for k, v in res.headers.items():
#     print(k, v)


# TODO ETag

size = 46167332
chunk_size = 1024 * 100

lst = list(range(0, size, chunk_size))
end_range = [lst[-1], size]
_range = list(zip(lst[:-1], [i - 1 for i in lst[1:]]))
_range.append(end_range)

print(_range)

import os

print(os.path.getsize('测试视频.mp4'))
print(os.path.getsize('download.mp4'))

