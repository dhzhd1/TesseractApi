# -*- coding: utf-8 -*-

import docker
from docker import APIClient, errors
import logging
from api_env import *
import time




class Docker:
	def __init__(self, base_url=None):
		self.handle = None
		self.connect_docker_daemon(base_url)


	def connect_docker_daemon(self, base_url=None):
		"""
		This method is used for connect local/remote docker host daemon
		:return: Return the docker operation handle for local host
		"""
		if base_url is None:
			base_url = 'unix:///var/run/docker.sock'
		try:
			self.handle = APIClient(base_url=base_url)
		except errors.APIError as e:
			print e.message
			global logging
			logging.error(str(e.message))


	def login_registry(self, login_user, login_pass, registry_srv=None):
		"""
		This method is used for log into docker registry server.
		:param login_user:  str: user name for login registry
		:param login_pass:  str: password for login registry
		:param registry_srv: str: uri for registry server address
		:return: result of login status for that registry
		"""
		login_status = self.handle.login(username=login_user, password=login_pass, registry=registry_srv)
		return login_status

	def get_docker_info(self):
		"""
		Get docker information
		:return: DICT string
		"""
		return self.handle.info()

	def get_image_list(self):
		"""
		Get all of the existing images list
		:return: DICT string for all of the images
		"""
		return self.handle.images()

	def public_image_search(self, keyword):
		"""
		get a result for searching the image from public/logged in registry
		:return:  DICT string of search result
		"""
		return self.handle.search(keyword)


	# TODO: get docker events implementation
	# def get_docker_events(self, since, until, filters, decode):
	# 	"""
	# 	get running docker service events
	# 	:return: DICT for service envents
	# 	"""
	# 	return self.handle.event()

	def get_disk_utils(self):
		"""
		get disk utilization for docker images
		:return: DICT of disk utilization
		"""
		return self.handle.df()

	def pull_image(self, name, tag=None, repo=None ):
		"""
		pull image from repository by repo/name:tag
		:param repo: String of repository(registry) name
		:param name: String of image name
		:param tag: String of tag name
		:return: DICT response
		"""
		if tag is None:
			tag = "latest"
		try:
			if repo is None:
				return self.handle.pull(name, tag=tag)
			else:
				return self.handle.pull(repo + "/" + name, tag)
		except errors.NotFound as e:
			return {'message': 'Image Not Found', 'status': 'failed'}

	def inspect_image(self, image_id):
		"""
		inspect an image
		:param image_id: String of docker image ID
		:return: DICT of inspecting results
		"""
		# TODO: will support image_id and "repo/name:tag" later
		return self.handle.inspect_image(image_id)

	def remove_image(self, image_id, force_remove=False):
		"""
		remove the specified image by image id
		:param image_id: String of Docker Image
		:param force_remove: True or False
		:return: DICT of result
		"""
		return self.handle.remove_image(image_id, force=force_remove)

	def tag_image(self, image, repository, force=False, tag=None):
		"""
		tag an image to new repository
		:param image: string of image id which to be tagged
		:param repository: string of new repository which image will be tag into
		:param tag: String new tag
		:param force: True or false
		:return: Boolean result of tag
		"""
		return self.handle.tag(image, repository, tag, force=force)

	def push_image(self, repository, tag=None, stream=False, auth_config=None):
		"""
		push image to new repository
		:param repository:  String for image to be push. Image ID or Repo/Name:tag
		:param tag: Tag for pushed image, if you don't need to change the tag, keep None.
		:param stream: by default is false stream the outpu as blocking generator
		:param auth_config: overrride the credential for login()
		:return: Result String or Generator(when use stream=True)
		"""
		if auth_config is None:
			return self.handle.push(repository, tag, stream=stream)
		else:
			return self.handle.pull(repository, tag, stream=stream, auth_config=auth_config)

	def save_image(self, image_name, save_path, tarball_name=None):
		"""
		save specified image to a tarball
		:param image_name: string of Image ID or "repository/image:tag"
		:param save_path:  string of path
		:param tarball_name: string of tarball name. If not specified it will use the image_name_datetime.tar
		:return: return status
		"""
		if tarball_name is None:
			tarball_name = image_name + "_" + str(time.time()).split('.')[0] + ".tar"
		try:
			img = self.handle.get_image(image_name)
			with open(save_path + '/' + tarball_name, 'w') as f:
				for chunk in img:
					f.write(chunk)
			return {"message": "Image {} saved at {}".format(image_name, save_path + "/" + tarball_name), "status": "succeed"}
		except Exception as e:
			return {"message": e.message, "status": "failed"}

	def load_image(self, tarball_name, repository, tag=None, changes=None):
		"""
		load image from local path or url load tarball image
		:param tarball_name:  string of full path of tarball image
		:param repository: string of full name of image name to be assign 'repo/name'
		:param tag: string of imported image. If set None, the tag will followed as the original image tag
		:return: return
		"""
		if repository is None or str(repository).strip() == "":
			repository = None
		if tag is None or str(tag).strip() == "":
			tag = None
		if changes is None or str(changes).strip() == "":
			changes = None
		return self.handle.import_image(tarball_name, repository=repository, tag=tag, changes=changes)

	def get_containers(self, all=False):
		"""
		get list of containers.
		:param all: by default is 'False'. It only shows the running containers. otherwise it shows all containers include the stop/exit ones.
		:return: return the dict of containers.
		"""
		# TODO: 'filter' function will be added later.
		return self.handle.containers(all=all)

	def new_container(self, args):
		"""
		create container according to the passed in parameters
		:param args: parameters dict
		:return:  return new container id
		"""
		result = self.handle.create_container(
			image=args.get('image'),
			command=args.get('command'),
			hostname=args.get('hostname'),
			user=args.get('user'),
			detach=False if args.get('detach') is None else args.get('detach'),
			stdin_open=False if args.get('stdin_open') is None else args.get('stdin_open'),
			tty=False if args.get('tty') is None else args.get('tty'),
			ports=args.get('ports'),
			environment=args.get('environment'),
			volumes=args.get('volumes'),
			network_disabled=False if args.get('network_disabled') is None else args.get('network_disabled'),
			name=args.get('name'),
			entrypoint=args.get('entrypoint'),
			working_dir=args.get('working_dir'),
			domainname=args.get('domainname'),
			host_config=args.get('host_config'),
			mac_address=args.get('mac_address'),
			labels=args.get('labels'),
			stop_signal=args.get('stop_signal'),
			networking_config=args.get('networking_config'),
			healthcheck=args.get('healthcheck'),
			stop_timeout=args.get('stop_timeout'),
			runtime=args.get('runtime')
		)
		return result

	def gen_host_conf(self,args):
		host_config = self.handle.create_host_config(
			# auto remove the container after it exited
			auto_remove=False if args.get('auto_remove') is None else args.get('auto_remove'),
			# volume binds  BOOL
			binds=args.get('binds'),
			# BlockIO weight relative device weight in form of : [{"Path":"device_path, "Weight": weight}] DICT
			blkio_weight_device=args.get('blkio_weight_device'),
			# Block IO weight, relative weight. accepts a weight value between 10 and 1000 INT
			blkio_weight=args.get('blkio_weight'),
			# Add kernel capabilities. eg. ['SYS_ADMIN', "MKNOD"]  str or List
			cap_add=args.get('cap_add'),
			# Drop kernel capabilities str or LIST
			cap_drop=args.get('cap_drop'),
			# The length of a CPU period in microseconds  INT
			cpu_period=args.get('cpu_period'),
			# Microseconds of CPU time that the container can get in a CPU period INT
			cpu_quota=args.get('cpu_quota'),
			# CPU shares (relative weight) INT
			cpu_shares=args.get('cpu_shares'),
			# CPUs in which to allow execution (0-3, 0, 1)  str
			cpuset_cpus=args.get('cpuset_cpus'),
			# Memory nodes (MEMs) in which to allow execution (0-3, 0,1). Only effecive on NUMA systems
			cpuset_mems=args.get('cpuset_mems'),
			# A list of cgroup rules to apply to the container LIST
			device_cgroup_rules=args.get('device_cgroup_rules'),
			# Limit read rate (bytes per sec) from a device in the form of : [{"Path":"device_path", "Rate":rate}]
			device_read_bps=args.get('device_read_bps'),
			# Limite read rate(IOPS) from a device
			device_read_iops=args.get('device_read_iops'),
			# Limit write rate (byte per sec) from a device.
			device_write_bps=args.get('device_write_bps'),
			# Limit write rate (IOPS) from a device
			device_write_iops=args.get('device_write_iops'),
			# Expose host devices to the container, as a list of string in the form  <path_on_host>:<path_in_container>:<cgroup_permissions>  LIST
			# Eg  /dev/sda:/dev/xvda:rwm allows container to hve read-write access to the host's /dev/sda via a node name /dev/xvda inside the container
			devices=args.get('devices'),
			# Set custom DNS servers LIST
			dns=args.get('dns'),
			# Additional options to be added to the container's resolve.conf file  LIST
			dns_opt=args.get('dns_opt'),
			# DNS search domains  LIST
			dns_search=args.get('dns_search'),
			# Addtional hostname to resolve inside the container as a mapping of hostname to IP address DICT
			extra_hosts=args.get('extra_hosts'),
			# List of additional group names and/or IDs that the container process iwll run as LIST
			group_add=args.get('group_add'),
			# Run an init inside the container that forwards signals and reaps process BOOL
			init=False if args.get('init') is None else args.get('init'),
			# Path to the docker-init binary
			init_path=args.get('init_path'),
			# Set the IPC mode for the container STRING
			ipc_mode=args.get('ipc_mode'),
			# Isolation technology to use. Default is None
			isolation=args.get('isolation'),
			# Either a dictionary mapping name to alias or as a list of (name, alias) tuples. DICT or LIST of TUPLES
			links=args.get('links'),
			# logging configuration, as a dictionary with keys:
			#   type: the logging driver name
			#   config: a dictionary of configuration for the logging driver
			log_config=args.get('log_config'),
			# LXC Config DICT
			lxc_conf=args.get('lxc_conf'),
			# memory limit. accepts float values which represent the memroy limit of created container in bytes or
			# a string with a units identification char(10000b, 10000K, 128m, 1g). If a string is specified without a
			# units character, byte are assumed as an   FLOAT or STR
			mem_limit=args.get('mem_limit'),
			# Tune a container's memory swappiness behavior. accepts number between 0 and 100. INT
			mem_swappiness=args.get('mem_swappiness'),
			# Maximum amount of memory + swap a container is allowed to consume. STR or INT
			memswap_limit=args.get('memswap_limit'),
			# Specification for mounts to be added to the container. More powerful alternative to binds.
			# Each item in the list is expected to be a docker.types.Mount object.  LIST
			mounts=args.get('mounts'),
			# Network mode:  STR
			#   bridge: Create a new network stack for the container on the bridge network
			#   none:   No network for this container
			#   container:<name|id> Reuse another container's netowrk stack.
			#   host:   Use the host network stack.
			network_mode=args.get('network_mode'),
			# whether to disable OOM killer BOOL
			oom_kill_disable=True if args.get('oom_kill_disable') is None else args.get('oom_kill_disable'),
			# An integer value containing the score given to the container in order to turn OOM killer preference INT
			oom_score_adj=args.get('oom_score_adj'),
			# If set to 'host', use the host PID namespace inside the container. STR
			pid_mode='host' if args.get('pid_mode') is None else args.get('pid_mode'),
			# Tune a container's pids limit. Set -1 for unlimited. INT
			pid_limit=-1 if args.get('pid_limit') is None else args.get('pid_limit'),
			# binging port for host and container
			port_bindings=args.get('port_bindings'),
			# give extended privileges to this container  BOOL
			privileged=False if args.get('privileged') is None else args.get('privileged'),
			# publish all ports to the hosts BOOL
			publish_all_ports=False if args.get('publish_all_ports') is None else args.get('publish_all_ports'),
			# mount the container's root filesystem as read only  BOOL
			read_only=False if args.get('read_only') is None else args.get('read_only'),
			# restart policy DICT
			#   Name one of 'on-failure' or 'always'
			#   MaximumRetryCount: Number of time to restart to container on failure
			restart_policy=args.get('restart_policy'),
			# A list of string values to customize labels for MLS system such as SELinux LIST
			security_opt=args.get('security_opt'),
			# Size of /dev/shm (eg.1G)  str or int
			shm_size=args.get('shm_size'),
			# Storage driver options per container as a key-value mapping  DICT
			storage_opt=args.get('storage_opt'),
			# kernel parameters to set in the container  DICT
			sysctls=args.get('sysctls'),
			# Temporary filesystems to mount, as a dictonary mapping a path inside the container to options for that path
			# eg. {'/mnt/vol1': '', '/mnt/vol2': 'size=3G, uid=1000'}
			tmpfs=args.get('tmpfs'),
			# ulimits to set inside the container as a list of dicts
			ulimits=args.get('ulimits'),
			# sets the user namespace mode for the container when user namespace remapping option is enables.
			# Supported values are: host STRING
			usens_mode=args.get('usens_mode'),
			# List of container names or IDS to get volumes from  LIST
			volumes_from=args.get('volumes_from'),
			# runtime to use with this container
			runtime=args.get('runtime')
		)
		return host_config

	def gen_net_conf(self,args):
		"""
		Generate netowrking config for creating a container
		:param args:  paramters for creating network
		:return: dictionary of a networking configuration file
		"""
		# Ref: http://docker-py.readthedocs.io/en/stable/api.html#docker.api.container.ContainerApiMixin.create_networking_config
		network_dict=self.handle.create_networking_config({args['network_name']: self.gen_ep_conf(args)})
		return network_dict

	def gen_ep_conf(self, args):
		"""
		This function is used for crate an endpoint parameters dictionary for create_networking_config
		:param args: Pass-in Parameters for Endpoint information
		:return:  Endpoint dictionary
		"""
		# Ref: http://docker-py.readthedocs.io/en/stable/api.html#docker.api.container.ContainerApiMixin.create_endpoint_config
		endpoint_dict = self.handle.create_endpoint_config(aliases=args['aliases'],
		                                                   links=args['links'],
		                                                   ipv4_address=args['ipv4_address'],
		                                                   ipv6_address=args['ipv6_address'],
		                                                   link_local_ips=args['link_local_ips'])
		return endpoint_dict

	def start_container(self, container_id):
		"""
		This func is for start a created container by ID
		:param container_id: string of container ID or Name Tag
		:return: dict of status
		"""
		return self.handle.start(container_id)

	def stop_container(self, container_id):
		"""
		This method is for stopping a running container by ID or Name
		:param container_id: String of container ID or name
		:return:  Dict of return status
		"""
		return self.handle.stop(container_id)

	def restart_container(self, container_id):
		"""
		This function is for restart a container by container id or name
		:param container_id: string of container id or name
		:return: dict of status
		"""
		return self.handle.restart(container_id)

	def remove_container(self, container_id):
		"""
		This function is used for remove a stopped container by ID or Name
		:param container_id: String of container ID or Name
		:return: DICT of status
		"""
		return self.handle.remove_container(container_id)

	def list_mapping_ports(self, container_id):
		"""
		This func will show all of the mapping of host-> container ports.
		:param container_id:  String of Container Name or ID
		:return: dict of ports mapping table
		"""
		return self.handle.port(container_id)

	def commit_to_image(self, args):
		"""
		This function is used for commiting the changed container to a image
		:param args[container_id]: container id or name
		:return: dict of status
		"""
		return self.handle.commit(container=args.get('container_id'),
		                          repository=args.get('repo_name'),
		                          tag=args.get('tag_name'),
		                          message=args.get('message'),
		                          author=args.get('author'),
		                          changes=args.get('changes'),
		                          conf=args.get('conf'))

	def pull_container_log(self, args):
		"""
		Pull logs of a running container
		:param args: args[container_id]: container id or name
		:return: return list of log lines
		"""
		return str(self.handle.logs(args['container_id'])).split('\n')


	def attach_container(self, container_id):
		# This 'attach' function also allow multiple parameters, this version only implement one
		# https://docker-py.readthedocs.io/en/stable/containers.html?highlight=exec#docker.models.containers.Container.attach
		return self.handle.attach(container_id)

	def exec_container(self, args):
		# there will be more parameters for choose, deployment later
		# in this version, only pass the 'cmd' parameter into method, other parameters keeps default value.
		# https://docker-py.readthedocs.io/en/stable/containers.html?highlight=exec#docker.models.containers.Container.exec_run

		return self.handle.exec_run(args['cmd'])

	def container_top(self, args):
		return self.handle.top(args['container_id'])


	def container_res_usage(self, args):
		# Method 'stats' returns a generator. Need to use next(gen) to get data
		return self.handle.stats(args['container_id'])

	def container_info(self, args):
		return  self.handle.inspect_container(args['container_id'])

