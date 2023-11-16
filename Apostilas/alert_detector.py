# -*- coding: utf-8 -*-
"""
Class Alert Detector.

This class provides alert detection rules in gas tanks for the project Jabil-Gasview.

Created on Mon Aug  7 15:53:04 2023

@author: Jasmine Moreira
"""

import pandas as pd
import numpy as np

class AlertDetector:
    """A class used to detect operational anomalies in gas tanks.
    
    This class can detect fast pressure variations (slope), steady states that can represent sensor failures (plateau) and ruptures of maximum and minimum limits.

    Attributes
    ----------
    lower_limit : float
        The lower limit for sensor readings, alerts will be generated for readings below this limit.
    upper_limit : float
        The upper limit for sensor readings, alerts will be generated for readings beyound this limit..
    slow_mavg_window : int
        The number of readings used to calculate the slow moving average (slow_mavg).
        The slow_mavg and fast_mavg are necessary for slope and plateau detection.     
    fast_mavg_window : int
        The number of readings used to calculate the fast moving average (fast_mavg).
        The slow_mavg and fast_mavg are necessary for slope and plateau detection. 
    mavg_delta : int    
        The minimum variation of the moving averages delta that defines a fast variation in sensor readings.
        If the difference between slow_mavg and fast_mavg is beyound mavg_delta, a slope alert is generated. 
    plateau_lenght : int
        The minimum number of sensor readings wich defines a plateau situation.     
    plateau_delta : float
        The maximum variation for the difference between slow_mavg and fast_mavg in order to stay into a plateau. 
 
    Methods
    -------
    set_data(data)
        Use to load the data for analysis. The data must be a Pandas Dataframe with a nom empty column named 'values', containing sensor readings. 
    set_lower_limit(lower)
        Use to set the lower_limit for sensor readings.
    set_upper_limit(upper_limit)
        Use to set the upper_limit for sensor readings.
    set_slow_mavg_window(slow_mavg_window)
        Use to set the slow moving average window (used for alert generation).
    set_fast_mavg_window(fast_mavg_window)
        Use to set the fast moving average window (used for alert generation).
    set_mavg_delta(mavg_delta)
        Use to set the moving average minimum delta for slope (fast variation) alert generation.
    set_plateau_length(plateau_lenght)
        Use to set the minimum number of steady readings to generate a plateau alert.
    set_plateau_delta(plateau_delta)
        Use to set the maximum variation for the difference between slow_mavg and fast_mavg in order to stay into a plateau.
    detect_maxmin_rupture()
        Use to detect maximum and minimum limits ruptures in data.
    detect_fast_slope()
        Use to detect fast sensor reading variations in data.
    detect_plateau()
        Use to detect steady reading intervals in data, equal or larger than plateau_lenght.
    detect_all()
        Use to detect all the types of anomalies (max and min rupture, slope and plateau).
    auto_tune()
        Use to set automatically (from data) the lower limit, upper limit and moving average delta values. 
    """
    
    # default parameters for construction
    LOWER_LIMIT = 100
    UPPER_LIMIT = 1300
    SLOW_MAVG_WINDOW = 20
    FAST_MAVG_WINDOW = 5
    MAVG_DELTA = 70
    PLATEAU_LENGTH = 2000
    PLATEAU_DELTA = 2    

    data = None
    def __init__(self):
        """Use to construct the object."""  
        self.set_lower_limit()
        self.set_upper_limit()
        self.set_slow_mavg_window()
        self.set_fast_mavg_window()
        self.set_mavg_delta()
        self.set_plateau_length()
        self.set_plateau_delta() 

    def set_data(self, data)->bool:
        if not isinstance(data, pd.core.frame.DataFrame):
            print('data in not a pandas Dataframe\n')
            return False
        if not 'values' in data:
            print('data has no \'values\' column.\n')
            return False
        if len(data['values'])<=20:
            print('insufficient data in \'values\' column.\n')
            return False            
        self.data = data
        return True
    
    def set_lower_limit(self, lower_limit: float = LOWER_LIMIT)->bool:
        if not isinstance(lower_limit,float) and not isinstance(lower_limit,int):
            print('lower_limit value must be int or float.\n')
            return False
        if not hasattr(self, 'upper_limit'):
            self.upper_limit = float("inf")
        if self.upper_limit <= lower_limit:
            print('lower limit must be smaller than upper limit.\n')
            return False
        self.lower_limit = lower_limit
        return True

    def set_upper_limit(self, upper_limit: float = UPPER_LIMIT)->bool:
        if not isinstance(upper_limit, float) and not isinstance(upper_limit, int):
            print('upper_limit value must be int or float.\n')
            return False
        if self.lower_limit >= upper_limit:
            print('upper limit must be greater than lower limit.\n')
            return False
        self.upper_limit = upper_limit
        return True        
     
    def set_slow_mavg_window(self, slow_mavg_window: int = SLOW_MAVG_WINDOW)->bool:
        if not isinstance(slow_mavg_window,int):
            print('slow_mavg_window value must be int.\n')
            return False
        if not hasattr(self, 'fast_mavg_window'):
            self.fast_mavg_window = 5 # used by class constructor to allow first settings
        if self.fast_mavg_window >= slow_mavg_window:
            print('fast_mavg_window size must be smaller than slow_mavg_window size.\n')
            return False
        if slow_mavg_window < 20:
            print('minimum allowed value for slow_mavg_window is 20.\n')
            return False
        self.slow_mavg_window = slow_mavg_window
        return True

    def set_fast_mavg_window(self, fast_mavg_window: int = FAST_MAVG_WINDOW)->bool:
        if not isinstance(fast_mavg_window,int):
            print('fast_mavg_window value must be int.\n')
            return False
        if self.slow_mavg_window <= fast_mavg_window:
            print('slow_mavg_window size must be greater than fast_mavg_window size.\n')
            return False
        if fast_mavg_window < 5:
            print('minimum allowed value for fast_mavg_window is 5.\n')
            return False
        self.fast_mavg_window = fast_mavg_window
        return True   
 
    def set_mavg_delta(self, mavg_delta: int = MAVG_DELTA)->bool:
        if not isinstance(mavg_delta, float) and not isinstance(mavg_delta, int):
            print('mavg_delta value must be int or float.\n')
            return False
        if 'self.upper_limit' in locals() and 'self.lower_limit' in locals():
            if (self.upper_limit - self.upper_limit) <= mavg_delta:
                print('mavg_delta must be smaller than upper_limit minus lower_limit interval.\n')
                return False
        self.mavg_delta = mavg_delta
        return True
      
    def set_plateau_length(self, plateau_length: int = PLATEAU_LENGTH)->bool:
        if not isinstance(plateau_length, int):
            print('plateau_length value must be int.\n')
            return False
        if plateau_length < 10:
            print('minimum allowed value for plateau_length is 10.\n')
            return False
        self.plateau_length = plateau_length
        return True

    def set_plateau_delta(self, plateau_delta: float = PLATEAU_DELTA)->bool:
        if not isinstance(plateau_delta, float) and not isinstance(plateau_delta, int):
            print('plateau_delta value must be int or float.\n')
            return False
        if plateau_delta < 0:
            print('plateau_delta must be equal or greater than 0.\n')
            return False
        self.plateau_delta = plateau_delta
        return True

    # detect max and min barrier rupture
    def __maxmin_calc__(self, row):
        return 1 if row['values'] < self.lower_limit or row['values'] > self.upper_limit else 0
    
    def detect_maxmin_rupture(self)->bool:
        self.data['maxmin_alert'] = self.data.apply(self.__maxmin_calc__ , axis=1)
        return True

    # detect fast slope 
    def __moving_average__(self,w):
        pad = pd.DataFrame([list(self.data['values'])[-1]]*(w-1))
        mavg = pd.DataFrame(np.convolve(self.data['values'], np.ones(w), 'valid') / w)
        return pd.concat([mavg, pad])
    
    def __mavg_calc__(self):
        data = self.data
        data['slow_ma'] = data['values']
        data['slow_ma'] = self.__moving_average__(self.slow_mavg_window).values    
        data['fast_ma'] = data['values']
        data['fast_ma'] = self.__moving_average__(self.fast_mavg_window).values
        data['delta_ma'] = data['slow_ma'] - data['fast_ma']
    
    def __mavg_delta_calc__(self, row):
        return 1 if row['delta_ma'] < self.mavg_delta*-1 or row['delta_ma'] > self.mavg_delta else 0
    
    def detect_fast_slope(self)->bool:
        self.__mavg_calc__()
        self.data['delta_ma_alert'] = self.data.apply(self.__mavg_delta_calc__ , axis=1)
        return True

    # detect plateau
    def detect_plateau(self)->bool:
        self.__mavg_calc__()
        pcnt = 0
        alert = []
        self.data.reset_index()
        for index,row in self.data.iterrows():
            pcnt = pcnt+1 if abs(row['delta_ma'])<self.plateau_delta else 0
            alert.append(1 if pcnt > self.plateau_length else 0)
        self.data['plateau_alert'] = alert    
        return True

    # detect all alert
    def detect_all(self)->bool:
        self.detect_maxmin_rupture()
        self.detect_fast_slope()
        self.detect_plateau()
        data = self.data
        data['alert'] = np.logical_or(data['maxmin_alert']==1, data['delta_ma_alert']==1)
        data['alert'] = np.logical_or(data['alert']==1, data['plateau_alert']==1)
        return True
    
    def auto_tune(self):
        # TODO TODO TODO
        # check for data
        # chech for parameters vs data (data must be sufficient)
        # max, min, delta as % of (min-max range)     
        # limits calculation
        mean = np.mean(self.data['values'])
        std = np.std(self.data['values'])
        zsc_inf = mean-2.5*std
        zsc_sup = mean+2.5*std
      
        self.set_lower_limit(zsc_inf)
        self.set_upper_limit(zsc_sup)
        self.set_mavg_delta(0.1*(zsc_sup-zsc_inf)) # 10% of the range       









