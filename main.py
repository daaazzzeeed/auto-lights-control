import settings as s
import loginWindow as lw
import motion_capture as mc


def load_config():
    f = open('settings.txt', 'r')
    data = f.readline().split(';')
    data[2] = data[2].split(',')
    data[0] = int(data[0])
    data[1] = int(data[1])
    data[2] = tuple(map(int, data[2]))
    data[3] = int(data[3]) * 60  # convert minutes to seconds
    return data


def check_if_logged_in():
    f = open('logged_in.txt', 'r')
    data = f.readline()
    if data == 'True':
        return True
    return False
    f.close()


lw.run_login()
logged_in = check_if_logged_in()


if logged_in:
    s.run_settings()
    config = load_config()
    mc.set_call_back()
    try:
        mc.start_detection("dog.mp4", config[0], config[1], config[2], config[3])
    except Exception as e:
        print('Finished with exit values: ' + str(e.args))
