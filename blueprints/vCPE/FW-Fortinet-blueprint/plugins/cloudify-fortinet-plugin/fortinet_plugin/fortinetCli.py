import paramiko

forti_username = 'admin'
forti_password = ''
fortinet_host_ip = '185.98.148.48'
port_id = 2
port_alias = 'portInB'


def exec_command(command, fortinet_host_ip):

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(fortinet_host_ip, username=forti_username,password=forti_password)

    print ("Execute Command >> \n {0}".format(command))

    stdin, stdout, stderr = ssh.exec_command(command)

    print stdout.channel.recv_exit_status()

#   type(stdin)
#    stdout.readlines()
#    stderr.readlines()

    ssh.close

def set_port(fortinet_host_ip, port_id, port_alias):

    command = \
        'config system interface\n' \
        '  edit port%s\n' \
        '    set mode dhcp\n' \
        '    set alias %s\n' \
        '    set allowaccess ping snmp\n' \
        'end' % (port_id, port_alias )

    exec_command(command, fortinet_host_ip)

def set_policy(fortinet_host_ip ):

    command = \
        'config firewall policy\n' \
        '  edit 2\n' \
        '    set name \"WebDef\"\n' \
        '    set srcintf \"port2\"\n' \
        '    set dstintf \"port3\"\n' \
        '    set srcaddr \"all\"\n' \
        '    set dstaddr \"all\"\n' \
        '    set action accept\n' \
        '    set schedule \"always\"\n' \
        '    set service \"Web Access\"\n' \
        'end'

    exec_command(command, fortinet_host_ip)


set_port(fortinet_host_ip, port_id, port_alias)
#set_policy(fortinet_host_ip)
