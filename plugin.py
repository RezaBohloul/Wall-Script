# encoding: utf-8

###########################################################################################################
#
#
# General Plugin
#
# Read the docs:
#
#
###########################################################################################################

from __future__ import division, print_function, unicode_literals
import objc
from GlyphsApp import Glyphs, WINDOW_MENU
from GlyphsApp.plugins import GeneralPlugin
from AppKit import NSMenuItem


class WallScript(GeneralPlugin):

	@objc.python_method
	def settings(self):
		self.name = Glyphs.localize({
			'en': 'Wall Script',
		})

	@objc.python_method
	def start(self):
		if Glyphs.versionNumber >= 3.3:
			newMenuItem = NSMenuItem(self.name, callback=self.WallScript, target=self)
		else:
			newMenuItem = NSMenuItem(self.name, self.WallScript)
		Glyphs.menu[WINDOW_MENU].append(newMenuItem)

	def WallScript(self, sender):
		"""Pin script's to the wall and enjoy"""
		print("WallScript")

	@objc.python_method
	def __file__(self):
		"""Please leave this method unchanged"""
		return __file__
