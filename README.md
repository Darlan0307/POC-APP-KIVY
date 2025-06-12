## POC - App Desktop Kivy

Nesse projeto estou realizando uma POC para testar a criação de uma aplicação Kivy para gerenciamento de banco de dados Oracle. Os seguintes pontos serão abordados:

- Receber via parâmetros dados de conexão como usuário, host e senha do banco de dados
- Conectar a um banco de dados Oracle com essas credenciais
- Fazer uma consulta qualquer e exibir os dados
- Gerar um executável que não precise de instalação

---

### Telas da aplicação

#### Login

![Tela de Login](./assets/login.png)

#### Execução das queries

![Tela principal](./assets/main.png)

---

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

---

### Criando arquivo de execução do app

#### Windows

```bash
./build.bat # arquivo criado para automatizar o processo
```

#### Linux

```bash
pthon3 build.py # arquivo criado para automatizar o processo
```

---

### Exemplos de scripts SQL

##### Criar tabela se não existir

```sql
CREATE TABLE departamentos (
id NUMBER PRIMARY KEY,
nome VARCHAR2(50) NOT NULL,
gerente VARCHAR2(100),
orcamento NUMBER(12,2)
)
```

##### Inserir dados

```sql

INSERT INTO departamentos VALUES (1,'TI', 'João Silva', 500000.00)
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
