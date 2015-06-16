import rospy

from kbhit import getch, kbhit, kbhit_init
from std_msgs.msg import Float64
from sensor_msgs.msg import JointState

#constants
NODE_REFRESH_FREQ = 20.0	# Hz
NODE_NAME = 'rrbot_teleop'

GRIPPER_LEFT_FINGER = '/rrbot/gripper_left_finger_joint_position_controller'
GRIPPER_RIGHT_FINGER = '/rrbot/gripper_right_finger_joint_position_controller'
JOINT1 = '/rrbot/joint1_position_controller'
JOINT2 = '/rrbot/joint2_position_controller'
JOINT3 = '/rrbot/joint3_position_controller'
JOINT_STATES = '/rrbot/joint_states'

GRIPPER = 'gripper'

key_map = { '1': ( JOINT1, False ),
			'2': ( JOINT1, True ),
			'3': ( JOINT2, False ),
			'4': ( JOINT2, True ),
			'5': ( JOINT3, False ),
			'6': ( JOINT3, True ),
			'7': ( GRIPPER, False ),
			'8': ( GRIPPER, True ),
		  }


#global variables
joint_states_dict = dict()
publishers_dict = dict()
publishers_value_dict = dict()

'''
example output from joint_states
header: 
  seq: 4423
  stamp: 
    secs: 90
    nsecs: 374000000
  frame_id: ''
name: ['gripper_left_finger_joint', 'gripper_right_finger_joint', 'joint1', 'joint2', 'joint3']
position: [4.421348976171494e-10, 0.0002607120824378332, -8.165849951780046e-08, -3.274204196657138e-08, 2.4348518756767135e-08]
velocity: [5.56805446627926e-07, 5.478045997894739e-07, 7.927141311369396e-07, -3.525149894199284e-07, -4.920708673459819e-07]
effort: [7.289490076805125e-06, 7.292358025155201e-06, 5.4576164920661085e-06, -6.276336783628267e-07, -0.000487305372764979]
'''

def joint_states_callback( msg ):
	'''
	callback to capture ros publication
	'''

	assert len( msg.name ) == len( msg.position )

	for i in range( len( msg.name ) ):
		joint_states_dict[ '/rrbot/' + msg.name[ i ] + '_position_controller' ] = float( msg.position[ i ] )
	
	if msg.header.seq % 100 == 0:
		print( joint_states_dict )

def main():
	kbhit_init()
	rospy.init_node( NODE_NAME )
	rate = rospy.Rate( NODE_REFRESH_FREQ ) # max frequency of sending target joint positions

	# set publishers
	publishers_dict[ JOINT1 ] = rospy.Publisher( JOINT1 + '/command', Float64, queue_size=10 )
	publishers_dict[ JOINT2 ] = rospy.Publisher( JOINT2 + '/command', Float64, queue_size=10 )
	publishers_dict[ JOINT3 ] = rospy.Publisher( JOINT3 + '/command', Float64, queue_size=10 )
	publishers_dict[ GRIPPER_LEFT_FINGER ] = rospy.Publisher( GRIPPER_LEFT_FINGER + '/command', Float64, queue_size=10 )
	publishers_dict[ GRIPPER_RIGHT_FINGER ] = rospy.Publisher( GRIPPER_RIGHT_FINGER + '/command', Float64, queue_size=10 )

	publishers_value_dict[ JOINT1 ] = 0.0
	publishers_value_dict[ JOINT2 ] = 0.0
	publishers_value_dict[ JOINT3 ] = 0.0
	publishers_value_dict[ GRIPPER_LEFT_FINGER ] = 0.0
	publishers_value_dict[ GRIPPER_RIGHT_FINGER ] = 0.0


	# set subscribers
	rospy.Subscriber( JOINT_STATES, JointState, joint_states_callback )

	while not rospy.is_shutdown():

		# broadcast value
		for t in publishers_dict:
			publishers_dict[ t ].publish( Float64( publishers_value_dict[ t ] ) )

		rate.sleep()

		# check for key
		if not kbhit():
			continue
		
		# got key
		k = getch()
			
		# check if key in dictionary
		if k in key_map:
			topic, up_down = key_map[ k ]
			
			# send message
			if topic == GRIPPER:
				p1 = publishers_value_dict[ GRIPPER_LEFT_FINGER ]
				p2 = publishers_value_dict[ GRIPPER_RIGHT_FINGER ]
				if up_down:
					publishers_value_dict[ GRIPPER_LEFT_FINGER ] = p1 + 0.01
					publishers_value_dict[ GRIPPER_RIGHT_FINGER ] = p2 - 0.01
				else:
					publishers_value_dict[ GRIPPER_LEFT_FINGER ] = p1 - 0.01
					publishers_value_dict[ GRIPPER_RIGHT_FINGER ] = p2 + 0.01
					
			else:
				p = publishers_value_dict[ topic ]
				if up_down:
					publishers_value_dict[ topic ] = p + 0.01
				else:
					publishers_value_dict[ topic ] = p - 0.01

	
	print( 'shutting down teleop' )


if __name__ == '__main__':
	main()
