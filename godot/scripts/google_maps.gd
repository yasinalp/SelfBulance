extends Node2D
var socket : PacketPeerUDP
var to_be_sent
# Declare member variables here. Examples:
# var a = 2
# var b = "text"
# Called when the node enters the scene tree for the first time.
onready var astar = AStar2D.new()
enum CONTROLLABLE{AGENT, TARGET, BLOCK}
var control = -1
onready var prev = $CanvasLayer/HBoxContainer/Prev
onready var curr = $CanvasLayer/HBoxContainer/Current
onready var next = $CanvasLayer/HBoxContainer/Next
onready var tileset = $Navigation2D/TileMap.tile_set
var curr_tile_index = 1
onready var end_points = [$Agent, $Target]
onready var nodes = $RoadNodes.get_children()
var start = false
var SPEED = 100
var path_info= Array()
var first_point=true
var prev_point
var current_heading
var direction
var pixel_number
var newpath 

func _ready():
#	$Line2D.points = $Navigation2D.get_simple_path($Agent.global_position, $Target.global_position)
	socket = PacketPeerUDP.new()
	socket.set_dest_address("127.0.0.1",4242)
	connect_all_nodes()
	connect_endpoints()
	find_draw_path()
	current_heading=$Agent.global_rotation
	pass # Replace with function body.

# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta):
	var mouse_pos = get_global_mouse_position()
	if control == CONTROLLABLE.AGENT:
		$Agent.global_position = mouse_pos
	elif control == CONTROLLABLE.TARGET:
		$Target.global_position = mouse_pos
	elif control == CONTROLLABLE.BLOCK:
		$Block.global_position = mouse_pos
	if control in [0,1] and not start:
		print("update end points")
		update_endpoint()
		find_draw_path()
	elif start:
		for point in newpath:
			#yon bul
			if first_point:
				first_point=false
				prev_point=point
			else:
				var the_angle = Vector2(1,0).rotated(current_heading).angle_to(point - prev_point)
				var angle=rad2deg(the_angle)
				if angle<-45:
					direction="sol"
				elif angle>45:
					direction="sag"
				else:
					direction = "duz"
				current_heading=(point - prev_point).angle()
				path_info.append(direction)
				pixel_number=prev_point.distance_to(point)
				path_info.append(pixel_number)
				prev_point=point
		to_be_sent = "["
		for path_element in path_info:
			if path_element is String:
				if path_info.find(path_element) == 0:
					to_be_sent += "'" + path_element +"'"
				else:
					to_be_sent += ", '" + path_element +"'"
			else:
				to_be_sent += ", " + str(path_element)
		to_be_sent +="]"
		print(to_be_sent)
		socket.put_packet(to_be_sent.to_utf8())
		start = false
#	$Line2D.points = $Navigation2D.get_simple_path($Agent.global_position, $Target.global_position)

func append_endpoints():
	var path = PoolVector2Array([$Agent.global_position])
	var start_point = astar.get_closest_point($Agent.global_position)
	var end_point = astar.get_closest_point($Target.global_position)
	
	var dis_agent = astar.get_point_position(start_point).distance_to($Target.global_position)
	
	path.append_array(astar.get_point_path(start_point, end_point))
	
	var dis_target = $Agent.global_position.distance_to($Target.global_position)
	var dis_last = $Agent.global_position.distance_to(astar.get_point_position(end_point))
	if dis_target < dis_last:
		path.set(path.size()-1, $Target.global_position.round())
	else:
		path.append($Target.global_position.round())
	if dis_target < dis_agent:
		path.remove(1)  # [agent, start_point, ..., end_point, target]
	$Line2D.points = path
	
#	print(String($Navigation2D/TileMap.world_to_map(mouse_pos)))
	pass

