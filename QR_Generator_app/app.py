#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import streamlit as st
import qrcode
import matplotlib.pyplot as plt
from PIL import Image

def generate_qr_code(youtube_link):
    # Create a QR Code instance
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    
    # Add the YouTube link to the QR Code
    qr.add_data(youtube_link)
    qr.make(fit=True)
    
    # Create an image from the QR Code instance
    img = qr.make_image(fill_color="black", back_color="white")
    
    return img

# Streamlit app interface
st.title("YouTube QR Code Generator")
st.write("Enter a YouTube link to generate a QR code.")

# Input for YouTube link
youtube_link = st.text_input("YouTube Link", "https://www.youtube.com/watch?v=2LEw8XQMjLM")

# Generate QR code on button click
if st.button("Generate QR Code"):
    if youtube_link:
        qr_image = generate_qr_code(youtube_link)
        
        # Save the image temporarily
        qr_image.save("youtube_qr_code.png")
        
        # Display the QR code image
        st.image("youtube_qr_code.png", caption="QR Code", use_column_width=True)

        # Download link
        with open("youtube_qr_code.png", "rb") as file:
            st.download_button("Download QR Code", file, "youtube_qr_code.png", "image/png")
    else:
        st.error("Please enter a valid YouTube link.")

