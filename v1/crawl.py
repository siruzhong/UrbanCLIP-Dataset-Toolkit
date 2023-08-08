import os

import requests
from PIL import Image


def check_if_exist(x, y, z):
    try:
        Image.open('./cdZoomImg/cd_{}_{}.png'.format(x, y))
        return True
    except:
        print('downloading...{}_{}'.format(x, y))
        return False


def getTileByXYZ():  # 根据x，y，z参数获取瓦片
    z = 19
    xidx = [101112, 101325]
    yidx = [37603, 37803]

    for y in range(yidx[0], yidx[1] + 1):
        for x in range(xidx[0], xidx[1] + 1):
            if not check_if_exist(x, y, z):
                url = "https://maponline3.bdimg.com/starpic/?qt=satepc&u=x={x};y={y};z={z};v=009;type=sate&fm=46&app=webearth2&v=009&udt=20140601".format(
                    x=x, y=y, z=z)
                savePngByXYZ(url, x, y, z)
        print(y)


def savePngByXYZ(url, x, y, z=19):  # 保存图片
    r = requests.get(url)
    os.makedirs('./cdZoomImg', exist_ok=True)
    sname = "./cdZoomImg/cd_{x}_{y}.png".format(x=x, y=y)  # 这里建议保存编码是y_x 这样下面合并图片也要适当改代码
    with open(sname, 'ab') as pngf:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:
                pngf.write(chunk)
                pngf.flush()


if __name__ == '__main__':
    getTileByXYZ()
