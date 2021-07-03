def devCallback(msg) -> dict:
    string_data = ""
    for byte in msg["bytes"]:
        string_data += ascii.unctrl(byte)

    sens_data_list = string_data.split(",")

    sens_data = {}
    sens_data["ax"] = float(sens_data_list[0])
    sens_data["ay"] = float(sens_data_list[1])
    sens_data["az"] = float(sens_data_list[2])
    sens_data["temp"] = float(sens_data_list[3])
    return sens_data
