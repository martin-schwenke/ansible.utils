# -*- coding: utf-8 -*-
# Copyright 2021 Red Hat
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""
filter plugin file for ipaddr filters: ipsubnet
"""
from __future__ import absolute_import, division, print_function

from functools import partial

from ansible.errors import AnsibleFilterError

from ansible_collections.ansible.utils.plugins.module_utils.common.argspec_validate import (
    AnsibleArgSpecValidator,
)
from ansible_collections.ansible.utils.plugins.plugin_utils.base.ipaddr_utils import (
    _need_netaddr,
    ipaddr,
)


__metaclass__ = type


try:
    from jinja2.filters import pass_environment
except ImportError:
    from jinja2.filters import environmentfilter as pass_environment

try:
    import netaddr

    HAS_NETADDR = True
except ImportError:
    # in this case, we'll make the filters return error messages (see bottom)
    HAS_NETADDR = False
else:

    class mac_linux(netaddr.mac_unix):
        pass

    mac_linux.word_fmt = "%.2x"

DOCUMENTATION = """
    name: ipsubnet
    author: Ashwini Mhatre (@amhatre)
    version_added: "2.5.0"
    short_description: This filter can be used to manipulate network subnets in several ways.
    description:
        - This filter can be used to manipulate network subnets in several ways.
    options:
        value:
            description:
            - subnets or individual address or any other values input for ipsubnet plugin
            type: str
            required: True
        query:
            description: |
                You can provide query as 1st argument.
                To check if a given string is a subnet, pass it through the filter without any arguments. If the given
                string is an IP address, it will be converted into a subnet.
                If you specify a subnet size as the first parameter of the ipsubnet() filter, and the subnet size is
                smaller than the current one, you will get the number of subnets a given subnet can be split into.
            type: str
            default: ''
        index:
            description: |
                The second argument of the ipsubnet() filter is an index number; by specifying it you can get a new subnet
                with the specified index.
            type: str
    notes:
"""

EXAMPLES = r"""
#### examples
# Ipsubnet filter plugin with different queries.
vars:
    address: '192.168.144.5'
    subnet: '192.168.0.0/16'
tasks:
      # If the given string is an IP address, it will be converted into a subnet.
      - name: convert IP address to subnet
        debug:
          msg: "{{ address | ansible.utils.ipsubnet }}"

      # check if a given string is a subnet
      - name: check if a given string is a subnet
        debug:
          msg: "{{ subnet | ansible.utils.ipsubnet }}"

      # Get the number of subnets a given subnet can be split into.
      - name: Get the number of subnets a given subnet can be split into.
        debug:
          msg: "{{ subnet | ansible.utils.ipsubnet(20) }}"

      # Get a new subnet with the specified index.
      - name: Get a 1st subnet
        debug:
          msg: "{{ subnet | ansible.utils.ipsubnet(20, 0) }}"

      # Get a new subnet with the specified index.
      - name: Get a last subnet
        debug:
          msg: "{{ subnet | ansible.utils.ipsubnet(20, -1) }}"

      # If you specify an IP address instead of a subnet, and give a subnet size as the first argument, the ipsubnet() |
      # filter will instead return the biggest subnet that contains that given IP address.
      - name: Get biggest subnet that contains that given IP address.
        debug:
          msg: "{{ address | ansible.utils.ipsubnet(20) }}"

      # Get smaller and smaller subnets by specifying an index number as a second argument
      - name: Get 1st smaller subnet by specifying 0 as index number
        debug:
          msg: "{{ address | ansible.utils.ipsubnet(18, 0) }}"

      # Get smaller and smaller subnets by specifying an index number as a second argument
      - name: Get last subnet
        debug:
          msg: "{{ address | ansible.utils.ipsubnet(18, -1) }}"

      # By specifying another subnet as a second argument, if the second subnet includes the first, you can determine |
      # the rank of the first subnet in the second.
      - name: The rank of the IP in the subnet (the IP is the 36870nth /32 of the subnet)
        debug:
          msg: "{{ address | ansible.utils.ipsubnet(subnet) }}"

      # By specifying another subnet as a second argument, if the second subnet includes the first, you can determine |
      # the rank of the first subnet in the second.
      - name:  The rank in the /24 that contain the address
        debug:
          msg: "{{ address | ansible.utils.ipsubnet('192.168.144.0/24') }}"

      # By specifying another subnet as a second argument, if the second subnet includes the first, you can determine |
      # the rank of the first subnet in the second.
      - name:  An IP with the subnet in the first /30 in a /24
        debug:
          msg: "{{ '192.168.144.1/30' | ansible.utils.ipsubnet('192.168.144.0/24') }}"

      # By specifying another subnet as a second argument, if the second subnet includes the first, you can determine |
      # the rank of the first subnet in the second.
      - name: he fifth subnet /30 in a /24
        debug:
          msg: "{{ '192.168.144.16/30' | ansible.utils.ipsubnet('192.168.144.0/24') }}"


