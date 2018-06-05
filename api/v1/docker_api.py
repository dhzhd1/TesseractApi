

class RegistryLogin(Resource):
	def post(self):
		args = parser.parse_args()
		if args['login_user'] is not None and args['login_pass'] is not None:
			return docker_host.login_registry(args['login_user'], args['login_pass'], args['registry_srv']), 201
		else:
			return return_invalidate_parameters_warning()