# -*- coding: utf-8 -*-
"""
This module implements a sampler threads controller.
"""
import tensorflow as tf

from niftynet.engine.signal import SESS_STARTED, SESS_FINISHED
from niftynet.utilities.util_common import traverse_nested


class SamplerThreading(object):
    """
    This class handles iteration events to start/stop samplers' threads.
    """

    def __init__(self, coordinator, num_threads=1, **_unused):
        self.coordinator = coordinator
        self.num_threads = num_threads

        SESS_STARTED.connect(self.start_sampler_threads)
        SESS_FINISHED.connect(self.stop_sampler_threads)

    def start_sampler_threads(self, sender, **_unused_msg):
        """
        Get samplers from application and try to run sampler's threads.

        :param sender:
        :param _unused_msg:
        :return:
        """
        sess = tf.get_default_session()
        if not sess or not self.coordinator:
            return
        try:
            for sampler in traverse_nested(sender.get_sampler()):
                if sampler is None:
                    continue
                sampler.run_threads(sess, self.coordinator, self.num_threads)
            tf.logging.info('filling queues (this can take a few minutes).')
        except (NameError, TypeError, AttributeError, IndexError):
            tf.logging.fatal(
                "samplers not running, pop_batch_op operations "
                "are blocked.")
            raise

    @staticmethod
    def stop_sampler_threads(sender, **_unused_msg):
        """
        Stop the sampler's threads

        :param sender: an instance of niftynet.application
        :param _unused_msg:
        :return:
        """
        try:
            tf.logging.info('stopping sampling threads')
            for sampler in traverse_nested(sender.get_sampler()):
                if sampler is None:
                    continue
                sampler.close_all()
        except (AttributeError, TypeError):
            pass
