from kivy.app import App
from kivy.uix.screenmanager import ScreenManager
from kivy.lang import Builder

from screens.login_screen import LoginScreen
from screens.main_screen import MainScreen

from utils.resource_path import resource_path

kv_file = resource_path('app.kv')
Builder.load_file(kv_file)
class OracleApp(App):
    def __init__(self, cmd_user=None, cmd_password=None, cmd_host=None, **kwargs):
        super().__init__(**kwargs)
        self.cmd_user = cmd_user
        self.cmd_password = cmd_password
        self.cmd_host = cmd_host
    
    def build(self):
        sm = ScreenManager()

        login_screen = LoginScreen(name='login',
                                   cmd_user=self.cmd_user,
                                   cmd_password=self.cmd_password,
                                   cmd_host=self.cmd_host)
        
        sm.add_widget(login_screen)
        sm.add_widget(MainScreen(name='main'))
        
        sm.current = 'login'
        
        return sm
    
    def get_application_name(self):        
        return "Gerenciador de Banco de Dados Oracle"
    
    def get_application_version(self):
        return "1.0.0"