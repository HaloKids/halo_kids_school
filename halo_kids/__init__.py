import pymysql

pymysql.version_info = (2, 2, 2, "final", 0) # <--- THIS FIXES THE ERROR
pymysql.install_as_MySQLdb()