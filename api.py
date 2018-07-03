#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Description: This file contains the RESTFul API defination

from api_env import *
import logging
import os, sys
from flask import Flask
from flask_restful import reqparse, abort, Api, Resource
from docker_wrap import *
from helper import search_result_filter


logging.basicConfig(filename=api_log, level=logging_level)


app = Flask(__name__)
api = Api(app)

docker_host = Docker()
if docker_host.handle is None:
	logging.error("Docker Host cann't be connected")
	exit(1)

def invalidate_parameters_warning():
	return {"message": "Invalidate Parameter"}, 400

# Define Request Parser
parser = reqparse.RequestParser()
for param in request_arguments:
	parser.add_argument(param)

# TODO: Rename all classes to match the partern:  Network-, Docker-, Container-, Image-
# Docker APIs
class RegistryLogin(Resource):
	def post(self):
		args = parser.parse_args()
		if args['login_user'] is not None and args['login_pass'] is not None:
			return docker_host.login_registry(args['login_user'], args['login_pass'], args['registry_srv']), 200
		else:
			return invalidate_parameters_warning()

# TODO: wait get_docker_events() function wrapper finished
# class DockerEvents(Resource):
# 	def get(self):
# 		return docker_host.get_docker_events(), 200

class DiskUtilization(Resource):
	def get(self):
		return docker_host.get_disk_utils(), 200

# Docker Image APIs
class DockerInfo(Resource):
	def get(self):
		return docker_host.get_docker_info(), 200

class ImagesList(Resource):
	def get(self, id_name=None):
		if id_name is None:
			return docker_host.get_image_list(), 200
		else:
			image_list = docker_host.get_image_list()
			return search_result_filter(image_list, ['RepoTags','Id'], keyword=id_name), 200

class ImageSearchOnPublicRegister(Resource):
	def post(self):
		args = parser.parse_args()
		if args['keyword'] is not None and str(args['keyword']).strip() != "":
			return docker_host.public_image_search(keyword=args['keyword']), 200
		else:
			return invalidate_parameters_warning()

class PullImage(Resource):
	def post(self):
		args=parser.parse_args()
		return docker_host.pull_image(args['image_name'], args['image_tag'], args['repo_name'])

class ImageInspect(Resource):
	def post(self):
		# TODO: will support "repo/name:tag" later
		args = parser.parse_args()
		if args['image_id'] is None:
			return invalidate_parameters_warning()
		else:
			return docker_host.inspect_image(args['image_id']), 200

class RemoveImage(Resource):
	def post(self):
		args = parser.parse_args()
		if args['image_id'] is None:
			return invalidate_parameters_warning()
		else:
			if  args['force'] is None:
				is_force = False
			else:
				is_force = True
			return docker_host.remove_image(args['image_id'], force_remove=is_force), 200

class ChangeImageTag(Resource):
	def post(self):
		args = parser.parse_args()
		# args['image_id'] is also could be "repo/image:tag" this function still work
		# args['repo_name'] is new repository name for tag into. "new_repo/new_image"
		# args['tag_name'] is new tag name to be assign to image, if None, "latest" will be assigned
		if args['image_id'] is None or args['repo_name'] is None:
			return invalidate_parameters_warning()
		else:
			if args['force'] is None:
				is_force = False
			else:
				is_force = True
			# return value should be boolean
			return docker_host.tag_image(args['image_id'], args['repo_name'], args['tag_name'], force=is_force), 200

class PushImage(Resource):
	def post(self):
		args = parser.parse_args()
		if args['repo_name'] is None:
			return invalidate_parameters_warning()
		else:
			return docker_host.push_image(args['repo_name'], args['tag']), 200

class SaveImage(Resource):
	def post(self):
		args = parser.parse_args()
		if not os.path.exists(args['save_path']) or args['image_name'] is None:
			return invalidate_parameters_warning()
		else:
			return docker_host.save_image(args['image_name'], args['save_path'], tarball_name=args['tarball_name']), 200

class LoadImage(Resource):
	def post(self):
		args = parser.parse_args()
		# args['tarball_name'] should be a full path for tarball. it could be local path or uri
		# args['image_name'] should be a full name of image with repository name 'repo/name'
		if os.path.isfile(args['tarball_name']) and args['image_name'] is not None:
			return docker_host.load_image(args['tarball_name'], repository=args['image_name'], tag=args['image_tag'],
			                              changes=args['changes'])
		else:
			return invalidate_parameters_warning()

class BuildImage(Resource):
	#TODO implement the function of build images from dockerfile
	# https://docker-py.readthedocs.io/en/stable/api.html#module-docker.api.build
	pass


