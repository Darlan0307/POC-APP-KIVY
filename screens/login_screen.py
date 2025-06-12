from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.screenmanager import Screen
from kivy.uix.gridlayout import GridLayout

from services.database_service import DatabaseService
from utils.helpers import show_popup, validate_required_field


class LoginScreen(Screen):
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db_service = DatabaseService()
        self._build_interface()
    
    def _build_interface(self):
        main_layout = BoxLayout(orientation='vertical', padding=20, spacing=15)

        title_label = Label(
            text='Conexão Oracle Database',
            height=10,
            font_size=28,
            bold=True
        )
        main_layout.add_widget(title_label)

        form_layout = self._create_form_layout()
        main_layout.add_widget(form_layout)
        
        button_layout = self._create_button_layout()
        main_layout.add_widget(button_layout)
        
        self.status_label = Label(
            text='Preencha os dados para conectar',
            height=10
        )
        main_layout.add_widget(self.status_label)
        
        self.add_widget(main_layout)
    
    def _create_form_layout(self):
        form_layout = GridLayout(cols=2, spacing=10)
        form_layout.bind(minimum_height=form_layout.setter('height'))
        
        form_layout.add_widget(Label(text='Usuário:', size_hint_y=None, height=40))
        self.user_input = TextInput(
            multiline=False,
            size_hint_y=None,
            height=40,
            hint_text='Digite o usuário do banco'
        )
        form_layout.add_widget(self.user_input)
        
        form_layout.add_widget(Label(text='Senha:', size_hint_y=None, height=40))
        self.password_input = TextInput(
            multiline=False,
            password=True,
            size_hint_y=None,
            height=40,
            hint_text='Digite a senha'
        )
        form_layout.add_widget(self.password_input)
        
        form_layout.add_widget(Label(text='Host:', size_hint_y=None, height=40))
        self.host_input = TextInput(
            multiline=False,
            size_hint_y=None,
            height=40,
            hint_text='Ex: localhost:1521/FREE',
            text='localhost:1521/FREE'
        )
        form_layout.add_widget(self.host_input)
        
        return form_layout
    
    def _create_button_layout(self):
        button_layout = BoxLayout(
            orientation='horizontal', 
            spacing=10, 
            size_hint_y=None, 
            height=50
        )
        
        connect_button = Button(text='Conectar')
        connect_button.bind(on_press=self.connect_to_database)
        button_layout.add_widget(connect_button)
        
        test_button = Button(text='Testar Conexão')
        test_button.bind(on_press=self.test_connection)
        button_layout.add_widget(test_button)

        test_dns_button = Button(text='Testar Formato DSN')
        test_dns_button.bind(on_press=self.test_connection_multiple_dsn)
        button_layout.add_widget(test_dns_button)
        
        return button_layout
    
    def _validate_fields(self):
        if not validate_required_field(self.user_input.text, 'Usuário'):
            return False
        if not validate_required_field(self.password_input.text, 'Senha'):
            return False
        if not validate_required_field(self.host_input.text, 'Host'):
            return False
        return True
    
    def _get_connection_data(self):
        return {
            'user': self.user_input.text.strip(),
            'password': self.password_input.text.strip(),
            'dsn': self.host_input.text.strip()
        }
    
    def test_connection(self, instance):
        if not self._validate_fields():
            return
        
        self.status_label.text = 'Testando conexão...'
        connection_data = self._get_connection_data()
        
        success, message = self.db_service.test_connection(**connection_data)
        
        if success:
            self.status_label.text = 'Conexão OK! ✓'
            show_popup('Sucesso', 'Conexão realizada com sucesso!')
        else:
            self.status_label.text = f'Erro na conexão: {message}'
            show_popup('Erro de Conexão', f'Não foi possível conectar:\n{message}')

    def test_connection_multiple_dsn(self, instance):
        if not self._validate_fields():
            return
        
        self.status_label.text = 'Testando conexão...'
        connection_data = self._get_connection_data()
        
        success, message = self.db_service.test_multiple_dsn_formats(**connection_data)
        
        if success:
            self.status_label.text = 'Conexão OK! ✓'
            show_popup('Sucesso', 'Conexão realizada com sucesso!')
        else:
            self.status_label.text = f'Erro na conexão: {message}'
            show_popup('Erro de Conexão', f'Não foi possível conectar:\n{message}')
    
    def connect_to_database(self, instance):
        if not self._validate_fields():
            return
        
        self.status_label.text = 'Conectando...'
        connection_data = self._get_connection_data()
        
        success, result = self.db_service.connect(**connection_data)
        
        if success:
            main_screen = self.manager.get_screen('main')
            main_screen.set_connection_info(
                connection_data['user'], 
                connection_data['dsn'], 
                result
            )

            self.manager.current = 'main'
        else:
            self.status_label.text = f'Erro na conexão: {result}'
            show_popup('Erro de Conexão', f'Não foi possível conectar:\n{result}')