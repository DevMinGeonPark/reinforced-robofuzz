def check(config, msg_list, state_dict, feedback_list):
    errs = list()
    msg = msg_list[0]
    msg_name = type(msg).__name__
    topic_name = f"/idltest_{msg_name}_out"

    if topic_name not in state_dict:
        errs.append(f"Topic {topic_name} is lost")
        return errs

    msg_out_list = state_dict[topic_name]
    if len(msg_out_list) != 1:
        errs.append("Multiple messages replayed by idl target")
        return errs

    (ts, msg_out) = msg_out_list[0]
    
    if not hasattr(msg, 'data') or not hasattr(msg_out, 'data'):
        errs.append("Message does not have 'data' attribute")
        return errs

    # 값 범위 검사 (에러 유발 값 허용)
    if isinstance(msg.data, (int, float)) and "Bool" not in msg_name and "Char" not in msg_name:
        min_val = getattr(msg, 'MIN', float('-inf'))
        max_val = getattr(msg, 'MAX', float('inf'))
        if isinstance(min_val, (int, float)) and isinstance(max_val, (int, float)):
            if not (min_val <= msg.data <= max_val):
                errs.append(f"Value {msg.data} is out of valid range for {msg_name}")
    elif isinstance(msg.data, list):
        for i, val in enumerate(msg.data):
            if isinstance(val, (int, float)) and "Bool" not in msg_name and "Char" not in msg_name:
                min_val = getattr(msg, 'MIN', float('-inf'))
                max_val = getattr(msg, 'MAX', float('inf'))
                if isinstance(min_val, (int, float)) and isinstance(max_val, (int, float)):
                    if not (min_val <= val <= max_val):
                        errs.append(f"Value {val} at index {i} is out of valid range for {msg_name}")

    # 타입 검사 (에러 유발 타입 허용)
    if type(msg.data) != type(msg_out.data):
        errs.append(f"Type mismatch: sent {type(msg.data)}, received {type(msg_out.data)}")

    # 값 일치 검사
    if "Array" not in msg_name:
        if msg.data != msg_out.data:
            errs.append(f"IN:{msg.data}|OUT:{msg_out.data} / Sent and replayed messages do not match")
    else:
        if isinstance(msg.data, list) and isinstance(msg_out.data, list):
            if len(msg.data) != len(msg_out.data):
                errs.append("Sent and replayed array lengths do not match")
            else:
                for i in range(len(msg.data)):
                    if msg.data[i] != msg_out.data[i]:
                        errs.append(f"Sent and replayed messages do not match at index {i}")
                        break
        else:
            errs.append("Array data is not of list type")

    return errs

# def check_nested(msg, msg_out, path=""):
#     errs = []
#     if isinstance(msg, (int, float, str, bool)):
#         if msg != msg_out:
#             errs.append(f"Mismatch at {path}: IN:{msg} | OUT:{msg_out}")
#     elif isinstance(msg, list):
#         if not isinstance(msg_out, list):
#             errs.append(f"Type mismatch at {path}: IN:list | OUT:{type(msg_out)}")
#         elif len(msg) != len(msg_out):
#             errs.append(f"Length mismatch at {path}: IN:{len(msg)} | OUT:{len(msg_out)}")
#         else:
#             for i, (in_item, out_item) in enumerate(zip(msg, msg_out)):
#                 errs.extend(check_nested(in_item, out_item, f"{path}[{i}]"))
#     elif hasattr(msg, '__dict__'):
#         if not hasattr(msg_out, '__dict__'):
#             errs.append(f"Type mismatch at {path}: IN:{type(msg)} | OUT:{type(msg_out)}")
#         else:
#             for attr in msg.__dict__:
#                 if not hasattr(msg_out, attr):
#                     errs.append(f"Missing attribute {attr} at {path}")
#                 else:
#                     errs.extend(check_nested(getattr(msg, attr), getattr(msg_out, attr), f"{path}.{attr}"))
#     elif isinstance(msg, (bytes, bytearray)):  # CharFixedArray 처리 추가
#         if msg != msg_out:
#             errs.append(f"Mismatch at {path}: IN:{msg} | OUT:{msg_out}")
#     else:
#         errs.append(f"Unsupported type at {path}: {type(msg)}")
#     return errs

# def check(config, msg_list, state_dict, feedback_list):
#     errs = list()
#     msg = msg_list[0]
#     msg_name = type(msg).__name__
#     topic_name = f"/idltest_{msg_name}_out"

#     if topic_name not in state_dict:
#         errs.append(f"Topic {topic_name} is lost")
#         return errs

#     msg_out_list = state_dict[topic_name]
#     if len(msg_out_list) != 1:
#         errs.append("Multiple messages replayed by idl target")
#         return errs

#     (ts, msg_out) = msg_out_list[0]
    
#     # 구조체 중첩 검사
#     errs.extend(check_nested(msg, msg_out))

#     return errs

# # 테스트를 위한 중첩 구조체 정의
# class NestedStruct:
#     def __init__(self, value):
#         self.data = value

# class OuterStruct:
#     def __init__(self, nested_value, array_value):
#         self.nested = NestedStruct(nested_value)
#         self.array = array_value

# # 테스트 함수
# def test_nested_structures():
#     # 정상 케이스
#     msg = OuterStruct(10, [1, 2, 3])
#     state_dict = {"/idltest_OuterStruct_out": [(0, OuterStruct(10, [1, 2, 3]))]}
#     result = check({}, [msg], state_dict, [])
#     print("Normal case:", result)

#     # 중첩 구조체 값 불일치
#     msg = OuterStruct(10, [1, 2, 3])
#     state_dict = {"/idltest_OuterStruct_out": [(0, OuterStruct(20, [1, 2, 3]))]}
#     result = check({}, [msg], state_dict, [])
#     print("Nested value mismatch:", result)

#     # 배열 불일치
#     msg = OuterStruct(10, [1, 2, 3])
#     state_dict = {"/idltest_OuterStruct_out": [(0, OuterStruct(10, [1, 2, 4]))]}
#     result = check({}, [msg], state_dict, [])
#     print("Array mismatch:", result)

#     # 구조 불일치
#     msg = OuterStruct(10, [1, 2, 3])
#     state_dict = {"/idltest_OuterStruct_out": [(0, NestedStruct(10))]}
#     result = check({}, [msg], state_dict, [])
#     print("Structure mismatch:", result)

# # 테스트 실행
# test_nested_structures()
