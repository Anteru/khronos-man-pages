#!/usr/bin/env python3

from html.parser import HTMLParser
import glob
import os
import collections
from jinja2 import Environment, FileSystemLoader

class OpenGLPageParser(HTMLParser):
	def GetReferenceEntry (self):
		return self.refentry
	
	def IsGLApi (self):
		return self.refentry.startswith ('gl') and not self.refentry.startswith ('gl_')
	
	def IsGLSL (self):
		return not self.IsGLApi ()
	
	def handle_starttag(self, tag, attrs):
		if tag == 'div':
			attrs = {k: v for (k, v) in attrs}
			if attrs.get ('class', None) == 'refentry':
				self.refentry = attrs ['id']
				
class Index:
	def __init__(self, prefixSize = 0):
		self._targets = dict ()
		self._prefixSize = prefixSize
	
	def AddEntry (self, title, target):
		self._targets [title] = target
			
	def ToNestedIndex (self):
		od = collections.OrderedDict (sorted (self._targets.items ()))
		
		level0 = collections.OrderedDict ()
		for k, v in od.items ():
			key = k[self._prefixSize].lower()
			if key not in level0:
				level0 [key] = list ()
			
			level0 [key].append ((k, v))
			
		# Upper-case/lower-case conversion above might require resorting
		return collections.OrderedDict (sorted(level0.items()))
				
if __name__ == '__main__':
	glslIndex = Index ()
	glIndex = Index (len('gl'))
	
	for page in glob.glob ('src/opengl/4.0/html/*.xhtml'):
		glPageParser = OpenGLPageParser()
		glPageParser.feed (open(page).read())
		
		if glPageParser.IsGLApi ():
			glIndex.AddEntry (glPageParser.GetReferenceEntry (),
					 os.path.basename (page))
		else:
			glslIndex.AddEntry (glPageParser.GetReferenceEntry (),
					 os.path.basename (page))
			
	jinjaEnv = Environment(loader=FileSystemLoader('templates'))
	
	indexTemplate = jinjaEnv.get_template ('gl-sidebar.html')
	print (indexTemplate.render(glIndex=glIndex.ToNestedIndex(),glslIndex=glslIndex.ToNestedIndex()))