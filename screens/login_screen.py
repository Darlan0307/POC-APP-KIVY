import asyncio
from kivy.uix.screenmanager import Screen
from kivy.clock import Clock
from kivy.lang import Builder

from services.database_service import DatabaseService
from utils.helpers import show_popup, validate_required_field
from utils.resource_path import resource_path

kv_file = resource_path('screens/login_screen.kv')
Builder.load_file(kv_file)

class LoginScreen(Screen):
    
    def __init__(self, cmd_user=None, cmd_password=None, cmd_host=None, **kwargs):
        super().__init__(**kwargs)
        self.db_service = DatabaseService()
        self.cmd_user = cmd_user
        self.cmd_password = cmd_password
        self.cmd_host = cmd_host
        self._auto_login_done = False
        self._is_connecting = False
        self._event_loop = None
    
    def on_enter(self):
        self._setup_event_loop()
        if (self.cmd_user and self.cmd_password and self.cmd_host and not self._auto_login_done):
            self.ids.user_input.text = self.cmd_user
            self.ids.password_input.text = self.cmd_password
            self.ids.host_input.text = self.cmd_host
            self._auto_login_done = True
            Clock.schedule_once(self._delayed_auto_login, 0)

    def _delayed_auto_login(self, dt):
        self._run_async_task(self.connect_to_database_async())
    
    def _run_async_task(self, coro):
        def run_in_thread():
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(coro)
            except Exception as e:
                Clock.schedule_once(
                    lambda dt: show_popup('Erro', f'Erro interno: {str(e)}'), 
                    0
                )
            finally:
                loop.close()
        
        import threading
        thread = threading.Thread(target=run_in_thread)
        thread.daemon = True
        thread.start()

    def _setup_event_loop(self):
        try:
            self._event_loop = asyncio.get_event_loop()
        except RuntimeError:
            self._event_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self._event_loop)
    
    def _validate_fields(self):
        if not validate_required_field(self.ids.user_input.text, 'Usuário'):
            return False
        if not validate_required_field(self.ids.password_input.text, 'Senha'):
            return False
        if not validate_required_field(self.ids.host_input.text, 'Host'):
            return False
        return True
    
    def _get_connection_data(self):
        return {
            'user': self.ids.user_input.text.strip(),
            'password': self.ids.password_input.text.strip(),
            'dsn': self.ids.host_input.text.strip()
        }
    
    def test_connection(self):
        if self._is_connecting:
            return
        
        if not self._validate_fields():
            return
        
        self._run_async_task(self.test_connection_async())
    
    async def test_connection_async(self):
        try:
            self._is_connecting = True
            self.ids.status_label.text = 'Testando conexão...'
            
            connection_data = self._get_connection_data()
            success, message = await self.db_service.test_connection(**connection_data)
            
            if success:
                self.ids.status_label.text = 'Conexão OK! ✓'
                Clock.schedule_once(
                    lambda dt: show_popup('Sucesso', 'Conexão realizada com sucesso!'), 
                    0
                )
            else:
                self.ids.status_label.text = f'Erro na conexão: {message}'
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
    
    def connect_to_database(self):
        if self._is_connecting:
            return
        
        if not self._validate_fields():
            return
        self._run_async_task(self.connect_to_database_async())

    async def connect_to_database_async(self):
        try:
            self._is_connecting = True
            self.ids.status_label.text = 'Conectando...'
            
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
                self.ids.status_label.text = f'Erro na conexão: {result}'
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