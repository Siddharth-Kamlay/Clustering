from django.shortcuts import render

import base64
from django.http import JsonResponse
import requests
import matplotlib
matplotlib.use('Agg')

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
import folium
from django.http import HttpResponse
import tempfile
import os

global data
global f2
global final_df
global latitude, longitude
global name_only

# Create your views here.

# views.py

def autocomplete_search(request):
    global data

    location = request.POST.get('location')
    url = f"https://api.foursquare.com/v3/autocomplete?query={location}&radius=10000&limit=10"
    headers = {
        "accept": "application/json",
        "Authorization": "fsq3I0WkNOJPlcmZ17tbS3WN06fCNt3VgH9Lht2z1Tl/hu4="
     }
    response = requests.get(url, headers=headers)
    data = response.json()
    results= []
    for i, result in enumerate(data.get('results', [])):
        if result['type'] == 'address':
            results.append({
                'primary_text': result['text']['primary'],
                'secondary_text': result['text']['secondary']
            })
        elif result['type'] == 'place':
            results.append({
                'primary_text': result['text']['primary'],
                'secondary_text': result['text']['secondary']
            })
    return render(request, 'search_results.html', {'results': results})

# views.py

def search_form(request):
    return render(request, 'search_form.html')

# views.py

# views.py
from django.shortcuts import render
import requests