func connect_all_nodes():
	print("nodes: ", nodes)
	for node in nodes:
		astar.add_point(node.get_instance_id(), node.global_position)
	for node_source in nodes:
		for node_target in nodes:
			if node_source != node_target:
				$ConnectionController.global_position = node_source.global_position
				$ConnectionController.cast_to = Vector2(node_source.global_position.distance_to(node_target.global_position), 0)
				$ConnectionController.rotation = node_target.global_position.angle_to_point(node_source.global_position)
				$ConnectionController.force_raycast_update()
				if not $ConnectionController.is_colliding():
	#				print("connected")
					var newline = Line2D.new()
					newline.width = 1
					add_child(newline)
					if not astar.are_points_connected(node_source.get_instance_id(), node_target.get_instance_id()):
						astar.connect_points(node_source.get_instance_id(), node_target.get_instance_id())
	#				newline.points = [$ConnectionController.position, $ConnectionController.position+$ConnectionController.cast_to.rotated($ConnectionController.rotation)]
					newline.points = [node_source.position, node_target.position]
					newline.default_color = Color(0.7,0.7,0.7)
				else:
					print("not")

func connect_endpoints():
	if astar.has_point($Agent.get_instance_id()):
		astar.remove_point($Agent.get_instance_id())
	astar.add_point($Agent.get_instance_id(), $Agent.global_position)
	if astar.has_point($Target.get_instance_id()):
		astar.remove_point($Target.get_instance_id())
	astar.add_point($Target.get_instance_id(), $Target.global_position)
	print("nodes: ", nodes)
	for end_point in end_points:
		$ConnectionController.global_position = end_point.global_position
		for node_target in nodes:
			$ConnectionController.cast_to = Vector2(end_point.global_position.distance_to(node_target.global_position), 0)
			$ConnectionController.rotation = node_target.global_position.angle_to_point(end_point.global_position)
			$ConnectionController.force_raycast_update()
			if not $ConnectionController.is_colliding():
#				print("connected")
#				var newline = Line2D.new()
#				newline.default_color = Color(1.0,0.1,0.1)
#				$Temporary.add_child(newline)
				if not astar.are_points_connected(end_point.get_instance_id(), node_target.get_instance_id()):
					astar.connect_points(end_point.get_instance_id(), node_target.get_instance_id())
#				newline.points = [$ConnectionController.position, $ConnectionController.position+$ConnectionController.cast_to.rotated($ConnectionController.rotation)]
#				newline.points = [end_point.position, node_target.position]
			else:
				print("not")

func update_endpoint():
	var end_point = end_points[control]
	if control == -1:
		end_point = $Agent
	var end_point_id = end_point.get_instance_id()
	if astar.has_point(end_point_id):
		astar.remove_point(end_point_id)
	astar.add_point(end_point_id, end_point.global_position)
	$ConnectionController.global_position = end_point.global_position
	$Temporary.get_child(0).queue_free()
	$Temporary.add_child(Node.new())
	for node_target in nodes:
		$ConnectionController.cast_to = Vector2(end_point.global_position.distance_to(node_target.global_position), 0)
		$ConnectionController.rotation = node_target.global_position.angle_to_point(end_point.global_position)
		$ConnectionController.force_raycast_update()
		if not $ConnectionController.is_colliding():
			print("yes..")
			var the_angle = Vector2(1,0).rotated($Agent.global_rotation).angle_to(node_target.global_position - $Agent.global_position)
			if (end_point == $Target or abs(the_angle) < PI/2.0) and not astar.are_points_connected(end_point_id, node_target.get_instance_id()):
				var newline = Line2D.new()
				newline.default_color = Color(0.8,0.8,0.5)
				newline.points = [end_point.position, node_target.position]
				$Temporary.get_child(1).add_child(newline)
				astar.connect_points(end_point_id, node_target.get_instance_id())
			else:
				print(end_point_id, node_target.get_instance_id())
		else:
			print("uuupssss")
			var newline = Line2D.new()
			newline.points = [end_point.position, node_target.position]
			newline.default_color = Color(1.0,0,0,0.15)
			$Temporary.get_child(1).add_child(newline)
			$CollisionFinder.global_position = $ConnectionController.get_collision_point()
			$CollisionFinder.rotation = $ConnectionController.rotation
	print("updated connections: ", astar.get_point_connections(end_point_id).size())

func find_draw_path():
	newpath = astar.get_point_path($Agent.get_instance_id(),$Target.get_instance_id())
	print("newpath:", newpath)
	$Line2D.points = newpath

