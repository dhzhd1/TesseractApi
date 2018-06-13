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



if __name__ == '__main__':
	app.run(debug=True)

