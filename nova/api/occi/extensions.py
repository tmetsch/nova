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

from nova import flags, log
from occi import backend, core_model
from occi.extensions import infrastructure


#Hi I'm a logger, use me! :-)
LOG = log.getLogger('nova.api.occi.extensions')

FLAGS = flags.FLAGS

#OS action extensions
OS_CHG_PWD = core_model.Action(
                'http://schemas.openstack.org/instance/action#',
                 'chg_pwd', 'Removes all data on the server and replaces' + \
                                     'it with the specified image (via Mixin).',
                 {'method': ''})

OS_REBUILD = core_model.Action(
                'http://schemas.openstack.org/instance/action#',
                 'rebuild', 'Removes all data on the server and replaces \
                                 it with the specified image (via Mixin).',
                 {'method': ''})
OS_REVERT_RESIZE = core_model.Action(
                'http://schemas.openstack.org/instance/action#',
                 'revert_resize', 'Revert the resize and roll back to \
                                                     the original server',
                 {'method': ''})
OS_CONFIRM_RESIZE = core_model.Action(
                'http://schemas.openstack.org/instance/action#',
                 'confirm_resize', 'Use this to confirm the resize action',
                 {'method': ''})

# Trusted Compute Pool technology mixin definition
TCP_ATTRIBUTES = {'eu.fi-ware.compute.tcp': ''}
TCP = core_model.Mixin(\
    'http://schemas.fi-ware.eu/occi/infrastructure/compute#',
    'tcp', attributes=TCP_ATTRIBUTES)


class TCPBackend(backend.MixinBackend):
    '''
    Trusted Compute Pool technology mixin backend handler
    '''
    def create(self, entity, extras):
        if not entity.kind == infrastructure.COMPUTE:
            raise AttributeError('This mixin cannot be applied to this kind.')
        entity.attributes['eu.fi-ware.compute.tcp'] = 'true'

    def delete(self, entity, extras):
        entity.attributes.pop('eu.fi-ware.compute.tcp')


class OsTemplate(core_model.Mixin):
    '''
    Represents the OS Template mechanism as per OCCI specification.
    An OS template is equivocal to an image in OpenStack
    '''
    def __init__(self, scheme, term, os_id, related=None, actions=None,
                 title='', attributes=None, location=None):
        super(OsTemplate, self).__init__(scheme, term, related, actions,
                                         title, attributes, location)
        self.os_id = os_id


class ResourceTemplate(core_model.Mixin):
    '''
    Represents the Resource Template mechanism as per OCCI specification.
    An Resource template is equivocal to a flavor in OpenStack.
    '''

    pass