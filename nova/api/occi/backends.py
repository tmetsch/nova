# vim: tabstop=4 shiftwidth=4 softtabstop=4

#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from nova import log as logging
from occi.backend import ActionBackend, KindBackend, MixinBackend
from occi.extensions.infrastructure import START, STOP, SUSPEND, RESTART, UP, \
    DOWN, ONLINE, BACKUP, SNAPSHOT, RESIZE, OFFLINE, NETWORK, NETWORKINTERFACE


LOG = logging.getLogger('nova.api.occi.backends')


class MyBackend(KindBackend, ActionBackend):
    '''
    An very simple abstract backend which handles update and replace for
    attributes. Support for links and mixins would need to added.
    '''

    def update(self, old, new):
        # here you can check what information from new_entity you wanna bring
        # into old_entity

        # trigger your hypervisor and push most recent information
        print('Updating a resource with id: ' + old.identifier)
        for item in new.attributes.keys():
            old.attributes[item] = new.attributes[item]

    def replace(self, old, new):
        print('Replacing a resource with id: ' + old.identifier)
        old.attributes = {}
        for item in new.attributes.keys():
            old.attributes[item] = new.attributes[item]
        old.attributes['occi.compute.state'] = 'inactive'


class ComputeBackend(MyBackend):
    '''
    A Backend for compute instances.
    '''

    def create(self, entity):
        # e.g. check if all needed attributes are defined...

        # adding some default dummy values:
        if 'occi.compute.hostname' not in entity.attributes:
            entity.attributes['occi.compute.hostname'] = 'dummy'
        if 'occi.compute.memory' not in entity.attributes:
            entity.attributes['occi.compute.memory'] = '2'
        # rest is set by SERVICE provider...
        entity.attributes['occi.compute.architecture'] = 'x86'
        entity.attributes['occi.compute.cores'] = '2'
        entity.attributes['occi.compute.speed'] = '1'

        # trigger your management framework to start the compute instance...
        entity.attributes['occi.compute.state'] = 'inactive'
        entity.actions = [START]

        print('Creating the virtual machine with id: ' + entity.identifier)

    def retrieve(self, entity):
        # trigger your management framework to get most up to date information

        # add up to date actions...
        if entity.attributes['occi.compute.state'] == 'inactive':
            entity.actions = [START]
        if entity.attributes['occi.compute.state'] == 'active':
            entity.actions = [STOP, SUSPEND, RESTART]
        if entity.attributes['occi.compute.state'] == 'suspended':
            entity.actions = [START]

    def delete(self, entity):
        # call the management framework to delete this compute instance...
        print('Removing representation of virtual machine with id: '
              + entity.identifier)

    def action(self, entity, action):
        if action not in entity.actions:
            raise AttributeError("This action is currently no applicable.")
        elif action == START:
            entity.attributes['occi.compute.state'] = 'active'
            # read attributes from action and do something with it :-)
            print('Starting virtual machine with id' + entity.identifier)
        elif action == STOP:
            entity.attributes['occi.compute.state'] = 'inactive'
            # read attributes from action and do something with it :-)
            print('Stopping virtual machine with id' + entity.identifier)
        elif action == RESTART:
            entity.attributes['occi.compute.state'] = 'active'
            # read attributes from action and do something with it :-)
            print('Restarting virtual machine with id' + entity.identifier)
        elif action == SUSPEND:
            entity.attributes['occi.compute.state'] = 'suspended'
            # read attributes from action and do something with it :-)
            print('Suspending virtual machine with id' + entity.identifier)


class NetworkBackend(MyBackend):
    '''
    Backend to handle network resources.
    '''

    def create(self, entity):
        # create a VNIC...
        entity.attributes['occi.network.vlan'] = '1'
        entity.attributes['occi.network.label'] = 'dummy interface'
        entity.attributes['occi.network.state'] = 'inactive'
        entity.actions = [UP]
        print('Creating a VNIC')

    def retrieve(self, entity):
        # update a VNIC
        if entity.attributes['occi.network.state'] == 'active':
            entity.actions = [DOWN]
        elif entity.attributes['occi.network.state'] == 'inactive':
            entity.actions = [UP]

    def delete(self, entity):
        # and deactivate it
        print('Removing representation of a VNIC with id:' + entity.identifier)

    def action(self, entity, action):
        if action not in entity.actions:
            raise AttributeError("This action is currently no applicable.")
        elif action.kind == UP:
            entity.attributes['occi.network.state'] = 'active'
            # read attributes from action and do something with it :-)
            print('Starting VNIC with id: ' + entity.identifier)
        elif action.kind == DOWN:
            entity.attributes['occi.network.state'] = 'inactive'
            # read attributes from action and do something with it :-)
            print('Stopping VNIC with id: ' + entity.identifier)


