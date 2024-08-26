import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import folium
from streamlit_folium import st_folium
import branca.colormap as cm
import io
import base64
from src.exception import CustomException
from src.pipeline.predict_pipeline import PredictOnUserInput



APP_TITLE = 'Birmingham Parking Availability Prediction'
APP_SUB_TITLE = 'The below map displays the coordinates of various parking lots in Birmingham, UK. Please select a date and time to view the forecasted availability across all parking lots. Additionally, you can choose individual parking lots below the map to explore its historical and projected trends.'


# Create initial map on Application Loading
def create_initial_map(df_ps_lat_long):

    try:

        min_lat, max_lat = df_ps_lat_long['Latitude'].min(), df_ps_lat_long['Latitude'].max()
        min_long, max_long = df_ps_lat_long['Longitude'].min(), df_ps_lat_long['Longitude'].max()

        # Create a base map centered around Birmingham, UK with specified zoom levels
        m = folium.Map(
            location=[(min_lat + max_lat) / 2, (min_long + max_long) / 2], 
            zoom_start=12, 
            min_zoom=12,  
            max_zoom=16,
        )

        for i, lot in df_ps_lat_long.iterrows():

            # Create a tooltip showing relevant information
            tooltip_content = f"""
                <div style="text-align: center;">
                    <strong>Parking Lot ID:</strong> {int(lot['ps_idx'])}<br>
                    <strong>Capacity:</strong> {int(lot['Capacity'])}<br>
                </div>
                """

            custom_tooltip = folium.Tooltip(tooltip_content, sticky=True)


            folium.CircleMarker(
                location=[lot['Latitude'], lot['Longitude']],
                # Border
                color='black',
                weight=2,
                opacity=1,
                # Marker Size and color
                radius=10,
                fill=True,
                fill_color='skyblue',
                fill_opacity=0.7,

                # Marker Tooltip
                # tooltip=f"Parking Lot Capacity: {int(lot['Capacity'])}",
                tooltip = custom_tooltip,

            ).add_to(m)

        return m

    except Exception as e:
        custom_exception =  CustomException(e, sys)
        print(custom_exception)





# Create map POST forecasting
def create_post_prediction_map(df_ps_lat_long_avail, colormap_inp):

    try:

        min_lat, max_lat = df_ps_lat_long_avail['Latitude'].min(), df_ps_lat_long_avail['Latitude'].max()
        min_long, max_long = df_ps_lat_long_avail['Longitude'].min(), df_ps_lat_long_avail['Longitude'].max()

        # Create a base map centered around Birmingham, UK with specified zoom levels
        m = folium.Map(
            location=[(min_lat + max_lat) / 2, (min_long + max_long) / 2], 
            zoom_start=12, 
            min_zoom=12,  
            max_zoom=16,
        )


        for i, lot in df_ps_lat_long_avail.iterrows():

            parking_lot_space_avail = round(lot['Availability'], 1)

            # Determie radius based on availability
            radius_tuned = 5 + ((parking_lot_space_avail)**0.6)

            # Determine color based on availability
            color_tuned = colormap_inp(parking_lot_space_avail)


            # Create a tooltip showing relevant information
            tooltip_content = f"""
                <div style="text-align: center;">
                    <strong>Parking Lot ID:</strong> {int(lot['ps_idx'])}<br>
                    <strong>Capacity:</strong> {int(lot['Capacity'])}<br>
                    <strong>Availability:</strong> {parking_lot_space_avail}%<br>
                </div>
                """

            custom_tooltip = folium.Tooltip(tooltip_content, sticky=True)


            folium.CircleMarker(
                location=[lot['Latitude'], lot['Longitude']],
                # Border
                color='black',
                weight=1.5,
                opacity=1,
                # Marker Size and color
                radius=radius_tuned,
                fill=True,
                fill_color=color_tuned,
                fill_opacity=0.9,

                # Marker Tooltip
                # tooltip=f"Parking Lot Capacity: {int(lot['Capacity'])}",
                tooltip=custom_tooltip,

                # Marker Popup
                # popup=f"Availability: {round(lot['Availability'], 1)}%",

            ).add_to(m)

        # # Add a color bar to the map
        # colormap.caption = 'Availability (%)'
        # m.add_child(colormap)

        return m
    
    except Exception as e:
        custom_exception =  CustomException(e, sys)
        print(custom_exception)




