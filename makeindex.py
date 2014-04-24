#!/usr/bin/env python3

from html.parser import HTMLParser
import glob
import os
import collections
from jinja2 import Environment, FileSystemLoader
import shutil
from bs4 import BeautifulSoup
import zipfile
import urllib.request

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
				
class OnlineDependencyResolver:
	"""Look at HTML files and try to download online dependencies like script
	and CSS files.
	
	As a special exception, MathJax will be ignored, as we assume the offline
	server comes with it's own local copy, and because MathJax loads a lot of
	stuff dynamically."""
	def __init__(self):
		self._requests = dict()
		
	def _register (self, url):
		import urllib.parse
		import os.path
		import hashlib
		from pathlib import Path
		
		if not url.startswith ('http') and not url.startswith ('//'):
			# Nothing to see here
			return url
				
		if url.startswith ('//'):
			url = 'http:' + url
		
		if url in self._requests:
			return self._requests [url][0]
		
		# special case handling for MathJax, which we ship manually
		mathJaxSource = 'https://c328740.ssl.cf1.rackcdn.com/mathjax/latest/'
		if url.startswith (mathJaxSource):
			# don't cache, just remove the prefix
			return url[len(mathJaxSource):]
		
		# Fetch from web, store in cache and create a new local filename
		content = urllib.request.urlopen (url).read ()
		contentHash = hashlib.sha256(content).hexdigest ()
		
		path = Path (urllib.parse.urlparse(url).path)
		
		filename = "{}_{}{}".format (path.stem, contentHash, path.suffix)
		
		self._requests [url] = (filename, content)
		
		return filename
	
	def ProcessPage (self, page):
		"""Replace online references with local file names and fetch the data
		from the internet.
		
		This method will only modify <script src="..."> and <link href="...">
		tags.
		
		Returns the adjusted HTML."""
		content = BeautifulSoup (open(page))
	
		# Find and replace script tags with local version
		for script in content.find_all ('script'):
			if script.get ('src'):
				script ['src'] = self._register (script.get ('src'))
				
		for link in content.find_all ('link'):
			if link.get ('href'):
				link ['href'] = self._register (link.get ('href'))

		return content.prettify().encode('utf-8')
	
	def GetOfflineData (self):
		return self._requests.values ()
				
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
	with open('build/gl/4.0/sidebar.html', 'w') as outputFile:
		outputFile.write (indexTemplate.render(
			glIndex=glIndex.ToNestedIndex(),
			glslIndex=glslIndex.ToNestedIndex()))
		
	with open('build/gl/4.0/index.html', 'w') as outputFile:
		outputFile.write (jinjaEnv.get_template ('index.html').render (
			title = 'OpenGL 4.x'))
		
	for page in glob.glob ('src/opengl/4.0/html/*html') + glob.glob ('src/opengl/4.0/html/*.css'):
		shutil.copy (page, 'build/gl/4.0/' + os.path.basename (page))
		
	# Offline build
	with zipfile.ZipFile ('build/offline/gl-4.0.zip', 'w') as output:
		odr = OnlineDependencyResolver()
		for page in glob.glob ('build/gl/4.0/*html'):
			output.writestr (os.path.basename (page), odr.ProcessPage (page))
		for css in glob.glob ('build/gl/4.0/*.css'):
			output.write (css, os.path.basename (css))
		for (filename, content) in odr.GetOfflineData ():
			output.writestr (filename, content)