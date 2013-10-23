#!/usr/bin/python
# getter.py --  A simple async downloader for files.
#
#    Copyright (C) 2013 Felipe Alcacibar <falcacibar@gmail.com>
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software
#    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

import logging
import yaml
import os
import sys
import csv

import multiprocessing
# import signal

from setproctitle import setproctitle

me = 'getter'

mydir = os.path.dirname(__file__)
mydir = mydir if not mydir == '' else '.'

datadir  = os.path.realpath(mydir + '/data')
filedir  = os.path.realpath(mydir + '/files')

def download(id, refurl, fileurl):
    setproctitle('%s: worker ' % (me))

    try:
        import mechanize
        import random

        if fileurl:
            exists = False
            for ext in mimetypes.values():
                exists=os.path.exists(filedir + '/' + str(id) + '.' + ext)
                if exists:
                    break

            if not exists:
                browserHeaders = random.choice(browsersHeaders.keys())

                log.info(
                    'download[%s] download element %s simulating %s broeser from url %s '
                    % (os.getpid(), id, browserHeaders, fileurl)
                )

                setproctitle('%s: downloading %s from %s' % (me, id, fileurl))

                httpreq = mechanize.Request(fileurl)
                for header in browsersHeaders[browserHeaders]['headers'].items():
                    httpreq.add_header(*header)

                httpreq.add_header('User-Agent', random.choice(browsersHeaders[browserHeaders]['user_agent']))
                if(refurl): httpreq.add_header('Referer', refurl)

                browser = mechanize.Browser()
                browser.set_handle_robots(False)

                try:
                    browser.open(httpreq)
                except (mechanize.HTTPError,mechanize.URLError) as err:
                    log.error(
                        'download[%s] error: failed download for %s from url %s (%s %s)'
                        % (os.getpid(), id, fileurl, err.getcode(), err.reason)
                    )
                else:
                    setproctitle('%s: saving %s' % (me, id))

                    httpres  = browser.response()
                    mimetype = next(header for header in httpres.info().headers if header.lower()[:13] == 'content-type:')[14:].strip().lower()

                    log.info(
                        'download[%s] download end successfully for %s from url %s'
                        % (os.getpid(), id, fileurl)
                    )

                    try:
                        ext = mimetypes[mimetype]
                    except (KeyError):
                        log.error(
                            'download[%s] error: download does not have a recognized mimetype (%s) for %s from url %s'
                            % (os.getpid(), mimetype, id, fileurl)
                        )
                    else:
                        filename = filedir + ('/%s.%s' % (id, ext))

                        file = open(filename, 'w+')
                        file.write(httpres.read());
                        file.close();

                        log.info(
                            'download[%s] file from %s saved as %s'
                            % (os.getpid(), id, filename)
                        )

        setproctitle('%s: idle worker' % (me))
    except (KeyboardInterrupt, SystemExit):
        return

def kill(*args, **kwargs):
    procPool.close()
    procPool.terminate()
    procPool.join()

if __name__ == '__main__':
    from optparse import OptionParser

    setproctitle('%s: main process' % (me))

    streamMimeTypes = open(mydir+'/mimetypes.yml')
    mimetypes = yaml.load(streamMimeTypes)
    streamMimeTypes.close()

    lsh = logging.StreamHandler(sys.stdout)
    lsh.setLevel(logging.DEBUG)
    lsh.setFormatter(logging.Formatter('%(asctime)s %(message)s'))

    log = logging.getLogger('getter')
    log.setLevel(logging.DEBUG)
    log.addHandler(lsh)

    streamYmlBrowsers = open(mydir+'/browser.yml', 'r')
    browsersHeaders   = yaml.load(streamYmlBrowsers)
    streamYmlBrowsers.close();

    parser = OptionParser()
    parser.add_option(
        '-w', '--workers'
        , dest='workers'
        , help='Number of concurrent download workers'
        , metavar='N'
        , default=10
        , type='int'
    )

    (option, args) = parser.parse_args();

    if option.workers < 1: option.workers = 1
    procPool = multiprocessing.Pool(option.workers)

#   signal.signal(signal.SIGINT, kill)
#   signal.signal(signal.SIGQUIT, kill)
#   signal.signal(signal.SIGTERM, kill)

    for file in os.listdir(datadir):
        if file[-4:] == '.csv':
            streamCsvData = open(datadir + '/' + file, 'r');
            data = csv.reader(streamCsvData, delimiter=',', quotechar='\"')

            try:
                for row in data:
                    if row[1].strip():
#                       download(int(row[0]), row[2].strip(), row[1].strip())
                        """
                        procPool.map(
                            download_star
                            , [[int(row[0]), row[2].strip(), row[1].strip()]]
                        )
                        """

                        proc = procPool.apply_async(
                            download
                            , args = (row[0].strip(), row[2].strip(), row[1].strip())
                        )

            except (KeyboardInterrupt):
                log.warn(
                        'main[%s] Interrupted by user'
                        % (os.getpid())
                )

                kill()
            except (SystemExit):
                log.warn(
                        'main[%s] Exiting...'
                        % (os.getpid())
                )

            streamCsvData.close()

    procPool.close()
    procPool.join()
