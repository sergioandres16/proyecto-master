import pymysql

class Conexion:

    def __init__(self):
        pass

    def conectar(self):
        ip="10.20.12.35"
        username="grupo1_final"
        paswd="grupo1_final"
        database="bd_general"
        con = pymysql.connect(host=ip,user= username,password=paswd, db=database)
        return con

    def Select(self,valores,tabla,condicion):
        con=self.conectar()
        resultado=0
        try:
            with con.cursor() as cur:
                if condicion=="-1":
                    cur.execute("Select "+valores+" from " +tabla)
                else:
                    sql="Select "+valores+" from "+tabla+ " where "+condicion
                    #print(sql)
                    cur.execute(sql)
                resultado = cur.fetchall()
        finally:
            con.close()
        return resultado

    def Insert(self,tabla,columna,valores):
        con=self.conectar()
        try:
            with con.cursor() as cur:
                #columna separadas por comas (,)
                #valores separados por comas (,)
                query="Insert into "+tabla+"("+columna+")"+" values ("+valores+")"
                #print(query)
                cur.execute(query)
                id=cur.lastrowid
                con.commit()
                return id
        finally:
            
            con.close()
           
    
    def Update(self,tabla,valores,condicion):
        con=self.conectar()
        try:
            with con.cursor() as cur:
                #valores separados por comas (,)
                #print("Update "+tabla+" set "+valores+" where "+condicion)
                cur.execute("Update "+tabla+" set "+valores+" where "+condicion)
                con.commit()
        finally:
            con.close()

    def Delete(self,tabla,condicion):
        con=self.conectar()
        try:
            with con.cursor() as cur:
                #valores separados por comas (,)
                cur.execute("Delete from "+tabla+" where "+condicion)
                con.commit()
        finally:
            con.close()

    def Consult(self,query):
        con=self.conectar()
        resultado=0
        try:
            with con.cursor() as cur:
                cur.execute(query)
                resultado = cur.fetchall()
        finally:
            con.close()
        return resultado

    def GetMaxVlan(self):
        con=self.conectar()
        try:
            with con.cursor() as cur:
                sql = "select max(vlan_id) as max_vlan from slice"
                cur.execute(sql)
                rows = cur.fetchall()
                return rows
        finally:
            con.close()

class Conexion2():
    def __init__(self):
        pass

    def conectar(self):
        ip="10.20.12.35"
        username="grupo1_final"
        paswd="grupo1_final"
        database="bd_cluster_final"
        con = pymysql.connect(host=ip,user= username,password=paswd, db=database)
        return con

    def Select(self,valores,tabla,condicion):
        con=self.conectar()
        resultado=0
        try:
            with con.cursor() as cur:
                if condicion=="-1":
                    cur.execute("Select "+valores+" from " +tabla)
                else:
                    sql="Select "+valores+" from "+tabla+ " where "+condicion
                    #print(sql)
                    cur.execute(sql)
                resultado = cur.fetchall()
        finally:
            con.close()
        return resultado

    def Insert(self,tabla,columna,valores):
        con=self.conectar()
        try:
            with con.cursor() as cur:
                #columna separadas por comas (,)
                #valores separados por comas (,)
                query="Insert into "+tabla+"("+columna+")"+" values ("+valores+")"
                #print(query)
                cur.execute(query)
                id=cur.lastrowid
                con.commit()
                return id
        finally:
            
            con.close()
           
    
    def Update(self,tabla,valores,condicion):
        con=self.conectar()
        try:
            with con.cursor() as cur:
                #valores separados por comas (,)
                #print("Update "+tabla+" set "+valores+" where "+condicion)
                cur.execute("Update "+tabla+" set "+valores+" where "+condicion)
                con.commit()
        finally:
            con.close()

    def Delete(self,tabla,condicion):
        con=self.conectar()
        try:
            with con.cursor() as cur:
                #valores separados por comas (,)
                cur.execute("Delete from "+tabla+" where "+condicion)
                con.commit()
        finally:
            con.close()

    def Consult(self,query):
        con=self.conectar()
        resultado=0
        try:
            with con.cursor() as cur:
                cur.execute(query)
                resultado = cur.fetchall()
        finally:
            con.close()
        return resultado

    def GetMaxVlan(self):
        con=self.conectar()
        try:
            with con.cursor() as cur:
                sql = "select max(vlan_id) as max_vlan from slice"
                cur.execute(sql)
                rows = cur.fetchall()
                return rows
        finally:
            con.close()

