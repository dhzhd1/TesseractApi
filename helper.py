# -*- coding: utf-8 -*-

import json

def search_result_filter(result_list, field_list, keyword):
	# input_data = json.loads(str(json_str))
	input_data = result_list
	output = []
	for field in field_list:
		results = [e for e in input_data if keyword in e[field] or keyword in ' '.join(e[field])]
		output += results
	return output

