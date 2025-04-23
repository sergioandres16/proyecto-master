from Conexion import *
class Listar:
    def Imagen():
        resultado=Conexion.Select("*","imagen","-1")

        return resultado
    def Topologia():
        resultado=Conexion.Select("*","topologia","-1")
        return resultado
    def Ram():
        resultado=Conexion.Select("*","ram","-1")
        return resultado