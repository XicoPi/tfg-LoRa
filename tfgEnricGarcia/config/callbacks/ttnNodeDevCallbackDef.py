def devCallback(sens_data: dict) -> int:

    event = -1
    if (sens_data["event"] == "interval"):
        event = 0
    elif (sens_data["event"] == "button"):
        event = 1
    elif (sens_data["event"] == "motion"):
        event = 2

    sens_data["event"] = event
    return sens_data
