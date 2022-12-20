import re

text_file = open("C:\\Users\\Security\\Desktop\\Testobject.txt", "r")
data = text_file.read()
text_file.close()

pattern = '^(?!1\s)([0-9]{1,4})[\s]*([0-9a-zA-Z]*)[\s]*(active|suspended){1}'
vlans = []

for line in data.split("\n"):
    matches = re.finditer(pattern,line)

    for match in matches:
        vlans.append((match.group(1),match.group(2)))

print(vlans)