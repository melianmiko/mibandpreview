#!/bin/python3
import os, json, math
from PIL import Image, ImageDraw

def new():
	return PreviewDrawer()

def radsin(angle):
	return math.sin(math.radians(angle))

def radcos(angle):
	return math.cos(math.radians(angle))

class PreviewDrawer:
	def __init__(self):
		self.canvas = Image.new("RGBA", (120, 240))

	def save(self, fn):
		self.canvas.save(fn)

	def getCanvas(self):
		return self.canvas

	def getRGBCanvas(self):
		c = Image.new("RGB", (120, 240))
		c.paste(self.canvas, (0,0), self.canvas)
		return c

	def calculateXYPos(self, data, size):
		x1 = data["TopLeftX"]
		x2 = data["BottomRightX"]
		y1 = data["TopLeftY"]
		y2 = data["BottomRightY"]

		pcw = x2-x1
		pch = y2-y1
		rp = x2-size[0] if x2-size[0] >= x1 else x1
		bp = y2-size[1] if y2-size[1] >= y1 else y1
		cx = x1+(x2-x1-size[0])/2 if x2 != 0 and x2-x1-size[0] > x1 else x1
		cy = y1+(y2-y1-size[1])/2 if y2 != 0 and y2-y1-size[1] > y1 else y1

		align = data["Alignment"]
		if align == "TopLeft" or align == "Top" or align == "Left":
			return [x1, y1]
		elif align == "BottomRight":
			return [rp, bp]
		elif align == "BottomLeft" or align == "Bottom":
			return [x1, bp]
		elif align == "TopRight" or align == "Right":
			return [rp, y1]
		elif align == "TopCenter" or align == "HCenter":
			return [ cx, y1 ]
		elif align == "BottomCenter":
			return [ cx, bp ]
		elif align == "CenterLeft" or align == "VCenter":
			return [ x1, cy ]
		elif align == "CenterRight":
			return [ rp, cy ]
		elif align == "Center":
			return [ cx, cy ]
		else:
			print("Align mode unsupported!!!!!")
			return [x1, y1]

	def buildHybridLine(self, data, a, dotIndex=-1, posixIndex=-1):
		isFloat = len(str(a).split(".")) > 1
		imgs = []
		if isFloat:
			a0 = int(str(a).split(".")[0])
			a1 = int(str(a).split(".")[1])
			imgs.append(self.buildNumberImg(data, a0))
			if dotIndex > 0:
				imgs.append(self.images[dotIndex])
			imgs.append(self.buildNumberImg(data, a1))
		else:
			imgs.append(self.buildNumberImg(data, a))

		imgs.append(self.images[posixIndex])
		spacing = data["Spacing"]

		fullWidth = 0
		fullHeight = 0
		for i in imgs:
			fullWidth += i.size[0]+spacing
			fullHeight = max(fullHeight, i.size[1])
		out = Image.new("RGBA", (fullWidth, fullHeight))
		x = 0
		for i in imgs:
			out.paste(i, (x, 0), i)
			x += i.size[0]+spacing
		return out

	def buildDateLine(self, data, dotIndex=-1, twoDMonth=False, twoDDay=False, date=(1,1)):
		imgs = []
		if twoDMonth:
			imgs.append(self.buildNumberImg(data, date[0], digits=2))
		else:
			imgs.append(self.buildNumberImg(data, date[0]))

		imgs.append(self.images[dotIndex])

		if twoDDay:
			imgs.append(self.buildNumberImg(data, date[1], digits=2))
		else:
			imgs.append(self.buildNumberImg(data, date[1]))

		spacing = data["Spacing"]

		fullWidth = 0
		fullHeight = 0
		for i in imgs:
			fullWidth += i.size[0]+spacing
			fullHeight = max(fullHeight, i.size[1])
		out = Image.new("RGBA", (fullWidth, fullHeight))
		x = 0
		for i in imgs:
			out.paste(i, (x, 0), i)
			x += i.size[0]+spacing
		return out

	def getImgSet(self, obj):
		out = []
		for a in range(obj["ImagesCount"]):
			out.append(self.images[obj["ImageIndex"]+a])
		return out

	def buildNumberImg(self, data, a, digits=0):
		startIndex = data["ImageIndex"]
		numimgs = self.getImgSet(data)
		spacing = data["Spacing"]
		spn = []

		if a == 0:
			spn.append(0)
		else:
			while a > 0:
				spn.append(a % 10)
				a = a // 10

		while len(spn) < digits:
			spn.append(0)

		spn = spn[::-1]
		w = -spacing
		h = 0
		for n in spn:
			w += numimgs[n].size[0]+spacing
			h = max(h, numimgs[n].size[1])
		if w < 0: w = 0
		if h < 0: h = 0

		img = Image.new("RGBA", (w, h))
		x = 0
		for n in spn:
			img.paste(numimgs[n],(x, 0), numimgs[n])
			x += numimgs[n].size[0]+spacing
		return img

	def putImages(self, imgArray):
		self.images = imgArray

	def addToCanvas(self, img, xy):
		x, y = xy
		sx = sy = 0
		if x < 0:
			sx = -x
			x = 0
		if y < 0:
			sy = -y
			y = 0
		self.canvas.alpha_composite(img, (x, y), (sx, sy))

	def drawObject(self, obj, value = 0):
		imgIndex = obj["ImageIndex"]
		imgId = imgIndex+value
		img = self.images[imgId]
		self.addToCanvas(img, ( obj["X"], obj["Y"] ) )

	def drawRectNumberObject(self, obj, value = 0, digits = 1):
		img = self.buildNumberImg(obj, value, digits=digits)
		x, y = self.calculateXYPos(obj, img.size)
		self.addToCanvas(img, ( int(x), int(y) ) )

	def drawAnalogDial(self, obj, angle = 0):
		cx = obj["Center"]["X"]
		cy = obj["Center"]["Y"]
		color = obj["Color"].replace("0x", "#")
		border = obj["OnlyBorder"]
		shape = obj["Shape"]
		draw = ImageDraw.Draw(self.canvas)
		angle = (angle-360 if angle > 360 else angle)

		points = []
		for dot in shape:
			angle2 = angle+90

			x = cx+(dot["X"]*radsin(angle))+(dot["Y"]*radsin(angle+90))
			y = cy-(dot["X"]*radcos(angle))-(dot["Y"]*radcos(angle+90))

			points.append((x,y))

		if border: draw.polygon(points, outline=color)
		else: draw.polygon(points, outline=color, fill=color)
