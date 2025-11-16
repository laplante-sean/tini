extends Control
class_name Main

@onready var login_page: Control = $LoginPage
@onready var margin_container: MarginContainer = $MarginContainer

func _on_login_button_pressed() -> void:
    login_page.show()
    margin_container.hide()

func _on_login_page_login_complete() -> void:
    login_page.hide()
    margin_container.show()
    # TODO: Query for new owned games?
