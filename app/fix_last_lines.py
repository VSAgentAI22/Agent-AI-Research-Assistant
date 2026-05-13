with open("app/build_index.py", "r") as f:
    lines = f.readlines()

# remove last 2 broken lines
lines = lines[:-2]

# add correct lines
lines.append('\nif _name_ == "_main_":\n')
lines.append('    build_index()\n')

with open("app/build_index.py", "w") as f:
    f.writelines(lines)

print("Fixed successfully.")
