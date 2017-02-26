from cloudify.workflows import ctx
from cloudify.decorators import workflow
from cloudify.decorators import operation
from cloudify.state import ctx_parameters as inputs
import re
import urllib
import requests
requests.packages.urllib3.disable_warnings()  # Surpress "InsecureRequestWarning" warning


@workflow
def load_configuration(filename, **kwargs):

    ctx.logger.info('Loading Configuration File....')

    vyatta_host_ip = get_host_ip(ctx)
    ctx.logger.info('vyatta_host_ip: {0}'.format(vyatta_host_ip))

    command = filename

#    exec_command(ctx, command, vyatta_host_ip)


@operation
def port_config(ctx, **kwargs):
    ctx.logger.info('Start port config task....')
    command = []
    port_idx = 4

    vyatta_host_ip = get_host_ip(ctx)
    ctx.logger.info('vyatta_host_ip: {0}'.format(vyatta_host_ip))

    for relationship in ctx.instance.relationships:
        ctx.logger.info('RELATIONSHIP type : {0}'.format(relationship.type))

        if 'connected_to' in relationship.type:
            target_ip = relationship.target.instance.runtime_properties['fixed_ip_address']
            ctx.logger.info('TARGET IP target_ip : {0}'.format(target_ip))
            cmd = 'set interfaces dataplane dp0s' + port_idx + ' description ' + relationship.target.node.name
            command.append(cmd)
            cmd = 'set interfaces dataplane dp0s' + port_idx + ' address ' + target_ip + '/24'
            command.append(cmd)
            port_idx = +1

        exec_command(ctx, command, vyatta_host_ip)


@operation
def route_policy_config(ctx, **kwargs):
    ctx.logger.info('Start route policy task....')
    command = []

    vyatta_host_ip = get_host_ip(ctx)
    ctx.logger.info('vyatta_host_ip: {0}'.format(vyatta_host_ip))

    # for relationship in ctx.instance.relationships:
    #     ctx.logger.info('RELATIONSHIP type : {0}'.format(relationship.type))
    #
    #     if 'connected_to' in relationship.type:
    #         target_ip = relationship.target.instance.runtime_properties['fixed_ip_address']
    #         ctx.logger.info('TARGET IP target_ip : {0}'.format(target_ip))
    #         cmd = 'set interfaces dataplane dp0s' + port_idx + ' description ' + relationship.target.node.name
    #         command.append(cmd)
    #         cmd = 'set interfaces dataplane dp0s' + port_idx + ' address ' + target_ip + '/24'
    #         command.append(cmd)
    #         port_idx = +1


    ### need to add ploicy here ....

    exec_command(ctx, command, vyatta_host_ip)


class VyattaControl(object):
    """
    Provides methods to show and modify Vyatta status and configurations.
    """

    def __init__(self, urlBase, user, passwd, ctx):

        self.urlBase = urlBase
# configuration API
        self.urlConfBase = urlBase + 'rest/conf'
# operation API
        self.urlOpBase = urlBase + 'rest/op'
        self.user = user
        self.passwd = passwd

    def getOpId(self, urlOpId, ctx):
        """
        Get the operation id, which is substring of the Location header in HTTP response.
        """

        rop = requests.post(urlOpId, auth=(self.user, self.passwd), verify=False)  # Request to get operation id
        return rop.headers['Location'].split('/')[2]  # Get Location header

    def getConfId(self, ctx):
        """
        Get the configuration id, which is substring of the Location header in HTTP response.
        """

        rconf = requests.post(self.urlConfBase, auth=(self.user, self.passwd), verify=False)
        return rconf.headers['Location'].split('/')[2]

    def deleteConfId(self, confId, ctx):
        """
        Delete existing Vyatta configuration session
        """

        urlConfDelete = self.urlConfBase + '/' + confId
        rdel = requests.delete(urlConfDelete, auth=(self.user, self.passwd), verify=False)
        return rdel.status_code

    def commandOperational(self, opCommands, ctx):
        """
        Call Vyatta operational mode commands from opCommands list.
        """
        for line in opCommands:
            urlOpCommand = self.urlOpBase + '/' + '/'.join(line.split(None))
            ropResult = requests.get(self.urlOpBase + '/' + self.getOpId(urlOpCommand),
                                     auth=(self.user, self.passwd),
                                     verify=False)  # Request to get the results

            ctx.logger.info('$ : {0}'.format(line))
            ctx.logger.info('{0}'.format(ropResult.text))

    def createEncodedUrl(self, confId, string, ctx):
        """
        URLencode every configuration words and form proper URL for REST API requests.
        :param confId: Configuration session ID
        :param string: One line Vyatta configuration commands and parameters
        :return: Encoded URL for Vyatta REST API
        """

        encodedWord = []
        for word in string.split():
            encodedWord.append(urllib.quote(word, safe=""))  # Encode each words, then make a list of words

        encodedUrl = self.urlConfBase + '/' + confId + '/' + '/'.join(' '.join(encodedWord).split(None))
        return encodedUrl

    def editConfig(self, config, ctx):
        """
        Read configurations from a LIST and send requests to Vyatta via REST API,
        then actually modify Vyatta configuration and commit configuration changes.
        """

        # Set configurations
        confId = self.getConfId()  # Get configuration ID

        for line in config:
            if not (re.compile("^#").match(line)
                    or re.compile("^$").match(line)):  # Skip line matches with "^#" or "^$"
                urlConfPut = self.createEncodedUrl(confId, line)
                rconf = requests.put(urlConfPut,
                                     auth=(self.user, self.passwd),
                                     verify=False)  # Request for configuration commands

                print("%s : %s" % (urlConfPut, rconf.status_code))

        # Commit configurations
        self.commitConfig(confId)

        # Save configurations
        self.saveConfig(confId)

        # Delete conf-id and return HTTP status code
        return self.deleteConfId(confId)

    def commitConfig(self, confId, ctx):
        """
        Commit configuration changes
        """

        urlConfCommit = self.urlConfBase + '/' + confId + '/commit'
        rconf = requests.post(urlConfCommit, auth=(self.user, self.passwd), verify=False)  # Request for commit
        ctx.logger.info('{0}  :  {1}'.format(urlConfCommit, rconf.status_code))
        return rconf.status_code

    def saveConfig(self, confId, ctx):
        """
         Save changes
        """
        urlConfSave = self.urlConfBase + '/' + confId + '/save'
        rconf = requests.post(urlConfSave, auth=(self.user, self.passwd), verify=False)  # Request for save
        ctx.logger.info('{0}  :  {1}'.format(urlConfSave, rconf.status_code))
        return rconf.status_code


def exec_command(ctx, command, vyatta_host_ip):

    ctx.logger.info('Open connection to host {0} '.format(vyatta_host_ip))

    vyatta_username = 'vyatta'
    vyatta_password = 'vyatta'
    urlBase = 'https://' + vyatta_host_ip + '/'

    vy = VyattaControl(ctx, urlBase, vyatta_username, vyatta_password)

    vy.editConfig(command)

    #vy.commandOperationalList(['show interfaces'])


def get_host_ip(ctx):
    for relationship in ctx.instance.relationships:
        if 'contained_in' in relationship.type:
            return relationship.target.instance.runtime_properties['ip']


def get_host_id(ctx):
    ctx.instance._get_node_instance_if_needed()
    return ctx.instance._node_instance.host_id
