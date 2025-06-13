import asyncio
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.screenmanager import Screen
from kivy.clock import Clock

from services.database_service import DatabaseService
from utils.helpers import show_popup


class MainScreen(Screen):
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db_service = DatabaseService()
        self.connection = None
        self.db_user = ''
        self.db_host = ''
        self._is_executing = False
        self._build_interface()
    
    def _build_interface(self):
        main_layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
      
        header_layout = self._create_header_layout()
        main_layout.add_widget(header_layout)
        
        title_label = Label(
            text='App Oracle Database',
            size_hint_y=None,
            height=50,
            font_size=24
            
        )
        main_layout.add_widget(title_label)
        
        query_layout = self._create_query_layout()
        main_layout.add_widget(query_layout)
        
        self.result_label = Label(
            text='Resultado das consultas aparecerá aqui',
            text_size=(None, None),
            halign='left',
            valign='top'
        )
        main_layout.add_widget(self.result_label)
        
        self.add_widget(main_layout)
    
    def _create_header_layout(self):
        header_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=50)
        
        self.connection_info = Label(
            text='Não conectado',
            font_size=16
        )
        header_layout.add_widget(self.connection_info)
        
        disconnect_button = Button(
            text='Desconectar',
            size_hint_x=None,
            width=120
        )
        disconnect_button.bind(on_press=self.disconnect)
        header_layout.add_widget(disconnect_button)
        
        return header_layout
    
    def _create_query_layout(self):
        query_layout = BoxLayout(orientation='vertical', spacing=10)
        
        query_layout.add_widget(Label(text='Consulta SQL:', size_hint_y=None, height=30))
        
        self.query_input = TextInput(
            hint_text='Digite sua consulta SQL aqui...',
            multiline=True,
            size_hint_y=None,
            height=150
        )
        query_layout.add_widget(self.query_input)
        
        execute_button = Button(text='Executar Consulta', size_hint_y=None, height=40)
        execute_button.bind(on_press=self.execute_query)
        query_layout.add_widget(execute_button)
        
        return query_layout
    
    def set_connection_info(self, user, host, connection):
        self.db_user = user
        self.db_host = host
        self.connection = connection
        self.db_service.set_connection(connection)
        self.connection_info.text = f'Conectado como: {user}@{host}'
    
    def execute_query(self, instance):
        if self._is_executing:
            return
        
        if not self.connection:
            show_popup('Erro', 'Não há conexão ativa com o banco')
            return
        
        query = self.query_input.text.strip()
        if not query:
            show_popup('Erro', 'Digite uma consulta SQL')
            return

        asyncio.create_task(self.execute_query_async(query))
    
    async def execute_query_async(self, query: str):
        try:
            self._is_executing = True
            
            success, result = await self.db_service.execute_query(query)
            
            if success:
                self.result_label.text = result
            else:
                self.result_label.text = f'Erro SQL: {result}'
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

    def disconnect(self, instance):
        if self._is_executing:
            return
        
        if self.connection:
            asyncio.create_task(self.disconnect_async())
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