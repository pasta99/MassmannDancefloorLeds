time_for_completion = 2
framerate = 0.059
fullsize = 100

n_steps = time_for_completion / framerate
print(n_steps)

step_size = fullsize / n_steps
print(step_size)