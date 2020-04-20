import numpy as np

a = np.ones((8, 8))
t = np.meshgrid((np.arange(4) - 2) % 8, np.arange(4))
a[t] = 2
print(a[t])

print("{0:b}".format(15).rjust(8, "0"))
