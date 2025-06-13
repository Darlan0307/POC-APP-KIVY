import asyncio
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.screenmanager import Screen
from kivy.uix.gridlayout import GridLayout
from kivy.clock import Clock

from services.database_service import DatabaseService
from utils.helpers import show_popup, validate_required_field


class LoginScreen(Screen):
    
    def __init__(self, cmd_user=None, cmd_password=None, cmd_host=None, **kwargs):
        super().__init__(**kwargs)
        self.db_service = DatabaseService()
        self.cmd_user = cmd_user
        self.cmd_password = cmd_password
        self.cmd_host = cmd_host
        self._auto_login_done = False
        self._is_connecting = False
        self._build_interface()
    
    def on_enter(self):
        if (self.cmd_user and self.cmd_password and self.cmd_host and not self._auto_login_done):
            self.user_input.text = self.cmd_user
            self.password_input.text = self.cmd_password
            self.host_input.text = self.cmd_host
            self._auto_login_done = True
            Clock.schedule_once(self._delayed_auto_login, 0)

    def _delayed_auto_login(self, dt):
        asyncio.create_task(self.connect_to_database_async())
    
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
            hint_text='Ex: localhost:1521/XE',
            text='localhost:1521/XE'
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
        """Wrapper síncrono para o teste de conexão assíncrono"""
        if self._is_connecting:
            return
        
        if not self._validate_fields():
            return
        
        # Executa o teste de forma assíncrona
        asyncio.create_task(self.test_connection_async())
    
    async def test_connection_async(self, instance):
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
    
    async def test_connection_async(self):
        try:
            self._is_connecting = True
            self.status_label.text = 'Testando conexão...'
            
            connection_data = self._get_connection_data()
            success, message = await self.db_service.test_connection(**connection_data)
            
            if success:
                self.status_label.text = 'Conexão OK! ✓'
                Clock.schedule_once(
                    lambda dt: show_popup('Sucesso', 'Conexão realizada com sucesso!'), 
                    0
                )
            else:
                self.status_label.text = f'Erro na conexão: {message}'
                Clock.schedule_once(
                    lambda dt: show_popup('Erro de Conexão', f'Não foi possível conectar:\n{message}'), 
                    0
                )
                
        except Exception as e:
            error_msg = f'Erro inesperado: {str(e)}'
            Clock.schedule_once(
                lambda dt: show_popup('Erro', error_msg), 
                0
            )
        finally:
            self._is_connecting = False
    
    def connect_to_database(self, instance):
        if self._is_connecting:
            return
        
        if not self._validate_fields():
            return

        asyncio.create_task(self.connect_to_database_async())

    async def connect_to_database_async(self):
        try:
            self._is_connecting = True
            self.status_label.text = 'Conectando...'
            
            connection_data = self._get_connection_data()
            success, result = await self.db_service.connect(**connection_data)
            
            if success:
                def switch_to_main(dt):
                    main_screen = self.manager.get_screen('main')
                    main_screen.set_connection_info(
                        connection_data['user'], 
                        connection_data['dsn'], 
                        result
                    )
                    self.manager.current = 'main'
                
                Clock.schedule_once(switch_to_main, 0)
                
            else:
                self.status_label.text = f'Erro na conexão: {result}'
                Clock.schedule_once(
                    lambda dt: show_popup('Erro de Conexão', f'Não foi possível conectar:\n{result}'), 
                    0
                )
                
        except Exception as e:
            error_msg = f'Erro inesperado: {str(e)}'
            Clock.schedule_once(
                lambda dt: show_popup('Erro', error_msg), 
                0
            )
        finally:
            self._is_connecting = False
    
    def on_leave(self):
        self._is_connecting = False