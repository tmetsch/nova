'''
Created on Jan 11, 2012

@author: openstack
'''

from nova import context
from nova import test
from nova import flags
from nova import image
from nova import rpc

from nova.image import fake

from nova.api.occi.compute import computeresource
from nova.api.occi import extensions

from occi.core_model import Entity

from nova.scheduler import driver as scheduler_driver

FLAGS = flags.FLAGS

def rpc_cast_wrapper(context, topic, msg, do_cast=True):
    '''
    The RPC cast wrapper so scheduler returns instances...
    '''
    if topic == FLAGS.scheduler_topic and \
            msg['method'] == 'run_instance':
        request_spec = msg['args']['request_spec']
        scheduler = scheduler_driver.Scheduler
        num_instances = request_spec.get('num_instances', 1)
        instances = []
        for x in xrange(num_instances):
            instance = scheduler().create_instance_db_entry(
                    context, request_spec)
            encoded = scheduler_driver.encode_instance(instance)
            instances.append(encoded)
        return instances
    else:
        pass

def fake_get_image_service(context, image_href):
    '''
    Make sure fake image service is used.
    '''
    tmp = image.fake.FakeImageService(), image_href
    return tmp

def fake_show(meh, context, id):
    '''
    Returns a single image...
    '''
    return {'id': id,
            'container_format': 'ami',
            'properties': {
                           'kernel_id': 1,
                           'ramdisk_id': 1}
            }

class TestOcciWsgiApp(test.TestCase):

    def setUp(self):
        super(TestOcciWsgiApp, self).setUp()

        self.user_id = 'fake'
        self.project_id = 'fake'
        self.context = context.RequestContext(self.user_id,
                                              self.project_id,
                                              is_admin=True)

        # setup image service...
        self.stubs.Set(image, 'get_image_service', fake_get_image_service)
        self.stubs.Set(fake._FakeImageService, 'show', fake_show)
        self.stubs.Set(rpc, 'cast', rpc_cast_wrapper)

        # OCCI related setup
        self.os_template = extensions.OsTemplate('http://schemas.openstack.org/template/os#', 'foo', '1')
        self.resource_template = extensions.ResourceTemplate('http://schemas.openstack.org/template/resource#', 'm1.small')

        self.entity = Entity("123", 'A test entity', None, [self.os_template, self.resource_template])
        self.extras = {'nova_ctx': self.context}

        self.class_under_test = computeresource.ComputeBackend()

    #---------------------------------------------------------- Test for succes

    def test_create_for_success(self):
        '''
        Try to create an OCCI entity.
        '''
        self.class_under_test.create(self.entity, self.extras)

    def test_retrieve_for_success(self):
        self.fail('To be implemented...')

    def test_update_for_success(self):
        self.fail('To be implemented...')

    def test_replace_for_success(self):
        self.fail('To be implemented...')

    def test_delete_for_success(self):
        self.fail('To be implemented...')

    def test_action_for_success(self):
        self.fail('To be implemented...')

    #--------------------------------------------------------- Test for Failure

    def test_create_for_failure(self):
        self.fail('To be implemented...')

    def test_retrieve_for_failure(self):
        self.fail('To be implemented...')

    def test_update_for_failure(self):
        self.fail('To be implemented...')

    def test_replace_for_failure(self):
        self.fail('To be implemented...')

    def test_delete_for_failure(self):
        self.fail('To be implemented...')

    def test_action_for_failure(self):
        self.fail('To be implemented...')

    #---------------------------------------------------------- Test for Sanity

    def test_create_for_sanity(self):
        self.fail('To be implemented...')

    def test_retrieve_for_sanity(self):
        self.fail('To be implemented...')

    def test_update_for_sanity(self):
        self.fail('To be implemented...')

    def test_replace_for_sanity(self):
        self.fail('To be implemented...')

    def test_delete_for_sanity(self):
        self.fail('To be implemented...')

    def test_action_for_sanity(self):
        self.fail('To be implemented...')