def search_location(request):
    global data
    global f2
    global final_df
    global latitude, longitude, name_only

    b = int(request.POST.get('serial_number', 0))
    if b == 0:
        longitude = float(request.POST.get('longitude'))
        latitude = float(request.POST.get('latitude'))

        url = f"https://api.foursquare.com/v3/places/search?ll={latitude},{longitude}&radius=10000&categories=12094&limit=40"
        headers = {
            "accept": "application/json",
            "Authorization": "fsq3I0WkNOJPlcmZ17tbS3WN06fCNt3VgH9Lht2z1Tl/hu4="
        }
    else:
        print('Please wait for 1 minute, the process takes time\n')
        if data['results'][b-1]['type']=='place':
            latitude=data['results'][b-1]['place']['geocodes']['main']['latitude']
            longitude=data['results'][b-1]['place']['geocodes']['main']['longitude']
            name_only=data['results'][b-1]['text']['primary']
            
        
        
        elif data['results'][b-1]['type']=='address':
            add=data['results'][b-1]['address']['address_id']
            name_only= data['results'][b-1]['text']['primary']
            url = (f"https://api.foursquare.com/v3/address/{add}")

            headers = {
                "accept": "application/json",
                "Authorization": "fsq3I0WkNOJPlcmZ17tbS3WN06fCNt3VgH9Lht2z1Tl/hu4="
            }

            response = requests.get(url, headers=headers)

            j2=response.json()
            
            
            latitude= j2['geocodes']['main']['latitude']
            longitude= j2['geocodes']['main']['longitude']
            


    url = f"https://api.foursquare.com/v3/places/search?ll={latitude},{longitude}&radius=10000&categories=12094&limit=40"
    
    headers = {
        "accept": "application/json",
        "Authorization": "fsq3I0WkNOJPlcmZ17tbS3WN06fCNt3VgH9Lht2z1Tl/hu4="
    }

    response = requests.get(url, headers=headers)
    j3 = response.json()

    if len(j3['results'])==0:
        print("No registered residental buildings present")
    
    else:
        df=pd.DataFrame(j3['results'])
        
        lon=[]
        lat=[]
        name=[]

        for i in range(0,40):
            lat.append(j3['results'][i]['geocodes']['main']['latitude'])
            lon.append(j3['results'][i]['geocodes']['main']['longitude'])
            name.append(j3['results'][i]['name'])

        f2=pd.DataFrame.from_dict({
            "Lat":lat,
            "Lng":lon,
            'Name':name
        })


        l2=[]
        for i in range(40):
            url = (f"https://api.foursquare.com/v3/places/search?ll={lat[i]}%2C{lon[i]}&radius=1000&categories=17067%2C17069%2C17070&limit=30")

            headers = {
                "accept": "application/json",
                "Authorization": "fsq3I0WkNOJPlcmZ17tbS3WN06fCNt3VgH9Lht2z1Tl/hu4="
            }
            
            response = requests.get(url, headers=headers)
            j4=response.json()
            K=len(j4['results'])
        
            l2.append(K)

        l3=[]

        for i in range(40):

            url = (f"https://api.foursquare.com/v3/places/search?ll={lat[i]}%2C{lon[i]}&radius=1000&categories=18021&limit=30")

            headers = {
                "accept": "application/json",
                "Authorization": "fsq3I0WkNOJPlcmZ17tbS3WN06fCNt3VgH9Lht2z1Tl/hu4="
            }

            response = requests.get(url, headers=headers)
            j4=response.json()

            K=len(j4['results'])

            l3.append(K)
        

        l4=[]
        for i in range(40):

            url = (f"https://api.foursquare.com/v3/places/search?ll={lat[i]}%2C{lon[i]}&radius=1000&categories=13065&limit=30")

            headers = {
                "accept": "application/json",
                "Authorization": "fsq3I0WkNOJPlcmZ17tbS3WN06fCNt3VgH9Lht2z1Tl/hu4="
            }

            response = requests.get(url, headers=headers)
            j4=response.json()

            K=len(j4['results'])
        
            l4.append(K)


        fi_data={
            'Lat':lat,
            'Lng':lon,
            'Fruits_Vegetables':l2,
            'Res':l4,
            'Sports':l3
        }

        final_df=pd.DataFrame.from_dict(fi_data)
        
        
        x=final_df.iloc[:,[0,1,2,3,4]].values
        
        mean=KMeans(n_clusters=3)
        y=mean.fit_predict(x)
        y
        
        
        final_df['Cluster']=y

        fig, axis = plt.subplots(1, 3, figsize=(15, 5))
        for i in range(3):
            plt.sca(axis[i])
            labels = ['Lat', 'Lng', 'Cluster']
            sns.boxplot(data=final_df[final_df['Cluster'] == i])
            plt.xticks(rotation=45)
            if i == 0:
                plt.title('Green')
            elif i == 1:
                plt.title('Yellow')
            else:
                plt.title('Red')

        # Save the subplots as a temporary image file
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmpfile:
            plt.savefig(tmpfile.name)
            tmpfile.seek(0)
            image_data = tmpfile.read()

        # Delete the temporary file
        os.unlink(tmpfile.name)

        encoded_image = base64.b64encode(image_data).decode('utf-8')

        # Return the image data as HTTP response
        return render(request, 'sub_plots.html', {'encoded_image': encoded_image}) 
        
        # Process j3 and pass the necessary data to the template
    return JsonResponse(j3,safe=False)


def show_subplots(request):
    return render(request, 'sub_plots.html')

def generate_folium_map(request):
    global final_df
    global latitude, longitude,name_only

    f = folium.Figure(width=1425, height=775)  # Adjust width and height as needed
    map_bom = folium.Map(location=[latitude,longitude], zoom_start=12)

    def color_producer(cluster):
        if cluster == 0:
            return 'green'
        elif cluster == 1:
            return 'orange'
        else:
            return 'red'

    latitudes = list(final_df['Lat'])
    longitudes = list(final_df['Lng'])
    labels = list(final_df['Cluster'])
    names = list(f2['Name'])
    for lat, lng, label, name in zip(latitudes, longitudes, labels, names):
        folium.CircleMarker(
            [lat, lng],
            fill=True,
            fill_opacity=1,
            popup=folium.Popup(name, max_width=300),
            radius=10,
            color=color_producer(label)
        ).add_to(map_bom)

    folium.Marker([latitude,longitude],popup=name_only).add_to(map_bom)

    map_bom.add_to(f)

    # Save the Folium map as an HTML file
    html_file =map_bom._repr_html_()

    # Return the path to the HTML file
    return render(request, 'map.html', {'html_file': html_file})