class StorageBackend(MyBackend):
    '''
    Backend to handle storage resources.
    '''

    def create(self, entity):
        # create a storage container here!

        entity.attributes['occi.storage.size'] = '1'
        entity.attributes['occi.storage.state'] = 'offline'
        entity.actions = [ONLINE]
        print('Creating a storage device')

    def retrieve(self, entity):
        # check the state and return it!

        if entity.attributes['occi.storage.state'] == 'offline':
            entity.actions = [ONLINE]
        if entity.attributes['occi.storage.state'] == 'online':
            entity.actions = [BACKUP, SNAPSHOT, RESIZE]

    def delete(self, entity):
        # call the management framework to delete this storage instance...
        print('Removing storage device with id: ' + entity.identifier)

    def action(self, entity, action):
        if action not in entity.actions:
            raise AttributeError("This action is currently no applicable.")
        elif action == ONLINE:
            entity.attributes['occi.storage.state'] = 'online'
            # read attributes from action and do something with it :-)
            print('Bringing up storage with id: ' + entity.identifier)
        elif action == OFFLINE:
            entity.attributes['occi.storage.state'] = 'offline'
            # read attributes from action and do something with it :-)
            print('Bringing down storage with id: ' + entity.identifier)
        elif action == BACKUP:
            print('Backing up...storage resource with id: '
                  + entity.identifier)
        elif action == SNAPSHOT:
            print('Snapshoting...storage resource with id: '
                  + entity.identifier)
        elif action == RESIZE:
            print('Resizing...storage resource with id: ' + entity.identifier)


class IpNetworkBackend(MixinBackend):
    '''
    A mixin backend for the IPnetworking.
    '''

    def create(self, entity):
        if not entity.kind == NETWORK:
            raise AttributeError('This mixin cannot be applied to this kind.')
        entity.attributes['occi.network.allocation'] = 'dynamic'
        entity.attributes['occi.network.gateway'] = '10.0.0.1'
        entity.attributes['occi.network.address'] = '10.0.0.1/24'

    def delete(self, entity):
        entity.attributes.pop('occi.network.allocation')
        entity.attributes.pop('occi.network.gateway')
        entity.attributes.pop('occi.network.address')


class IpNetworkInterfaceBackend(MixinBackend):
    '''
    A mixin backend for the IPnetowkringinterface.
    '''

    def create(self, entity):
        if not entity.kind == NETWORKINTERFACE:
            raise AttributeError('This mixin cannot be applied to this kind.')
        entity.attributes['occi.networkinterface.address'] = '10.0.0.65'
        entity.attributes['occi.networkinterface.gateway'] = '10.0.0.1'
        entity.attributes['occi.networkinterface.allocation'] = 'dynamic'

    def delete(self, entity):
        entity.attributes.pop('occi.networkinterface.address')
        entity.attributes.pop('occi.networkinterface.gateway')
        entity.attributes.pop('occi.networkinterface.allocation')


class StorageLinkBackend(KindBackend):
    '''
    A backend for the storage links.
    '''

    def create(self, entity):
        entity.attributes['occi.storagelink.deviceid'] = 'sda1'
        entity.attributes['occi.storagelink.mountpoint'] = '/'
        entity.attributes['occi.storagelink.state'] = 'mounted'

    def delete(self, entity):
        entity.attributes.pop('occi.storagelink.deviceid')
        entity.attributes.pop('occi.storagelink.mountpoint')
        entity.attributes.pop('occi.storagelink.state')


class NetworkInterfaceBackend(KindBackend):
    '''
    A backend for the network links.
    '''

    def create(self, link):
        link.attributes['occi.networkinterface.state'] = 'up'
        link.attributes['occi.networkinterface.mac'] = 'aa:bb:cc:dd:ee:ff'
        link.attributes['occi.networkinterface.interface'] = 'eth0'

    def delete(self, link):
        link.attributes.pop('occi.networkinterface.state')
        link.attributes.pop('occi.networkinterface.mac')
        link.attributes.pop('occi.networkinterface.interface')
