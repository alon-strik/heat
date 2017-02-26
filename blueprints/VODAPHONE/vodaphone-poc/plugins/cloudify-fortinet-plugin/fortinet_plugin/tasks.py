from pyFG import FortiOS
from cloudify.decorators import operation
from cloudify.state import ctx_parameters as inputs


forti_username = 'admin'
forti_password = 'admin'
portMask = '255.255.255.0'


@operation
def test(ctx, **kwargs):

    ctx.logger.info('Start test >>>>>>>>>')
    host_id = get_host_id(ctx)
    ctx.logger.info('host_id : {0}'.format(host_id))

    host_instance = ctx._endpoint.get_node_instance(host_id)
    host_node = ctx._endpoint.get_node(host_instance.node_id)
    ctx.logger.info('host_node : {0}'.format(host_node))


@operation
def port_config(ctx, **kwargs):
    ctx.logger.info('Start port config task....')
    port_id = 2  # port 1 reserved for admin

    fortinet_host_ip = get_host_ip(ctx)
    ctx.logger.info('Fortinet_host_ip: {0}'.format(fortinet_host_ip))

    for relationship in ctx.instance.relationships:
        ctx.logger.info('RELATIONSHIP type : {0}'.format(relationship.type))

        if 'connected_to' in relationship.type:
            port_alias = relationship.target.node.name
            ctx.logger.info('RELATIONSHIP target node name: {0}'.format(port_alias))

            target_ip = relationship.target.instance.runtime_properties['fixed_ip_address']
            ctx.logger.info('TARGET IP target_ip : {0}'.format(target_ip))

            set_port(ctx, fortinet_host_ip, target_ip, port_id, port_alias)
            port_id += 1


def set_port(ctx, fortinet_host_ip, target_ip, port_id, port_alias):
    ctx.logger.info('Configure fw port ....')

    command = \
        'config system interface\n' \
        '   edit port%s\n' \
        '       set mode static\n' \
        '       set allowaccess ping\n' \
        '       set alias %s\n' \
        '       set ip %s  %s\n' \
        '   next\n' \
        'end' % (port_id, port_alias, target_ip, portMask)

    exec_command(ctx, command, fortinet_host_ip)


@operation
def policy_config(ctx, **kwargs):
    ctx.logger.info('Start policy task....')

    fortinet_host_ip = get_host_ip(ctx)
    ctx.logger.info('Fortinet_host_ip: {0}'.format(fortinet_host_ip))

    set_policy(ctx, fortinet_host_ip)


def set_policy(ctx, fortinet_host_ip):

    command = \
        'config firewall policy\n' \
        '  edit 1\n' \
        '    set srcintf \"any\"\n' \
        '    set dstintf \"any\"\n' \
        '    set srcaddr \"all\"\n' \
        '    set dstaddr \"all\"\n' \
        '    set action accept\n' \
        '    set schedule \"always\"\n' \
        '    set service \"ALL\"\n' \
        '  next\n' \
        'end'

    exec_command(ctx, command, fortinet_host_ip)

@operation
def route_config(ctx, **kwargs):
    ctx.logger.info('Start route task....')

    fortinet_host_ip = get_host_ip(ctx)
    ctx.logger.info('Fortinet_host_ip: {0}'.format(fortinet_host_ip))

    target_ip = '0.0.0.0'

# if relationship is attached get the ip

    for relationship in ctx.instance.relationships:
        if 'connected_to' in relationship.type:
            target_ip = relationship.target.instance.runtime_properties['fixed_ip_address']

    gateway = inputs['gateway']
    port_id = 3
    portMask = '0.0.0.0'

    set_route(ctx, fortinet_host_ip, gateway, target_ip, portMask, port_id)


def set_route(ctx, fortinet_host_ip, gateway, target_ip, portMask, port_id):

    command = \
        'config router static\n' \
        '  edit 1\n' \
        '    set dst %s %s\n' \
        '    set gateway %s\n' \
        '    set device port%s\n' \
        '  next\n' \
        'end' % (target_ip, portMask, gateway, port_id)

    exec_command(ctx, command, fortinet_host_ip)


def exec_command(ctx, command, fortinet_host_ip):

    ctx.logger.info('Open connection to host {0} '.format(fortinet_host_ip))
    conn = FortiOS(fortinet_host_ip, username=forti_username, password=forti_password)
    conn.open()

    ctx.logger.info("Execute Command >> \n {0}".format(command))

    conn.execute_command(command)
    conn.close()


def get_host_ip(ctx):
    for relationship in ctx.instance.relationships:
        if 'contained_in' in relationship.type:
            return relationship.target.instance.runtime_properties['ip']


def get_host_id(ctx):
    ctx.instance._get_node_instance_if_needed()
    return ctx.instance._node_instance.host_id
