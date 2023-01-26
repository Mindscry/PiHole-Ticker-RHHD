# Starfield generator; uniform speed but increase in star density

import random
import unicornhathd
import time

# Set the brightness of the Unicorn HAT HD
unicornhathd.brightness(0.6)

# Initialize the star count, star speed, and stars list
star_count = 3
star_speed = 0.05
stars = []

# Populate the stars list with initial star coordinates
for i in range(0, star_count):
    stars.append((random.uniform(4, 11), random.uniform(4, 11), 0))

# Initialize the stop flag and start time variables
stop_flag = False
start_time = time.perf_counter()

try:
    while not stop_flag:
        unicornhathd.clear()

        # Get the elapsed time since the start of the script
        elapsed_time = time.perf_counter() - start_time

        # If 60 seconds have passed, set the stop flag to True
        if elapsed_time >= 60:
            stop_flag = True
            unicornhathd.off()
        # If the star count is less than 30 and 2 seconds have passed
        # increment the star count, and add a new star to the stars list
        elif star_count < 30:
            if elapsed_time >= 2:
                star_count += 1
                stars.append((random.uniform(4, 11), random.uniform(4, 11), 0))
                start_time = time.perf_counter()
        # engage        
        for i in range(0, star_count):
            stars[i] = (
                stars[i][0] + ((stars[i][0] - 8.1) * star_speed),
                stars[i][1] + ((stars[i][1] - 8.1) * star_speed),
                stars[i][2] + star_speed * 50)

            if stars[i][0] < 0 or stars[i][1] < 0 or stars[i][0] > 16 or stars[i][1] > 16:
                stars[i] = (random.uniform(4, 11), random.uniform(4, 11), 0)

            v = stars[i][2]

            unicornhathd.set_pixel(stars[i][0], stars[i][1], v, v, v)

        unicornhathd.show()

except KeyboardInterrupt:
    unicornhathd.clear()
    unicornhathd.off()