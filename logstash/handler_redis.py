#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import logging
import redis

from logstash import formatter


class RedisLogstashHandler(logging.Handler):
    def __init__(self, host='localhost', port=6379, db=0, password=None, 
                 logging_list='logstash', in_order=True, version=1, tags=None,
                 message_type='logstash', fqdn=False, *args, **kwargs):

        # init Redis connection and define Redis list used for logging
        self._redis = redis.Redis(host=host, port=port, db=db, password=password)
        self._logging_list = logging_list

        # set whether you want the logs to arrive sequentially
        # by locking a mutex when handling a message to be sent
        self._in_order = in_order

        # the usual formatter setting business
        fn = formatter.LogstashFormatterVersion0 if version == 0 \
             else formatter.LogstashFormatterVersion1
        self.formatter = fn(message_type, tags, fqdn)

        super(RedisLogstashHandler, self).__init__(*args, **kwargs)

    def emit(self, record):
        try:
            self._redis.rpush(self._logging_list, self.format(record))
        except:
            self.handleError(record)

    def createLock(self):
        if self._in_order:
            super(RedisLogstashHandler, self).createLock()
        else:
            self.lock = None
