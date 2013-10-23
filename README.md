getter
======

A simple async downloader for files.

 - Simulate random browser headers
 - Referer URL
 - Multi-process (-w switch)
 - MIME Type strict (only certain MIME types are allowed)
 - CSV input for urls

The bad things
--------------

I cannot find a suitable way to catch ctrl+c signal. If you want to stop it you have to kill it


Requirements
-------------

 - mechanize
 - yaml
 - setproctitle


**Disclamer**: This born as an experiment to improve my precarious python knowledge, download some images and use the multiprocess library. Everyone are welcome to comment the code