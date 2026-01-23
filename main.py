import streamlit as st
import pandas as pd
import os
import csv
from datetime import datetime
from openai import OpenAI
from langchain_openai import ChatOpenAI
from langchain.agents import AgentState, create_agent
from langchain.agents.middleware import dynamic_prompt, ModelRequest
from PIL import Image, ImageFile
import base64


#Background
def get_base64_of_bin_file(bin_file):
    with open(bin_file, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

img_base64 = get_base64_of_bin_file("Car.png")

background_css = f"""
<style>
[data-testid="stAppViewContainer"] {{
    background-image: url("data:image/png;base64,{img_base64}");
    background-size: cover;
    background-repeat: no-repeat;
    background-attachment: fixed;
}}

[data-testid="stHeader"] {{
    background-color: rgba(0,0,0,0);
}}
</style>
"""
ImageFile.LOAD_TRUNCATED_IMAGES = True
img = Image.open("VBCarSharing.png")

image_url1 = "https://www.toyota.com.sg/showroom/new-models/-/media/f774090eab764ec6823ef7bd29e9950e.png"
image_url2 = "https://images.hgmsites.net/lrg/2025-toyota-prius-limited-gs-angular-front-exterior-view_100965385_l.webp"
image_url3 = "https://cdn.carchoice.com.sg/web/brandnew/colour-toyota-rav4-gxl-hybrid-GLACIER%20WHITE.png?alt=media&token=17008c5b-a5a3-46bd-a1a2-6dc40797faa5"
image_url4 = "https://s3-ap-southeast-1.amazonaws.com/motoristprod/editors%2Fimages%2F1664429131076-cx3-feature.jpg"
image_url5 = "https://media.mediaresults.com/wp-content/uploads/2025/08/26-trailseeker.webp"


#Setup AI
API_KEY = st.secrets["OPENAI_API_KEY"]
@dynamic_prompt
def context(request: ModelRequest) -> str:
  return """
  You are a helpful assistant built into a car rental website called VB Transport to answer queries about the cars and related topics. Use the following context in your responses:
  We offer the Toyota Sienta ($5/h), Toyota Prius($3/h), Toyota RAV4($8/h), Mazda CX-3($10/h), and Subaru e-Outback($15/h) for rental.
  The Toyota Sienta is the family flexible favourite. It is a hybrid 7 seater(2 front + 3 middle + 2 rear). With all seats taken, this car can barely fit 2 backpacks (50L). With the 3rd row folded, the huge flat boot can fit 3 large suitcases and a stroller (575L).
  The Toyota Prius(Sedan/Liftback - 2023/2024 model) is a 5 seater that can fit 1 large and 1 medium sized suitcase (370L).
  The Toyota RAV4(2024 model) is a spacious SUV. It is a 5 seater with a very large boot space and could fit 3 large suitcases with room to spare (580L). Its wide opening makes it easy to load strollers or golf bags.
  The Madza CX-3 is a compact crossover, stylish but tight on space. Its a 5 seater, but beware, the rear leg room is tight for tall adults. It has a small bootspace and can fir either 1 large suitcase or 2 carry-on bags (240L).
  The Subaru e-Outback is a 5 seater with a boot space that can fit a lot of stuff (912L).

  If they go off topic, bring them back or tell them your unsure of how to answer that or something along those lines.
  """
agent = create_agent(ChatOpenAI(model="gpt-4o-mini", api_key=API_KEY), tools=[], middleware=[context])
def get_completion(prompt):
  return agent.invoke({"messages":[{"role":"user", "content":prompt}]})["messages"][1].content


#Setup Page
st.set_page_config(layout="centered", page_title="VB Transport Ltd")
current_datetime = datetime.now()

if "current_page" not in st.session_state:
    st.session_state.current_page = "Home"

def navigate_to(page):
    st.session_state.current_page = page

# Sidebar Navigation Buttons
if st.sidebar.button("Home", width=1000):
    navigate_to("Home")
if st.sidebar.button("Car Rental", width=1000):
    navigate_to("Car Rental")
if st.sidebar.button("List of Available Cars", width=1000):
    navigate_to("List of Available Cars")
if st.sidebar.button("Help", width=1000):
    navigate_to("Help")

#Home
if st.session_state.current_page == 'Home':
    st.markdown(background_css, unsafe_allow_html=True)
    st.title("VB CarSharing")
    st.write(":red[#1 Car Rental Company in Singapore]")
    st.text("VB Transport has served our customers' needs for 30 years and continuing. In"
                 "order to keep up with the times, VB CarSharing was launched to serve customers"
                 "who wish to rent a car, or find a cheaper alternative to buying a car. With"
                 "over 100 vehicles in our fleet, we will continue striving to create the"
                 "best customer experience for all.")
    st.image(img, width = 1000)
    if st.button("Rent a Car", width=1000):
        navigate_to("Car Rental")
#Car Rental
elif st.session_state.current_page == "Car Rental":
    st.header("Car Rental Form")

    with st.form("profile_form"):
        name = st.text_input("Name")
        email = st.text_input("Email")
        option = st.selectbox(
            "Which car would you like to rent?",
            ("Toyota Sienta", "Toyota Prius", "Toyota RAV4","Mazda CX-3", "Subaru e-Outback"),
        )
        newsletter = st.checkbox("Subscribe to newsletter")
        submitted = st.form_submit_button("Submit")

    if submitted:
        #Save to CSV
        csv_file = "rental_bookings.csv"
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        booking_data = [current_time, name, email, option, newsletter]

        file_exists = os.path.isfile(csv_file)
        with open(csv_file, "a", newline="") as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(["Date", "Name", "Email", "Car Selected", "Newsletter"])
            writer.writerow(booking_data)

        # Recient Display
        # We use st.container with a border to look like a physical receipt
        st.divider()
        with st.container(border=True):
            st.markdown("### ✅ Booking Receipt")
            st.caption(f"Transaction ID: {hash(current_time)}")

            col1, col2 = st.columns(2)
            with col1:
                st.write("**Customer:**")
                st.write(name)
                st.write(email)
            with col2:
                st.write("**Vehicle:**")
                st.write(option)
                st.write(f"_{current_time}_")

            st.divider()
            st.write("Please present this receipt at the counter.")

        st.toast("Booking saved successfully!")

#List of Available Cars
elif st.session_state.current_page == "List of Available Cars":
    st.header("Cars Available")

    with st.container(horizontal=True, horizontal_alignment="distribute"):
      st.image(image_url1, caption="Toyota Sienta", width=500)
      with st.container():
        st.subheader("Toyota Sienta")
        st.text("💺: 7 Seater without back row folded")
        st.text("Boot Space: 50L without back row folded")
        st.text("Rate: $5/hr")

    with st.container(horizontal=True, horizontal_alignment="distribute"):
      st.image(image_url2, caption="Toyota Prius (Sedan)", width=500)
      with st.container():
        st.subheader("Toyota Prius (Sedan)")
        st.text("💺: 5 Seater")
        st.text("Boot Space: 370L")
        st.text("Rate: $3/hr")
    with st.container(horizontal=True, horizontal_alignment="distribute"):
      st.image(image_url3, caption="Toyota RAV4 (2024)", width=500)
      with st.container():
        st.subheader("Toyota RAV4 (2024)")
        st.text("💺: 5 Seater")
        st.text("Boot Space: 580L")
        st.text("Rate: $8/hr")
    with st.container(horizontal=True, horizontal_alignment="distribute"):
      st.image(image_url4, caption="Mazda CX-3",width=500)
      with st.container():
        st.subheader("Mazda CX-3")
        st.text("💺: 5 Seater")
        st.text("Boot Space: 240L")
        st.text("Rate: $10/hr")
    with st.container(horizontal=True, horizontal_alignment="distribute"):
      st.image(image_url5, caption="Subaru e-Outback", width=500)
      with st.container():
        st.subheader("Subaru e-Outback")
        st.text("💺: 5 Seater")
        st.text("Boot Space: 912L")
        st.text("Rate: $15/hr")

#Help
elif st.session_state.current_page == "Help":
  st.title("AI Chatbot")

  if "messages" not in st.session_state:
    st.session_state.messages = []

  if "user_message" not in st.session_state:
    st.session_state.user_message = ""

  if st.session_state.user_message:
    st.session_state.messages.append({"role": "user:", "content": st.session_state.user_message})
    msg = get_completion(st.session_state.user_message)
    st.session_state.messages.append({"role": "assistant", "content": msg})
    st.session_state.user_message = ""

  with st.container(height=400):
    for msg in st.session_state.messages:
      with st.chat_message(msg["role"]):
        st.write(msg["content"])

  st.text_input("Ask anything about our car rental service", key="user_message")


#Bottom Text
st.caption("2026 VB Ltd®")
