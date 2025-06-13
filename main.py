import sys
from app import OracleApp

if __name__ == '__main__':
    user = password = host = None

    if len(sys.argv) >= 4:
        user = sys.argv[1]
        password = sys.argv[2]
        host = sys.argv[3]

    OracleApp(cmd_user=user, cmd_password=password, cmd_host=host).run()