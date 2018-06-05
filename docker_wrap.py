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
