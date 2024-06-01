import pandas as pd
import streamlit as st
import mysql.connector as sql
import cv2
import os
from PIL import Image
import matplotlib.pyplot as plt
from streamlit_option_menu import option_menu
import plotly.express as px
from io import StringIO
import easyocr
import sqlalchemy as sa
import re

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

#global variable
extractedData = []

#connecting with mysql database
mydb = sql.connect(host='localhost',
                   user='root',
                   password='admin',
                   database='bizcard')
mycursor = mydb.cursor(buffered=True)

#mycursor.execute("create database bizcard")
mycursor.execute('''create table if not exists card_data
                 (
                 id integer primary key auto_increment,
                 company_name text,
                 card_holder varchar(50),
                 designation text,
                 mobile_number varchar(50),
                 email text,
                 website text,
                 area text,
                 city text,
                 state text, 
                 pin_code varchar(10),
                 image longblob
                 )

''')
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
        imageInfo = []
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
                for i in res:
                    count = 0
                    for j in i:
                        if count == 1:
                            imageInfo.append(j)
                        count += 1
                        if count > 1:
                            break

        def img_to_binary(file):
            # Convert image data to binary format
            with open(file, 'rb') as file:
                binaryData = file.read()
            return binaryData
        imageData = {"company_name" : [],
                    "card_holder" : [],
                    "designation" : [],
                    "mobile_number" :[],
                    "email" : [],
                    "website" : [],
                    "area" : [],
                    "city" : [],
                    "state" : [],
                    "pin_code" : [],
                    "image" : []
                }
        imageData['image'].append(img_to_binary(saved_img))
        st.write(imageInfo)
        def imageDict(imageInfo):
            mobile_count=0
            for ind, i in enumerate(imageInfo):
                # To get WEBSITE_URL
                if "www " in i.lower() or "www." in i.lower():
                    imageData["website"].append(i)
                elif "WWW" in i:
                    imageData["website"] = imageInfo[4] +"." + imageInfo[5]

                # To get EMAIL ID
                elif "@" in i:
                    imageData["email"].append(i)

                # To get MOBILE NUMBER
                
                elif "-" in i:
                    if mobile_count < 1:
                        imageData["mobile_number"].append(i)
                    mobile_count += 1
     
                # To get COMPANY NAME  
                elif ind == len(imageData)-1:
                    imageData["company_name"].append(i)

                # To get CARD HOLDER NAME
                elif ind == 0:
                    imageData["card_holder"].append(i)

                # To get DESIGNATION
                elif ind == 1:
                    imageData["designation"].append(i)

                # To get AREA
                if re.findall('^[0-9].+, [a-zA-Z]+',i):
                    imageData["area"].append(i.split(',')[0])
                elif re.findall('[0-9] [a-zA-Z]+',i):
                    imageData["area"].append(i)

                # To get CITY NAME
                match1 = re.findall('.+St , ([a-zA-Z]+).+', i)
                match2 = re.findall('.+St,, ([a-zA-Z]+).+', i)
                match3 = re.findall('^[E].*',i)
                if match1:
                    imageData["city"].append(match1[0])
                elif match2:
                    imageData["city"].append(match2[0])
                elif match3:
                    imageData["city"].append(match3[0])

                # To get STATE
                state_match = re.findall('[a-zA-Z]{9} +[0-9]',i)
                if state_match:
                    imageData["state"].append(i[:9])
                elif re.findall('^[0-9].+, ([a-zA-Z]+);',i):
                    imageData["state"].append(i.split()[-1])
                if len(imageData["state"])== 2:
                    imageData["state"].pop(0)

                # To get PINCODE        
                if len(i)>=6 and i.isdigit():
                    imageData["pin_code"].append(i)
                elif re.findall('[a-zA-Z]{9} +[0-9]',i):
                    imageData["pin_code"].append(i[10:])
        imageDict(imageInfo)
        
        def create_df(imageData):
            df = pd.DataFrame.from_dict(imageData, orient='index')
            df = df.transpose()
            return df
        df = create_df(imageData)
        st.success("### Data Extracted!")
        st.write(df)

        if st.button("Upload to SQL Database", type="primary"):
            for i,row in df.iterrows():
                #here %S means string values 
                sql = """INSERT INTO card_data(company_name,card_holder,designation,mobile_number,email,website,area,city,state,pin_code,image)
                         VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
                mycursor.execute(sql, tuple(row))
                # the connection is not auto committed by default, so we must commit to save our changes
                mydb.commit()
            st.success('Data uploaded to MySQL Database successfully')
            st.balloons()
elif selected == 'Modify':
    col1,col2,col3 = st.columns([3,3,2])
    col2.markdown("## Alter or Delete the data here")
    column1,column2 = st.columns(2,gap="large")
    try:
        with column1:
            mycursor.execute("SELECT card_holder FROM card_data")
            result = mycursor.fetchall()
            business_cards = {}
            for row in result:
                business_cards[row[0]] = row[0]
            selected_card = st.selectbox("Select a card holder name to update", list(business_cards.keys()))
            st.markdown("#### Update or modify any data below")
            mycursor.execute("select company_name,card_holder,designation,mobile_number,email,website,area,city,state,pin_code from card_data WHERE card_holder=%s",
                            (selected_card,))
            result = mycursor.fetchone()

            # DISPLAYING ALL THE INFORMATIONS
            company_name = st.text_input("Company_Name", result[0])
            card_holder = st.text_input("Card_Holder", result[1])
            designation = st.text_input("Designation", result[2])
            mobile_number = st.text_input("Mobile_Number", result[3])
            email = st.text_input("Email", result[4])
            website = st.text_input("Website", result[5])
            area = st.text_input("Area", result[6])
            city = st.text_input("City", result[7])
            state = st.text_input("State", result[8])
            pin_code = st.text_input("Pin_Code", result[9])

            if st.button("Commit changes to DB"):
                # Update the information for the selected business card in the database
                mycursor.execute("""UPDATE card_data SET company_name=%s,card_holder=%s,designation=%s,mobile_number=%s,email=%s,website=%s,area=%s,city=%s,state=%s,pin_code=%s
                                    WHERE card_holder=%s""", (company_name,card_holder,designation,mobile_number,email,website,area,city,state,pin_code,selected_card))
                mydb.commit()
                st.success("Information updated in database successfully.")

        with column2:
            mycursor.execute("SELECT card_holder FROM card_data")
            result = mycursor.fetchall()
            business_cards = {}
            for row in result:
                business_cards[row[0]] = row[0]
            selected_card = st.selectbox("Select a card holder name to Delete", list(business_cards.keys()))
            st.write(f"### You have selected :green[**{selected_card}'s**] card to delete")
            st.write("#### Proceed to delete this card?")

            if st.button("Yes Delete Business Card"):
                mycursor.execute(f"DELETE FROM card_data WHERE card_holder='{selected_card}'")
                mydb.commit()
                st.success("Business card information deleted from database.")
    except:
        st.warning("There is no data available in the database")
    
    if st.button("View updated data"):
        mycursor.execute("select company_name,card_holder,designation,mobile_number,email,website,area,city,state,pin_code from card_data")
        updated_df = pd.DataFrame(mycursor.fetchall(),columns=["Company_Name","Card_Holder","Designation","Mobile_Number","Email","Website","Area","City","State","Pin_Code"])
        st.write(updated_df)
