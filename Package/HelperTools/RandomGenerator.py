# import numpy as np
# from Package.DataStructures.plotDataFormat import LineGraphData, LevelGraphData, VectorGraphData
# import types
# from typing import Any
#
# data_types = dict(line=LineGraphData, level=LevelGraphData, vector=VectorGraphData)
#
#
# class BaseGeneratorException(Exception):
#     """Base High level exception to notify user to errors related to the Generator"""
#
#     def __init__(self, ID: str, obj: Any, message: str):
#         self.ID = ID
#         self.obj = obj
#         self.message = message
#         super().__init__(message)
#
#     def __str__(self):
#         return "Error Message: %s ; @ Error source ID: %s\n " \
#                "The problematic variable can be accessed by catching the Exception and referencing \"exception.obj\"" % (
#                    self.message, self.ID)
#
#
# class DatatypeNotSupportedException(BaseGeneratorException):
#     """High level exception raised when the requested DataType is not supported"""
#
#
# @types.coroutine
# def get_random():
#     cmd = yield "What Data type do you need?"
#     # print("cmd= ", cmd)
#     DS = data_types.get(cmd)
#     data = None
#     if DS:
#         if cmd == "line":
#             RB = DS.get_RB()
#             data = DS(x_Data=RB(size_max=100), y_Data=dict(channel_0=RB(size_max=100),
#                                                            channel_1=RB(size_max=100)))
#             data.x_Data.append(list(np.arange(100)))
#             for id_ in data.y_Data.keys():
#                 data.y_Data[id_].append(np.random.random(100))
#             print(data)
#             yield data
#         elif cmd == "level":
#             data= DS(x_Data=dict(g1=np.array([0, 1, 2, 3]), g2=np.random.uniform(0, 4, 4)),
#                       y_Data=dict(g1=np.random.random(4), g2=np.array([0, 1, 2, 3])))
#             print(data)
#             yield data
#         elif cmd == "vector":
#             X, Y = np.meshgrid(np.linspace(0, 2 * np.pi, 30), np.linspace(0, 2 * np.pi, 30))  # create grid
#             data = DS(x_Data=X, y_Data=Y, u_Data=np.random.random(X.shape), v_Data=np.random.random(Y.shape))
#             print(data)
#             yield data
#         else:
#             print("WTF")
#     else:
#         raise DatatypeNotSupportedException(ID=cmd, obj=data_types, message="Data type is not Supported")
#
# async def userInterface():
#     generator = get_random()
#     print("data results = ", await generator)
#     return "This is too complicated"
#
# if __name__ == '__main__':
#     inter = userInterface()
#     inter.send(None)
#     inter.send("level")
#     inter.send("line")
#     # bank = get_random()
#     # bank.send(None)
#     # while(True):
#     #     try:
#     #         userCmd= input("give you command master: ")
#     #         if userCmd == "stop":
#     #             break
#     #         Result = bank.send(userCmd)
#     #         print(Result)
#     #     except StopIteration:
#     #         pass