func create_path():
	var path_points = $Line2D.points
	var path_curve = Curve2D.new()
	for i in path_points.size():
		if i>0 and i<path_points.size()-1:
			var point_angle = (path_points[i-1] - path_points[i]).angle()
			var in_point = Vector2(20,0).rotated(point_angle)
#			path_curve.add_point(path_points[i], path_points[i].normalized()*SPEED, path_points[i].normalized()*SPEED)  # path_points[i-1]
			path_curve.add_point(path_points[i],in_point, -in_point)
		elif i == 0:
			var point_angle = $Agent.rotation
			var lerped_angle = lerp_angle($Agent.rotation, (path_points[1] - $Agent.position).angle(), 0.5)
			var out_point = Vector2(20,0).rotated(lerped_angle)
			path_curve.add_point(path_points[i], -out_point, out_point)
		else:
			path_curve.add_point(path_points[i],Vector2(0,0), Vector2(0,0))
	$Path2D.curve = path_curve
	$Path2D/PathFollow2D.offset = 0
	
func set_previous_tile(world_pos:Vector2):
	var tile_coord = $Navigation2D/TileMap.world_to_map(world_pos)
	var current_tile = $Navigation2D/TileMap.get_cellv(tile_coord)
	$Navigation2D/TileMap.set_cellv(tile_coord, current_tile-1)

func set_tile(world_pos:Vector2):
	var tile_coord = $Navigation2D/TileMap.world_to_map(world_pos)
	$Navigation2D/TileMap.set_cellv(tile_coord, curr_tile_index)

func set_next_tile(world_pos:Vector2):
	var tile_coord = $Navigation2D/TileMap.world_to_map(world_pos)
	var current_tile = $Navigation2D/TileMap.get_cellv(tile_coord)
	$Navigation2D/TileMap.set_cellv(tile_coord, current_tile+1)

func _unhandled_input(event):
#	print("event occured: ", event.as_text())
	if event is InputEventKey:
		if event.pressed:
			if event.scancode == KEY_Z:
#				set_previous_tile(get_global_mouse_position())
				_on_left_pressed()
			elif event.scancode == KEY_X:
				set_tile(get_global_mouse_position())
			elif event.scancode == KEY_C:
#				set_next_tile(get_global_mouse_position())
				_on_right_pressed()
			elif event.scancode == KEY_E:
				$Agent.look_at(get_global_mouse_position())
				update_endpoint()
				find_draw_path()
			if event.scancode == KEY_ENTER:
				start = true
				create_path()
			if event.scancode == KEY_T:
				print("shift pressed")
				control = CONTROLLABLE.TARGET
				start = false
			elif event.scancode == KEY_CONTROL:
				print("control pressed")
				control = CONTROLLABLE.AGENT
				start = false
			elif event.scancode == KEY_B:
				print("alt pressed")
				control = CONTROLLABLE.BLOCK
		elif event.scancode == KEY_CONTROL:
			print("released")
			control = -1
		elif event.scancode == KEY_T:
			control = -1
			connect_endpoints()
	elif not event is InputEventMouse:
#		print("break")
		return
	elif event.button_mask == 16:
		$Camera2D.global_position = $Camera2D.global_position.linear_interpolate(get_global_mouse_position(), 0.1)
		$Camera2D.zoom *= 1.1
	elif event.button_mask == 8:
		$Camera2D.global_position = $Camera2D.global_position.linear_interpolate(get_global_mouse_position(), 0.1)
		$Camera2D.zoom *= 0.9
	elif event.button_mask && BUTTON_MASK_LEFT == BUTTON_MASK_LEFT:
		if event.pressed:
			print("active")
			set_process(true)
		else:
			print("deactive")
#			set_process(false)

func _on_left_pressed():
	curr_tile_index = (curr_tile_index - 1) % tileset.get_last_unused_tile_id()
	next.texture = curr.texture
	curr.texture = prev.texture
	prev.texture = tileset.tile_get_texture(curr_tile_index - 1)
	pass # Replace with function body.


func _on_right_pressed():
	curr_tile_index = (curr_tile_index + 1) % tileset.get_last_unused_tile_id()
	prev.texture = curr.texture
	curr.texture = next.texture
	next.texture = tileset.tile_get_texture(curr_tile_index + 1)
	pass # Replace with function body.
