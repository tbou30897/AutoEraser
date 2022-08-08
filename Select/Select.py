#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -*- Python -*-

"""
 @file Select.py
 @brief ModuleDescription
 @date $Date$


"""
import math
import sys
import time
import tkinter as tk
from PIL import Image, ImageTk  # 画像データ用
import cv2
import numpy
sys.path.append(".")

# Import RTM module
import RTC
import OpenRTM_aist


# Import Service implementation class
# <rtc-template block="service_impl">

# </rtc-template>

# Import Service stub modules
# <rtc-template block="consumer_import">
# </rtc-template>


# This module's spesification
# <rtc-template block="module_spec">
select_spec = ["implementation_id", "Select",
		 "type_name",         "Select",
		 "description",       "ModuleDescription",
		 "version",           "1.0.0",
		 "vendor",            "Ruchi",
		 "category",          "GUI",
		 "activity_type",     "STATIC",
		 "max_instance",      "1",
		 "language",          "Python",
		 "lang_type",         "SCRIPT",
		 "conf.default.Width", "800",
		 "conf.default.Height", "450",

		 "conf.__widget__.Width", "text",
		 "conf.__widget__.Height", "slider.1",
		 "conf.__constraints__.Width", "400<=x<=1600",
		 "conf.__constraints__.Height", "225<=x<=900",

         "conf.__type__.Width", "int",
         "conf.__type__.Height", "int",

		 ""]
# </rtc-template>

