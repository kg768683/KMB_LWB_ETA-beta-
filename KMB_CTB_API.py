

import os
import sys
import streamlit as st
import pandas as pd
import numpy as np
import requests
from datetime import datetime
from streamlit_folium import st_folium
import folium

# to start : streamlit run KMB_CTB_API.py

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


if 'selected_direction_ctb' not in st.session_state:
    st.session_state.selected_direction_ctb = {}

if 'selected_stop_ctb' not in st.session_state:
    st.session_state.selected_stop_ctb = {}

if 'selected_stop_id_ctb' not in st.session_state:
    st.session_state.selected_stop_id_ctb = {}


if 'eta_1' not in st.session_state:
    st.session_state.eta_1 = []

if 'eta_2' not in st.session_state:
    st.session_state.eta_2 = []

# MAIN Body

if st.session_state.step == 1:

    base_url = "https://data.etabus.gov.hk"
    endpoint_routelist = "/v1/transport/kmb/route/"
    route_list = base_url + endpoint_routelist
    response_rtl = requests.get(route_list)
    response_rtl.raise_for_status()
    data_rtl = response_rtl.json()
    df_rtl = data_rtl["data"]

    route_numbers = []

    for item in df_rtl:
        route_numbers.append(item["route"])

    st.header("Hong Kong Bus Route ETA")
    st.subheader("This is a test application...")
    st.divider()

    st.write("Please enter your route number:")
    user_route_input = str(st.text_input("Route number", placeholder="route number eg: 1A, 84M, X42C")).upper()
    bus_com = st.radio("Select the bus company", ["KMB", "CTB"])
    route_num = str(user_route_input)

    if user_route_input:
        if bus_com == "KMB":
            if route_num in route_numbers:
                for item in df_rtl:
                    if item["route"] == route_num:
                        user_direction_button = st.button(f'{item["dest_tc"]}\n{item["dest_en"]}', key=f'dir_{item["route"]}{item["bound"]}{item["service_type"]}')
                        if user_direction_button:
                            st.session_state.selected_direction["route"] = item["route"]
                            st.session_state.selected_direction["bound"] = item["bound"]
                            st.session_state.selected_direction["service_type"] = item["service_type"]
                            st.session_state.step = 2

        if bus_com == "CTB":
            route = str(route_num)
            ctb_base_url = "https://rt.data.gov.hk/v2/transport/citybus/"
            endpoint_ctb_rtl = f"route/CTB/{route}"
            ctb_rtl_url = ctb_base_url + endpoint_ctb_rtl

            response_ctb_rtl = requests.get(ctb_rtl_url)
            response_ctb_rtl.raise_for_status()
            data_ctb_rtl = response_ctb_rtl.json()
            df_ctb_rtl = data_ctb_rtl["data"]

            user_selected_direction_button_ctb_in = st.button(f'{df_ctb_rtl["orig_tc"]}\n{df_ctb_rtl["orig_en"]}')
            user_selected_direction_button_ctb_out = st.button(f'{df_ctb_rtl["dest_tc"]}\n{df_ctb_rtl["dest_en"]}')
            if user_selected_direction_button_ctb_in:
                st.session_state.selected_direction_ctb["route"] = df_ctb_rtl["route"]
                st.session_state.selected_direction_ctb["dest_tc"] = df_ctb_rtl["orig_tc"]
                st.session_state.selected_direction_ctb["bound"] = "inbound"

                st.session_state.step = 11
            if user_selected_direction_button_ctb_out:
                st.session_state.selected_direction_ctb["route"] = df_ctb_rtl["route"]
                st.session_state.selected_direction_ctb["dest_tc"] = df_ctb_rtl["dest_tc"]
                st.session_state.selected_direction_ctb["bound"] = "outbound"

                st.session_state.step = 11

    else:
        st.error("Please enter a valid route number")