def generate_plot(historical_data, forecasted_data, ps_idx):

    try:

        fig, ax = plt.subplots(figsize=(11, 7))

        # Plot historical and forecasted data
        ax.plot(historical_data.index, historical_data.values, label='Historical', marker='o', linewidth=2.5)
        ax.plot(forecasted_data.index, forecasted_data.values, label='Forecasted', linestyle='--', marker='o',linewidth=2.5)
        ax.set_xlabel('DateTime', fontsize=18)
        ax.set_ylabel('Occupancy(%)', fontsize=18)
        ax.set_title(f'PARK_ID {ps_idx}: Historical and Forecasted Occupancy (%)', fontweight='bold', fontsize=20)
        ax.legend()
        ax.grid(True)

        # Save the plot to a buffer
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        # Convert the buffer to a base64 string
        img_base64 = base64.b64encode(buf.read()).decode('utf-8')
        buf.close()

        # Display the plot in Streamlit
        st.markdown(f'<img src="data:image/png;base64,{img_base64}" style="width:100%;height:auto;">', unsafe_allow_html=True)

    except Exception as e:
        custom_exception =  CustomException(e, sys)
        print(custom_exception)





# Create the colorbar as a custom HTML string
def create_colorbar_html(colormap):

    try:

        colormap.caption = "Parking Availability (%)"
        colormap_html = colormap._repr_html_()
        return f'<div style="text-align: center;">{colormap_html}</div>'
    
    except Exception as e:
        custom_exception =  CustomException(e, sys)
        print(custom_exception)



# Run the prediction model and fetch forecasts for all parking lots
def forecast(user_inp_date:str, user_inp_time:str):
    try:
        predict_obj = PredictOnUserInput(date_inp=user_inp_date, time_inp=user_inp_time)
        forecast_ps_avail_dict = predict_obj.forcast_all_parkLots()

        return forecast_ps_avail_dict
    except Exception as e:
        custom_exception =  CustomException(e, sys)
        print(custom_exception)



def main():

    try:
        
        # Page configuration for wide layout
        st.set_page_config(APP_TITLE, layout="centered")

        # Applying custom CSS for consistent padding and title styling
        st.markdown("""
            <style>
                .title {
                    font-size: 2rem;
                    font-weight: bold;
                    text-align: center;
                    color: #1892BA; /* Optional: Adjust text color */
                }
                .subtitle {
                text-align: center;
                font-size: 1.2rem; /* Adjust font size here */
                color: #060608; /* Optional: Adjust text color */
                }
                .stSidebar {
                    background-color: #f0f2f6;
                    padding: 1rem;
                }
                .stButton button {
                    width: 60%;
                    padding: 0.75rem;
                    background-color: red;
                    color: white !important;
                    border-radius: 0.5rem;
                    margin: 1rem auto;
                    cursor: pointer;
                    border: none;
                    display: block;
                    text-align: center;
                    font-weight: bold;
                    font-size: 1.5rem !important;
                    
                }
                .stButton button:hover {
                    background-color: green;
                    color: white;
                }
            </style>
            """, unsafe_allow_html=True)



        # Main Title  
        st.caption(f"<div class='title'>{APP_TITLE}</div>", unsafe_allow_html=True)
        # Sub-Title  
        st.caption(f"<div class='subtitle'>{APP_SUB_TITLE}</div>", unsafe_allow_html=True)


        # Load the geo-locations of parking lots
        df_lat_long = pd.read_csv('artifacts/df_ps_lat_long.csv')  # Contains latitude, longitude of parking lots
        # print(df_lat_long.shape)


        # Create sidebar for user input: Date and time
        st.sidebar.header("Parking Availability Prediction")
        selected_date = st.sidebar.date_input("Select Date", min_value=pd.to_datetime('2016-12-13'), max_value=pd.to_datetime('2016-12-19'))
        selected_time = st.sidebar.selectbox("Select Time", ["08:00", "08:30", "09:00", "09:30", "10:00", "10:30", 
                                                            "11:00", "11:30", "12:00", "12:30", "13:00", "13:30", 
                                                            "14:00", "14:30", "15:00", "15:30", "16:00", "16:30"])
        


        # Create a predict button with custom styling
        predict_clicked = st.sidebar.button("Predict")



        # Define a colormap
        colormap = cm.linear.RdYlGn_09.scale(0, 100).to_step(100)
        # colormap = cm.linear.Spectral_11.scale(0, 100).to_step(100)


        forecasted_dict = {}
        # Forecast on Predict Button Click Event:
        if predict_clicked:

            # Get forecasted time series
            forecasted_dict = forecast(user_inp_date=str(selected_date), user_inp_time=str(selected_time))

            # Retrieve the latest data point
            latest_availability = {'ps_idx':[], 'Availability':[]}
            for ps_idx in list(forecasted_dict.keys()):

                availability_at_user_dt = forecasted_dict[ps_idx]['forecast'].iloc[-1]
                latest_availability['ps_idx'].append(ps_idx)
                latest_availability['Availability'].append(availability_at_user_dt)

            # Generating a dataframe with the availability information at user inputted datetime
            df_latest_avail_info = pd.DataFrame(latest_availability)

            df_latest_avail_info_merged = pd.merge(df_lat_long, df_latest_avail_info, on='ps_idx', how='inner')

            # # DEBUG
            # print(selected_date, selected_time)
            # print(df_latest_avail_info_merged.shape)
            # print(df_latest_avail_info_merged)
            # print('-'*50)

            # Generate map post prediction
            st.session_state['map'] = create_post_prediction_map(df_ps_lat_long_avail=df_latest_avail_info_merged, 
                                                                colormap_inp=colormap)
            
            st.session_state['historical_forecast_dict'] = forecasted_dict




        # Create colorbar HTML
        colorbar_html = create_colorbar_html(colormap)
        # Embed colorbar
        st.components.v1.html(colorbar_html, height=50,)


        # Show Initial Map on Web-App Loading and updated map post forecasting
        if 'map' not in st.session_state:
            map_ = create_initial_map(df_ps_lat_long=df_lat_long)
        else:
            map_ = st.session_state['map']

        
        # Render the map
        st_folium(map_, width=800, height=600)



        # View Historical and Projected Trends across parking lots
        selected_park_lot_id = st.slider('Select Parking Lot ID:', min_value=1, max_value=27, value=1)


        # Show Trend post prediction
        if 'historical_forecast_dict' in st.session_state:
            
            prediction_dict = st.session_state['historical_forecast_dict']
            historical_trend = np.round(100-prediction_dict[selected_park_lot_id]['train'].iloc[-126:], 2)
            forecsted_trend = np.round(100-prediction_dict[selected_park_lot_id]['forecast'], 2)
            generate_plot(historical_data=historical_trend, forecasted_data=forecsted_trend, ps_idx=selected_park_lot_id)


    except Exception as e:
        custom_exception =  CustomException(e, sys)
        print(custom_exception)


    









