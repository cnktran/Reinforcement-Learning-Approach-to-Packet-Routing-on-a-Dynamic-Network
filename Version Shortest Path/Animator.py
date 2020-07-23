import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt 
import matplotlib.image as mgimg
from matplotlib import animation

def animate(frame_ct):
	fig = plt.figure()

	# initiate an empty  list of "plotted" images 
	myimages = []

	#loops through available png:s
	for p in range(0, frame_ct):

	    ## Read in picture
	    fname = "network_images/dynet%i.png" %p 
	    img = mgimg.imread(fname)
	    plt.axis('off')
	    imgplot = plt.imshow(img)

	    # append AxesImage object to the list
	    myimages.append([imgplot])

	## create an instance of animation
	my_anim = animation.ArtistAnimation(fig, myimages, interval=1000, blit=True, repeat_delay=2000)
	Writer = animation.writers['ffmpeg']
	writer = Writer(fps=2, metadata=dict(artist='Me'), bitrate=1800)
	my_anim.save("animation.mp4", writer=writer)