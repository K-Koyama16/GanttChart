

import numpy as np
import pandas as pd
import time
import copy

import plotly
import plotly.express as px
import plotly.graph_objects as go
print('plotly', plotly.__version__)

import streamlit as st


df_base = pd.read_csv("./data/sample.csv", header=0)
df_base["START"] = pd.to_datetime(df_base["START"])
df_base["FINISH"] = pd.to_datetime(df_base["FINISH"])

fig = px.timeline(df_base, x_start="START", x_end="FINISH", y="AXS", color ='GROUP')
fig.show()
