def check(config, msg_list, state_dict, feedback_list):
    errs = list()

    msg = msg_list[0]
    msg_name = type(msg).__name__
    topic_name = f"/idltest_{msg_name}_out"

    if topic_name not in state_dict:
        errs.append(f"Topic {topic_name} is lost")
        feedback_list.append(Feedback("TOPIC_LOST", 1.0))

    else:
        # replayed by rclcpp target
        msg_out_list = state_dict[topic_name]

        if len(msg_out_list) != 1:
            print("[-] multiple messages replayed by idl target")
            exit(-1)

        (ts, msg_out) = msg_out_list[0]

        if "Array" not in msg_name:
            # == operator exists for built-in types
            if msg != msg_out:
                errs.append("Sent and replayed messages do not match")
                feedback_list.append(Feedback("TYPE_MISMATCH", calculate_type_diff(msg, msg_out)))
            else:
                feedback_list.append(Feedback("TYPE_MATCH", 0.0))

            # Check max value
            if hasattr(msg, "max_value") and msg.data > msg.max_value:
                errs.append(f"Value {msg.data} exceeds maximum {msg.max_value}")
                feedback_list.append(Feedback("MAX_EXCEEDED", msg.data - msg.max_value))

            # Check min value  
            if hasattr(msg, "min_value") and msg.data < msg.min_value:
                errs.append(f"Value {msg.data} is below minimum {msg.min_value}")
                feedback_list.append(Feedback("MIN_EXCEEDED", msg.min_value - msg.data))

        else:
            # for Array types
            if len(msg.data) != len(msg_out.data):
                errs.append("Sent and replayed array lengths do not match")
                feedback_list.append(Feedback("ARRAY_LENGTH_MISMATCH", abs(len(msg.data) - len(msg_out.data))))
            else:
                type_diff = 0.0
                for i in range(len(msg.data)):
                    if msg.data[i] != msg_out.data[i]:
                        errs.append("Sent and replayed messages do not match")
                        type_diff += calculate_type_diff(msg.data[i], msg_out.data[i])
                feedback_list.append(Feedback("ARRAY_TYPE_MISMATCH", type_diff))

    return errs

def calculate_type_diff(v1, v2):
    if type(v1) != type(v2):
        return 1.0
    elif isinstance(v1, (int, float)):
        return abs(v1 - v2)
    elif isinstance(v1, str):
        return 0.0 if v1 == v2 else 1.0
    else:
        return 0.0