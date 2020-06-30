extends Node2D

signal angle_changed

# Declare member variables here. Examples:
# var a = 2
# var b = "text"


# Called when the node enters the scene tree for the first time.
func _ready():
	$Direction.position = $Sprite.position
	connect("angle_changed", self,"_angle_changed")
	for i in $Path2D.curve.get_point_count():
		print("Point ", i, ": ")
		print("Position: ", $Path2D.curve.get_point_position(i))
		print("in: ", $Path2D.curve.get_point_in(i))
		print("out: ", $Path2D.curve.get_point_out(i))
		if i>0 and i<$Path2D.curve.get_point_count()-1:
			print("Angle of position: ", rad2deg(($Path2D.curve.get_point_position(i-1) - $Path2D.curve.get_point_position(i)).angle()))
			print("Angle of in: ", rad2deg($Path2D.curve.get_point_in(i).angle()))
			print("Angle of out: ", rad2deg($Path2D.curve.get_point_out(i).angle()))
	pass # Replace with function body.


# Called every frame. 'delta' is the elapsed time since the previous frame.
#func _process(delta):
#	pass

func _angle_changed():
	$Sprite.look_at(get_global_mouse_position())
	var point_angle = ($Path2D.curve.get_point_position(0).angle_to_point($Path2D.curve.get_point_position(1)))
	var points = [Vector2(0,0), Vector2(100,0).rotated(point_angle)]
	$Direction.points = points
	pass

func _input(event):
	if event is InputEventKey:
		if event.scancode == KEY_E and event.pressed:
			emit_signal("angle_changed")
