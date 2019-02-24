import re

def get_flags(string, flags):
    data = []
    num_flags = len(flags)
    for index, flag in enumerate(flags):
        term = "-{0}".format(flag)
        loc = string.find(term) + len(term) + 1
        if index == num_flags - 1:
            end = len(string)
        else:
            end = string.find("-{0}".format(flags[index + 1]))
        data.append(string[loc:end])
    
    return data

def get_flags_re(string, flags):
    data = []
    for flag in flags:
        ex = "-{0} ([^-]*)".format(flag)
        print(ex)
        data.append(re.fullmatch(ex, string))

    return data

a = "!bet -name OW -multi 2 -options 'win' 'lose'"
af = ["name", "multi", "options"]
for item in get_flags(a, af):
    print(item)