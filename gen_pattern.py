import matplotlib.pyplot as plt
import numpy as np

# Parameters for the checkerboard
rows = 6  # Number of rows (6 squares)
cols = 9  # Number of columns (9 squares)
square_size = 25  # Size of each square in mm

# Convert square size to inches (1 inch = 25.4 mm)
square_size_inch = square_size / 25.4

# Create the checkerboard pattern
checkerboard = np.zeros((rows, cols))
for i in range(rows):
    for j in range(cols):
        if (i + j) % 2 == 0:
            checkerboard[i, j] = 1

# Plot the checkerboard
fig, ax = plt.subplots(figsize=(cols * square_size_inch, rows * square_size_inch))
ax.imshow(checkerboard, cmap='gray', interpolation='nearest')
ax.axis('off')

# Save the checkerboard as a PDF for printing
plt.savefig("checkerboard_9x6_25mm.pdf", bbox_inches='tight', pad_inches=0)
plt.close()

print("Checkerboard saved as 'checkerboard_9x6_25mm.pdf'")