 # Copyright (c) 2022 McCoy Software Solutions
 # Apache License 2.0
from kreature import Kreature

Jim = Kreature("Jim")
Danny = Kreature("Danny")

print(Jim.log[0])
print(Danny.log[0])

whatJimDoes = Jim.decideWhatToDo(Danny)

print("Jim will %s Danny." % whatJimDoes)