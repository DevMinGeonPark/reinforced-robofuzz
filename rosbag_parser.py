import math
import sqlite3
from rclpy.serialization import deserialize_message
from rosidl_runtime_py.utilities import get_message

def trim_ts(ts, digits=16):
    if len(str(ts)) < digits:
        ts = int(str(ts).zfill(digits))
    else:
        ts = int(str(ts)[:digits])

    return ts


class RosbagParser:
    flag_topic_name = "/listen_flag"
    debug = False

    def __init__(self, db_file):
        self.conn, self.cursor = self.connect(db_file)

        topics = self.get_all_topics()

        self.topic_name_type_map = {
            topic_name: topic_type
            for topic_id, topic_name, topic_type, _, _ in topics
        }

        self.topic_id_name_map = {
            topic_id: topic_name
            for topic_id, topic_name, topic_type, _, _ in topics
        }

        self.topic_name_msg_map = {
            topic_name: get_message(topic_type)
            for topic_id, topic_name, topic_type, _, _ in topics
        }

        self.messages = self.get_all_messages()

        found = self.find_flag_info()
        if not found:
            self.abort = True
        else:
            self.abort = False

    def connect(self, db_file):
        """Make connection to an SQLite database file."""

        conn = sqlite3.connect(db_file)
        c = conn.cursor()

        return conn, c

    def get_all_topics(self):
        """get all topic names and types"""

        self.cursor.execute("SELECT * from topics;")

        rows = self.cursor.fetchall()

        if self.debug:
            for row in rows:
                print(row)

        return rows

    def get_all_messages(self):

        self.cursor.execute("SELECT * from messages;")

        rows = self.cursor.fetchall()

        if self.debug:
            for row in rows:
                print(row)

        return rows

    def find_flag_info(self):
        """Find listen_flag topic id"""
        return True

        found = False
        for topic_id, topic_name in self.topic_id_name_map.items():
            if topic_name == self.flag_topic_name:
                self.flag_topic_id = topic_id
                found = True

        if not found:
            print("[-] listen_flag message is dropped")

        return found

    def process_messages(self) -> dict:
        """
        Retrieve messages published only when listen_flag is activated,
        and deserialize the CDR-formatted data.
        """

        filtered_messages_by_topic = dict()

        """
        start_ts = 0
        end_ts = 0
        listen_flag = False
        for msg_id, topic_id, ts, data in self.messages:
            if topic_id == self.flag_topic_id:
                flag_data = deserialize_message(
                    data, self.topic_name_msg_map[self.flag_topic_name]
                )

                if listen_flag is False:
                    start_ts = flag_data.data
                    listen_flag = True
                else:
                    end_ts = flag_data.data
                    listen_flag = False

                    break

        """

        with open("/tmp/start_ts", "r") as f:
            start_ts = int(f.readline())
        with open("/tmp/end_ts", "r") as f:
            end_ts = int(f.readline())

        # trim/extend digits for comparison
        digits = 16 # 10 + 6 (e.g., 1641420015.780356)
        start_ts = trim_ts(start_ts, digits)
        end_ts = trim_ts(end_ts, digits)

        # print(start_ts, end_ts)

        for msg_id, topic_id, ts, data in self.messages:
            # if topic_id != self.flag_topic_id:
            ts_trimmed = trim_ts(ts, digits)
            if ts_trimmed > start_ts and ts_trimmed < end_ts:
                topic_name = self.topic_id_name_map[topic_id]
                deserialized_data = deserialize_message(
                    data, self.topic_name_msg_map[topic_name]
                )
                if topic_name not in filtered_messages_by_topic:
                    filtered_messages_by_topic[topic_name] = [
                        (ts, deserialized_data)
                    ]
                else:
                    filtered_messages_by_topic[topic_name].append(
                        (ts, deserialized_data)
                    )

        return filtered_messages_by_topic

    def process_all_messages(self) -> dict:
        """
        Retrieve all messages recorded in the rosbag
        and deserialize the CDR-formatted data.
        """

        filtered_messages_by_topic = dict()

        for msg_id, topic_id, ts, data in self.messages:
            topic_name = self.topic_id_name_map[topic_id]
            deserialized_data = deserialize_message(
                data, self.topic_name_msg_map[topic_name]
            )
            if topic_name not in filtered_messages_by_topic:
                filtered_messages_by_topic[topic_name] = [
                    (ts, deserialized_data)
                ]
            else:
                filtered_messages_by_topic[topic_name].append(
                    (ts, deserialized_data)
                )

        return filtered_messages_by_topic


