from cloudify.workflows import ctx
from cloudify.decorators import workflow
import paramiko


def exec_command(username,password, command):

    fortigate_host_ip = ctx.instance.host_ip
    ctx.logger.info('HOST_IP: {0}'.format(ctx.instance.host_ip))

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(fortigate_host_ip, username=username,password=password)

    stdin, stdout, stderr = ssh.exec_command(command)
    ctx.logger.info('Exit status >> {0}'.format(stdout.channel.recv_exit_status()))

    ssh.close



@workflow
def create_policy(username, password, policyId, policyName, srcintf, dstintf, action, serviceName, **kwargs):

    ctx.logger.info('Start FW policy configuration....')

    for node in ctx.nodes:
        ctx.logger.info("node.id {0}".format(node.id))

        # if node.id == 'Fortigate':
            # instance_node = ctx.get_node_instance(node.id)
            # ctx.logger.info('instance_node >>>> : {0}'.format(instance_node))
            #instance_node_host = ctx.get_node_instance(instance_node._node_instance.host_id)
#           for instance in node.instances:
            #ctx.logger.info('HOST_IP: {0}'.format(instance_node_host))

    command = \
        'config firewall policy\n' \
        '  edit %s\n' \
        '    set name %s\n' \
        '    set srcintf %s\n' \
        '    set dstintf %s\n' \
        '    set srcaddr all\n' \
        '    set dstaddr all\n' \
        '    set action %s\n' \
        '    set schedule always\n' \
        '    set service \"%s\"\n' \
        'end' % (policyId, policyName, srcintf, dstintf, action, serviceName)

    ctx.logger.info('Execute Command >> \n {0}'.format(command))

#    exec_command(username,password,command)


@workflow
def create_service(username, password, protocol, portrange, serviceName, **kwargs):

    ctx.logger.info('Start FW service creation....')

    for node in ctx.nodes:
        ctx.logger.info("node.id {0}".format(node.id))
        # if node.id == 'Fortigate':
        # if node.id == 'fortigate_ip':
        #     instance_node = ctx.get_node_instance(node.id)
        #     ctx.logger.info('instance_node: {0}'.format(instance_node))
#            instance_node_host = ctx.get_node_instance(instance_node._node_instance.host_id)
#            for instance in node.instances:
#            ctx.logger.info('HOST_IP: {0}'.format(instance_node_host))

    command = \
        'config firewall service custom\n' \
        '   edit %s\n' \
        '       set protocol \"%s\"\n' \
        '       set tcp-portrange %s\n' \
        'end' % (serviceName, protocol, portrange)

    ctx.logger.info('Execute Command >> \n {0}'.format(command))

#    exec_command(username,password,command)

