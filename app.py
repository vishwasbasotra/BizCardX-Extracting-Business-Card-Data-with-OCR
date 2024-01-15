import pandas as pd
import json
import streamlit as st
import mysql.connector
import numpy as np
import cv2
import os
from PIL import Image
import matplotlib.pyplot as plt
from streamlit_option_menu import option_menu
import plotly.express as px
from io import StringIO
import easyocr

#Configuring streamlit header
im = Image.open("biz.jpg")
st.set_page_config(page_title="BizCardX: Extracting Business Card Data with OCR", page_icon=im, layout='wide')

# header section
st.title(":orange[BizCardX: Extracting Business Card Data with OCR:]")

#adding a selectbox
selected = option_menu(None, ["Home","Upload & Extract","Modify"], 
                       icons=["house","cloud-upload","pencil-square"],
                       default_index=0,
                       orientation="horizontal",
                       styles={"nav-link": {"font-size": "20px", "text-align": "centre", "margin": "0px", "--hover-color": "#6495ED"},
                               "icon": {"font-size": "20px"},
                               "container" : {"max-width": "6000px"},
                               "nav-link-selected": {"background-color": "#6495ED"}})
st.header("", divider='rainbow')

if selected == 'Home':
    col1,col2 = st.columns(2)
    with col1:
        st.markdown("### :green[**Technologies Used :**] Python,easy OCR, Streamlit, SQL, Pandas")
        st.markdown("### :green[**Overview :**] In this streamlit web app you can upload an image of a business card and extract relevant information from it using easyOCR. You can view, modify or delete the extracted data in this app. This app would also allow users to save the extracted information into a database along with the uploaded business card image. The database would be able to store multiple entries, each with its own business card image and extracted information.")
    with col2:
        st.image("dataset/home.png")

elif selected == 'Upload & Extract':
    #adding a file uploader
    uploaded_file = st.file_uploader("Choose an image", type=["png","jpeg","jpg"])

    def save_card(uploaded_card):
            with open(os.path.join("uploaded_cards",uploaded_card.name), "wb") as f:
                f.write(uploaded_card.getbuffer())   
    
    def image_preview(image,res): 
            spacer = 100
            font=cv2.FONT_HERSHEY_SIMPLEX
            for detection in res: 
                top_left = tuple(detection[0][0])
                bottom_right = tuple(detection[0][2])
                text = detection[1]
                image = cv2.rectangle(image,top_left,bottom_right,(0,255,0),3)
                image = cv2.putText(image,text,(20,spacer), font, 0.5,(0,255,0),2,cv2.LINE_AA)
                spacer+=15
            plt.figure(figsize=(10,10))
            plt.imshow(image)
            #plt.show()

    if uploaded_file is not None:
        col1,col2 = st.columns(2)
        with col1:
            # Displaying the image:
            st.image(uploaded_file, caption='Uploaded Business Card')
            save_card(uploaded_file)
        with col2:
            with st.spinner("Please wait processing image..."):
                saved_img = os.getcwd()+ "\\" + "uploaded_cards"+ "\\"+ uploaded_file.name
                image = cv2.imread(saved_img)
                reader = easyocr.Reader(['en'], gpu=True)
                res = reader.readtext(saved_img)
                st.markdown("### Image Processed and Data Extracted")
                st.set_option('deprecation.showPyplotGlobalUse', False)
                st.pyplot(image_preview(image,res), use_container_width=True) 
else:
    st.write('Hellow')
