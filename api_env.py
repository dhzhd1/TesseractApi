# -*- coding: utf-8 -*-

# Description: this file contains all of the constant of the api
import logging

request_arguments = ['login_user', 'login_pass', 'registry_srv', 'keyword', 'repo_name', 'image_name', 'image_tag',
                     'image_id', 'force', 'save_path', 'load_path', 'tarball_name', 'changes', 'all', 'command',
                     'hostname', 'user', 'detach', 'stdin_open', 'tty', 'ports', 'environment', 'volumes',
                     'network_disabled', 'name', 'entrypoint', 'working_dir', 'domainname', 'host_config',
                     'mac_address', 'labels', 'stop_signal', 'networking_config', 'healthcheck', 'stop_timeout',
                     'runtime']
api_log = './logs/api.log'
docker_op_log = './logs/docker.log'
logging_level = logging.DEBUG
docker_host_list =['unix:///var/run/docker.sock']