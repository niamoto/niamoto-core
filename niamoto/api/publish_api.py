# coding: utf-8

import sys

from niamoto.data_publishers.base_data_publisher import PUBLISHER_REGISTRY
from niamoto.exceptions import WrongPublisherKeyError, \
    UnavailablePublishFormat


def publish(publisher_key, publish_format, *args, destination=sys.stdout,
            **kwargs):
    """
    Api method for processing and publishing data.
    :param publisher_key:
    :param publish_format:
    :param destination
    :return:
    """
    publisher_instance = get_publisher_class(publisher_key)()
    if publish_format not in publisher_instance.get_publish_formats():
        m = "The publish format '{}' is unavailable with the '{}' publisher."
        raise UnavailablePublishFormat(
            m.format(publish_format, publisher_key)
        )
    data, p_args, p_kwargs = publisher_instance.process(*args, **kwargs)
    kwargs.update(p_kwargs)
    publisher_instance.publish(
        data,
        publish_format,
        *p_args,
        destination=destination,
        **kwargs
    )


def list_publish_formats(publisher_key):
    """
    Return the publish formats accepted by a publisher.
    :param publisher_key:
    :return:
    """
    publisher_class = get_publisher_class(publisher_key)
    return publisher_class.get_publish_formats()


def get_publisher_class(publisher_key):
    """
    Return a publisher class from its key.
    :param publisher_key: The key of the publisher.
    :return: The publisher class corresponding to the key.
    """
    if publisher_key not in PUBLISHER_REGISTRY:
        m = "The publisher key '{}' does not exist.".format(publisher_key)
        raise WrongPublisherKeyError(m)
    publisher = PUBLISHER_REGISTRY[publisher_key]
    return publisher['class']
