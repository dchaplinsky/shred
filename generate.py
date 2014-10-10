# import click
import os
from math import sqrt, ceil
from random import choice, randint
import exifread
import cv2
import glob
import shutil


class Img(object):
    def __init__(self, fname, default_dpi):
        self.fname = fname
        self.img = cv2.imread(fname)
        self.dpi = self.determine_dpi(default_dpi)

    def determine_dpi(self, default_dpi):
        def parse_resolution(val):
            x = map(int, map(str.strip, str(val).split("/")))
            if len(x) == 1:
                return x[0]
            elif len(x) == 2:
                return int(round(float(x[0]) / x[1]))
            else:
                raise ValueError

        with open(self.fname, "rb") as f:
            tags = exifread.process_file(f)

        try:
            if "Image XResolution" in tags and "Image YResolution" in tags:
                return (parse_resolution(tags["Image XResolution"]),
                        parse_resolution(tags["Image YResolution"]))
        except ValueError:
            pass

        return (default_dpi, default_dpi)

    def __repr__(self):
        return u"<%s>: %s/%s DPI" % (self.fname, self.dpi[0], self.dpi[1])


class Sheet(Img):
    def cut_one_shred(self, shred, offset=None, angle=0):
        ratio = self.dpi[0] * 1.0 / shred.dpi[0]
        mask = cv2.resize(
            shred.img,
            (int(shred.img.shape[1] * ratio),
             int(shred.img.shape[0] * ratio)),
            interpolation=cv2.INTER_AREA)

        s_w, s_h = mask.shape[:2]
        s_diag = int(ceil(sqrt(s_w ** 2 + s_h ** 2)))
        w, h = self.img.shape[:2]
        assert(w > s_diag)
        assert(h > s_diag)

        if offset is None:
            offset = [randint(0, w - s_diag), randint(0, h - s_diag)]

        img_crp = self.img[offset[0]:offset[0] + s_diag,
                           offset[1]:offset[1] + s_diag]

        M = cv2.getRotationMatrix2D((s_diag / 2,
                                     s_diag / 2), angle, 1)

        img_crp = cv2.warpAffine(img_crp, M, (s_diag, s_diag))

        dx = int((s_diag - s_w) / 2.)
        dy = int((s_diag - s_h) / 2.)
        img_crp = img_crp[dx:dx + s_w,
                          dy:dy + s_h]

        img_crp = cv2.bitwise_and(img_crp, img_crp, mask=mask[:, :, 0])
        img_crp = cv2.cvtColor(img_crp, cv2.cv.CV_BGR2BGRA)
        img_crp[:, :, 3] = mask[:, :, 0]

        return img_crp

    def __repr__(self):
        return u"<Sheet %s>: %s/%s DPI" % (
            self.fname, self.dpi[0], self.dpi[1])


class Shred(Img):
    def __repr__(self):
        return u"<Shred %s>: %s/%s DPI" % (
            self.fname, self.dpi[0], self.dpi[1])


def load_sheets(default_dpi=600):
    return [Sheet(fname, default_dpi) for fname in glob.glob("src/sheets/*")]


def load_shreds(default_dpi=300):
    return [Shred(fname, default_dpi) for fname in glob.glob("src/shreds/*")]


if __name__ == '__main__':
    sheets = load_sheets()
    shreds = load_shreds()

    devi = 90
    repeat = 5
    out_dir = "out"

    if os.path.exists(out_dir):
        shutil.rmtree(out_dir)

    for x in xrange(-devi, devi + 1):
        dir_for_angle = os.path.join(out_dir, str(x))
        os.makedirs(dir_for_angle)

        for i in xrange(repeat):
            sheet = choice(sheets)
            shred = choice(shreds)

            test_shred = sheet.cut_one_shred(shred, angle=x)

            print(x, i)
            cv2.imwrite(os.path.join(dir_for_angle, "%s.png" % i), test_shred)