if st.session_state.step == 2:

    base_url = "https://data.etabus.gov.hk"

    endpoint_onlystops = "/v1/transport/kmb/stop"

    endpoint_rtstoplist = "/v1/transport/kmb/route-stop"

    onlystops_list = base_url + endpoint_onlystops

    rtstop_list = base_url + endpoint_rtstoplist

    response_ostl = requests.get(onlystops_list)
    response_ostl.raise_for_status()
    data_ostl = response_ostl.json()
    df_ostl = data_ostl["data"]

    response_rtstl = requests.get(rtstop_list)
    response_rtstl.raise_for_status()
    data_rtstl = response_rtstl.json()
    df_rtstl = data_rtstl["data"]

    st.header("KMB Route ETA")
    st.subheader("KMB Route")
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
    endpoint_stop_details = f"/v1/transport/kmb/stop/{user_selected_stop_ID}"

    eta_url = base_url + endpoint_eta
    stop_details_url = base_url + endpoint_stop_details

    response_eta= requests.get(eta_url)
    response_eta.raise_for_status()
    data_eta = response_eta.json()
    df_eta = data_eta["data"]

    response_std = requests.get(stop_details_url)
    response_std.raise_for_status()
    data_std = response_std.json()
    df_data_std = data_std["data"]

    endpoint_onlystops = "/v1/transport/kmb/stop"

    endpoint_rtstoplist = "/v1/transport/kmb/route-stop"

    onlystops_list = base_url + endpoint_onlystops

    rtstop_list = base_url + endpoint_rtstoplist

    response_ostl = requests.get(onlystops_list)
    response_ostl.raise_for_status()
    data_ostl = response_ostl.json()
    df_ostl = data_ostl["data"]

    response_rtstl = requests.get(rtstop_list)
    response_rtstl.raise_for_status()
    data_rtstl = response_rtstl.json()
    df_rtstl = data_rtstl["data"]


    st.header("KMB Route ETA")
    st.subheader("Whats your ETA")
    st.divider()

    for item in df_ostl:
        if item["stop"] == user_selected_stop_ID:
            st.subheader("ETA for")
            st.header(f"\n{user_route} {item["name_tc"]} \nis as follows:")

    st.divider()

    for item in df_eta:
        if item["eta_seq"] == 1:
            eta1_unsorted = item["eta"]
            if eta1_unsorted == None:
                st.title(f"NO ETA at current time")
                st.text(f"Last updated: {item['data_timestamp']}")
            else:
                dt1 = datetime.fromisoformat(eta1_unsorted)
                true_eta1 = dt1.strftime('%H:%M')
                st.header(f"{true_eta1}      | {item["rmk_tc"]}  |  {item["co"]}")

        if item["eta_seq"] == 2:
            eta2_unsorted = item["eta"]
            if eta2_unsorted == None:
                st.title(f"NO ETA at current time")

            else:
                dt2 = datetime.fromisoformat(eta2_unsorted)
                true_eta2 = dt2.strftime('%H:%M')
                st.header(f"{true_eta2}      | {item["rmk_tc"]}  |  {item["co"]}")
                st.text(f"Last updated: {item['data_timestamp']}")


    for item in df_ostl:
        if item["stop"] == user_selected_stop_ID:
            lat_cor = item["lat"]
            long_cor = item["long"]
            m = folium.Map(location=[lat_cor, long_cor], zoom_start=25)
            folium.Marker(
                [lat_cor, long_cor],
                popup=item["name_tc"],
                tooltip=item["name_tc"],
            ).add_to(m)

            st_data = st_folium(m, width = 250, height= 250)

    return_to_rt_btn = st.button("Return to Route\n(Please click TWICE)")
    return_to_search_btn = st.button("Return to Search\n(Please click TWICE)")

    if return_to_rt_btn:
        st.session_state.step = 2

    if return_to_search_btn:
        st.session_state.step = 1

if st.session_state.step == 11:
    user_route = st.session_state.selected_direction_ctb.get("route", "")
    user_dest = st.session_state.selected_direction_ctb.get("dest_tc", "")
    bound = st.session_state.selected_direction_ctb.get("bound", "")

    ctb_base_url = "https://rt.data.gov.hk/v2/transport/citybus/"
    endpoint_ctb_route_stop = f"route-stop/CTB/{user_route}/{bound}"

    ctb_rtstl_url = ctb_base_url + endpoint_ctb_route_stop

    response_ctb_rtstl = requests.get(ctb_rtstl_url)
    response_ctb_rtstl.raise_for_status()
    data_ctb_rtstl = response_ctb_rtstl.json()
    df_ctb_rtstl= data_ctb_rtstl["data"]

    st.header("CTB Route ETA")
    st.subheader("Pick your stop")
    st.divider()


    stops_in_route_ctb = []
    seq_of_stops_ctb = []

    for item in df_ctb_rtstl:
        if bound == "inbound":
            if item["route"] == user_route and item["dir"] == "I":
                stops_in_route_ctb.append(item["stop"])
                seq_of_stops_ctb.append(item["seq"])
        if bound == "outbound":
            if item["route"] == user_route and item["dir"] == "O":
                stops_in_route_ctb.append(item["stop"])
                seq_of_stops_ctb.append(item["seq"])

    stop_ctb_dict = dict(zip(stops_in_route_ctb, seq_of_stops_ctb))
    sorted_stop_ctb_dict = sorted(stop_ctb_dict, key=stop_ctb_dict.get)


    name_tc_ctb_stop = []
    name_en_ctb_stop = []
    index_ctb = []

    for id in sorted_stop_ctb_dict:
        ctb_base_url = "https://rt.data.gov.hk/v2/transport/citybus/"
        endpoint_ctb_stop = f"stop/{id}"

        ctb_stop_url = ctb_base_url + endpoint_ctb_stop
        response_ctb_stl = requests.get(ctb_stop_url)
        response_ctb_stl.raise_for_status()
        data_ctb_stl = response_ctb_stl.json()
        df_ctb_stl = data_ctb_stl["data"]

        name_tc_ctb_stop.append(df_ctb_stl["name_tc"])

    for i, name in enumerate(name_tc_ctb_stop, start=0):
        stop_selection_ctb_button = st.button(f"{i + 1}: {name_tc_ctb_stop[i]}", key=f"but_{i}ky")
        if stop_selection_ctb_button:
            st.session_state.stop_name_seq = i + 1
            st.session_state.selected_stop_ctb["name_tc"] = name_tc_ctb_stop[i]
            st.session_state.step = 12




