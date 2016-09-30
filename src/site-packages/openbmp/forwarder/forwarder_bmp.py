# -*- coding: utf-8 -*-
"""OpenBMP forwarder

  Copyright (c) 2013-2015 Cisco Systems, Inc. and others.  All rights reserved.
  This program and the accompanying materials are made available under the
  terms of the Eclipse Public License v1.0 which accompanies this distribution,
  and is available at http://www.eclipse.org/legal/epl-v10.html

  .. moduleauthor:: Tim Evens <tievens@cisco.com>
"""
import socket
import multiprocessing

from time import sleep
from openbmp.forwarder.logger import init_mp_logger


class BMPWriter(multiprocessing.Process):
    """ BMP Forwarder

        Pops messages from forwarder queue and transmits them to remote bmp collector.
    """

    def __init__(self, cfg, forward_queue, log_queue):
        """ Constructor

            :param cfg:             Configuration dictionary
            :param forward_queue:   Output for BMP raw message forwarding
            :param log_queue:       Logging queue - sync logging
        """
        multiprocessing.Process.__init__(self)
        self._stop = multiprocessing.Event()

        self._cfg = cfg
        self._fwd_queue = forward_queue
        self._log_queue = log_queue
        self.LOG = None
        self._isConnected = False

        self._sock = None

    def run(self):
        """ Override """
        self.LOG = init_mp_logger("bmp_writer", self._log_queue)

        self.LOG.info("Running bmp_writer")

        self.connect()

        try:
            # wait for the mapping config to be loaded
            while not self.stopped():
                if self._cfg and 'logging' in self._cfg:
                    break

            # Read queue
            while not self.stopped():

                # Do not pop any message unless connected
                if self._isConnected:
                    msg = self._fwd_queue.get()

                    sent = False
                    while not sent:
                        sent = self.send(msg.BMP_MSG)

                    self.LOG.debug("Received bmp message: %s %s %s", msg.COLLECTOR_ADMIN_ID,
                                   msg.ROUTER_IP, msg.ROUTER_NAME)
                else:
                    self.LOG.info("Not connected, attempting to reconnect")
                    sleep(1)
                    self.connect()

        except KeyboardInterrupt:
            pass

        self.LOG.info("rewrite stopped")

    def connect(self):
        """ Connect to remote collector

        :return: True if connected, False otherwise/error
        """
        try:
            self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._sock.connect((self._cfg['collector']['host'], self._cfg['collector']['port']))
            self._isConnected = True
            self.LOG.info("Connected to remote collector: %s:%d", self._cfg['collector']['host'],
                          self._cfg['collector']['port'])

        except socket.error as msg:
            self.LOG.error("Failed to connect to remote collector: %r", msg)
            self._isConnected = False

    def send(self, msg):
        """ Send BMP message to socket.

            :param msg:     Message to send/write

            :return: True if sent, False if not sent
        """
        sent = False

        try:
            self._sock.sendall(msg)
            sent = True

        except socket.error as msg:
            self.LOG.error("Failed to send message to collector: %r", msg)
            self.disconnect()
            sleep(1)
            self.connect()

        return sent

    def disconnect(self):
        """ Disconnect from remote collector
        """
        if self._sock:
            self._sock.close()
            self._sock = None

        self._isConnected = False

    def stop(self):
        self._stop.set()

    def stopped(self):
        return self._stop.is_set()
