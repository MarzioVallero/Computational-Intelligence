hintMap = {}
hintMap["pippo"] = []
for i in range(5):
    hintMap["pippo"].append([[1, 2, 3, 4, 5], ["green", "red", "blue", "yellow", "white"], False])
print(hintMap)
hintMap["pippo"][0][0].remove(1)
hintMap["pippo"][0][1].remove("green")
print(hintMap)
