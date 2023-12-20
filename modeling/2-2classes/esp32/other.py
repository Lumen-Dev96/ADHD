import os


def read_flash_config(default_config: dict):
    file_list = os.listdir()
    if 'config' in file_list:
        file = None
        try:
            file = open('config', 'r')
            config_str = file.read()
            file.close()
            config = eval(config_str)
            for key in config.keys():
                default_config[key] = config[key]
        except:
            print('Read file error')
            if file is not None:
                file.close()
            file = open('config', 'w')
            file.write(str(default_config))
            file.close()
    else:
        print('No such file')
        file = open('config', 'w')
        file.write(str(default_config))
        file.close()


def update_flash_config(old_config: dict, update_config: dict):
    for key in update_config.keys():
        old_config[key] = update_config[key]
    file = open('config', 'w')
    file.write(str(old_config))
    file.close()
