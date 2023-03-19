import boto3, json, constants

websocket_client = boto3.client('apigatewaymanagementapi', endpoint_url=constants.WEBSOCKET_ENDPOINT_URL)
ddb_client = boto3.client('dynamodb')

def tv_toggle(power_state):
	response = ddb_client.get_item(
		TableName=constants.DDB_TABLE_NAME,
		Key={constants.DDB_PK: {
			'S': constants.DDB_PK_VALUE
		}})
	
	connection_id = response['Item']['connectionId']['S']

	print('Connection Id: {}'.format(connection_id))

	data = json.dumps({'action': 'toggle_power', 'state': power_state}).encode('utf-8')

	print('Sending to websocket: {}'.format(data))

	response = websocket_client.post_to_connection(
		ConnectionId=connection_id,
		Data=data
	)

def tv_volume_step(volume_steps):
	response = ddb_client.get_item(
		TableName=constants.DDB_TABLE_NAME,
		Key={constants.DDB_PK: {
			'S': constants.DDB_PK_VALUE
		}})
	
	connection_id = response['Item']['connectionId']['S']

	print('Connection Id: {}'.format(connection_id))

	data = json.dumps({'action': 'volume_step', 'volume_steps': volume_steps}).encode('utf-8')

	print('Sending to websocket: {}'.format(data))

	websocket_client.post_to_connection(
		ConnectionId=connection_id,
		Data=data
	)

def tv_playback_controller(playback_action):
	response = ddb_client.get_item(
		TableName=constants.DDB_TABLE_NAME,
		Key={constants.DDB_PK: {
			'S': constants.DDB_PK_VALUE
		}})
	
	connection_id = response['Item']['connectionId']['S']

	print('Connection Id: {}'.format(connection_id))

	data = json.dumps({'action': 'playback_controller', 'playback_action': playback_action}).encode('utf-8')

	print('Sending to websocket: {}'.format(data))

	websocket_client.post_to_connection(
		ConnectionId=connection_id,
		Data=data
	)