# PLAY [Ipsubnet filter plugin with different queries.] ****************************************************************
# TASK [convert IP address to subnet] *************************************************************************
# task path: /Users/amhatre/ansible-collections/playbooks/test_ipsubnet.yaml:10
# Loading collection ansible.utils from /Users/amhatre/ansible-collections/collections/ansible_collections/ansible/utils
# ok: [localhost] => {
#     "msg": "192.168.144.5/32"
# }
#
# TASK [check if a given string is a subnet] ******************************************************************
# task path: /Users/amhatre/ansible-collections/playbooks/test_ipsubnet.yaml:15
# Loading collection ansible.utils from /Users/amhatre/ansible-collections/collections/ansible_collections/ansible/utils
# ok: [localhost] => {
#     "msg": "192.168.0.0/16"
# }
#
# TASK [Get the number of subnets a given subnet can be split into.] ******************************************
# task path: /Users/amhatre/ansible-collections/playbooks/test_ipsubnet.yaml:20
# Loading collection ansible.utils from /Users/amhatre/ansible-collections/collections/ansible_collections/ansible/utils
# ok: [localhost] => {
#     "msg": "16"
# }
#
# TASK [Get a 1st subnet] *************************************************************************************
# task path: /Users/amhatre/ansible-collections/playbooks/test_ipsubnet.yaml:25
# Loading collection ansible.utils from /Users/amhatre/ansible-collections/collections/ansible_collections/ansible/utils
# ok: [localhost] => {
#     "msg": "192.168.0.0/20"
# }
#
# TASK [Get a last subnet] ************************************************************************************
# task path: /Users/amhatre/ansible-collections/playbooks/test_ipsubnet.yaml:30
# Loading collection ansible.utils from /Users/amhatre/ansible-collections/collections/ansible_collections/ansible/utils
# ok: [localhost] => {
#     "msg": "192.168.240.0/20"
# }
#
# TASK [Get biggest subnet that contains that given IP address.] **********************************************
# task path: /Users/amhatre/ansible-collections/playbooks/test_ipsubnet.yaml:35
# Loading collection ansible.utils from /Users/amhatre/ansible-collections/collections/ansible_collections/ansible/utils
# ok: [localhost] => {
#     "msg": "192.168.144.0/20"
# }
#
# TASK [Get 1st smaller subnet by specifying 0 as index number] ***********************************************
# task path: /Users/amhatre/ansible-collections/playbooks/test_ipsubnet.yaml:40
# Loading collection ansible.utils from /Users/amhatre/ansible-collections/collections/ansible_collections/ansible/utils
# ok: [localhost] => {
#     "msg": "192.168.128.0/18"
# }
#
# TASK [Get last subnet] **************************************************************************************
# task path: /Users/amhatre/ansible-collections/playbooks/test_ipsubnet.yaml:45
# Loading collection ansible.utils from /Users/amhatre/ansible-collections/collections/ansible_collections/ansible/utils
# ok: [localhost] => {
#     "msg": "192.168.144.4/31"
# }
#
# TASK [The rank of the IP in the subnet (the IP is the 36870nth /32 of the subnet)] **************************
# task path: /Users/amhatre/ansible-collections/playbooks/test_ipsubnet.yaml:50
# Loading collection ansible.utils from /Users/amhatre/ansible-collections/collections/ansible_collections/ansible/utils
# ok: [localhost] => {
#     "msg": "36870"
# }
#
# TASK [The rank in the /24 that contain the address] *********************************************************
# task path: /Users/amhatre/ansible-collections/playbooks/test_ipsubnet.yaml:55
# Loading collection ansible.utils from /Users/amhatre/ansible-collections/collections/ansible_collections/ansible/utils
# ok: [localhost] => {
#     "msg": "6"
# }
#
# TASK [An IP with the subnet in the first /30 in a /24] ******************************************************
# task path: /Users/amhatre/ansible-collections/playbooks/test_ipsubnet.yaml:60
# Loading collection ansible.utils from /Users/amhatre/ansible-collections/collections/ansible_collections/ansible/utils
# ok: [localhost] => {
#     "msg": "1"
# }
#
# TASK [he fifth subnet /30 in a /24] *************************************************************************
# task path: /Users/amhatre/ansible-collections/playbooks/test_ipsubnet.yaml:65
# Loading collection ansible.utils from /Users/amhatre/ansible-collections/collections/ansible_collections/ansible/utils
# ok: [localhost] => {
#     "msg": "5"
# }

