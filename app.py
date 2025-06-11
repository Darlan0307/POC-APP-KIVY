from kivy.app import App
from kivy.uix.screenmanager import ScreenManager

from screens.login_screen import LoginScreen
from screens.main_screen import MainScreen


class OracleApp(App):
    
    def build(self):
        sm = ScreenManager()
        
        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(MainScreen(name='main'))
        
        sm.current = 'login'
        
        return sm
    
    def get_application_name(self):
        return "Gerenciador de Banco de Dados Oracle"
    
    def get_application_version(self):
        return "1.0.0"