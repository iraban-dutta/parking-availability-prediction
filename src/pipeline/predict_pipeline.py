import sys
import numpy as np
import pandas as pd
# from sklearn.preprocessing import StandardScaler
# import xgboost as xgb
from src.exception import CustomException
from src.utils import load_object


class PredictOnUserInput:

    def __init__(self, date_inp:str, time_inp:str):
        
        self.datetime_inp = pd.to_datetime(date_inp + ' ' + time_inp + ':00')
        self.forecast_index_list = None

        self.data_dict = {}
        self.scaler_dict = {}
        self.model_dict = {}



    def load_artifacts(self):
        
        try:

            # Loading time series data, fitted standard_scaler, fitted XGBoost models
            self.data_dict  = load_object(file_path='artifacts/reg_v1_train_test_dict.pkl')
            self.scaler_dict  = load_object(file_path='artifacts/fit_std_scaler_dict.pkl')
            self.model_dict = load_object(file_path='artifacts/fit_models_best_dict.pkl')

            # Loading Forecast Index and saving in a list
            self.forecast_index_list = self.data_dict[1]['test'].index

        except Exception as e:
            custom_exception =  CustomException(e, sys)
            print(custom_exception)

        

    def get_forecast_steps(self):

        try:
            forecast_steps = np.where(self.forecast_index_list==self.datetime_inp)[0][0] + 1
            return forecast_steps
        
        except Exception as e:
            custom_exception =  CustomException(e, sys)
            print(custom_exception)
        


    def forcast_single_parkLot(self, steps, df_org, std_scaler, model):

        try:

            df_appended = df_org.copy()
            
            for step in range(0, steps):
                # print(forecast_index_list[step])
                
                # Get timestamp to predict for
                sample_ts = self.forecast_index_list[step]

                # Get temporal features
                sample_year = sample_ts.year
                sample_month = sample_ts.month
                sample_day = sample_ts.day
                sample_dayOfWeek = sample_ts.dayofweek
                sample_isWeekend = 1 if sample_dayOfWeek in [5, 6] else 0
                sample_hour = sample_ts.hour
                sample_minute = sample_ts.minute
                
                # DEBUG:
                # print(sample_year, sample_month, sample_day, sample_dayOfWeek, sample_isWeekend, sample_hour, sample_minute)

                # Get lag features
                occu_rt_lag1 = df_appended.iloc[-1].loc['Occupancy_Rate']
                occu_rt_lag2 = df_appended.iloc[-2].loc['Occupancy_Rate']
                occu_rt_lag3 = df_appended.iloc[-3].loc['Occupancy_Rate']
                occu_rt_lag18 = df_appended.iloc[-18].loc['Occupancy_Rate']
                occu_rt_lag19 = df_appended.iloc[-19].loc['Occupancy_Rate']
                occu_rt_lag20 = df_appended.iloc[-20].loc['Occupancy_Rate']

                
                # Framing the dataframe for predict sample
                df_sample = pd.DataFrame(index=[sample_ts], data={'Year':[sample_year], 'Month':[sample_month], 'Day':[sample_day], 
                                                                'DayOfWeek':[sample_dayOfWeek], 'isWeekend':[sample_isWeekend], 
                                                                'Hour':[sample_hour], 'Minute':[sample_minute], 
                                                                'lag_1':[occu_rt_lag1], 'lag_2':[occu_rt_lag2], 'lag_3':[occu_rt_lag3], 
                                                                'lag_18':[occu_rt_lag18], 'lag_19':[occu_rt_lag19],'lag_20':[occu_rt_lag20]})
                
                
                # Scaling the predict sample
                X_sample_scl = std_scaler.transform(df_sample)
                
                # DEBUG:
                # print(df_sample.shape)
                # print(X_sample_scl.shape)
                
                # Get the prediction out
                pred_sample = model.predict(X_sample_scl)
                pred_sample = 0 if pred_sample<0 else (100 if pred_sample>100 else pred_sample) # Cap the output to 0% & 100%
                
                # DEBUG:
                # print(pred_sample)
                
                
                # Add the predicted output to the dataframe so that future points can be predicted
                df_sample['Occupancy_Rate'] = pred_sample
                
            
                # Concatenating to the tail of the original time series 
                df_appended = pd.concat([df_appended, df_sample], axis=0)
                
            
            return df_appended


        except Exception as e:
            custom_exception =  CustomException(e, sys)
            print(custom_exception)    


    def occupancy_to_availability(self, fr_dict):
        
        try:
            fr_mod_dict = {}
            for ps_idx in list(fr_dict.keys()):
                
                fr_mod_dict[ps_idx] = {}
                fr_mod_dict[ps_idx]['train'] = 100.0-fr_dict[ps_idx]['train']
                fr_mod_dict[ps_idx]['test'] = 100-fr_dict[ps_idx]['test']
                fr_mod_dict[ps_idx]['forecast'] = 100-fr_dict[ps_idx]['forecast']

            return fr_mod_dict
    
        except Exception as e:
            custom_exception =  CustomException(e, sys)
            print(custom_exception)    




    def forcast_all_parkLots(self):
        
        try:

            # Load Artifacts
            self.load_artifacts()

            # Get Forecasting steps:
            forecast_nsteps = self.get_forecast_steps()

            # # DEBUG:
            # print('Forecast steps:', forecast_nsteps)
            # print('Park Lot IDs:', list(self.data_dict.keys()))
            # print('Forecast Index List:', self.forecast_index_list)

            
            forecast_dict = {}
            # Forecast for all ParkLots
            for ps_idx in list(self.data_dict.keys())[:]:
                
                df_train_ps = self.data_dict[ps_idx]['train']
                std_scaler = self.scaler_dict[ps_idx]
                xgbr_model = self.model_dict[ps_idx]
                
                # Get forecast
                df_forecasted = self.forcast_single_parkLot(steps=forecast_nsteps, 
                                                            df_org=df_train_ps, 
                                                            std_scaler=std_scaler, 
                                                            model=xgbr_model)
                
                
                # Save the forecasted values
                forecast_dict[ps_idx] = {}
                # forecast_dict[ps_idx]['train'] = df_forecasted['Occupancy_Rate'].iloc[:-forecast_nsteps]
                forecast_dict[ps_idx]['train'] = self.data_dict[ps_idx]['train']['Occupancy_Rate']
                forecast_dict[ps_idx]['test'] = self.data_dict[ps_idx]['test']['Occupancy_Rate']
                forecast_dict[ps_idx]['forecast'] = df_forecasted['Occupancy_Rate'].iloc[-forecast_nsteps:]


            # Get availability
            forecast_availability_dict = self.occupancy_to_availability(forecast_dict)

            # # DEBUG
            # print(forecast_dict[1]['forecast'])
            # print('-'*50)
            # print(forecast_availability_dict[1]['forecast'])
            # print('-'*50)

            return forecast_availability_dict            


        except Exception as e:
            custom_exception =  CustomException(e, sys)
            print(custom_exception)


if __name__=='__main__':

    try: 
    
        predict_obj = PredictOnUserInput(date_inp='2016-12-14', time_inp='15:30')
        test_dict = predict_obj.forcast_all_parkLots()

        print(test_dict.keys())
        print(test_dict[1]['train'].shape)
        print(test_dict[1]['test'].shape)
        print(test_dict[1]['forecast'].shape)

        print('Test-ORIGINAL:')
        print(test_dict[1]['test'].iloc[:34])
        print('-'*50)
        print('Test-FORECAST:')
        print(test_dict[1]['forecast'])
    
    except Exception as e:
        custom_exception =  CustomException(e, sys)
        print(custom_exception)


