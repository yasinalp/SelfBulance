extends Node2D


# Declare member variables here. Examples:
# var a = 2
# var b = "text"


# Called when the node enters the scene tree for the first time.
func _ready():
	$Direction.position = $Agent.position
	pass # Replace with function body.


# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta):
	var the_angle = Vector2(1,0).rotated($Agent.global_rotation).angle_to($Target.global_position - $Agent.global_position)
	var lerped_angle = lerp_angle($Agent.global_rotation, ($Target.global_position - $Agent.global_position).angle(), 0.5)
	$Direction.rotation = lerped_angle
	$Label.rect_position = ($Target.position + $Agent.position + Vector2(100,0).rotated($Agent.rotation))/2.0
	$Label.text = String(rad2deg(the_angle))
	$A2T.points = [$Target.position, $Agent.position]
	$A2R.points = [$Agent.position, $Agent.position + Vector2(100,0).rotated($Agent.rotation)]
	pass

func _input(event):
	if event is InputEventKey:
		if event.scancode == KEY_E:
			$Agent.look_at(get_global_mouse_position())