if __name__ == "__main__":
    main()






















# # Page configuration for wide layout
# st.set_page_config(layout="wide")


# # Applying custom CSS for consistent padding and title styling
# st.markdown("""
#     <style>
#         .reportview-container .main .block-container {
#             padding-top: 2rem;
#             padding-right: 1rem;
#             padding-left: 1rem;
#             padding-bottom: 2rem;
#             max-width: 1200px;
#         }
#         h1 {
#             font-size: 2.5rem;
#             font-weight: bold;
#             text-align: center;
#             color: #1892BA; /* Optional: Make title color green */
#         }
#         .stSidebar {
#             background-color: #f0f2f6;
#             padding: 1rem;
#         }
#         .centered-text {
#             text-align: center;
#             font-size: 1.25rem; /* Adjust font size here */
#             color: #E6EBED; /* Optional: Adjust text color */
#         }
#         .stButton button {
#             width: 60%;
#             padding: 0.75rem;
#             background-color: red;
#             color: white !important;
#             border-radius: 0.5rem;
#             margin: 1rem auto;
#             cursor: pointer;
#             border: none;
#             display: block;
#             text-align: center;
#             font-weight: bold;
#             font-size: 1.5rem !important;
            
#         }
#         .stButton button:hover {
#             background-color: green;
#             color: white;
#         }
#         .map-container {
#             display: flex;
#             justify-content: center;
#             width: 100%;
#         }
#         .map-container .folium-map {
#             width: 100% !important;
#             height: 600px; /* Set a height for the map */
#         }
#     </style>
#     """, unsafe_allow_html=True)



# # Load the geo-locations of parking lots
# df_lat_long = pd.read_csv('artifacts/df_ps_lat_long.csv')  # Contains latitude, longitude of parking lots


# # Create sidebar for user input: Date and time
# st.sidebar.header("Parking Availability Prediction")
# selected_date = st.sidebar.date_input("Select Date", min_value=pd.to_datetime('2016-12-13'), max_value=pd.to_datetime('2016-12-19'))
# selected_time = st.sidebar.selectbox("Select Time", ["08:00", "08:30", "09:00", "09:30", "10:00", "10:30", 
#                                                      "11:00", "11:30", "12:00", "12:30", "13:00", "13:30", 
#                                                      "14:00", "14:30", "15:00", "15:30", "16:00", "16:30"])



# # Create a predict button with custom styling
# predict_clicked = st.sidebar.button("Predict")







# print('Session State:', st.session_state)






# # Handle the map based on predictions or show initial map
# if predict_clicked:
#     print(str(selected_date))
#     print(str(selected_time)) 








# # Main Ttitle
# st.title("Birmingham Parking Availability Prediction")

# # Sub-Title
# st.markdown("<div class='centered-text'>Select a date and time to see the forecasted availability, and click on a parking lot to explore its historical and forecasted trends.</div>", unsafe_allow_html=True)



# # Render the map centered
# with st.container():
#     st.markdown('<div class="map-container">', unsafe_allow_html=True)
#     folium_static(map_)
#     st.markdown('</div>', unsafe_allow_html=True)
