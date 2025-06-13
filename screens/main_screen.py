import asyncio
from kivy.uix.screenmanager import Screen
from kivy.clock import Clock
from kivy.lang import Builder

from services.database_service import DatabaseService
from utils.helpers import show_popup
from utils.resource_path import resource_path

kv_file = resource_path('screens/main_screen.kv')
Builder.load_file(kv_file)

class MainScreen(Screen):
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db_service = DatabaseService()
        self.connection = None
        self.db_user = ''
        self.db_host = ''
        self._is_executing = False

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
    
    def set_connection_info(self, user, host, connection):
        self.db_user = user
        self.db_host = host
        self.connection = connection
        self.db_service.set_connection(connection)
        self.ids.connection_info.text = f'Conectado como: {user}@{host}'
    
    def execute_query(self):
        if self._is_executing:
            return
        
        if not self.connection:
            show_popup('Erro', 'Não há conexão ativa com o banco')
            return
        
        query = self.ids.query_input.text.strip()
        if not query:
            show_popup('Erro', 'Digite uma consulta SQL')
            return
        self._run_async_task(self.execute_query_async(query))
    
    async def execute_query_async(self, query: str):
        try:
            self._is_executing = True

            Clock.schedule_once(
                lambda dt: setattr(self.ids.result_label, 'text', 'Executando consulta...'), 
                0
            )
            
            success, result = await self.db_service.execute_query(query)
            
            if success:
                Clock.schedule_once(
                    lambda dt: setattr(self.ids.result_label, 'text', result), 
                    0
                )
            else:
                Clock.schedule_once(
                    lambda dt: setattr(self.ids.result_label, 'text', f'Erro SQL: {result}'), 
                    0
                )
                Clock.schedule_once(
                    lambda dt: show_popup('Erro SQL', result), 
                    0
                )
                
        except Exception as e:
            error_msg = f'Erro inesperado: {str(e)}'
            Clock.schedule_once(
                lambda dt: show_popup('Erro', error_msg), 
                0
            )
        finally:
            self._is_executing = False

    def disconnect(self):
        if self._is_executing:
            return
        
        if self.connection:
            self._run_async_task(self.disconnect_async())
        else:
            self.manager.current = 'login'
    
    async def disconnect_async(self):
        try:
            await self.db_service.disconnect()
            self.connection = None
            
            Clock.schedule_once(lambda dt: setattr(self.manager, 'current', 'login'), 0)
            
        except Exception as e:
            Clock.schedule_once(
                lambda dt: show_popup('Erro', f'Erro ao desconectar: {str(e)}'), 
                0
            )