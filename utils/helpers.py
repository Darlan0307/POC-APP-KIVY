from kivy.uix.popup import Popup
from kivy.uix.label import Label


def show_popup(title: str, message: str):
    popup = Popup(
        title=title,
        content=Label(
            text=message, 
            text_size=(400, None), 
            halign='center'
        ),
        size_hint=(0.8, 0.4)
    )
    popup.open()


def validate_required_field(field_value: str, field_name: str) -> bool:
    if not field_value or not field_value.strip():
        show_popup('Erro', f'Por favor, digite o {field_name}')
        return False
    return True

def is_select_query(query: str) -> bool:
    return query.strip().upper().startswith('SELECT')
