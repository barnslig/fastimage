#!/usr/bin/env python2
import PIL.Image
import PIL.ImageOps
import cStringIO
import os
import urlparse

class ImageResizer(object):
	method = PIL.Image.ANTIALIAS
	default_size = (500, 380)
	max_size = (600, 600)
	quality = 80
	root = 'images/'

	def __init__(self, **kwargs):
		self.__dict__.update(kwargs)

	def resize_image(self, path, size):
		orig = PIL.Image.open(path)
		thumb = PIL.ImageOps.fit(orig, size, self.method)
		out = cStringIO.StringIO()
		thumb.save(out, 'JPEG', quality=self.quality, optimize=True, progressive=True)
		dest = out.getvalue()
		out.close()
		return dest

	def __call__(self, environ, start_response):
		q = urlparse.parse_qs(environ['QUERY_STRING'])
		path = os.path.join(self.root, environ['PATH_INFO'][1:])
		size = self.default_size

		if os.path.isfile(path):
			if 'w' in q and 'h' in q:
				w = int(q['w'][0])
				h = int(q['h'][0])
				if w <= self.max_size[0] and h <= self.max_size[1]:
					size = (w, h)

			status = '200 Here you go'
			data = self.resize_image(path, size)
			response_headers = [
				('Content-Type', 'image/jpeg'),
				('Content-Length', str(len(data)))
			]
		else:
			status = '404 Not found'
			data = 'No such file or directory'
			response_headers = [
				('Content-Type', 'text/plain'),
				('Content-Length', str(len(data)))
			]

		start_response(status, response_headers)
		return iter([data])

app = ImageResizer()