from io import BytesIO

from skimage import io
from skimage.transform import rescale

from vdv.MediaResolver import MediaResolver

import uuid

MAX_IMAGE_SIDE = 1024
MIN_IMAGE_SIDE = 256
MAX_ASPECT_RATIO = 1.34

class ImageResolver(MediaResolver):
    def __init__(self, data):
        super().__init__(data)
        self.type = 'image'

    def Resolve(self):
        try:
            img = io.imread(BytesIO(self.data))
        except Exception as e:
            print(e)
            return None

        w, h = img.shape[1], img.shape[0]

        aspect = max(w, h) / min(w, h)
        if aspect > MAX_ASPECT_RATIO:
            new_t = int(min(w, h) * MAX_ASPECT_RATIO)
            dt = int((max(w, h) - new_t) / 2)
            if min(w, h) == h:
                img = img[:, dt:(dt + new_t)]
            else:
                img = img[dt:(dt + new_t), :]

            w, h = img.shape[1], img.shape[0]


        if max(w, h) > MAX_IMAGE_SIDE:
            ds = MAX_IMAGE_SIDE / max(w, h)
            img = rescale(image=img, scale=ds)

        if min(w, h) < MIN_IMAGE_SIDE:
            return None

        self.url = './images/%s.jpg' % uuid.uuid4().hex
        io.imsave(self.url, img)
        return self.url



