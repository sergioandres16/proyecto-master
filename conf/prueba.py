import pymysql

ip="localhost"
username="root"
paswd="root"
database="pruebafinal"
con = pymysql.connect(host=ip,user= username,password=paswd, db=database)
resultado=[]
try:
    with con.cursor() as cur:
        cur.execute("Select * from usuario where nombre='diego'")
        #resultado.append(cur.fetchone())
        for row in cur:
            print(row)
    with con.cursor() as cur1:
        cur1.execute("Select * from usuario")
    resultado1 = cur1.fetchall()
    
    print(resultado)
    print("\n##########\n")
    print(resultado1)
finally:
	con.close()