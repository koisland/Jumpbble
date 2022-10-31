extends CanvasLayer

signal start_game

onready var player_info = get_node("../Player")

func show_message(text):
	$Message.text = text
	$Message.show()

func _ready():
	# Set letters in UI.
	for letter in player_info.arr_bag:
		$LettersUI.add_item(letter)
	
	$LettersUI.select(0)

func _on_LettersUI_item_selected(index):
	var selected_letter: String =  $LettersUI.get_item_text(index)
	player_info.selected_letter = selected_letter