"""

RETURN = """
  data:
    type: raw
    description:
      - Returns values valid for a particular query.
"""


@pass_environment
def _ipsubnet(*args, **kwargs):
    """Manipulate IPv4/IPv6 subnets"""
    keys = ["value", "query", "index"]
    data = dict(zip(keys, args[1:]))
    data.update(kwargs)
    aav = AnsibleArgSpecValidator(data=data, schema=DOCUMENTATION, name="ipsubnet")
    valid, errors, updated_data = aav.validate()
    if not valid:
        raise AnsibleFilterError(errors)
    return ipsubnet(**updated_data)


def ipsubnet(value, query="", index="x"):
    """Manipulate IPv4/IPv6 subnets"""

    try:
        vtype = ipaddr(value, "type")
        if vtype == "address":
            v = ipaddr(value, "cidr")
        elif vtype == "network":
            v = ipaddr(value, "subnet")

        value = netaddr.IPNetwork(v)
    except Exception:
        return False
    query_string = str(query)
    if not query:
        return str(value)

    elif query_string.isdigit():
        vsize = ipaddr(v, "size")
        query = int(query)

        try:
            float(index)
            index = int(index)

            if vsize > 1:
                try:
                    return str(list(value.subnet(query))[index])
                except Exception:
                    return False

            elif vsize == 1:
                try:
                    return str(value.supernet(query)[index])
                except Exception:
                    return False

        except Exception:
            if vsize > 1:
                try:
                    return str(len(list(value.subnet(query))))
                except Exception:
                    return False

            elif vsize == 1:
                try:
                    return str(value.supernet(query)[0])
                except Exception:
                    return False

    elif query_string:
        vtype = ipaddr(query, "type")
        if vtype == "address":
            v = ipaddr(query, "cidr")
        elif vtype == "network":
            v = ipaddr(query, "subnet")
        else:
            msg = "You must pass a valid subnet or IP address; {0} is invalid".format(query_string)
            raise AnsibleFilterError(msg)
        query = netaddr.IPNetwork(v)
        for i, subnet in enumerate(query.subnet(value.prefixlen), 1):
            if subnet == value:
                return str(i)
        msg = "{0} is not in the subnet {1}".format(value.cidr, query.cidr)
        raise AnsibleFilterError(msg)
    return False


class FilterModule(object):
    """IP address and network manipulation filters"""

    filter_map = {
        # IP addresses and networks
        "ipsubnet": _ipsubnet,
    }

    def filters(self):
        """ipsubnet filter"""
        if HAS_NETADDR:
            return self.filter_map
        else:
            return dict((f, partial(_need_netaddr, f)) for f in self.filter_map)