# Docker Container APIs
class ListContainers(Resource):
	def post(self):
		args = parser.parse_args()
		if args['all'] is not None:
			return docker_host.get_containers(all=True), 200
		else:
			return docker_host.get_containers(), 200

class CreateContainer(Resource):
	def post(self):
		args = parser.parse_args()
		new_container = docker_host.create_container(args=args)
		return new_container, 200

class StartContainer(Resource):
	def post(self):
		args = parser.parse_args()
		if args.get('container_id') is None:
			return invalidate_parameters_warning()
		else:
			return docker_host.start_container(args.get('container_id')), 200

class StopContainer(Resource):
	def post(self):
		args = parser.parse_args()
		if args.get('container_id') is None:
			return invalidate_parameters_warning()
		else:
			return docker_host.stop_container(args.get('container_id')), 200

class RestartContainer(Resource):
	def post(self):
		args = parser.parse_args()
		if args.get('container_id') is None:
			return invalidate_parameters_warning()
		else:
			return docker_host.restart_container(args.get('container_id')), 200

class RemoveContainer(Resource):
	def post(self):
		args = parser.parse_args()
		if args.get('container_id') is None:
			return invalidate_parameters_warning()
		else:
			return docker_host.remove_container(args.get('container_id')), 200

class ListMappingPorts(Resource):
	def post(self):
		args = parser.parse_args()
		if args.get('container_id') is None:
			return invalidate_parameters_warning()
		else:
			return docker_host.list_mapping_ports(args.get('container_id')), 200

class CommitContainer(Resource):
	def post(self):
		args = parser.parse_args()
		if args.get('container_id') is None or args.get('repo_name') is None or args.get('tag_name') is None:
			return invalidate_parameters_warning()
		else:
			return docker_host.commit_to_image(args), 200

class ExecContainer(Resource):
	# Container 'exec' function and redirect the console to a web based terminal console.
	def post(self):
		args = parser.parse_args()
		if args.get('container_id') is None:
			return  invalidate_parameters_warning()
		else:
			if args.get('cmd') is None:
				return docker_host.attach_container(args['container_id'])
			else:
				return docker_host.exec_container(args['container_id'], args['cmd']), 200

class AttachContainer(Resource):
	def post(self):
		args = parser.parse_args()
		if args.get('container_id') is None:
			return invalidate_parameters_warning()
		else:
			return docker_host.attach_container(args['container_id'])

class ContainerLog(Resource):
	def post(self):
		args = parser.parse_args()
		if args.get('container_id') is None:
			return  invalidate_parameters_warning()
		else:
			return docker_host.pull_container_log(args), 200

class DisplayContainerProcesses(Resource):
	def post(self):
		args = parser.parse_args()
		if args.get('container_id') is None:
			return invalidate_parameters_warning()
		else:
			return docker_host.container_top(), 200

class ContainerResourceUsage(Resource):
	def post(self):
		args = parser.parse_args()
		if args.get('container_id') is None:
			return invalidate_parameters_warning()
		else:
			return docker_host.container_res_usage(args), 200

class ContainerInfo(Resource):
	def post(self):
		args = parser.parse_args()
		if args.get('container_id') is None:
			return invalidate_parameters_warning()
		else:
			return docker_host.container_info(args), 200

class ExportContainer(Resource):
	# TODO: Export Container to a Tar file
	pass

class ImportContainer(Resource):
	# TODO: Import Tar file to a container
	pass

# Docker Networking API
class NetworkConnect(Resource):
	# TODO: Connect a container to a network
	def post(self):
		pass

class NetworkCreate(Resource):
	# TODO: Create a network
	def post(self):
		pass

class NetworkRemove(Resource):
	# TODO: Remove a network
	def post(self):
		pass

class NetworkDisconnect(Resource):
	# TODO: Disconnect a container from a network
	def post(self):
		pass

class NetworkInspect(Resource):
	# TODO: Display detailed information on one or more networks
	def post(self):
		pass

class NetworkList(Resource):
	# TODO: List Networks
	def post(self):
		pass

# Docker Volume API
class VolumeCreate(Resource):
	# TODO: Create a volume
	def post(self):
		pass

class VolumeRemove(Resource):
	# TODO: Remove a Volume
	def post(self):
		pass

class VolumeInspect(Resource):
	# TODO: Disply detailed information on one of more volumes
	def post(self):
		pass

class VolumeList(Resource):
	# TODO: List Volumes
	def post(self):
		pass

# NOTE: This version is for a single node environment. Swarm support doesn't included.
#       For later multiple node support will use K8S implementation.

