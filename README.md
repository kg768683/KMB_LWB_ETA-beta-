This is an application developed with the Hong Kong Open Data for the Real Time Arrival Data of buses in Hong Kong.
The datasets consist of 2 parts: KMB_LWB and CTB, the 2 main bus operators in Hong Kong.

The dashboard/ interface is developed using streamlit.
When running the codes, just simply type " streamlit run {file_name}.py"

KMB_CTB_API.py has integrated functions for checking bus route arrival time(ETA) for both bus compaines.
However, for jointed routes for both compaines, it is still required to check on separate selections.
Please select which company you are looking for, then enter the route and press enter.

main.py is as title, a ETA checking app for only KMB and LWB routes.
Using the abovementioned datasets.
This is the base codes for KMB_CTP_API as well.