if __name__ == "__main__":
    db3_file = "states-0.bag/states-0.bag_0.db3"
    db3_file = "rosbags/px4-pushup.bag/states-0.bag_0.db3"
    db3_file = "rosbags/states-replay-1641356645.0672185.bag/states-replay-1641356645.0672185.bag_0.db3"
    db3_file = "logs/20220104-204610/rosbags/1641354651.1355603/states-0.bag/states-0.bag_0.db3"
    db3_file = "logs/20220105-165934/rosbags/1641419985.117267/states-0.bag/states-0.bag_0.db3"
    db3_file = "./states-replay-1641419985.117267.bag/states-replay-1641419985.117267.bag_0.db3"
    db3_file = "./states-replay-1641444258.535236.bag/states-replay-1641444258.535236.bag_0.db3"
    db3_file = "logs/20220105-193319/rosbags/1641443932.2358694/states-0.bag/states-0.bag_0.db3"
    db3_file = "scan.bag/scan.bag_0.db3"
    db3_file = "logs/20220128-122952/rosbags/1643407191.4075294/states-0.bag/states-0.bag_0.db3"

    # moveit2
    db3_file = "logs/20220221-120228/rosbags/1645463044.7800531/states-0.bag/states-0.bag_0.db3"
    db3_file = "states-0.bag/states-0.bag_0.db3"
    parser = RosbagParser(db3_file)
    msgs = parser.process_all_messages()
    print(msgs.keys())

    joint_states = msgs["/joint_states"]
    panda_arm_controller_state = msgs["/panda_arm_controller/state"]
    move_action_status = msgs["/move_action/_action/status"]
    motion_plan_requests = msgs["/motion_plan_request"]

    for (ts, cont_state) in panda_arm_controller_state:
        print(cont_state.error.positions)
        print(len(cont_state.error.positions))


    # gc = motion_plan_requests[0][1].goal_constraints[0]
    # print(gc.position_constraints[0].constraint_region.primitive_poses[0].position)
    # print(gc.orientation_constraints[0].orientation)
    # exit(0)

    # print(len(motion_plan_requests))
    # for (ts, mpr) in motion_plan_requests:
        # print(ts)
        # print(mpr)

    # for (ts, cont_state) in panda_arm_controller_state:
        # p = cont_state.actual.positions
        # f = math.degrees
        # # print(f(p[0]), f(p[1]), f(p[2]), f(p[3]), f(p[4]), f(p[5]), f(p[6]))
        # print(p[0], f(p[0]))

    # print(joint_states[0][1].position)
    # print()
    # print(panda_arm_controller_state[0][1])
    # print()
    # print(move_action_status)


    exit(0)

    parser = RosbagParser(db3_file)
    # px4
    msgs = parser.process_messages()

    # tb3
    # msgs = parser.process_all_messages()

    # scan_msgs = msgs["/scan"]
    # for ts, scan in scan_msgs:
        # print(scan)
        # print(max(scan.ranges))

    # gps1 = msgs["/VehicleGpsPosition_PubSubTopic"]
    # gps2 = msgs["/VehicleGlobalPosition_PubSubTopic"]

    # # f_lat = open("gps_lat_comparison", "w")
    # # f_lon = open("gps_lon_comparison", "w")
    # for i in range(min(len(gps1), len(gps2))):
        # # f_lat.write(str(gps1[i][1].lat) + "\t" + str(gps2[i][1].lat) + "\n")
        # # f_lon.write(str(gps1[i][1].lon) + "\t" + str(gps2[i][1].lon) + "\n")
        # print(gps1[i][1].lat, gps1[i][1].lon)
        # print(gps2[i][1].lat * 10000000, gps2[i][1].lon * 10000000)

    # # f_lat.close()
    # # f_lon.close()

    # acceleration (accelerometer values)
    # acc = msgs["/VehicleAcceleration_PubSubTopic"]
    # for m in acc:
        # a_x = m[1].xyz[0]
        # a_y = m[1].xyz[1]
        # a_z = m[1].xyz[2] + 9.8
        # a_hor = math.sqrt(pow(a_x, 2) + pow(a_y, 2))

        # # print(a_z)

        # # if a_z < -4.0:
            # # print("MPC_ACC_UP_MAX violation!", a_z)
        # # if a_z > 3.0:
            # # print("MPC_ACC_DOWN_MAX violation!", a_z)
        # if a_hor > 5.0:
            # print(a_x, a_y, a_z)
            # print("MPC_ACC_HOR_MAX violation!", a_hor)

    mc = msgs["/ManualControlSetpoint_PubSubTopic"]
    for m in mc:
        c_x = m[1].x
        c_y = m[1].y
        c_z = m[1].z
        c_r = m[1].r
        print(c_x, c_y, c_z, c_r)

    # location and speed (odometry)
    # odom_msgs = msgs["/VehicleOdometry_PubSubTopic"]
    # for (ts, odom) in odom_msgs:
        # print(odom.z, odom.vz)

    # acceleration (local position)
    # pos_msgs = msgs["/VehicleLocalPosition_PubSubTopic"]
    # for (ts, pos) in pos_msgs:
        # print(pos.z, pos.vz, pos.az)



