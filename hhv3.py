## Human Habitat too v3

# Import libraries
import numpy as np
import pandas as pd
import streamlit as st
import rasterio
from rasterio.plot import show
from rasterio.crs import CRS
import rioxarray as rxr
import matplotlib.pyplot as plt
# from matplotlib import cm
import folium
from streamlit_folium import folium_static 
import branca
import branca.colormap as cm
import altair as alt

#import ctypes
#user32 = ctypes.windll.user32
#screensize = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)
#scwidth = user32.GetSystemMetrics(0)
#widthparam = (scwidth/100)*70

# Page setup
apptitle = 'HH app'
st.set_page_config(page_title=apptitle, page_icon='mikc.png', layout="wide")

# List of available data

data_list = pd.read_excel('Layers/HH_layers.xlsx')
data_keys = list(data_list.Name)

    

# Choosing factors
st.sidebar.markdown("## Faktoru izvēlne")
pos_factors = st.sidebar.multiselect('Pozitīvie faktori (+1):', data_keys, ['Ainavas atvērtums'])
neg_factors = st.sidebar.multiselect('Negatīvie faktori (-1):', data_keys)

# Creating layer for display from factors

A = rxr.open_rasterio('Layers/10301.png').squeeze()
A1 = rxr.open_rasterio('Layers/10301.tif').squeeze()
A.data[A.data>=0]=0
A = A.astype(np.float64)
n = 0
for factor in pos_factors:
    filename = 'Layers/' + data_list.Layer[data_list.Name==factor].values[0]
    B = rxr.open_rasterio(filename).squeeze()
    A.data += B.data
    n += 1
for factor in neg_factors:
    filename = 'Layers/' + data_list.Layer[data_list.Name==factor].values[0]
    B = rxr.open_rasterio(filename).squeeze()
    A.data -= B.data
    n += 1
A.data = A.data/n
A_max = A.data.max()
A.data[A.data<0] = 0
A.data = A.data*255/A_max
A = A.astype(np.uint8)
cm1 = plt.get_cmap('jet') # Define colormap form matplotlib library
A_rgb = cm1(A)


st.sidebar.markdown("## Vizualizāciju izvēlne")
A_thresh = st.sidebar.slider('Slieksnis datu vizualizēšanai:', min_value = 0, max_value = 100, value = 0)
A_rgb[:,:,3] = A.data>(2.55*A_thresh)
A_bounds = A1.rio.bounds(recalc=True)
  

#Displaying results
colormap = cm.LinearColormap(colors=['darkblue', 'blue', 'cyan', 'yellow', 'orange', 'red'], index=None, vmin=0, vmax=A_max)
st.title('Cilvēka dzīvotnes modelēšanas rīks')
st.markdown("Demo versija Cēsu novadam")
transparency = st.sidebar.slider('Caurspīdīguma maiņa:', min_value = 0.0, max_value = 1.0, value = 0.5)

tiles = "https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}"
EsriAttribution = "Google"


    
map1 = folium.Map(location=[57.22, 25.42], zoom_start=9, tiles = None)
fg=folium.FeatureGroup(name='Dzīvotnes kartējums', show=True)
map1.add_child(fg)
folium.raster_layers.ImageOverlay(
    image=A_rgb, 
    bounds=[[A_bounds[1], A_bounds[0]], [A_bounds[3], A_bounds[2]]],
    opacity= 1 - transparency,
    name = 'Dzīvotnes kartējums',
    control=True
    ).add_to(map1)
map1.add_child(colormap)

folium.TileLayer('stamentoner',name='OSM melnbalts', show = True).add_to(map1)
folium.TileLayer(tiles = tiles,name='Google satelīts', attr=EsriAttribution).add_to(map1)
folium.TileLayer('openstreetmap',name='OSM klasisks').add_to(map1)
folium.LayerControl().add_to(map1)
folium_static(map1, width = 900) #, width = widthparam)



#Plotting histogram
st.text("")
st.markdown("**Iegūtā kartējuma vērtību sadalījums pēc platības [ha]:**")
A_list = list(A.data[A.data>0]/(255/A_max))
histogram, bin_edges = np.histogram(A_list, bins= 20, range=(0, 100))
hist_df = pd.DataFrame()
hist_df['Vērtība']  = bin_edges[1:]
hist_df['Platība, ha']  = histogram*0.04

fig = alt.Chart(hist_df).mark_area(line={'color':'black'},
    color=alt.Gradient(
        gradient='linear',
        stops=[alt.GradientStop(color='white', offset=0),
               alt.GradientStop(color='black', offset=1)],
        x1=1,
        x2=1,
        y1=1,
        y2=0)
    ).encode(
    x='Vērtība',
    y='Platība, ha'
).properties(
    width=900,
    height=200
)
st.altair_chart(fig) #, use_container_width=True)

# Displaying description
st.markdown("**Pozitīvie faktori ar koeficienta vērtību +1:**")
if len(pos_factors)>0:
    for factor in pos_factors:
        st.markdown('***' + factor + '***')
        st.markdown(data_list.Comment[data_list.Name==factor].values[0])
else:
    st.text('- Nav izvēlēts neviens')
st.markdown("**Negatīvie faktori ar koeficienta vērtību -1:**")
if len(neg_factors)>0:
    for factor in neg_factors:
        st.markdown('***' + factor + '***')
        st.markdown(data_list.Comment[data_list.Name==factor].values[0])
else:
    st.markdown('*Nav izvēlēts neviens*')
        
st.markdown("") 
st.markdown("")
st.markdown("")       
st.image('mikc.png', width=300)
st.markdown('Cilvēka dzīvotnes modelēšanas rīks izstrādāts projekta \"Inovatīvs telpiskās plānošanas pakalpojums lauku reģionu attīstībai\" Eiropas Kosmosa aģentūras programmas \"Eiropas sadarbības valstu plāns\" ietvaros.')
st.markdown('Papildus informācijai sazinieties ar agris.brauns@mikc.lv')