##
# @class Select
# @brief ModuleDescription
#
#
class Select(OpenRTM_aist.DataFlowComponentBase):

	##
	# @brief constructor
	# @param manager Maneger Object
	#
	def __init__(self, manager):
		OpenRTM_aist.DataFlowComponentBase.__init__(self, manager)

		self._d_ShowImage = OpenRTM_aist.instantiateDataType(RTC.CameraImage)
		"""
		Select target image
		"""
		self._ShowImageIn = OpenRTM_aist.InPort("ShowImage", self._d_ShowImage)
		self._d_CompeteMotion = OpenRTM_aist.instantiateDataType(RTC.TimedString)
		"""
		"""
		self._CompeteMotionIn = OpenRTM_aist.InPort("CompeteMotion", self._d_CompeteMotion)
		self._d_StatusCode = OpenRTM_aist.instantiateDataType(RTC.TimedUShort)
		"""
		"""
		self._StatusCodeIn = OpenRTM_aist.InPort("StatusCode", self._d_StatusCode)
		self._d_StartPoint = OpenRTM_aist.instantiateDataType(RTC.Point2D)
		"""
		 - Semantics: Percentage from top left
		 - Unit: ratio
		"""
		self._StartPointOut = OpenRTM_aist.OutPort("StartPoint", self._d_StartPoint)
		self._d_EndPoint = OpenRTM_aist.instantiateDataType(RTC.Point2D)
		"""
		 - Semantics: Percentage from top left
		 - Unit: ratio
		"""
		self._EndPointOut = OpenRTM_aist.OutPort("EndPoint", self._d_EndPoint)





		# initialize of configuration-data.
		# <rtc-template block="init_conf_param">
		"""
		
		 - Name:  Width
		 - DefaultValue: 800
		"""
		self._Width = [800]
		"""
		
		 - Name:  Height
		 - DefaultValue: 450
		"""
		self._Height = [450]

		# </rtc-template>
		self.photoImage = [None]
		self.showImg = [None]
		self.window = [None]
		self.canvas = [None]
		self.img = [None]
		self.startX = [0]
		self.startY = [0]
		self.startPos = [0, 0]
		self.endPos = [0, 0]
		self.clickCount = [0]
		self.shiftState = [False]
		self.pos = numpy.array([[0, 0], [self._Width[0], 0], [0, self._Height[0]], [self._Width[0], self._Height[0]]])
		self.cache = numpy.array([[0, 0], [0, 0], [0, 0], [0, 0]])
		self.points = [None, None, None, None]

	def onClick(self, event):
		self.startX[0] = numpy.clip(event.x, 0, self._Width)
		self.startY[0] = numpy.clip(event.y, 0, self._Height)

		if(self.shiftState):
			target = self.points[self.clickCount]
			self.cache[self.clickCount] = [event.x, event.y]
			current = self.canvas.coords(target)
			#todo magick number
			moveX = event.x - current[2] + 5
			moveY = event.y - current[3] + 5
			self.canvas.move(target, moveX, moveY)
			self.clickCount = (self.clickCount + 1) % 4

			if(self.clickCount == 0):
				self.pos = self.cache
	
	def drag(self, event):
		#todo
		self.canvas.coords(self.rect, self.startX, self.startY, event.x, event.y)
	
	def release(self, event):
		endX = numpy.clip(event.x, 0, self._Width[0])
		endY = numpy.clip(event.y, 0, self._Height[0])

		self.startPos = numpy.array([self.startX, self.startY])
		self.endPos = numpy.array([endX, endY])
		self.canvas.corrds(rect, 0, 0, 0, 0)

	def isShift(keysym):
		return keysym == "Shift_L" or keysym == "Shift_R"

	def keyPress(self, e):
		if(isShift(e.keysym)):
			self.shiftState = True
	
	def keyRelease(self, e):
		if(isShift(e.keysym)):
			self.shiftState = False

	#$def fit(self, img, ratio, p1, p2, p3, p4):
	def fit(self, img, ratio, p1, p2, p3, p4):
		# l -> left
		# r -> right
		# t -> top
		# b -> bottom

		centerX = (p1[0] + p2[0] + p3[0] + p4[0]) / 4
		centerY = (p1[1] + p2[1] + p3[1] + p4[1]) / 4

		lt = [0, 0]
		rt = [0, 0]
		lb = [0, 0]
		lb = [0, 0]

		for p in [p1, p2, p3, p4]:
			if(p[0] <= centerX):
				if(p[1] <= centerY):
					lt = p
				else:
					lb = p
			else:
				if(p[1] <= centerY):
					rt = p
				else:
					rb = p

		width = numpy.linalg.norm(rt - lt)
		width = math.floor(width * ratio)

		height = numpy.linalg.norm(lb - lt)
		height = math.floor(height)

		src = numpy.float32([lt, rt, lb, rb])
		dst = numpy.float32([[0, 0], [width, 0], [0, height], [width, height]])
		
		matrix = cv2.getPerspectiveTransform(src, dst)
		return cv2.warpPerspective(img, matrix, (width, height))

	def reset(self, event):
		self.pos = numpy.array([0, 0], [self._Width, 0], [0, self._Height], [self._Width, self._Height])

	##
	#
	# The initialize action (on CREATED->ALIVE transition)
	# formaer rtc_init_entry()
	#
	# @return RTC::ReturnCode_t
	#
	#
	def onInitialize(self):
		# Bind variables and configuration variable

		# Set InPort buffers
		self.addInPort("ShowImage",self._ShowImageIn)
		self.addInPort("CompeteMotion",self._CompeteMotionIn)
		self.addInPort("StatusCode",self._StatusCodeIn)

		# Set OutPort buffers
		self.addOutPort("StartPoint",self._StartPointOut)
		self.addOutPort("EndPoint",self._EndPointOut)

		# Set service provider to Ports

		# Set service consumers to Ports

		# Set CORBA Service Ports

		return RTC.RTC_OK

	###
	##
	## The finalize action (on ALIVE->END transition)
	## formaer rtc_exiting_entry()
	##
	## @return RTC::ReturnCode_t
	#
	##
	#def onFinalize(self):
	#
	#	return RTC.RTC_OK

	###
	##
	## The startup action when ExecutionContext startup
	## former rtc_starting_entry()
	##
	## @param ec_id target ExecutionContext Id
	##
	## @return RTC::ReturnCode_t
	##
	##
	#def onStartup(self, ec_id):
	#
	#	return RTC.RTC_OK

	###
	##
	## The shutdown action when ExecutionContext stop
	## former rtc_stopping_entry()
	##
	## @param ec_id target ExecutionContext Id
	##
	## @return RTC::ReturnCode_t
	##
	##
	#def onShutdown(self, ec_id):
	#
	#	return RTC.RTC_OK

	##
	#
	# The activated action (Active state entry action)
	# former rtc_active_entry()
	#
	# @param ec_id target ExecutionContext Id
	#
	# @return RTC::ReturnCode_t
	#
	#
	def onActivated(self, ec_id):
		self.window = [tk.Tk()]
		self.window[0].geometry('{0}x{1}'.format(self._Width[0], self._Height[0]))
		self.window[0].update_idletasks()
		self.window[0].title('whiteboard')
		self.window[0].resizable(False, False)

		self.canvas = [tk.Canvas(self.window[0])]
		self.canvas[0].pack(expand=True, fill=tk.BOTH)

		return RTC.RTC_OK

	##
	#
	# The deactivated action (Active state exit action)
	# former rtc_active_exit()
	#
	# @param ec_id target ExecutionContext Id
	#
	# @return RTC::ReturnCode_t
	#
	#
	def onDeactivated(self, ec_id):
	
		return RTC.RTC_OK

	##
	#
	# The execution action that is invoked periodically
	# former rtc_active_do()
	#
	# @param ec_id target ExecutionContext Id
	#
	# @return RTC::ReturnCode_t
	#
	#
	def onExecute(self, ec_id):
		#this method is only check and set img then show img
		#check in port
		if(self._ShowImageIn.isNew()):
			#in port has new buffer
			#read buffer and reshape as cv2 img
			rawImage = self._ShowImageIn.read()
			self.img[0] = numpy.frombuffer(rawImage.pixels, numpy.uint8).reshape((rawImage.height, rawImage.width, 3))
			self.img[0] = cv2.cvtColor(self.img[0], cv2.COLOR_BGRA2BGR)

		#object identity
		if(self.img[0] is not None):
			self.img[0] = cv2.resize(self.img[0], (self._Width[0], self._Height[0]))
			self.img[0] = self.fit(self.img[0], 1, self.pos[0], self.pos[1], self.pos[2], self.pos[3])
			self.img[0] = cv2.resize(self.img[0], (self._Width[0], self._Height[0]))

			cv_image = cv2.cvtColor(self.img[0], cv2.COLOR_BGR2RGB)
			# NumPyのndarrayからPillowのImageへ変換
			pil_image = Image.fromarray(cv_image)
			self.photoImage[0] = ImageTk.PhotoImage(image=pil_image)
			# 画像の描画
			self.showImg[0] = self.canvas[0].create_image(
					self.window[0].winfo_width() / 2,       # 画像表示位置(Canvasの中心)
					self.window[0].winfo_height() / 2,                   
					image=self.photoImage[0]  # 表示画像データ
					)
			self.canvas[0].lower(self.showImg[0])

			self.window[0].update_idletasks()
			self.window[0].update()

			#cv2.imshow('WhiteBoard', self.img[0])
			#param->ms
			#cv2.waitKey(1)

		return RTC.RTC_OK

	###
	##
	## The aborting action when main logic error occurred.
	## former rtc_aborting_entry()
	##
	## @param ec_id target ExecutionContext Id
	##
	## @return RTC::ReturnCode_t
	##
	##
	#def onAborting(self, ec_id):
	#
	#	return RTC.RTC_OK

	###
	##
	## The error action in ERROR state
	## former rtc_error_do()
	##
	## @param ec_id target ExecutionContext Id
	##
	## @return RTC::ReturnCode_t
	##
	##
	#def onError(self, ec_id):
	#
	#	return RTC.RTC_OK

	###
	##
	## The reset action that is invoked resetting
	## This is same but different the former rtc_init_entry()
	##
	## @param ec_id target ExecutionContext Id
	##
	## @return RTC::ReturnCode_t
	##
	##
	#def onReset(self, ec_id):
	#
	#	return RTC.RTC_OK

	###
	##
	## The state update action that is invoked after onExecute() action
	## no corresponding operation exists in OpenRTm-aist-0.2.0
	##
	## @param ec_id target ExecutionContext Id
	##
	## @return RTC::ReturnCode_t
	##

	##
	#def onStateUpdate(self, ec_id):
	#
	#	return RTC.RTC_OK

	###
	##
	## The action that is invoked when execution context's rate is changed
	## no corresponding operation exists in OpenRTm-aist-0.2.0
	##
	## @param ec_id target ExecutionContext Id
	##
	## @return RTC::ReturnCode_t
	##
	##
	#def onRateChanged(self, ec_id):
	#
	#	return RTC.RTC_OK




def SelectInit(manager):
    profile = OpenRTM_aist.Properties(defaults_str=select_spec)
    manager.registerFactory(profile,
                            Select,
                            OpenRTM_aist.Delete)

def MyModuleInit(manager):
    SelectInit(manager)

    # Create a component
    comp = manager.createComponent("Select")

def main():
	mgr = OpenRTM_aist.Manager.init(sys.argv)
	mgr.setModuleInitProc(MyModuleInit)
	mgr.activateManager()
	mgr.runManager()

if __name__ == "__main__":
	main()

