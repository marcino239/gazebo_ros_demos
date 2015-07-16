#!/usr/bin/python

import sys
import rosbag
import numpy as np
import cPickle as pickle
import rospy

usuage = '''
	bag_query.py bag_file output_file.pkl min_time max_time topic1 [topic2 ...]
'''


def main( argv ):
	if len( argv ) < 6:
		print( usuage )
		return
	
	if argv[2] == '-h':
		print( usuage )
		return

	bag_file = argv[1]
	output_file = argv[2]
	
	# check min time
	min_time_set = True
	if argv[3].lower() == 'min':
		min_time_set = False
	else:
		min_time = rospy.Time.from_sec( float( argv[3] ) )
		
	# check max time
	max_time_set = True
	if argv[4].lower() == 'max':
		max_time_set = False
	else:
		max_time = rospy.Time.from_sec( float( argv[4] ) )
	
	# get list of topics from what ever is left
	topics_full_name = []
	topics = []
	values = []
	for t in argv[ 5: ]:
		topics_full_name.append( t )
		slash_location = t.rfind( '/' )
		topics.append( t[ :slash_location ] )
		values.append( t[ slash_location + 1: ] )

	
	# open bag file
	bag = rosbag.Bag( bag_file )
	
	series = []
	
	# run loop and filter topics, saving them into hdf5 file
	for i in range( len( topics ) ):
		arr = np.empty( (0,2), np.float64 )
		
		for topic, msg, t in bag.read_messages( topics=[ topics[ i ] ] ):
			if min_time_set:
				if t < min_time:
					continue
					
			if max_time_set:
				if t >= max_time:
					continue
					
			val = eval( 'msg.' + values[ i ] )
			arr = np.append( arr, np.array( [[ t.to_time(), val ]] ), axis=0 )

		series.append( arr )


	# output dictionary
	d = { 'topics': topics_full_name, 'data': series }
	pickle.dump( d, open( output_file, 'wb' ) )
	

if __name__ == '__main__':
	main( sys.argv )
