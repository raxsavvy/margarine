# Copyright (C) 2014 by Alex Brandt <alex.brandt@rackspace.com>
#
# margarine is freely distributable under the terms of an MIT-style license.
# See COPYING or http://www.opensource.org/licenses/mit-license.php.

import vagrant


def is_vagrant_up(box_name):
    '''Checks if the specified host is up in the vagrant environment.

    Parameters
    ----------

    :``box_name``: Vagrant box name to check the status of

    Return
    ------

    True if the specified host is up; otherwise, False.

    '''

    return vagrant.Vagrant().status(box_name).get(box_name, 'not_created') == 'running'