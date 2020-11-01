import sys, os, json
sys.path.append(os.path.dirname(__file__))

import PreviewDrawer
from PIL import Image

def from_path(path, fixmissing=False):
	l = Loader_MiBand4()
	l.loadFromDir(path ,fixmissing=fixmissing)
	return l

class Loader_MiBand4:
	def __init__(self):
		self.data = {}

	def setSettings(self, config):
		self.data = config

	def loadFromDir(self, path, fixmissing=False):
		self.images = {}
		self.config = {}

		placeholder = Image.new("RGBA", (1,1))

		for f in os.listdir(path):
			if os.path.splitext(path+"/"+f)[1] == ".json":
				with open(path+"/"+f, "r") as jsf:
					self.config = json.load(jsf)
					break

		for a in range(9000):
			fn = path+"/"+str(a).zfill(4)+".png"
			if os.path.isfile(fn):
				img = Image.open(fn)
				img = img.convert("RGBA")
				self.images[a] = img
			elif fixmissing:
				self.images[a] = placeholder

	def getAviableProps(self):
		return ["H0", "H1", "M0", "M1", "S0", "S1", "STEPS", "STEPS_TARGET",
			"PULSE", "DISTANCE", "CALORIES", "MONTH", "DAY", "WEEKDAY_LANG",
			"WEEKDAY", "24H", "APM_CN", "APM_PM", "BATTERY", "BLUETOOTH",
			"MUTE", "LOCK", "ANIMATION_FRAME"]

	def render(self):
		pvd = PreviewDrawer.new()
		pvd.putImages(self.images)

		config = self.config
		data = self.data

		dataKeys = self.getAviableProps()
		for a in dataKeys:
			if not a in data: data[a] = 1

		# Base
		if "Background" in config: pvd.drawObject(config["Background"]["Image"])

		# Time
		if "Time" in config:
			if "Hours" in config["Time"]:
				if "Tens" in config["Time"]["Hours"]: pvd.drawObject(config["Time"]["Hours"]["Tens"], data["H0"])
				if "Ones" in config["Time"]["Hours"]: pvd.drawObject(config["Time"]["Hours"]["Ones"], data["H1"])
			if "Minutes" in config["Time"]:
				if "Tens" in config["Time"]["Minutes"]: pvd.drawObject(config["Time"]["Minutes"]["Tens"], data["M0"])
				if "Ones" in config["Time"]["Minutes"]: pvd.drawObject(config["Time"]["Minutes"]["Ones"], data["M1"])
			if "DelimiterImage" in config["Time"]: pvd.drawObject(config["Time"]["DelimiterImage"])

		# Activity
		if "Activity" in config:
			if "Steps" in config["Activity"]: pvd.drawRectNumberObject(config["Activity"]["Steps"]["Number"], data["STEPS"])
			if "Pulse" in config["Activity"]: pvd.drawRectNumberObject(config["Activity"]["Pulse"]["Number"], data["PULSE"])
			if "Distance" in config["Activity"]:
				dist = config["Activity"]["Distance"]
				img = pvd.buildHybridLine(dist["Number"], data["DISTANCE"],
					dotIndex=dist["DecimalPointImageIndex"],
					posixIndex=dist["SuffixImageIndex"])
				x, y = pvd.calculateXYPos(dist["Number"], img.size)
				pvd.addToCanvas(img, (int(x),int(y)))
			if "Calories" in self.config["Activity"]:
				kcal = self.config["Activity"]["Calories"]
				img = pvd.buildHybridLine(kcal["Number"], data["CALORIES"],
					posixIndex=kcal["SuffixImageIndex"])
				x, y = pvd.calculateXYPos(kcal["Number"], img.size)
				pvd.addToCanvas(img, (int(x),int(y)))

		# Date and weekday
		twoDMonth = False
		twoDDay = False
		if "Date" in config:
			if "MonthAndDay" in config["Date"]:
				if "TwoDigitsDay" in config["Date"]["MonthAndDay"]:
					twoDDay = config["Date"]["MonthAndDay"]["TwoDigitsDay"]
				if "TwoDigitsMonth" in config["Date"]["MonthAndDay"]:
					twoDMonth = config["Date"]["MonthAndDay"]["TwoDigitsMonth"]
				if "OneLine" in config["Date"]["MonthAndDay"]:
					dotIndex = config["Date"]["MonthAndDay"]["OneLine"]["DelimiterImageIndex"]
					date = config["Date"]["MonthAndDay"]["OneLine"]["Number"]
					img = pvd.buildDateLine(date, dotIndex, twoDMonth, twoDDay, (data["DAY"], data["MONTH"]))
					x, y = pvd.calculateXYPos(date, img.size)
					pvd.addToCanvas(img, (int(x),int(y)))
				if "Separate" in config["Date"]["MonthAndDay"]:
					if "Month" in config["Date"]["MonthAndDay"]["Separate"]:
						pvd.drawRectNumberObject(config["Date"]["MonthAndDay"]["Separate"]["Month"],
							value=data["MONTH"], digits=(2 if twoDMonth else 1))
					if "Day" in self.config["Date"]["MonthAndDay"]["Separate"]:
						pvd.drawRectNumberObject(config["Date"]["MonthAndDay"]["Separate"]["Day"],
							value=data["DAY"], digits=(2 if twoDDay else 1))
			if "WeekDay" in self.config["Date"]:
				pvd.drawObject(self.config["Date"]["WeekDay"], value=data["WEEKDAY_LANG"]*7+data["WEEKDAY"])
			if "DayAmPm" in self.config["Date"] and not data["24H"]:
				apm = config["Date"]["DayAmPm"]
				if data["APM_CN"]:
					if data["APM_PM"]: index = apm["ImageIndexPMCN"]
					else: index = apm["ImageIndexAMCN"]
				else:
					if data["APM_PM"]: index = apm["ImageIndexPMEN"]
					else: index = apm["ImageIndexAMEN"]
				pvd.addToCanvas(pvd.images[index], (apm["X"], apm["Y"]))

		# Indicators
		if "StepsProgress" in config:
			if "Linear" in config["StepsProgress"]:
				index = config["StepsProgress"]["Linear"]["StartImageIndex"]
				segments = config["StepsProgress"]["Linear"]["Segments"]
				progress = min(1, data["STEPS"] / data["STEPS_TARGET"])
				curSegment = int(len(segments) * progress)
				for i in range(curSegment):
					img = pvd.images[index+i]
					pvd.addToCanvas(img, (segments[i]["X"], segments[i]["Y"]))
		if "Heart" in config:
			if "Scale" in config["Heart"]:
				index = config["Heart"]["Scale"]["StartImageIndex"]
				segments = config["Heart"]["Scale"]["Segments"]
				i = max(0,int(min(1,(data["PULSE"]-100)/100)*len(segments)-1))
				img = pvd.images[index+i]
				pvd.addToCanvas(img, (segments[i]["X"], segments[i]["Y"]))

		if "Status" in config:
			if "DoNotDisturb" in config["Status"]:
				if "ImageIndexOn" in config["Status"]["DoNotDisturb"] and data["MUTE"]:
					pvd.addToCanvas(pvd.images[config["Status"]["DoNotDisturb"]["ImageIndexOn"]],
						(config["Status"]["DoNotDisturb"]["Coordinates"]["X"],
						config["Status"]["DoNotDisturb"]["Coordinates"]["Y"]))
				if "ImageIndexOff" in config["Status"]["DoNotDisturb"] and not data["MUTE"]:
					pvd.addToCanvas(pvd.images[config["Status"]["DoNotDisturb"]["ImageIndexOff"]],
						(config["Status"]["DoNotDisturb"]["Coordinates"]["X"],
						config["Status"]["DoNotDisturb"]["Coordinates"]["Y"]))
			if "Lock" in config["Status"]:
				if "ImageIndexOn" in config["Status"]["Lock"] and data["LOCK"]:
					pvd.addToCanvas(pvd.images[config["Status"]["Lock"]["ImageIndexOn"]],
						(config["Status"]["Lock"]["Coordinates"]["X"],
						config["Status"]["Lock"]["Coordinates"]["Y"]))
				if "ImageIndexOff" in config["Status"]["Lock"] and not data["LOCK"]:
					pvd.addToCanvas(pvd.images[config["Status"]["Lock"]["ImageIndexOff"]],
						(config["Status"]["Lock"]["Coordinates"]["X"],
						config["Status"]["Lock"]["Coordinates"]["Y"]))
			if "Bluetooth" in config["Status"]:
				if "ImageIndexOn" in config["Status"]["Bluetooth"] and data["BLUETOOTH"]:
					pvd.addToCanvas(pvd.images[config["Status"]["Bluetooth"]["ImageIndexOn"]],
						(config["Status"]["Bluetooth"]["Coordinates"]["X"],
						config["Status"]["Bluetooth"]["Coordinates"]["Y"]))
				if "ImageIndexOff" in config["Status"]["Bluetooth"] and not data["BLUETOOTH"]:
					pvd.addToCanvas(pvd.images[config["Status"]["Bluetooth"]["ImageIndexOff"]],
						(config["Status"]["Bluetooth"]["Coordinates"]["X"],
						config["Status"]["Bluetooth"]["Coordinates"]["Y"]))
			if "Battery" in config["Status"]:
				if "Text" in config["Status"]["Battery"]:
					pvd.drawRectNumberObject(config["Status"]["Battery"]["Text"], value=data["BATTERY"])
				if "Icon" in config["Status"]["Battery"]:
					value = int(config["Status"]["Battery"]["Icon"]["ImagesCount"]*(data["BATTERY"]/100))
					if value >= config["Status"]["Battery"]["Icon"]["ImagesCount"]:
						value=config["Status"]["Battery"]["Icon"]["ImagesCount"]-1
					pvd.drawObject(config["Status"]["Battery"]["Icon"], value=value)

		# Analog clock
		if "AnalogDialFace" in config:
			if "Hours" in config["AnalogDialFace"]:
				angle = 30*( (data["H0"]*10+data["H1"])+(data["M0"]*10+data["M1"])/60 )
				pvd.drawAnalogDial(config["AnalogDialFace"]["Hours"], angle=angle)
				if "CenterImage" in config["AnalogDialFace"]["Hours"]:
					pvd.drawObject(config["AnalogDialFace"]["Hours"]["CenterImage"])
			if "Minutes" in config["AnalogDialFace"]:
				angle = 360*( (data["M0"]*10+data["M1"])/60 )
				pvd.drawAnalogDial(config["AnalogDialFace"]["Minutes"], angle=angle)
				if "CenterImage" in config["AnalogDialFace"]["Minutes"]:
					pvd.drawObject(config["AnalogDialFace"]["Minutes"]["CenterImage"])
			if "Seconds" in config["AnalogDialFace"]:
				angle = 360*( (data["S0"]*10+data["S1"])/60 )
				pvd.drawAnalogDial(config["AnalogDialFace"]["Seconds"], angle=angle)
				if "CenterImage" in config["AnalogDialFace"]["Seconds"]:
					pvd.drawObject(config["AnalogDialFace"]["Seconds"]["CenterImage"])

		# Other
		if "Other" in config:
			if "Animation" in config["Other"]:
				pvd.drawObject(config["Other"]["Animation"]["AnimationImage"], value=data["ANIMATION_FRAME"])

		return pvd.getCanvas()
