import paramiko
from cloudify.decorators import operation
from cloudify.state import ctx_parameters as inputs

forti_username = 'admin'
forti_password = ''
portMask = '255.255.255.0'


@operation
def port_config(ctx, **kwargs):
    ctx.logger.info('Start port config task....')
    port_id = 2  # port 1 reserved for admin

    host_id = get_host_id(ctx)
    fortinet_host_ip = ctx._endpoint.get_host_node_instance_ip(host_id=host_id)
    ctx.logger.info('fortinet host ip : {0}'.format(fortinet_host_ip))

    for relationship in ctx.instance.relationships:
        ctx.logger.info('RELATIONSHIP type : {0}'.format(relationship.type))

        if 'connected_to' in relationship.type:

#            port_alias = relationship.target.node.name
#            ctx.logger.info('RELATIONSHIP target node name: {0}'.format(port_alias))
#            target_ip = relationship.target.instance.runtime_properties['fixed_ip_address']
#            ctx.logger.info('TARGET IP target_ip : {0}'.format(target_ip))

            set_port(ctx, fortinet_host_ip, port_id)

            port_id += 1


def set_port(ctx, fortinet_host_ip, port_id):

    ctx.logger.info('Configure fw port ....')

    command = \
        'config system interface\n' \
        '  edit port%s\n' \
        '    set mode dhcp\n' \
        '    set allowaccess ping snmp\n' \
        '  next\n' \
        'end' % (port_id )

    exec_command(ctx, command, fortinet_host_ip)


# @operation
# def fw_config(ctx, **kwargs):
#     ctx.logger.info('Start fw configuration....')
#
#     fortinet_host_ip = get_host_ip(ctx)
#     ctx.logger.info('Fortinet_host_ip: {0}'.format(fortinet_host_ip))
#
#     set_policy(ctx, fortinet_host_ip)


# def set_policy(ctx, fortinet_host_ip) :
#
#     gateway = '172.30.0.1'
#     subnet = '172.30.0.0'
#
#     command = \
#         'config router static\n' \
#         '   edit 1\n' \
#         '     set dst  0.0.0.0/24\n' \
#         '     set gateway  %s\n' \
#         '     set device port2\n' \
#         'end' % gateway
#
#     exec_command(ctx, command, fortinet_host_ip)
#
#     command = \
#         'config firewall address\n' \
#         '   edit rule1\n' \
#         '       set subnet %s/24\n' \
#         '       set associated-interface port2\n' \
#         'end' % subnet
#
#     exec_command(ctx, command, fortinet_host_ip)
#
#     command = \
#         'config firewall service custom\n' \
#         '   edit firewallServer\n' \
#         '       set protocol "TCP"\n' \
#         '       set tcp-portrange 50-1000\n' \
#         'end'
#
#     exec_command(ctx, command, fortinet_host_ip)
#
#     command = \
#         'config firewall policy\n' \
#         '  edit 1\n' \
#         '    set srcintf \"port2\"\n' \
#         '    set dstintf \"port3\"\n' \
#         '    set srcaddr \"all\"\n' \
#         '    set dstaddr \"all\"\n' \
#         '    set action accept\n' \
#         '    set schedule \"always\"\n' \
#         '    set service \"firewallServer\"\n' \
#         '  next\n' \
#         'end'
#
#     exec_command(ctx, command, fortinet_host_ip)


def exec_command(ctx, command, fortinet_host_ip):

    ctx.logger.info('Open connection to host {0} '.format(fortinet_host_ip))

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(fortinet_host_ip, username='admin',password='')

    ctx.logger.info("Execute Command >> \n {0}".format(command))

    stdin, stdout, stderr = ssh.exec_command(command)
    type(stdin)
    stdout.readlines()







# @operation
# def route_config(ctx, **kwargs):
#     ctx.logger.info('Start route task....')
#
#     fortinet_host_ip = get_host_ip(ctx)
#     ctx.logger.info('Fortinet_host_ip: {0}'.format(fortinet_host_ip))
#
#     target_ip = '0.0.0.0'
#
# # if relationship is attached get the ip
#
#     for relationship in ctx.instance.relationships:
#         if 'connected_to' in relationship.type:
# #            target_ip = relationship.target.instance.runtime_properties['fixed_ip_address']
#             target_ip = relationship.target.instance.runtime_properties['fixed_ip']
#
#     gateway = inputs['gateway']
#     port_id = 3
#     portMask = '0.0.0.0'
#
#     set_route(ctx, fortinet_host_ip, gateway, target_ip, portMask, port_id)
#
#
# def set_route(ctx, fortinet_host_ip, gateway, target_ip, portMask, port_id):
#
#     command = \
#         'config router static\n' \
#         '  edit 1\n' \
#         '    set dst %s %s\n' \
#         '    set gateway %s\n' \
#         '    set device port%s\n' \
#         '  next\n' \
#         'end' % (target_ip, portMask, gateway, port_id)
#
#     exec_command(ctx, command, fortinet_host_ip)
#
#
# def set_license(ctx, fortinet_host_ip):
#
#     ftp_server = '10.0.1.27'
#     ftp_username = ''
#     ftp_password = ''
#     license_file_name = ''
#
#     command = \
#         'restore vmlicense ftp %s %s:27 %s $s\n' % (license_file_name, ftp_server, ftp_username, ftp_password)
#
#     exec_command(ctx, command, fortinet_host_ip)
#
# # Validate license
#
#     command = \
#         'configure system central-management\n' \
#         'set type fortimanager\n' \
#         'set fmg X.X.X.X\n' \
#         'set include-default-servers disable\n'
#
#     exec_command(ctx, command, fortinet_host_ip)


def get_host_ip(ctx):
    for relationship in ctx.instance.relationships:
        if 'contained_in' in relationship.type:
            return relationship.target.instance.runtime_properties['ip']


def get_host_id(ctx):
    ctx.instance._get_node_instance_if_needed()
    return ctx.instance._node_instance.host_id

