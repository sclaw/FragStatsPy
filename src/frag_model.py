import os
import subprocess
import shutil
import sqlite3
import pandas as pd
from osgeo import gdal


class FragModel:


    strategy_code_dict = {None: 'NSTD',
                          'window': 'XMWA',
                          'user_tiles': 'XUPT',
                          'uniform_tiles': 'XUNI',
                          'user_pts': 'PUPP',
                          'random_overlap': 'RWOV',
                          'random_no_overlap': 'RNOV'}
    strategy_num_dict = {None: 1,
                         'window': 2,
                         'user_tiles': 3,
                         'uniform_tiles': 4,
                         'user_pts': 5,
                         'random_overlap': 6,
                         'random_no_overlap': 7}

    def __init__(self, path, exe_path=r'C:\Program Files\Fragstats 4.2\frg_cmd.exe') -> None:
        self.name = os.path.basename(path)[:-3]
        self.db_path = path

        if not os.path.exists(self.db_path):
            print(f'Initializing model at {self.db_path}')
            shutil.copyfile(os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'model_template.db')), self.db_path)
        
        self.db = sqlite3.connect(self.db_path)

        self.exe_path = exe_path
        if not os.path.exists(self.exe_path):
            raise RuntimeError(f'Fragstats executable was not found at: {self.exe_path}\nPlease specify the fragstats executable path using the exe_path argument')

    def set_output_base_path(self, path):
        self.db.execute(f'UPDATE frg_table_strings SET value = "{path}" WHERE string_name = "OUTPUT_FOLDER_PATH"')
        self.db.commit()

    def set_sampling_strategy(self, strategy=None, cell=False, patch=False, landscape=False):        
        for run, level in zip([cell, patch, landscape], ['CELL', 'PATCH', 'LANDS']):
            if run:
                options_string = f'DO_{self.strategy_code_dict[strategy]}_{level}_LEVEL_STATS'
                self.db.execute(f'UPDATE frg_table_options SET value = 1 WHERE option_name = "{options_string}"')
        self.db.execute(f'UPDATE frg_table_numerics SET value = {self.strategy_num_dict[strategy]} WHERE numeric_name = "ANALYSIS_TYPE"')
        self.db.commit()

    def set_user_provided_tiles(self, path):
        string = f'{path}, x, 999, x, x, 1, x, IDF_GeoTIFF'
        self.db.execute(f'UPDATE frg_table_strings SET value = "{string}" WHERE string_name = "XUPT_GRID_INFO"')
        self.db.commit()

    def toggle_metric(self, level, metric, stat=None, on=True):
        metric_name = f'{level.lower()}{metric.upper()}'
        if stat:
            metric_name = f'{metric_name}_{stat.upper()}'
        if on:
            value = 1
        else:
            value = 0

        # Check if metric is valid
        metric_row = self.db.execute(f'SELECT "Row Found" FROM frg_table_metrics WHERE metric_name = "{metric_name}"').fetchall()
        assert len(metric_row) != 0, f"Metric {metric_name} is not a valid Fragstats metric"
        
        self.db.execute(f'UPDATE frg_table_metrics SET value = "{value}" WHERE metric_name = "{metric_name}"')
        self.db.commit()
    
    def run_command(self, command):
        self.db.execute(command)
        self.db.commit()

    def load_landscape_layer(self, in_path, allow_class_zero=1, background_value=999):
        print(f'Loading landscape later at {in_path}')
        landscape = dict()
        dataset = gdal.Open(in_path)
        band = dataset.GetRasterBand(1)
        band.ComputeStatistics(0)
        transform = dataset.GetGeoTransform()

        landscape['name_external'] = in_path
        landscape['io_info'] = '[BAND:1]'
        landscape['driver_lib'] = 'GDAL'
        landscape['driver_name'] = 'GeoTIFF grid (.tif)'
        landscape['driver_id'] = '63B45E15-C8E5-44f6-A9AB-60E1852CDB5D'
        landscape['col_count'] = dataset.RasterXSize
        landscape['row_count'] = dataset.RasterYSize
        pixel_width = transform[1]
        pixel_height = transform[5]
        assert abs(pixel_width) == abs(pixel_height), 'Fragstats requires square cells'
        landscape['cell_size'] = abs(pixel_height)
        landscape['xll'] = transform[0]
        landscape['yll'] = transform[3]
        landscape['xur'] = landscape['xll'] + (landscape['col_count'] * pixel_width)
        landscape['yur'] = landscape['yll'] + (landscape['row_count'] * pixel_height)
        landscape['no_data_value'] = band.GetNoDataValue()
        landscape['allow_class_zero'] = allow_class_zero
        landscape['background_value'] = background_value
        landscape['id'] = 1
        landscape['model_id'] = 1
        landscape['name_internal'] = ''

        col_string = ', '.join(landscape.keys()) 
        val_string = '", "'.join([str(i) for i in landscape.values()])
        self.db.execute(f'INSERT OR REPLACE INTO frg_landscape_layers({col_string}) VALUES("{val_string}")')
        for key, val in landscape.items():
            self.db.execute(f'UPDATE frg_landscape_layers SET {key} = "{val}"')
        self.db.execute('INSERT OR REPLACE INTO sqlite_sequence(name, seq) VALUES("frg_landscape_layers", "1")')
        self.db.commit()
    
    def run_model(self):
        print('Running model')
        subprocess.run([self.exe_path, '/m', self.db_path])

