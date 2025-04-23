import os
import sys
sys.path.append(os.getcwd())
from Modules.UserInterface import *
userInterface = UserInterface()
UserInterface.iniciar_programa()



############## LAB 5 ################

# from Modules.SliceAdministrator import *
# data = {"nodos": {"Mn11": {"enlaces": ["Mn21", "Mn12"], "config": {"type": "manual", "info_config": ["4", "3221225472", "4294967296"], "imagen": ["cirros"]}}, "Mn12": {"enlaces": ["Mn22", "Mn11"], "config": {"type": "manual", "info_config": ["2", "2147483648", "2147483648"], "imagen": ["cirros"]}}, "Mn21": {"enlaces": ["Mn11", "Mn22"], "config": {"type": "manual", "info_config": ["4", "2147483648", "8589934592"], "imagen": ["cirros"]}}, "Mn22": {"enlaces": ["Mn12", "Mn21"], "config": {"type": "manual", "info_config": ["2", "1073741824", "4294967296"], "imagen": ["cirros"]}}}, "nombre": "slice_prueba1", "ultimo_nodo": 4, "zona": {"nombre": "Pabellón V"}}
1
# sliceAdministrator = SliceAdministrator()
# data_ordenada, result = sliceAdministrator.create_topology(data)

# print("--- RESULTADO FINAL ---")
# if result:
#     print(data_ordenada)
# else:
#     print("==> No es posible instancia esta topología ##")