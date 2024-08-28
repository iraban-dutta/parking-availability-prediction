## End-to-End ML Project: Parking Availability Prediction

<!-- ------------------------------------------------------------------------------------------------ -->
### **Important Links:**
1. [Deployed Web Application](https://parking-availability-prediction.onrender.com/) (Deployment is on a free cloud plan, which may result in slower initial load times)
2. [Technical Blog](https://medium.com/@irabandutta.2020/predicting-parking-space-availability-in-birmingham-085432404d37)


<!-- ------------------------------------------------------------------------------------------------ -->
## Table of Contents:
1. [Introduction](#introduction)
2. [Web Application Snapshot](#web-application-snapshot)
3. [Dataset Overview and Data Cleaning](#dataset-overview-and-data-cleaning)
4. [EDA and Feature Engineering](#eda-and-feature-engineering)
5. [Model Training](#model-training)
6. [Hyperparameter Tuning and Model Selection](#hyperparameter-tuning-and-model-selection)
7. [Deployment](#deployment)
8. [Run Streamlit Web App Locally](#run-streamlit-web-app-locally)

<!-- ------------------------------------------------------------------------------------------------ -->
## **Introduction**

This data science project focuses on predicting parking space availability at different times of the day across various parking lots in Birmingham, UK. Such a model could be integrated into a smart city platform, helping drivers find available parking spots in real time, thereby reducing the time spent searching for parking and lowering emissions from idling vehicles. This work utilizes an [open-source dataset](https://archive.ics.uci.edu/dataset/482/parking+birmingham) from the UCI Machine Learning Repository.

<!-- ------------------------------------------------------------------------------------------------ -->
## **Web Application Snapshot**

<img width="641" alt="image" src="https://github.com/user-attachments/assets/38f4cdc2-4be4-42bb-8bf5-4e51d3817864">

<!-- ------------------------------------------------------------------------------------------------ -->
## **Dataset Overview and Data Cleaning**

The dataset used in this project spans 11 weeks from October 2016 to December 2016, capturing data across 30 parking lots in Birmingham. Each day is divided into 30-minute intervals, from 8:00 AM to 4:30 PM, resulting in 18 data points per day. The first step in any data science project is understanding the data at hand, followed by cleaning it to ensure that the models can learn effectively.

Data Cleaning steps involved:
- Rounding timestamps to the nearest 30 minutes to ensure consistency across the dataset.
- Handling missing values:
  - Completely Missing Days: Imputed by replicating data from the previous or next corresponding weekday.
  - Partially Missing Days: Imputed on a day-by-day basis by employing a combination of backfill and forward-fill strategies.

<!-- ------------------------------------------------------------------------------------------------ -->
## **EDA and Feature Engineering**

### Some key insights from the EDA are documented below:

The parking lot occupancy rate when plotted against time shows strong seasonal patterns. Daily seasonal patterns are seen across all parking lots. Some parking lots exhibit both daily and weekly seasonality as shown below:
<img width="1209" alt="image" src="https://github.com/user-attachments/assets/74a6b71a-3ae9-4627-bb39-1395434d8bc6">

The parking space demand trends are different for weekdays and weekends
![image](https://github.com/user-attachments/assets/4a421f3a-6c12-40ba-9c30-dce4f4721971)

### Feature Engineering:
Simple features were created and they can be categorized into 3 types:
- Day based features (extracted from the timestamp value)
  - Month
  - Day of Month
  - Day of Week
  - isWeekend
- Time based features (extracted from the timestamp value)
  - Hour
  - Minute
- Lag based features
  - Lagged versions of the time series data at different lag intervals served as lagged features

<!-- ------------------------------------------------------------------------------------------------ -->
## **Model Training**

### Deciding the evaluation metric:
RMSE was chosen as the evaluation metric because of the following reasons:
- RMSE gives more weight to large errors, which is crucial when predicting occupancy rates, as significant deviations can lead to a poor user experience in real-world applications.
- The cons of RMSE are not particularly relevant for this project.
  - RMSE is sensitive to outliers but there were no significant outliers in our target variable.
  - RMSE is scale dependent. However since the occupancy rate (which is the target) is a percentage-based variable, the scale-dependent nature of RMSE did not pose any issues.

### Training:
We proceeded with training different classes of models. They can be summarized as:
- Time series-based models: Exponential Smoothing Models (SES, TES), SARIMA
- Regression-based models: Random Forest, XGBoost
- Hybrid Models: These were essentially regression models but we added the output of Exponentially Smoothing Models as input features for the regression model.

<!-- ------------------------------------------------------------------------------------------------ -->
## **Hyperparameter Tuning and Model Selection**

### Hyperparameter Tuning:
After initial experiments with various models, we selected and fine-tuned five specific models for further analysis and evaluation.
- TES: Triple Exponential Smoothing
- RFR: Random Forest Regressor
- XGBR: XGBoost Regressor
- RFR_Hybrid: Random Forest Regressor with TES Model’s output as an input feature
- XGBR_Hybrid: XGBoost Regressor with TES Model’s output as an input feature

### Model Evaluation Process:
The evaluation process involved predicting the occupancy rates for the last week across all the parking lots. Each model thus produced an array of RMSE values corresponding to all the targets. The length of this array was same as the number of parking lots for which predictions were being made. To effectively compare the performance of different models, the following aggregate metrics on the RMSE arrays generated by each model were calculated:

- Mean RMSE: The average RMSE across all the parking lots, providing a general sense of the model’s accuracy.
- Standard Deviation of RMSE: This metric captured the variability in the model’s performance across different parking lots.
- Minimum and Maximum RMSE: These values indicated the best and worst predictions made by the model.
- Percentile-based Range: For each array of RMSE values, the difference between the RMSE value at the 85th percentile and that at the 15th percentile was calculated. This range provided insight into the model’s consistency by showing the spread of RMSE values across most of the parking lots.

### Model Evaluation Summary Table:
<img width="676" alt="image" src="https://github.com/user-attachments/assets/46e09141-4d5f-4714-b771-d30aa3a9b421">

### Model Evaluation Summary Chart:
<img width="1217" alt="image" src="https://github.com/user-attachments/assets/1082a0b5-5e9b-4efd-80ea-8fd5f2aafc9b">

### BEST Model:
The XGBoost Regressor (XGBR) was yielding the best results across all the parking lots. The key highlights of this model were as follows:
- It achieved the lowest mean RMSE value (2.84%) across all the model types.
- It achieved the lowest value for the worst-case RMSE value reported for a parking lot which was 5.45%.
- The spread of the RSME values across all the parking lots was also low as denoted by the standard deviation and percentile-based range values. This ensured that the the variability in the model’s error was low across all the parking lots which implied consistency of performance.

<!-- ------------------------------------------------------------------------------------------------ -->
## **Deployment**

The predictive model was deployed using Streamlit, a popular framework for deploying Machine learning POCs.

### Adding location information:
To enhance the interactivity and user experience of the web application, we utilized an additional [open-source dataset](https://hub.arcgis.com/datasets/bureau::department-for-transport-uk-car-parks/explore?location=52.479720%2C-1.842789%2C12.32) that included latitude and longitude coordinates for parking lots across the UK. By applying simple filters and smart matching techniques, we estimated the coordinates for the parking lots in our dataset based on their capacity information.

### Functioning of the web app:
The user can input any date and time up to one week in the future from the current date. The app then calls the appropriate methods from the PredictOnUserInput class, loading the trained models and generating occupancy rate predictions for each parking lot at the specified time. 

The models forecast the parking lot occupancy rate. The availability rate is calculated by subtracting the occupancy rate from 100%. Each parking lot marker dynamically updates in shape and color to visually represent the current availability rate as shown below.

<img width="654" alt="image" src="https://github.com/user-attachments/assets/c2cca080-9484-4182-a765-d103538103b3">

Additionally, the app features visualizing historical and forecasted trends for individual parking lots. Users can select any parking lot to view a time series plot of the latest week’s occupancy rates, along with the forecasted values leading up to their chosen date and time. This feature provides valuable insights into parking demand trends and helps users make informed decisions about when and where to park.

<img width="674" alt="image" src="https://github.com/user-attachments/assets/0caebf91-58e6-4f5e-b231-2f760af4efb9">


<!-- ------------------------------------------------------------------------------------------------ -->
## **Run Streamlit Web App Locally**

1. Clone the git repository
```bash
git clone <repository-url>
```
2. Descend into the cloned directory and create a virtual environment
```bash
cd <repository-name>

python -m venv venv
```
3. Activate the virtual environment
- macOS:
```bash
source venv/bin/activate
```
- Windows:
```bash
venv\Scripts\activate
```
4. Install the required libraries
```bash
pip install -r requirements.txt
```
5. Start the Streamlit server
```bash
streamlit run app.py
```
6. Access the web application locally at http://127.0.0.1:8501/















