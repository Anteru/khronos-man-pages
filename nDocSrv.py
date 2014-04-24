#!/usr/bin/env python3
# coding=utf8
# @author: Matthäus G. Chajdas
# @license: 3-clause BSD
"""
Serve files out of a ZIP file.
"""

import socketserver
from http.server import SimpleHTTPRequestHandler
import threading
import urllib.parse
import webbrowser
import zipfile

class Archive:
	def __init__ (self, archiveName, directoryPrefix=''):
		self._archive = zipfile.ZipFile (open(archiveName, 'rb'))
		self._prefix = directoryPrefix
		self._files = set (self._archive.namelist ())
		
	def Get (self, filename):
		if self._prefix + filename in self._files:
			return self._archive.read (self._prefix + filename)
		else:
			return None

class DocServer(socketserver.ThreadingTCPServer):
	def __init__(self, archives, host='localhost', port=80):
		super(DocServer, self).__init__((host, port), DocServer.RequestHandler)

		self.cacheLock = threading.Lock()
		self.cache = {}
		self.cacheSize = 0

		self.fileLock = threading.Lock()
		
		self._archives = archives
		
	class RequestHandler(SimpleHTTPRequestHandler):
		protocol_version = 'HTTP/1.1'
		server_version = 'niven nDocSrv 1.1'

		def _GuessMimeType(p):
			if p.endswith('.html') or p.endswith ('.xhtml'):
				return 'text/html; charset=utf-8'
			elif p.endswith('.css'):
				return 'text/css'
			elif p.endswith('.png'):
				return 'image/png'
			elif p.endswith('.js'):
				return 'application/javascript'
			else:
				return 'text/plain'
	
		def log_message(self, format, *args):
			pass
		
		def do_GET(self):
			request = urllib.parse.urlparse(self.path)
			path = request.path
			if path == '/':
				path = 'index.html'
			else:
				path = path[1:]
			content = None
			
			try:
				cacheHit = False
				with self.server.cacheLock:
					if path in self.server.cache:
						content = self.server.cache [path]
						cacheHit = True

				# Could not fetch from cache
				if content is None:
					with self.server.fileLock:
						for archive in self.server._archives:
							content = archive.Get (path)
							if content:
								break
						else:
							self.send_error(404, 'Could not find "{}"'.format (path))
							return
							
				self.send_response(200)
				self.send_header('Content-type', self.__class__._GuessMimeType(path))
				self.send_header('Content-length', len(content))
				self.send_header('Cache-Control', 'max-age=600,public')
				self.end_headers()
				self.wfile.write(content)

				if cacheHit == False:
					print ("Caching '{}'".format (path))
					with self.server.cacheLock:
						self.server.cache[path] = content
						self.server.cacheSize += len(content)
			
						if self.server.cacheSize > (2<<20):
							print ('Flushing cache')
							self.server.cache.clear()
							self.server.cacheSize = 0

			except Exception:
				import traceback
				self.send_error(500, traceback.format_exc())
			return

if __name__ == '__main__':
	import sys
	PORT = 31337
	
	archiveName = 'html.zip'
	if len(sys.argv) > 1:
		archiveName = sys.argv [1]
			
	archives = list ()
	archives.append (Archive ('mathjax-2.2.zip', 'mathjax-MathJax-727332c/'))
	archives.append (Archive (archiveName))
			
	docServer = DocServer(archives, 'localhost', PORT)

	def OpenBrowser():
		webbrowser.open('http://localhost:{}'.format(PORT))

	def Quit():
		trayIcon.setVisible(False)
		docServer.shutdown()
		exit()

	def Serve():
		print("serving at port", PORT)
		docServer.serve_forever()

	serverThread = threading.Thread(target=Serve)
	serverThread.start()

	OpenBrowser()

	serverThread.join()