if st.session_state.step == 12:
    user_route = st.session_state.selected_direction_ctb.get("route", "")
    user_dest = st.session_state.selected_direction_ctb.get("dest_tc", "")
    user_selected_stop_tc = st.session_state.selected_stop_ctb.get("name_tc", "")
    bound = st.session_state.selected_direction_ctb.get("bound", "")
    stop_seq_ctb = st.session_state.stop_name_seq

    ctb_base_url = "https://rt.data.gov.hk/v2/transport/citybus/"
    endpoint_ctb_route_stop = f"route-stop/CTB/{user_route}/{bound}"

    ctb_rtstl_url = ctb_base_url + endpoint_ctb_route_stop

    response_ctb_rtstl = requests.get(ctb_rtstl_url)
    response_ctb_rtstl.raise_for_status()
    data_ctb_rtstl = response_ctb_rtstl.json()
    df_ctb_rtstl = data_ctb_rtstl["data"]

    for item in df_ctb_rtstl:
        if bound == "inbound":
            if item["route"] == user_route and item["dir"] == "I" and item["seq"] == stop_seq_ctb:
                user_selected_stop_ID = item["stop"]
                st.session_state.selected_stop_id_ctb["selected_stop_id_ctb"] = user_selected_stop_ID
        if bound == "outbound":
            if item["route"] == user_route and item["dir"] == "O" and item["seq"] == stop_seq_ctb:
                user_selected_stop_ID = item["stop"]
                st.session_state.selected_stop_id_ctb["selected_stop_id_ctb"] = user_selected_stop_ID

    user_selected_stop_ID = st.session_state.selected_stop_id_ctb.get("selected_stop_id_ctb", "")


    endpoint_ctb_eta = f"eta/CTB/{user_selected_stop_ID}/{user_route}"

    ctb_eta_url = ctb_base_url + endpoint_ctb_eta

    response_ctb_eta = requests.get(ctb_eta_url)
    response_ctb_eta.raise_for_status()
    data_ctb_eta = response_ctb_eta.json()
    df_ctb_eta = data_ctb_eta["data"]


    endpoint_ctb_stop = f"stop/{user_selected_stop_ID}"

    ctb_stop_url = ctb_base_url + endpoint_ctb_stop
    response_ctb_stl = requests.get(ctb_stop_url)
    response_ctb_stl.raise_for_status()
    data_ctb_stl = response_ctb_stl.json()
    df_ctb_stl = data_ctb_stl["data"]


    st.header("CTB Route ETA")
    st.subheader("No data will show if there is no ETA")
    st.divider()

    st.subheader("ETA for")
    st.header(f"{user_route} {user_selected_stop_tc} \n is as follows:")

    st.divider()
    try:
        for item in df_ctb_eta:
            if item["eta_seq"] == 1:
                eta1_unsorted = item["eta"]
                if eta1_unsorted == None:
                    st.title(f"NO ETA at current time")
                    st.text(f"Last updated: {item['data_timestamp']}")
                else:
                    dt1 = datetime.fromisoformat(eta1_unsorted)
                    true_eta1 = dt1.strftime('%H:%M')
                    st.header(f"{true_eta1}      | {item["rmk_tc"]}  |  {item["co"]}")

            if item["eta_seq"] == 2:
                eta2_unsorted = item["eta"]
                if eta2_unsorted == None:
                    st.title(f"NO ETA at current time")

                else:
                    dt2 = datetime.fromisoformat(eta2_unsorted)
                    true_eta2 = dt2.strftime('%H:%M')
                    st.header(f"{true_eta2}      | {item["rmk_tc"]}  |  {item["co"]}")
                    st.text(f"Last updated: {item['data_timestamp']}")
    except ValueError:
        st.header("No ETA")

    if df_ctb_stl["stop"] == user_selected_stop_ID:
        lat_cor = df_ctb_stl["lat"]
        long_cor = df_ctb_stl["long"]
        m = folium.Map(location=[lat_cor, long_cor], zoom_start=25)
        folium.Marker(
                        [lat_cor, long_cor],
                        popup=df_ctb_stl["name_tc"],
                        tooltip=df_ctb_stl["name_tc"],
                    ).add_to(m)

        st_data = st_folium(m, width = 250, height= 250)

    return_to_rtctb_btn = st.button("Return to Route\n(Please click TWICE)")
    return_to_searchctb_btn = st.button("Return to Search\n(Please click TWICE)")

    if return_to_rtctb_btn:
        st.session_state.step = 11

    if return_to_searchctb_btn:
        st.session_state.step = 1






































