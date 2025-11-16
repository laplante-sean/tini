extends Control
class_name LoginPage

signal login_complete()


func _on_login_button_pressed() -> void:
    # DO login - if success
    login_complete.emit()
