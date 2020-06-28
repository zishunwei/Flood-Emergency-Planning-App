import os

from gui import init_gui

def check_files():
    """Check the existence of all files request by the program.

    :return: True or False
        Return True when all files exits, otherwise, return False
    """
    all_file_exist = True
    file_dic = {'SZ.asc': 'Material/elevation/SZ.asc',
                'SZ.prj': 'Material/elevation/SZ.prj',
                'solent_itn.json': 'Material/itn/solent_itn.json',
                'raster-50k_2724246.tif':'Material/background/raster-50k_2724246.tif',
                'isle_of_wight.shp': 'Material/shape/isle_of_wight.shp',
                'isle_of_wight.shx': 'Material/shape/isle_of_wight.shx',
                'isle_of_wight.prj': 'Material/shape/isle_of_wight.prj',
                'isle_of_wight.dbf': 'Material/shape/isle_of_wight.dbf'}
    for key, value in file_dic.items():
        if os.path.exists(value):
            print(key + ' file exists!')
        else:
            all_file_exist = False
            print('Can not find ' + value + 'in root directory')
    return all_file_exist

def main():
    if check_files():
        window = init_gui()
        # Show the window
        window.mainloop()
    else:
        return

if __name__ == '__main__':
    main()

