#!/usr/bin/env python
# ver 0.2.1 2009.09.11
# VISUALATELIER R&D

import os
import sys
import time
import subprocess
import tempfile
import urllib
import json
import base64
from multiprocessing import freeze_support
from optparse import OptionParser

import requests

sys.path.append(os.path.dirname(__file__))
# Download sequence.py from examples repo
import sequence


parser = OptionParser()

parser.add_option('--project', dest = 'project', default = None, help = 'Project code')
parser.add_option('-u', action = 'store_true', dest = 'upload', default = False, help = 'Upload to shotty')

(options, args) = parser.parse_args()


# python-firebase-1.2
from firebase import firebase
fb = firebase.FirebaseApplication('https://<<STUDIO>>.firebaseio.com/')
authentication = firebase.FirebaseAuthentication('rmT3XFW6tVG4T8JelfZ1hb8tyM1Pm1NBCsxwdpIl', None, extra={'uid': 'simplelogin:4'})
fb.authentication = authentication


settings = fb.get('/projects/' + options.project + '/settings', None)
shots = fb.get('/shots/' + options.project, None)



try:
    BASE_PLATE_PATH = settings['plate']
except:
    sys.stderr.write('Settings for plate path does not exist.\n')
    sys.exit(1)




def SequenceThumbGen(fframe, lframe, name):
    import uuid
    thmbStorePath = tempfile.gettempdir()
    if not os.path.exists(thmbStorePath):
        sys.stderr.write('Warning %s does not exist' % thmbStorePath)
        sys.exit(1)
    freeze_support()
    first = os.path.join(thmbStorePath, (name + '_fframe.jpg'))
    subprocess.check_call(['convert', fframe, '-resize', '50%', '-gravity', 'center', '-crop', '640x320+0+0', '-set', 'film-gamma', '1.7', first])

    print 'Thumbnail - %s' % first
    return first




allowed_extensions = ['.dpx', '.cin', '.tga', '.png']

for _id in shots:
    shot = shots[_id]

    shot_code = shot['code'].replace('-', settings['delimiter']).replace('_', settings['delimiter'])
    shot_name = ('%s%s%s') % (shot['sequence'].upper(), settings['delimiter'], shot['code'].replace('-', settings['delimiter']).replace('_', settings['delimiter']))

    # shot_plate_path = os.path.join(BASE_PLATE_PATH, str(shot['sequence']).upper(), shot['code'])
    shot_plate_path = BASE_PLATE_PATH.replace('%S', str(shot['sequence']).upper()).replace('%ID', shot_code)
    # shot_plate_path = os.path.join(BASE_PLATE_PATH, str(shot['sequence']).upper(), shot_name)



    # exists_sources_name = [ plate['code'] for plate in shot['plate'] ]

    print shot_plate_path

    # s = sequence.glob(os.path.join(shot_plate_path, shot_name))
    s = sequence.glob(os.path.join(os.path.normpath(shot_plate_path), '*'))
    # print s
    if len(s) == 1:
        print '\tMain plate ', s
        seq = s[0]
        ff = str(seq[0])
        lf = str(seq[-1])
        sname, srange = seq.sequenceName()
        try:
            range = sequence.Range(srange[0])
        except:
            range = sequence.Range('1-1')
        path, filename = os.path.split(sname)
        root, ext = os.path.splitext(filename)
        count = len(range)
        if count == 1: lf = ff
        frames = list(range)
        fframe = str(frames[0])
        lframe = str(frames[-1])

        plateKey = filename.replace('@', '').replace('.', '').replace('#', '')

        if 'plates' not in shot or plateKey not in shot['plates'].keys():
            print 'Plate', plateKey

            if ext in allowed_extensions and options.upload:


                thumb = SequenceThumbGen(ff, lf, shot_name)

                url = 'http://raketa.shotty.cc/api/plate/upload'
                files = {'file': open(thumb, 'rb')}
                r = requests.post(url, files=files)

                if r.status_code == requests.codes.ok:

                    data = {
                            'path': path,
                            'code': filename,
                            'count': str(count),
                            'ff': int(fframe),
                            'lf': int(lframe),
                            'poster': r.json(),
                            'main': True,

                        }

                    print data
                    print 'shot firebase id', _id

                    # time.sleep(1)
                    fb.put('/shots/' + options.project + '/' + _id + '/plates/', plateKey, data)
