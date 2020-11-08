import sys, os, json
sys.path.append(os.path.dirname(__file__))

import PreviewDrawer
from PIL import Image

def from_path(path, fixmissing=False):
	l = Loader_MiBand5()
	l.loadFromDir(path ,fixmissing=fixmissing)
	return l

class Loader_MiBand5:
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
			"MUTE", "LOCK", "ANIMATION_FRAME", "ALARM_ON", "WEATHER_ICON",
			"TEMP_CURRENT", "TEMP_DAY", "TEMP_NIGHT"]

	def render(self):
		pvd = PreviewDrawer.new(size=(126,294))
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
					posixIndex=dist["KmSuffixImageIndex"])
				x, y = pvd.calculateXYPos(dist["Number"], img.size)
				pvd.addToCanvas(img, (int(x),int(y)))
			if "Calories" in self.config["Activity"]:
				pvd.drawRectNumberObject(self.config["Activity"]["Calories"]["Text"], data["CALORIES"])

		# Date and weekday
		twoDDay = False
		twoDMonth = False
		if "Date" in config:
			if "MonthAndDayAndYear" in config["Date"]:
				if "TwoDigitsDay" in config["Date"]["MonthAndDayAndYear"]:
					twoDDay = config["Date"]["MonthAndDayAndYear"]["TwoDigitsDay"]
				if "TwoDigitsMonth" in config["Date"]["MonthAndDayAndYear"]:
					twoDMonth = config["Date"]["MonthAndDayAndYear"]["TwoDigitsMonth"]
				if "Separate" in config["Date"]["MonthAndDayAndYear"]:
					if "Month" in config["Date"]["MonthAndDayAndYear"]["Separate"]:
						pvd.drawRectNumberObject(config["Date"]["MonthAndDayAndYear"]["Separate"]["Month"],
							value=data["MONTH"], digits=(2 if twoDMonth else 1))
					if "MonthsEN" in config["Date"]["MonthAndDayAndYear"]["Separate"]:
						pvd.drawObject(config["Date"]["MonthAndDayAndYear"]["Separate"]["MonthsEN"],
							value=data["MONTH"]-1)
					if "Day" in self.config["Date"]["MonthAndDayAndYear"]["Separate"]:
						pvd.drawRectNumberObject(config["Date"]["MonthAndDayAndYear"]["Separate"]["Day"],
							value=data["DAY"], digits=(2 if twoDDay else 1))
			if "ENWeekDays" in self.config["Date"] and data["WEEKDAY_LANG"] == 2:
				pvd.drawObject(self.config["Date"]["ENWeekDays"], value=data["WEEKDAY"])
			if "CNWeekDays" in self.config["Date"] and data["WEEKDAY_LANG"] == 0:
				pvd.drawObject(self.config["Date"]["CNWeekDays"], value=data["WEEKDAY"])
			if "CN2WeekDays" in self.config["Date"] and data["WEEKDAY_LANG"] == 1:
				pvd.drawObject(self.config["Date"]["CN2WeekDays"], value=data["WEEKDAY"])
			if "DayAmPm" in self.config["Date"] and not data["24H"]: #TESTME
				apm = config["Date"]["DayAmPm"]
				if data["APM_CN"]:
					if data["APM_PM"]: index = apm["ImageIndexPMCN"]
					else: index = apm["ImageIndexAMCN"]
				else:
					if data["APM_PM"]: index = apm["ImageIndexPMEN"]
					else: index = apm["ImageIndexAMEN"]
				pvd.addToCanvas(pvd.images[index], (apm["X"], apm["Y"]))

		# Indicators # FIXME
		if "StepsProgress" in config:
			if "LineScale" in config["StepsProgress"]:
				progress = min(1, data["STEPS"] / data["STEPS_TARGET"])
				curSegment = int(config["StepsProgress"]["LineScale"]["ImagesCount"] * progress)
				if curSegment >= config["StepsProgress"]["LineScale"]["ImagesCount"]:
					curSegment = config["StepsProgress"]["LineScale"]["ImagesCount"]-1
				pvd.drawObject(config["StepsProgress"]["LineScale"], value=curSegment)
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

		# Status
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
				if "ImageIndexOn" in config["Status"]["Lock"] and not data["LOCK"]:
					pvd.addToCanvas(pvd.images[config["Status"]["Lock"]["ImageIndexOn"]],
						(config["Status"]["Lock"]["Coordinates"]["X"],
						config["Status"]["Lock"]["Coordinates"]["Y"]))
				if "ImageIndexOff" in config["Status"]["Lock"] and data["LOCK"]:
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

		# Battery
		if "Battery" in config:
			if "BatteryText" in config["Battery"]:
				batt = config["Battery"]["BatteryText"]
				posix = -1
				if "SuffixImageIndex" in batt: posix = batt["SuffixImageIndex"]
				img = pvd.buildHybridLine(batt["Coordinates"], data["BATTERY"],
					posixIndex=posix)
				x, y = pvd.calculateXYPos(batt["Coordinates"], img.size)
				pvd.addToCanvas(img, (int(x),int(y)))
			if "BatteryIcon" in config["Battery"]:
				value = int(config["Battery"]["BatteryIcon"]["ImagesCount"]*(data["BATTERY"]/100))
				if value >= config["Battery"]["BatteryIcon"]["ImagesCount"]:
					value=config["Battery"]["BatteryIcon"]["ImagesCount"]-1
				pvd.drawObject(config["Battery"]["BatteryIcon"], value=value)
			if "Linear" in config["Battery"]:
				index = config["Battery"]["Linear"]["StartImageIndex"]
				segments = config["Battery"]["Linear"]["Segments"]
				progress = data["BATTERY"]/100
				curSegment = int(len(segments) * progress)
				for i in range(curSegment):
					img = pvd.images[index+i]
					pvd.addToCanvas(img, (segments[i]["X"], segments[i]["Y"]))

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

		# Alarm
		if "Alarm" in config:
			if "Text" in config["Alarm"] and data["ALARM_ON"]:
				value = data["H0"]*10+data["H1"]+data["M0"]*0.1+data["M1"]*0.01
				value = round(value, 2)
				alarm = config["Alarm"]
				img = pvd.buildHybridLine(alarm["Text"], value,
					dotIndex=alarm["DelimiterImageIndex"],
					digits_after_dot=2, digits_before_dot=2)
				x, y = pvd.calculateXYPos(alarm["Text"], img.size)
				pvd.addToCanvas(img, (int(x),int(y)))
			if "ImageOn" in config["Alarm"] and data["ALARM_ON"]:
				pvd.drawObject(config["Alarm"]["ImageOn"])
			if "ImageOff" in config["Alarm"] and not data["ALARM_ON"]:
				pvd.drawObject(config["Alarm"]["ImageOff"])
			if "ImageNoAlarm" in config["Alarm"] and not data["ALARM_ON"]:
				pvd.drawObject(config["Alarm"]["ImageNoAlarm"])

		# Weather
		if "Weather" in config:
			if "Icon" in config["Weather"]:
				if "CustomIcon" in config["Weather"]["Icon"]:
					pvd.drawObject(config["Weather"]["Icon"]["CustomIcon"], value=data["WEATHER_ICON"])
			if "Temperature" in config["Weather"]:
				if "Current" in config["Weather"]["Temperature"]:
					c = config["Weather"]["Temperature"]["Current"]
					i = pvd.buildHybridLine(c["Number"], data["TEMP_CURRENT"],
						minusIndex=c["MinusImageIndex"], posixIndex=c["DegreesImageIndex"])
					x, y = pvd.calculateXYPos(c["Number"], i.size)
					pvd.addToCanvas(i, (int(x),int(y)))
				if "Today" in config["Weather"]["Temperature"]:
					if "OneLine" in config["Weather"]["Temperature"]["Today"]:
						c = config["Weather"]["Temperature"]["Today"]["OneLine"]
						imgs = []
						v = data["TEMP_DAY"]
						if v < 0: imgs.append(pvd.images[c["MinusSignImageIndex"]])
						if v < 0: v = -v
						imgs.append(pvd.buildNumberImg(c["Number"], v))
						if "DelimiterImageIndex" in c:
							imgs.append(pvd.images[c["DelimiterImageIndex"]])
						v = data["TEMP_NIGHT"]
						if v < 0: imgs.append(pvd.images[c["MinusSignImageIndex"]])
						if v < 0: v = -v
						imgs.append(pvd.buildNumberImg(c["Number"], v))
						if "DelimiterImageIndex" in c and c["AppendDegreesForBoth"]:
							imgs.append(pvd.images[c["DelimiterImageIndex"]])
						o = pvd.concatImgArray(imgs)
						x, y = pvd.calculateXYPos(c["Number"], o.size)
						pvd.addToCanvas(o, (int(x), int(y)))

		# Other
		if "Other" in config:
			if "Animation" in config["Other"]:
				for a in config["Other"]["Animation"]:
					if data["ANIMATION_FRAME"] < a["AnimationImages"]["ImagesCount"]:
						pvd.drawObject(a["AnimationImages"], value=data["ANIMATION_FRAME"])

		return pvd.getCanvas()
