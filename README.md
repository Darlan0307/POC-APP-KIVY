## POC - App Desktop Kivy

### Etapas para executar

> Necessário ter o [python3](https://www.python.org/downloads/) e o [docker](https://docs.docker.com/engine/install/) instalados

##### Criar e ativar ambiente virtual

```bash
python3 -m venv venv
source venv/bin/activate
```

##### Instalar dependências

```bash
 pip install -r requirements.txt
```

##### Rodar o banco de testes

```bash
 docker run -d \
 --name oracle-free \
 -p 1521:1521 \
 -e ORACLE_PASSWORD=MinhaSenh@123 \
 -v oracle-data:/opt/oracle/oradata \
 gvenzl/oracle-free:23-slim
```

##### Verificar se o banco está pronto para uso

```bash
docker logs -f oracle-free

# Deve aparecer a mensagem:
# DATABASE IS READY TO USE!
```

##### Rodar o aplicativo

```bash
python3 main.py
```

##### Informações de conexão

- Usuário: system
- Senha: MinhaSenh@123
- Host: localhost:1521/FREE

### Exemplos de scripts SQL

##### Criar tabela se não existir

```sql
CREATE TABLE IF NOT EXISTS departamentos (
id NUMBER PRIMARY KEY AUTO_INCREMENT,
nome VARCHAR2(50) NOT NULL,
gerente VARCHAR2(100),
orcamento NUMBER(12,2)
)
```

##### Inserir dados

```sql

INSERT INTO departamentos VALUES ('TI', 'João Silva', 500000.00)
```

##### Visualizar dados

```sql
SELECT * FROM departamentos
```

#### Caso queira apagar o banco

```bash
docker stop oracle-free
docker rm oracle-free
docker volume rm oracle-data
```

---

#### Erros comuns

##### Caso apareça o error "MTDev is not supported by your version of linux"

```bash
sudo apt-get install libmtdev-dev
```

##### Caso apareça o error "Unable to find any valuable Cutbuffer provider."

```bash
sudo apt-get install xclip xsel
```
