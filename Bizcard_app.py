# Importing necessary libraries
import streamlit as st
from streamlit_option_menu import option_menu
import easyocr  # For Optical Character Recognition (OCR)
from PIL import Image  # For image processing
import pandas as pd  # For data manipulation
import numpy as np  # For numerical operations
import re  # For regular expressions
import io  # For handling input-output operations
import sqlite3  # For database operations
import base64

# Function to extract text from an uploaded image
def image_to_text(path):
  # Load the uploaded image
  input_img = Image.open(path)

  # Convert the image to a NumPy array for OCR processing
  image_array = np.array(input_img)
  
  # Initialize EasyOCR reader for English language
  reader = easyocr.Reader(['en'])

  # Extract text from the image (detail=0 suppresses bounding box details)
  text = reader.readtext(image_array, detail=0)
  return text, input_img


# Function to structure extracted text into predefined categories
def Extracted_text(texts):
  # Dictionary to hold business card details
  ext_dict = {"NAME":[], "DESIGNATION":[], "COMPANY_NAME":[], "CONTACT":[], "EMAIL":[], "WEBSITE":[],"ADDRESS":[], "PINCODE":[],}

  # Assign the first two text lines as Name and Designation
  ext_dict["NAME"].append(texts[0])
  ext_dict["DESIGNATION"].append(texts[1])

  # Loop through the remaining text and categorize based on pattern matching
  for i in range(2, len(texts)):

    if texts[i].startswith("+") or (texts[i].replace("-","").isdigit() and '-' in texts[i]):
      ext_dict["CONTACT"].append(texts[i])

    elif "@" in texts[i] and ".com" in texts[i]:
      ext_dict["EMAIL"].append(texts[i])

    elif "www" in texts[i] or "WWW" in texts[i] or "Www" in texts[i] or "wWw" in texts[i] or "wwW" in texts[i]:
      small = texts[i].lower()
      ext_dict["WEBSITE"].append(small)

    elif "Tamil Nadu" in texts[i] or "TamilNadu" in texts[i] or texts[i].isdigit():
      ext_dict["PINCODE"].append(texts[i])

    elif re.match(r"^[A-Za-z]",texts[i]):
      ext_dict["COMPANY_NAME"].append(texts[i])

    else:
      # Clean up address text by removing commas or semicolons
      remove_colon = re.sub(r'[,;]','',texts[i])
      ext_dict["ADDRESS"].append(remove_colon)
   
  # Combine multiple values for each key into a single string
  for key,value in ext_dict.items():
    if len(value) > 0:
            ext_dict[key] = [" ".join(value)]
    else:
        ext_dict[key] = ["NA"]  # Default value if no data is found

  return ext_dict

# Configure Streamlit page
st.set_page_config(page_title ="Bizcard", page_icon=":bar_chart:", layout="wide")

# Title and navigation menu
st.title("Extracting Business Card Data with OCR")

# Sidebar menu for navigation
menu_options = ["Home", "Upload & Modifying", "Delete"]
selected_option = st.radio("Select an option:", menu_options)

# Home page logic
if selected_option == "Home":
  st.write("Welcome to the Bizcard OCR application!")

