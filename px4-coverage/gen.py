import os
import subprocess as sp

def cmp_token(a, b):
    a_tokens = a.replace(".info", "").split("-")
    b_tokens = b.replace(".info", "").split("-")

    if a_tokens[1] == b_tokens[1]:
        return int(a_tokens[2]) >= (b_tokens[2])
    else:
        return int(a_tokens[1] >= b_tokens[1])

tracefiles = [f for f in os.listdir("./") if f.endswith(".info")]

tracefiles.sort(
    key=lambda a:float(f'{a.split("-")[1]}.{a.split("-")[2].replace(".info", "")}')
)
print(tracefiles)

for ti, trace in enumerate(tracefiles):
    print(f"{ti} / {len(tracefiles)} {trace}")
    tokens = trace.replace(".info", "").split("-")
    dirname = tokens[1] + "-" + tokens[2]

    gen_cmd = "genhtml "
    gen_cmd += f"{trace} "
    gen_cmd += "--branch-coverage "
    gen_cmd += f"-o {dirname}"

    o = sp.check_output(gen_cmd, shell=True)
    print(o.split(b"\n")[-4:])

    with open("log", "a") as f:
        f.write("-----\n" + trace + "\n")
        for line in o.split(b"\n")[-4:]:
            f.write(line.decode() + "\n")


