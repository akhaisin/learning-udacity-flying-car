import argparse
import logging
import time
from collections import deque
from enum import Enum
from typing import List, Deque

import numpy as np
from udacidrone import Drone
from udacidrone.connection import Connection, MavlinkConnection
from udacidrone.messaging import MsgID


def logger():
    return logging.getLogger(__name__)

class States(Enum):
    MANUAL = 0
    ARMING = 1
    TAKEOFF = 2
    WAYPOINT = 3
    LANDING = 4
    DISARMING = 5


class BackyardFlyer(Drone):

    def __init__(self, connection: Connection):
        super().__init__(connection)
        self.target_position = np.array([0.0, 0.0, 0.0], dtype=float)
        self.all_waypoints: Deque[List[float]] = deque()
        self.in_mission = True
        self.check_state = {}

        # initial state
        self.flight_state: States = States.MANUAL

        self.register_callback(MsgID.LOCAL_POSITION, self.local_position_callback)
        self.register_callback(MsgID.LOCAL_VELOCITY, self.velocity_callback)
        self.register_callback(MsgID.STATE, self.state_callback)

    def local_position_callback(self):
        """
        This triggers when `MsgID.LOCAL_POSITION` is received and self.local_position contains new data
        """
        logger().debug("local position callback: local_position=%s", self.local_position)

        if self.flight_state == States.TAKEOFF:
            takeoff_percentage = -1.0 * self.local_position[2] / self.target_position[2]
            logger().info('takeoff percentage: %s', takeoff_percentage)
            if takeoff_percentage > 0.95:
                self.all_waypoints = deque(self.calculate_box())
                logger().info('waypoints number: %s', len(self.all_waypoints))
                self.waypoint_transition()
        elif self.flight_state == States.WAYPOINT:
            distance_to_target = np.linalg.norm(self.target_position[0:2] - self.local_position[0:2])
            logger().info('distance to target: %s', distance_to_target)
            if distance_to_target < 1.0:
                if len(self.all_waypoints) > 0:
                    self.waypoint_transition()
                else:
                    if np.linalg.norm(self.local_velocity[0:2]) < 1.0:
                        self.landing_transition()

    def velocity_callback(self):
        """
        This triggers when `MsgID.LOCAL_VELOCITY` is received and self.local_velocity contains new data
        """
        logger().debug("velocity callback: local_velocity=%s", self.local_velocity)

        # When the drone is landing, check if the drone altitude is close to 0
        if self.flight_state == States.LANDING:
            if self.global_position[2] - self.global_home[2] < 0.1:
                if abs(self.local_position[2]) < 0.05:
                    self.disarming_transition()

    def state_callback(self):
        """
        This triggers when `MsgID.STATE` is received and self.armed and self.guided contain new data
        """
        logger().debug("state callback: armed=%s, guided=%s, state_time=%s, status=%s", self.armed, self.guided, self.state_time, self.status)

        if self.in_mission:
            if self.flight_state == States.MANUAL:
                self.arming_transition()
            elif self.flight_state == States.ARMING:
                if self.armed:
                    self.takeoff_transition()
            elif self.flight_state == States.DISARMING:
                if not self.armed and not self.guided:
                    self.manual_transition()

    def calculate_box(self) -> List[List[float]]:
        """
        1. Return waypoints to fly a box
        """
        local_waypoints = [[10.0, 0.0, 3.0], [10.0, 10.0, 3.0], [0.0, 10.0, 3.0], [0.0, 0.0, 3.0]]
        return local_waypoints

    def arming_transition(self):
        """
        1. Take control of the drone
        2. Pass an arming command
        3. Set the home location to current position
        4. Transition to the ARMING state
        """
        logger().info("arming transition")

        self.take_control()
        self.arm()
        self.set_home_position(self.global_position[0],
                               self.global_position[1],
                               self.global_position[2])

        self.flight_state = States.ARMING
        

    def takeoff_transition(self):
        """
        1. Set target_position altitude to 3.0m
        2. Command a takeoff to 3.0m
        3. Transition to the TAKEOFF state
        """
        logger().info("takeoff transition")
        
        target_altitude = 3.0
        self.target_position[2] = target_altitude
        self.takeoff(target_altitude)
        self.flight_state = States.TAKEOFF

    def waypoint_transition(self):
        """
        1. Command the next waypoint position
        2. Transition to WAYPOINT state
        """
        logger().info("waypoint transition")

        self.target_position = self.all_waypoints.popleft()
        logger().info('target position: %s', self.target_position)
        logger().info('waypoint left: %s', len(self.all_waypoints))

        # Calculate heading, so drone will fly forward to the target position
        heading = np.arctan2(self.target_position[1] - self.local_position[1], self.target_position[0] - self.local_position[0])
        self.cmd_position(self.target_position[0], self.target_position[1], self.target_position[2], heading)

        self.flight_state = States.WAYPOINT

    def landing_transition(self):
        """
        1. Command the drone to land
        2. Transition to the LANDING state
        """
        logger().info("landing transition")

        self.land()
        self.flight_state = States.LANDING

    def disarming_transition(self):
        """
        1. Command the drone to disarm
        2. Transition to the DISARMING state
        """
        logger().info("disarm transition")
        
        self.disarm()
        self.release_control()
        self.flight_state = States.DISARMING

    def manual_transition(self):
        """This method is provided
        
        1. Release control of the drone
        2. Stop the connection (and telemetry log)
        3. End the mission
        4. Transition to the MANUAL state
        """
        logger().info("manual transition")

        self.release_control()
        self.stop()
        self.in_mission = False
        self.flight_state = States.MANUAL

    def start(self):
        """This method is provided
        
        1. Open a log file
        2. Start the drone connection
        3. Close the log file
        """
        logger().info("Creating log file")
        self.start_log("Logs", "NavLog.txt")
        logger().info("starting connection")
        self.connection.start()
        logger().info("Closing log file")
        self.stop_log()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=5760, help='Port number')
    parser.add_argument('--host', type=str, default='127.0.0.1', help="host address, i.e. '127.0.0.1'")
    parser.add_argument('--debug', action="store_const", dest="loglevel", const=logging.DEBUG, default=logging.INFO)
    args = parser.parse_args()

    LOGGING_FORMAT = '%(asctime)s %(name)s %(levelname)s %(message)s'
    logging.basicConfig(format=LOGGING_FORMAT, level=args.loglevel)

    conn = MavlinkConnection('tcp:{0}:{1}'.format(args.host, args.port), threaded=False, PX4=False)
    drone = BackyardFlyer(conn)
    time.sleep(2)
    
    # Starts message loop.
    # LOCAL_POSITION and LOCAL_VELOCITY messages are received when the drone coordinates message received.
    # STATE messages are received when the drone state message received.
    drone.start()

