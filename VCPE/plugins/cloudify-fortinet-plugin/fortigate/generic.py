# #######
# Copyright (c) 2016 GigaSpaces Technologies Ltd. All rights reserved
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
#    * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    * See the License for the specific language governing permissions and
#    * limitations under the License.
'''
    Fortinet.FortiGate.Generic
    ~~~~~~~~~~~~~~~~~~~~~~~~~~
    Low-level functions
'''

from cloudify import ctx
from cloudify.exceptions import NonRecoverableError, RecoverableError
import fabric.api
import fabric.state
from fabric.exceptions import NetworkError, CommandTimeout

# pylint: disable=R0903


class Generic(object):
    '''
        Generic, low-level interface for interacting with a FortiGate
        device via SSH

    :param dict ssh_config:
        Key-value pair that get sent to `fabric.api.settings`
    '''
    def __init__(self, ssh_config):
        # Set the SSH configuration options
        self.ssh_config = ssh_config
        if not isinstance(self.ssh_config, dict):
            raise NonRecoverableError(
                'ssh_config is required to be of type dict')
        # Set SSH defaults
        if self.ssh_config.get('use_shell') is None:
            self.ssh_config['use_shell'] = False
        if self.ssh_config.get('always_use_pty') is None:
            self.ssh_config['always_use_pty'] = False
        if self.ssh_config.get('command_timeout') is None:
            self.ssh_config['command_timeout'] = 10

    def execute(self, command):
        '''
            Low-level method for executing SSH commands

        :param string command:
            SSH command to execute (passed directly to `fabric.api.run`)
        :rtype: fabric.operations._AttributeString
        returns: SSH stdout
        :raises: :exc:`cloudify.exceptions.RecoverableError`,
                 :exc:`cloudify.exceptions.NonRecoverableError`
        '''
        # Set Fabric DEBUG output
        fabric.state.output.debug = True
        # Execute the command
        ctx.logger.info('Executing {0}'.format(command))
        try:
            with fabric.api.settings(**self.ssh_config):
                return fabric.api.run(command)
        except NetworkError as ex:
            raise RecoverableError(ex)
        except CommandTimeout as ex:
            raise RecoverableError(ex)
