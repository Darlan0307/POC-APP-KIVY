import oracledb
from typing import Tuple, Union, Any
from utils.helpers import is_select_query


class DatabaseService:
    
    def __init__(self):
        self.connection = None
    
    def test_connection(self, user: str, password: str, dsn: str) -> Tuple[bool, str]:
        try:
            connection = oracledb.connect(user=user, password=password, dsn=dsn)
            connection.close()
            return True, "Conexão realizada com sucesso"
        
        except oracledb.Error as e:
            error_msg = str(e).split('\n')[0]
            return False, error_msg
        
        except Exception as e:
            return False, str(e)
    
    def connect(self, user: str, password: str, dsn: str) -> Tuple[bool, Union[Any, str]]:
        try:
            self.connection = oracledb.connect(user=user, password=password, dsn=dsn)
            return True, self.connection
        
        except oracledb.Error as e:
            error_msg = str(e).split('\n')[0]
            return False, error_msg
        
        except Exception as e:
            return False, str(e)
    
    def set_connection(self, connection):
        self.connection = connection
    
    def execute_query(self, query: str) -> Tuple[bool, str]:
        if not self.connection:
            return False, "Não há conexão ativa com o banco"
        
        try:
            cursor = self.connection.cursor()
            cursor.execute(query)
            
            if is_select_query(query):
                results = cursor.fetchall()
                if results:
                    result_text = self._format_select_results(results)
                    return True, f'Resultado:\n{result_text}'
                else:
                    return True, 'Consulta executada - Nenhum resultado retornado'
            else:
                self.connection.commit()
                return True, f'Comando executado com sucesso\nLinhas afetadas: {cursor.rowcount}'
        
        except oracledb.Error as e:
            error_msg = str(e).split('\n')[0]
            return False, error_msg
        
        except Exception as e:
            return False, str(e)
        
        finally:
            if 'cursor' in locals():
                cursor.close()
    
    def _format_select_results(self, results) -> str:
        formatted_results = []
        for row in results:
            row_str = []
            for value in row:
                if value is None:
                    row_str.append('NULL')
                else:
                    row_str.append(str(value))
            formatted_results.append(' | '.join(row_str))
        
        return '\n'.join(formatted_results)
    
    def disconnect(self):
        if self.connection:
            try:
                self.connection.close()
            except:
                pass 
            finally:
                self.connection = None
    
    def is_connected(self) -> bool:
        return self.connection is not None