"""
Anything after two slashes is treated as a comment.
"""

filename = 'input.txt'
offset = 12

with open(filename, 'r') as f:
    data = f.read().split('\n')

data = [line.split() for line in data]

for line in data:
    if len(line) >= 2 and line[1] != '//':
        line[1] = int(line[1])
        line[1] += offset
        line[1] = str(line[1])

data = [" ".join(line) for line in data]
data = "\n".join(data)

with open('output.txt', 'w') as f:
    f.write(data)
