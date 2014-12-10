#!/usr/bin/env python
import os
import sys
from optparse import OptionParser

parser = OptionParser()
parser.add_option('--project', dest='project', default=None, help='Project code')
(options, args) = parser.parse_args()

from firebase import firebase
fb = firebase.FirebaseApplication('URL')
authentication = firebase.FirebaseAuthentication('', 'ilya.lindberg@gmail.com', extra={'uid': ''})
fb.authentication = authentication

settings = fb.get('/projects/' + options.project + '/settings', None)
shots = fb.get('/shots/' + options.project, None)

try: 
    BASE_PROJECT_PATH = settings['root']
except:
    sys.stderr.write('Settings for root path does not exist.\n')
    sys.exit(1)

for sid, shot in shots.iteritems() :
	scene = shot['sequence'].upper()
	shot_name = ('%s%s%s') % (scene, settings['delimiter'], shot['code'])
	print shot_name

	paths = []
	dirs = ['dailies',
			 'hires',
			 'animation',
			 'tracking/proxy',
			 'scripts/nk',
			 'images/img',
			 'images/render',
			 'images/refs',
			 'images/tex',
			 '3d/houdini',
			 '3d/maya']
	for i in dirs:
		paths.append(os.path.join(BASE_PROJECT_PATH, options.project.upper(), 'comp', scene, shot['code'], i))

	for item in paths:
		if not os.path.exists(item):
			os.makedirs(item)

