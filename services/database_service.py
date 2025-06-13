import oracledb
import asyncio
from typing import Tuple, Union, Any, List
from utils.helpers import is_select_query
from utils.logger import logger
from utils.get_oracle_client_path import get_oracle_client_path

oracledb.init_oracle_client(lib_dir=get_oracle_client_path())
class DatabaseService:
    
    def __init__(self):
        self.connection = None
    
    async def test_connection(self, user: str, password: str, dsn: str) -> Tuple[bool, str]:
        
        dsn_formats = self.get_dsn_formats(dsn)

        if not dsn_formats:
            return False, "Formato de DSN inválido"

        for i, dsn_format in enumerate(dsn_formats):
            try:
                
                connection = await asyncio.get_event_loop().run_in_executor(
                    None, 
                    lambda: oracledb.connect(user=user, password=password, dsn=dsn_format)
                )

                connection.close()
                return True, "Conexão realizada com sucesso"
            except oracledb.Error as e:
                logger.error(f"Erro Oracle ao testar conexão com formato {i+1}: {dsn_format} - {str(e)}")
                continue
        
        return False, "Nenhum formato de DSN funcionou"
    
    async def connect(self, user: str, password: str, dsn: str) -> Tuple[bool, Union[Any, str]]:
        dsn_formats = self.get_dsn_formats(dsn)

        if not dsn_formats:
            return False, "Formato de DSN inválido"
        
        for i, dsn_format in enumerate(dsn_formats):
            try:
                self.connection = await asyncio.get_event_loop().run_in_executor(
                    None, 
                    lambda: oracledb.connect(user=user, password=password, dsn=dsn_format)
                )
                return True, self.connection
            except oracledb.Error as e:
                logger.error(f"Erro Oracle ao tentar conectar com formato {i+1}: {dsn_format} - {str(e)}")
                continue

        return False, "Nenhum formato de DSN funcionou"
    
    def set_connection(self, connection):
        self.connection = connection
    
    async def execute_query(self, query: str) -> Tuple[bool, str]:
        if not self.connection:
            return False, "Não há conexão ativa com o banco"
        
        cursor = None
        try:
            def _execute_query():
                nonlocal cursor
                cursor = self.connection.cursor()
                cursor.execute(query)
                
                if is_select_query(query):
                    results = cursor.fetchall()
                    return results
                else:
                    self.connection.commit()
                    return cursor.rowcount
            
            result = await asyncio.get_event_loop().run_in_executor(None, _execute_query)
            
            if is_select_query(query):
                if result:
                    result_text = self._format_select_results(result)
                    return True, f'Resultado:\n{result_text}'
                else:
                    return True, 'Consulta executada - Nenhum resultado retornado'
            else:
                return True, f'Comando executado com sucesso\nLinhas afetadas: {result}'
        
        except oracledb.Error as e:
            error_msg = str(e).split('\n')[0]
            logger.error(f"Erro Oracle ao tentar executar query: {str(e)}")
            return False, error_msg
        
        except Exception as e:
            logger.error(f"Erro Oracle ao tentar executar query: {str(e)}")
            return False, str(e)
        
        finally:
            if cursor:
                await asyncio.get_event_loop().run_in_executor(None, cursor.close)
    
    
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
    
    async def disconnect(self):
        if self.connection:
            try:
                await asyncio.get_event_loop().run_in_executor(None, self.connection.close)
            except Exception as e:
                logger.error(f"Erro ao desconectar: {str(e)}")
                pass
            finally:
                self.connection = None
    
    def is_connected(self) -> bool:
        return self.connection is not None
    
    def get_dsn_formats(self,dsn: str) -> List[str] | None:
        if ':' in dsn and '/' in dsn:
            host_port, service = dsn.split('/', 1)
            host, port = host_port.split(':', 1)
            port = int(port)
        else:
            return None
        
        dsn_formats = [
            dsn,
            f"{host}:{port}/{service}", 
            f"(DESCRIPTION=(ADDRESS=(PROTOCOL=TCP)(HOST={host})(PORT={port}))(CONNECT_DATA=(SERVICE_NAME={service})))",
            f"(DESCRIPTION=(ADDRESS=(PROTOCOL=TCP)(HOST={host})(PORT={port}))(CONNECT_DATA=(SID={service})))",
        ]
        return dsn_formats