# Section for uploading, viewing, and modifying business card data
elif selected_option == "Upload & Modifying":
  # File uploader for business card images
  imag = st.file_uploader("Upload The File", type=["png","jpg","jpeg"])

  if imag is not None:
    # Display the uploaded image
    st.image(imag, width = 300)
    # Extract text from the uploaded image
    text_image, input_image =image_to_text(imag)
    # Organize the extracted text into categories
    text_dict = Extracted_text(text_image)

    if text_dict:
      st.success("TEXT IS EXTRACTED SUCCESSFULLY")

    # Convert the extracted data into a DataFrame
    df = pd.DataFrame(text_dict)

    # Convert the image into byte format for database storage
    Img_byte = io.BytesIO()
    input_image.save(Img_byte, format='PNG')
    Img_data = Img_byte.getvalue()

    # Add image data to the DataFrame
    card = {"IMAGE":[Img_data]}
    df_1 = pd.DataFrame(card)
    Concat_df = pd.concat([df,df_1], axis=1)
    st.dataframe(Concat_df)
    
    # Save button to store extracted data in the database
    button_1 = st.button("Save", use_container_width = True)

    if button_1:
      # Connect to SQLite database
      mydb = sqlite3.connect("Bizcard_data.db")
      cur = mydb.cursor()

      # Create a database table if it doesn't exist
      Create_tab_query = """CREATE TABLE IF NOT EXISTS bizcard_details(name varchar(250),
                                                                      designation varchar(250),
                                                                      company_name varchar(250),
                                                                      contact varchar(250),
                                                                      email varchar(250),
                                                                      website text,
                                                                      address text,
                                                                      pincode varchar(250),
                                                                      image text)"""

      cur.execute(Create_tab_query)
      mydb.commit()

      # Insert extracted data into the table
      Insert_val_query = """INSERT INTO bizcard_details(name,
                                                        designation,
                                                        company_name,
                                                        contact,
                                                        email,
                                                        website,
                                                        address,
                                                        pincode,
                                                        image)
                            VALUES(?,?,?,?,?,?,?,?,?)"""

      datas = Concat_df.values.tolist()
      cur.executemany(Insert_val_query, datas)
      mydb.commit()

      st.success("SAVED SUCCESSFULLY")
  
  # Options to preview or modify records
  method = st.radio("SELECT THE METHOD",["NONE","PREVIEW","MODIFY"])

  if method == "NONE":
    st.write("")

  if method == "PREVIEW":
    # Display all records from the database
    mydb = sqlite3.connect("Bizcard_data.db")
    cur = mydb.cursor()
    Select_query = """SELECT * FROM bizcard_details"""
    cur.execute(Select_query)
    tab = cur.fetchall()
    mydb.commit()

    table_df = pd.DataFrame(tab, columns=("NAME","DESIGNATION","COMPANY_NAME","CONTACT","EMAIL","WEBSITE","ADDRESS","PINCODE","IMAGE"))
    st.dataframe(table_df)

  elif method == "MODIFY":
    # Allow users to select and modify a record
    mydb = sqlite3.connect("Bizcard_data.db")
    cur = mydb.cursor()
    Select_query = "SELECT * FROM bizcard_details"
    cur.execute(Select_query)
    tab = cur.fetchall()
    mydb.commit()

    table_df = pd.DataFrame(tab, columns=("NAME","DESIGNATION","COMPANY_NAME","CONTACT","EMAIL","WEBSITE","ADDRESS","PINCODE","IMAGE"))

    col1, col2 = st.columns(2)
    with col1:
      # Select a record by name
      selected_name = st.selectbox("SELECT THE NAME",table_df["NAME"])

    # Extract data of the selected record
    df_3 = table_df[table_df["NAME"] == selected_name]
    df_4 = df_3.copy()

    # Input fields to modify record details
    col1,col2 = st.columns(2)
    with col1:
      modify_name = st.text_input("Name",df_3["NAME"].unique()[0])
      modify_desig = st.text_input("Designation",df_3["DESIGNATION"].unique()[0])
      modify_comp = st.text_input("Company_name",df_3["COMPANY_NAME"].unique()[0])
      modify_cont = st.text_input("Contact",df_3["CONTACT"].unique()[0])
      modify_email = st.text_input("Email",df_3["EMAIL"].unique()[0])

      df_4["NAME"] = modify_name
      df_4["DESIGNATION"] = modify_desig
      df_4["COMPANY_NAME"] = modify_comp
      df_4["CONTACT"] = modify_cont
      df_4["EMAIL"] = modify_email


    with col2:
      modify_web = st.text_input("Websit",df_3["WEBSITE"].unique()[0])
      modify_add = st.text_input("Address",df_3["ADDRESS"].unique()[0])
      modify_pin = st.text_input("Pincode",df_3["PINCODE"].unique()[0])
      modify_img = st.text_input("Image",df_3["IMAGE"].unique()[0])

      df_4["WEBSITE"] = modify_web
      df_4["ADDRESS"] = modify_add
      df_4["PINCODE"] = modify_pin
      df_4["IMAGE"] = modify_img

    st.dataframe(df_4)

    # Save modifications to the database
    col1,col2 = st.columns(2)
    with col1:
      button_3 = st.button("Modify", use_container_width= True)

    if button_3:
      # Delete the old record and insert the modified one
      mydb = sqlite3.connect("Bizcard_data.db")
      cur = mydb.cursor()
      cur.execute(f"DELETE FROM bizcard_details WHERE NAME = '{selected_name}'")
      mydb.commit()

      Insert_val_query = """INSERT INTO bizcard_details(name,
                                                        designation,
                                                        company_name,
                                                        contact,
                                                        email,
                                                        website,
                                                        address,
                                                        pincode,
                                                        image)
                            VALUES(?,?,?,?,?,?,?,?,?)"""

      datas = df_4.values.tolist()
      cur.executemany(Insert_val_query, datas)
      mydb.commit()

      st.success("MODIFIED SUCCESSFULLY")

elif selected_option == "Delete":
  # Connect to the SQLite database
  mydb = sqlite3.connect("Bizcard_data.db")
  cur = mydb.cursor()

  # Create two columns for layout
  col1,col2 = st.columns(2)
  with col1:
    # Fetch all names from the database
    Select_query = "SELECT NAME FROM bizcard_details"
    cur.execute(Select_query)
    table1 = cur.fetchall() # Fetch all rows
    mydb.commit()

    # Create a list of names for the dropdown
    names=[]
    for i in table1:
      names.append(i[0])

    # Dropdown menu to select a name
    name_sel = st.selectbox("SELECT THE NAME", names)

  # Column 2: Select the designation for the selected name
  with col2:
    # Fetch the designation associated with the selected name
    Select_query = f"SELECT DESIGNATION FROM bizcard_details WHERE NAME ='{name_sel}'"
    cur.execute(Select_query)
    table2 = cur.fetchall() # Fetch all rows
    mydb.commit()

    # Create a list of designations for the dropdown
    desig=[]
    for j in table2:
      desig.append(j[0])

    # Dropdown menu to select a designation
    designation_sel = st.selectbox("SELECT THE DESIGNATION", desig)

  # Check if both name and designation are selected
  if name_sel and designation_sel:
    # Create three columns for layout
    col1,col2,col3 = st.columns(3)

    # Column 1: Display selected name and designation
    with col1:
      st.write(f"SELECTED NAME:{name_sel}")
      st.write("")
      st.write("")
      st.write("")
      st.write(f"SELECTED DESIGNATION:{designation_sel}")

    # Column 2: Add a delete button
    with col2:
      st.write("")
      st.write("")
      st.write("")
      st.write("")

      # Delete button to remove the record
      remove = st.button("Delete",use_container_width= True)

      if remove:
        # Delete the record matching the selected name and designation
        cur.execute(f"DELETE FROM bizcard_details WHERE NAME = '{name_sel}'AND DESIGNATION = '{designation_sel}'")
        mydb.commit()
        
        # Display a warning message to confirm deletion
        st.warning("DELETED")