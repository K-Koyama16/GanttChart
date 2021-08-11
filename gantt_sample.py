import pandas as pd
import time
import copy
import datetime

import plotly
import plotly.express as px
import plotly.graph_objects as go
print('plotly', plotly.__version__)

import streamlit as st


df_default = pd.read_csv("./data/sample.csv", header=0)
df_default["START"] = pd.to_datetime(df_default["START"])
df_default["FINISH"] = pd.to_datetime(df_default["FINISH"])
df_default["T_DISPATCHED"] = pd.to_datetime(df_default["T_DISPATCHED"])

#Standard Output
if 0:
    fig = px.timeline(df_default, x_start="START", x_end="FINISH", y="AXS", color ='GROUP')
    fig.show()

# ***Dynamic Gantt Chart***

df_base={}
df_base["M"] =  df_default
df_base["O"] =  df_default

st_now_time = st.empty()
base_time = datetime.datetime(2021, 2, 2, 8, 50)
st_now_time.write(base_time)


def make_adddatalist(df,typ):

    global base_time

    df = df.sort_values("T_DISPATCHED")
    #df["T_DISPATCHED_Timedelta"] = pd.to_timedelta(df["T_DISPATCHED"])
    df["T_DISPATCHED_Timedelta"] = df["T_DISPATCHED"] - datetime.datetime(1970,1,1,0,0)
    df["T_DISPATCHED_minute"] = df["T_DISPATCHED_Timedelta"].map(lambda x: x.total_seconds()/60.0)
    df["T_DISPATCHED_minute"] = df["T_DISPATCHED_minute"]- (base_time-datetime.datetime(1970,1,1,0,0)).total_seconds()/60.0 #基準の時間を設定
    df["T_DISPATCHED_minute"] = df["T_DISPATCHED_minute"].astype(int)
    df["T_DISPATCHED_hour"] = df["T_DISPATCHED_Timedelta"].map(lambda x: x.total_seconds()/3600.0)
    df["T_DISPATCHED_hour"] = df["T_DISPATCHED_hour"]- (base_time-datetime.datetime(1970,1,1,0,0)).total_seconds()/3600.0 #基準の時間を設定
    df["T_DISPATCHED_hour"] = df["T_DISPATCHED_hour"].astype(int)

    df["x"] = df["FINISH"]-df["START"]
    df["x"] = df["x"]/datetime.timedelta(milliseconds=1)
    df["START"] = pd.to_datetime(df["START"])

    df.loc[df["GROUP"]=="PRE","GROUP_idx"] = 0
    df.loc[df["GROUP"]=="MAIN","GROUP_idx"] = 1
    df.loc[df["GROUP"]=="POST","GROUP_idx"] = 2

    datalist = df[["GROUP_idx","START","x","AXS_"+typ,"T_DISPATCHED_minute"]].to_numpy()
    return datalist

# Task list
dic_add_datalist = {}
dic_add_datalist["M"] = make_adddatalist(df_base["M"],"M")
dic_add_datalist["O"] = make_adddatalist(df_base["O"],"O")

# Create Figuring Areas
def base_figure(df, typ):
    axs = "AXS_"+typ
    initial_dic = []
    for i in sorted(set(list(df[axs].values))):
        initial_dic.append(dict([(axs,i), ("START",datetime.datetime(2021,2,2,0,0)), ("FINISH",datetime.datetime(2021,2,2,0,0)), ("GROUP","PRE")]))
        initial_dic.append(dict([(axs,i), ("START",datetime.datetime(2021,2,2,0,0)), ("FINISH",datetime.datetime(2021,2,2,0,0)), ("GROUP","MAIN")]))
        initial_dic.append(dict([(axs,i), ("START",datetime.datetime(2021,2,2,0,0)), ("FINISH",datetime.datetime(2021,2,2,0,0)), ("GROUP","POST")]))
    df_ini = pd.DataFrame(initial_dic)

    fig = px.timeline(df_ini, x_start="START",x_end="FINISH", y=axs,color="GROUP")
    f = go.FigureWidget(fig)
    return f


dic_f = {}
dic_f["M"] = base_figure(df_base["M"],"M")
dic_f["O"] = base_figure(df_base["O"],"O")

st_gantt_m = st.plotly_chart(dic_f["M"], use_container_width=True,sharing="streamlit")
st_gantt_o = st.plotly_chart(dic_f["O"], use_container_width=True,sharing="streamlit")

default_layout = {}
default_layout["M"] = copy.deepcopy(dic_f["M"].layout)
default_layout["O"] = copy.deepcopy(dic_f["O"].layout)


# Add data to figure and arrange layout.
def add_tasks(f, add_data, dlayout):
    
    f_base_list = list(f.data[int(add_data[0])].base)
    f_x_list = list(f.data[int(add_data[0])].x)
    f_y_list = list(f.data[int(add_data[0])].y)
    
    f_base_list.append(add_data[1])
    f_x_list.append(add_data[2])
    f_y_list.append(add_data[3])
    
    f.data[int(add_data[0])].base = tuple(f_base_list)
    f.data[int(add_data[0])].x = tuple(f_x_list)
    f.data[int(add_data[0])].y = tuple(f_y_list)
    f.layout = dlayout

    return f


if st.button("Run"):

    if 0:
        for i in range(len(dic_add_datalist["W"][:30])):

            time.sleep(1)
            dic_f["M"] = add_tasks(dic_f["M"], dic_add_datalist["M"][i], default_layout["M"])
            dic_f["O"] = add_tasks(dic_f["O"], dic_add_datalist["O"][i], default_layout["O"])

            st_gantt_m.plotly_chart(dic_f["M"], use_container_width=True,sharing="streamlit")
            st_gantt_o.plotly_chart(dic_f["O"], use_container_width=True,sharing="streamlit")
    
    if 1:
        for i in range(61):
            now_time = base_time + datetime.timedelta(minutes=i)
            time.sleep(1)
            st_now_time.write(now_time)
            
            for idx, add in enumerate(dic_add_datalist["M"]):
                if add[4] == i:
                    dic_f["M"] = add_tasks(dic_f["M"], dic_add_datalist["M"][idx], default_layout["M"])
            for idx, add in enumerate(dic_add_datalist["O"]):
                if add[4] == i:
                    dic_f["O"] = add_tasks(dic_f["O"], dic_add_datalist["O"][idx], default_layout["O"])
            
            st_gantt_m.plotly_chart(dic_f["M"], use_container_width=True,sharing="streamlit")
            st_gantt_o.plotly_chart(dic_f["O"], use_container_width=True,sharing="streamlit")

