# Copyright 2022 Red Hat, Inc.
#
# Author: Gris Ge <fge@redhat.com>
#
# This file is part of cloud-init. See LICENSE file for license information.

import re
import os
import yaml

from cloudinit import subp
from . import renderer

from libnmstate import generate_configurations


NM_CONF_FOLDER = "/etc/NetworkManager/system-connections/"


class Renderer(renderer.Renderer):
    def __init__(self, config=None):
        pass

    # We are supposed to only create configurations
    def render_network_state(self, network_state, templates=None, target=None):
        plugin_confs = generate_configurations(network_state.config["desired"])
        for conf in plugin_confs.get("NetworkManager", []):
            save_nm_conf(get_con_id(conf), conf)


def available(target=None):
    try:
        import libnmstate

        return True
    except ModuleNotFoundError:
        return False


def save_nm_conf(connection_id, content):
    if connection_id is None:
        # TODO: blame nmstate
        return
    file_path = f"{NM_CONF_FOLDER}/{connection_id}.nmconnection"
    with open(file_path, "w") as fd:
        fd.write(content)

    os.chmod(file_path, 0o600)
    os.chown(file_path, 0, 0)


def get_con_id(conf):
    is_connection_section = False
    for line in conf.split("\n"):
        if not is_connection_section and re.match("^\[connection\]$", line):
            is_connection_section = True
            continue
        if is_connection_section:
            if re.match("^\[", line):
                is_connection_section = False
                continue
            result = re.match("^id=(.+)$", line)
            if result:
                return result.group(1)
    return None
