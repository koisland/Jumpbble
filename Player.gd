extends KinematicBody2D

# Nodes
onready var grid = get_node("../Grid")
onready var hud = get_node("../HUD/LettersUI")


const FILE_TILES := "res://config/letters.json"

# Starting tiles.
var dict_tiles_info := read_tiles_file()
var dict_tiles_mv_values := get_tiles_mv_values(dict_tiles_info)
var arr_tiles := generate_tiles(dict_tiles_info)
var int_allowed_tiles := 7
var arr_bag := PoolStringArray()
# Set selected letter.
var selected_letter = null


func read_tiles_file() -> Dictionary:
	var file_tiles = File.new()
	
	if file_tiles.open(FILE_TILES, File.READ) != OK:
		push_error("Tiles JSON file doesn't exist.")
	var str_json_tiles = file_tiles.get_as_text()
	file_tiles.close()
	
	var dict_tiles = JSON.parse(str_json_tiles)
	if dict_tiles.error != OK:
		push_error("Invalid format for tiles JSON file.")
	return dict_tiles.result

func get_tiles_mv_values(tiles: Dictionary) -> Dictionary:
	var dict_tiles_mv_values = {}
	var int_letter_mv_value = 0
	
	for tile in tiles.keys():
		int_letter_mv_value += 1
		dict_tiles_mv_values[tile] = int_letter_mv_value
		
	return dict_tiles_mv_values

func generate_tiles(tiles: Dictionary) -> PoolStringArray:
	var arr_tiles := PoolStringArray()
	for letter in dict_tiles_info.keys():
		var n_letters: int  = dict_tiles_info[letter]["Number"]
		for i in range(n_letters):
			arr_tiles.push_back(letter)
	
	return arr_tiles

func init_bag() -> void:
	for i in range(int_allowed_tiles):
		var random_tile = arr_tiles[randi() % arr_tiles.size()]
		arr_bag.push_back(random_tile)
		
func _ready() -> void:
	# Init the bag of letter to choose from.
	init_bag()

func _process(delta: float) -> void:
	var vec_grid_pos = grid.calculate_grid_coordinates($AnimatedSprite.position)
	var int_grid_pos_change: int
	
	# Set grid position change.
	if selected_letter == null:
		int_grid_pos_change = dict_tiles_mv_values[arr_bag[0]]
	else:
		int_grid_pos_change = dict_tiles_mv_values[selected_letter]

	# Check movements.
	if Input.is_action_pressed("up"):
		vec_grid_pos.y += -1 * int_grid_pos_change
	if Input.is_action_pressed("down"):
		vec_grid_pos.y += int_grid_pos_change
	if Input.is_action_pressed("left"):
		vec_grid_pos.x += -1 * int_grid_pos_change
	if Input.is_action_pressed("right"):
		vec_grid_pos.x += int_grid_pos_change
	
	# Set coords to loop if goes past grid.
	var grid_dim =  grid.cell_quadrant_size
	vec_grid_pos.x = abs((int(vec_grid_pos.x) + grid_dim) % grid_dim)
	vec_grid_pos.y = abs((int(vec_grid_pos.y) + grid_dim) % grid_dim)
	
	var vec_map_coords = grid.calculate_map_position(vec_grid_pos)
	var int_new_pos_idx = grid.as_index(vec_grid_pos)
	# Set sprite new position.
	$AnimatedSprite.position = vec_map_coords
	yield(get_tree().create_timer(1.0), "timeout")
