
import os
import sys
import streamlit as st
import pandas as pd
import numpy as np
import requests
from datetime import datetime

# API Section#########################################

base_url = "https://data.etabus.gov.hk"

endpoint_routelist = "/v1/transport/kmb/route/"

endpoint_onlystops = "/v1/transport/kmb/stop"

endpoint_rtstoplist = "/v1/transport/kmb/route-stop"




route_list = base_url + endpoint_routelist

onlystops_list = base_url + endpoint_onlystops

rtstop_list = base_url + endpoint_rtstoplist

response_rtl = requests.get(route_list)
response_rtl.raise_for_status()
data_rtl = response_rtl.json()
df_rtl = data_rtl["data"]

route_numbers = []


for item in df_rtl:
    route_numbers.append(item["route"])

response_ostl = requests.get(onlystops_list)
response_ostl.raise_for_status()
data_ostl = response_ostl.json()
df_ostl = data_ostl["data"]


response_rtstl = requests.get(rtstop_list)
response_rtstl.raise_for_status()
data_rtstl = response_rtstl.json()
df_rtstl = data_rtstl["data"]

#API Section########################################
# session state

if 'step' not in st.session_state:
    st.session_state.step = 1

if 'selected_direction' not in st.session_state:
    st.session_state.selected_direction = {}

if 'stop_id' not in st.session_state:
    st.session_state.stop_id = []

if 'selected_stop' not in st.session_state:
    st.session_state.selected_stop = {}

if 'stop_name_id' not in st.session_state:
    st.session_state.stop_name_id = {}

if 'stop_name_seq' not in st.session_state:
    st.session_state.stop_name_seq = 0

if 'eta_1' not in st.session_state:
    st.session_state.eta_1 = []

if 'eta_2' not in st.session_state:
    st.session_state.eta_2 = []

# MAIN Body

if st.session_state.step == 1:
    st.header("KMB Route ETA")
    st.subheader("this is a test page, page 1")
    st.divider()

    st.write("Please enter your route number:")
    user_route_input = str(st.text_input("Route number", placeholder="route number eg: 1A, 84M, X42C")).upper()


    if user_route_input:
        if user_route_input in route_numbers:
            for item in df_rtl:
                if item["route"] == user_route_input:
                    user_direction_button = st.button(f'{item["dest_tc"]}\n{item["dest_en"]}', key=f'dir_{item["route"]}{item["bound"]}{item["service_type"]}')
                    if user_direction_button:
                        st.session_state.selected_direction["route"] = item["route"]
                        st.session_state.selected_direction["bound"] = item["bound"]
                        st.session_state.selected_direction["service_type"] = item["service_type"]
                        st.session_state.step = 2
        else:
            st.error("Please enter a valid route number")

if st.session_state.step == 2:
    st.header("KMB Route ETA")
    st.subheader("this is a test page, page 2")
    st.divider()
    st.write("Please select your stop:")

    # st.write(f"user_route = {st.session_state.selected_direction.get("route", "")}")
    # st.write(f"user_bound = {st.session_state.selected_direction.get("bound", "")}")
    # st.write(f"user_service_type = {st.session_state.selected_direction.get("service_type", "")}")

    user_route = st.session_state.selected_direction.get("route", "")
    user_bound = st.session_state.selected_direction.get("bound", "")
    user_service_type = st.session_state.selected_direction.get("service_type", "")

    stops_in_route = []
    seq_of_stops = []

    for item in df_rtstl:
        if item["route"] == user_route:
            if item["bound"] == user_bound:
                if item["service_type"] == user_service_type:
                    stops_in_route.append(item["stop"])
                    seq_of_stops.append(int(item["seq"]))

    stop_dict = dict(zip(stops_in_route, seq_of_stops))
    sorted_stop_dict = sorted(stop_dict, key=stop_dict.get)

    name_tc_stop = []
    name_en_stop = []
    index = []

    for item in df_ostl:
        for i in range(len(sorted_stop_dict)):
            if sorted_stop_dict[i] == item["stop"]:

                name_tc_stop.append(item["name_tc"])
                name_en_stop.append(item["name_en"])
                index.append(i)

    name_dict = dict(zip(name_tc_stop, index))
    sorted_name_dict = sorted(name_dict, key=name_dict.get)

    for i, name in enumerate(sorted_name_dict, start=0):
        stop_selection_button = st.button(f"{i + 1}: {sorted_name_dict[i]}", key=f"btn_{i + 1}")
        if stop_selection_button:
            st.session_state.stop_name_seq = i+1
            st.session_state.selected_stop["name_tc"] = f"{sorted_stop_dict[i]}"
            st.session_state.step = 3

if st.session_state.step == 3:
    user_route = st.session_state.selected_direction.get("route", "")
    user_service_type = st.session_state.selected_direction.get("service_type", "")
    user_selected_stop_ID = st.session_state.selected_stop.get("name_tc", "")
    stop_seq = st.session_state.stop_name_seq

    base_url = "https://data.etabus.gov.hk"
    endpoint_eta = f"/v1/transport/kmb/eta/{user_selected_stop_ID}/{user_route}/{user_service_type}"

    eta_url = base_url + endpoint_eta

    response_eta= requests.get(eta_url)
    response_eta.raise_for_status()
    data_eta = response_eta.json()
    df_eta = data_eta["data"]


    st.header("KMB Route ETA")
    st.subheader("this is a test page, page 3")
    st.divider()

    for item in df_ostl:
        if item["stop"] == user_selected_stop_ID:
            st.subheader("ETA of for")
            st.header(f"\n{user_route} {item["name_tc"]} \nis as follows:")

    st.divider()

    for item in df_eta:
        if item["eta_seq"] == 1:
            eta1_unsorted = item["eta"]
            if eta1_unsorted == None:
                st.title(f"NO ETA at current time")
            else:
                dt1 = datetime.fromisoformat(eta1_unsorted)
                true_eta1 = dt1.strftime('%H:%M')
                st.header(f"{true_eta1}      | {item["rmk_tc"]}")

        if item["eta_seq"] == 2:
            eta2_unsorted = item["eta"]
            if eta2_unsorted == None:
                st.title(f"NO ETA at current time")
            else:
                dt2 = datetime.fromisoformat(eta2_unsorted)
                true_eta2 = dt2.strftime('%H:%M')
                st.header(f"{true_eta2}      | {item["rmk_tc"]}")

































