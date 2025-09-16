import pandas as pd
import folium
from folium.plugins import HeatMap
import logging
from pathlib import Path
from folium.plugins import MarkerCluster

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
# --- Step 1: Load CSV ---
CSV_PATH = "results/csvs_in/orders_geo_location.csv"
df = pd.read_csv(CSV_PATH)

# If you have NaNs, drop them
df = df.dropna(subset=["order_lat", "order_lng"])

# --- Step 2: Create base map centered on Brazil ---
brazil_center = [-14.2350, -51.9253]  # approximate center of Brazil
m = folium.Map(location=brazil_center, zoom_start=4)

# --- Step 3: Add HeatMap layer ---
# HeatMap expects a list of [lat, lng] pairs
heat_data = df[["order_lat", "order_lng"]].values.tolist()
HeatMap(
    heat_data,
    radius=15,       # 🔼 increase point influence area (default ~8)
    blur=25,         # 🔼 smoother glow, bigger diffused areas
    min_opacity=0.3, # 🔼 ensures faint areas remain visible
    max_zoom=6       # 🔽 keep intensity visible when zoomed out
).add_to(m)


# --- Step 4: Save to HTML ---
m.save("brazil_heatmap.html")
print("✅ Map saved to brazil_heatmap.html")

#g2 
## Group by zip prefix and compute counts + mean coordinates
zip_groups = (
    df.groupby("customer_zip_code_prefix")
      .agg(order_count=("order_lat","count"),
           lat=("order_lat","mean"),
           lng=("order_lng","mean"))
      .reset_index()
)

m1 = folium.Map(location=brazil_center, zoom_start=4)

# Base heat layer
HeatMap(df[["order_lat", "order_lng"]].values.tolist(),
        radius=15, blur=25, min_opacity=0.3).add_to(m1)

# Add one CircleMarker per zip group with tooltip
for _, row in zip_groups.iterrows():
    folium.CircleMarker(
        location=[row.lat, row.lng],
        radius=6,
        color="blue",
        fill=True,
        fill_opacity=0.6,
        tooltip=f"ZIP {row.customer_zip_code_prefix}: {row.order_count} orders"
    ).add_to(m1)

m1.save("brazil_heatmap_zip_tooltips.html")
print("✅ Saved brazil_heatmap_zip_tooltips.html")

#g3
m2 = folium.Map(location=brazil_center, zoom_start=4)

HeatMap(df[["order_lat","order_lng"]].values.tolist(),
        radius=15, blur=25, min_opacity=0.3).add_to(m2)

cluster = MarkerCluster().add_to(m2)

for _, row in df.iterrows():
    folium.Marker(
        location=[row.order_lat, row.order_lng],
        tooltip=(f"Order: {row.order_id}<br>"
                 f"Customer: {row.customer_id}<br>"
                 f"ZIP: {row.customer_zip_code_prefix}")
    ).add_to(cluster)

m2.save("brazil_heatmap_cluster1.html")
print("✅ Saved brazil_heatmap_cluster1.html")

#g4
m2 = folium.Map(location=brazil_center, zoom_start=4)

HeatMap(df[["order_lat","order_lng"]].values.tolist(),
        radius=15, blur=25, min_opacity=0.3).add_to(m2)

cluster = MarkerCluster().add_to(m2)

for _, row in df.iterrows():
    folium.Marker(
        location=[row.order_lat, row.order_lng],
        tooltip=(f"Order: {row.order_id}<br>"
                 f"Customer: {row.customer_id}<br>"
                 f"ZIP: {row.customer_zip_code_prefix}")
    ).add_to(cluster)

m2.save("brazil_heatmap_cluster2.html")
print("✅ Saved brazil_heatmap_cluster2.html")