# Tesseract System API
# User API
class UserCreate(Resource):
	# TODO: Create System User
	def post(self):
		pass

class UserRemove(Resource):
	# TODO: Remove a User
	def post(self):
		pass

class UserModify(Resource):
	# TODO: Modify a User
	def post(self):
		pass

class UserList(Resource):
	# TODO: Get all users or search
	def post(self):
		pass

class UserChangePassword(Resource):
	# TODO: Change password for user
	def post(self):
		pass

# Group API
class GroupCreate(Resource):
	# TODO: Create a group
	def post(self):
		pass

class GroupRemove(Resource):
	# TODO: Remove a group
	def post(self):
		pass

class GroupModify(Resource):
	# TODO: Modify a Group
	def post(self):
		pass

class GroupList(Resource):
	# TODO: List all groups or search
	def post(self):
		pass

# System HW Info
class HwHDD(Resource):
	# TODO: get all hdd information and utilization
	def post(self):
		pass

class HwMemory(Resource):
	# TODO: get memory information and utilization
	def post(self):
		pass

class GpuInfo(Resource):
	# TODO: get gpu information /could use filter to get specified information/ could specify gpu number /driver ver
	def post(self):
		pass

class GpuPowerUtils(Resource):
	# TODO: get gpu utilization: memory, power,
	def post(self):
		pass

class GpuProcesses(Resource):
	# TODO: get process inforamtion for specified gpu or all gpus
	def post(self):
		pass

class GpuPowerCap(Resource):
	# TODO: get/set gpu power cap
	def post(self):
		pass


# Setup API resource routing

# Implementation of Docker API routing
api.add_resource(RegistryLogin, '/api/v1/docker/login')
api.add_resource(DockerInfo, '/api/v1/docker/info')
api.add_resource(DiskUtilization, '/api/v1/docker/disk_util')

# Implementation of Docker Image API Routing
api.add_resource(ImagesList, '/api/v1/docker/image', '/api/v1/docker/image/<string:id_name>')
api.add_resource(ImageSearchOnPublicRegister, '/api/v1/docker/image/search')
api.add_resource(PullImage, '/api/v1/docker/image/pull')
api.add_resource(ImageInspect, '/api/v1/docker/image/inspect')
api.add_resource(RemoveImage, '/api/v1/docker/image/remove')
api.add_resource(ChangeImageTag, '/api/v1/docker/image/tag')
api.add_resource(PushImage, '/api/v1/docker/image/push')
api.add_resource(SaveImage, '/api/v1/docker/image/save')
api.add_resource(LoadImage, '/api/v1/docker/image/load')

# Implementation of Docker Container API Routing
api.add_resource(ListContainers, '/api/v1/docker/container')
api.add_resource(CreateContainer, '/api/v1/docker/container/create')
api.add_resource(StartContainer, '/api/v1/docker/container/start')
api.add_resource(StopContainer, '/api/v1/docker/container/stop')
api.add_resource(RestartContainer, '/api/v1/docker/container/restart')
api.add_resource(RemoveContainer, '/api/v1/docker/container/remove')
api.add_resource(ListMappingPorts, '/api/v1/docker/container/port')
api.add_resource(CommitContainer, '/api/v1/docker/container/commit')
api.add_resource(ExecContainer, '/api/v1/docker/container/exec')
api.add_resource(ContainerLog, '/api/v1/docker/container/log')
api.add_resource(DisplayContainerProcesses, '/api/v1/docker/container/top')
api.add_resource(ContainerResourceUsage, '/api/v1/docker/container/stats')
api.add_resource(ContainerInfo, '/api/v1/docker/container/inspect')


# Implementation of Docker Networking API Routing
api.add_resource(NetworkCreate, '/api/v1/docker/network/create')
api.add_resource(NetworkConnect, '/api/v1/docker/network/connect')
api.add_resource(NetworkDisconnect, '/api/v1/docker/network/disconnect')
api.add_resource(NetworkInspect, '/api/v1/docker/network/inspect')
api.add_resource(NetworkList, '/api/v1/docker/network')
api.add_resource(NetworkRemove, '/api/v1/docker/network/remove')

# Implementation of Docker Volume API Routing
api.add_resource(VolumeList, '/api/v1/docker/volume')
api.add_resource(VolumeCreate, '/api/v1/docker/volume/create')
api.add_resource(VolumeInspect, '/api/v1/docker/volume/inspect')
api.add_resource(VolumeRemove, '/api/v1/docker/volume/remove')


# Implementation of Tesseract System Level API Routing


if __name__ == '__main__':
	app.run(debug=True)

