# 1 89 32 2 5 6 7 8 9 10 11 12 13 14 18
# 89 32 2 5 6 7 8 9 10 11 12 13 14 18 1
# public_key_5000.pem
from tkinter import filedialog
from tkinter import *
from stegano import lsb
import speech_recognition as sr         
import cv2
import math
import os
import shutil
from subprocess import call,STDOUT
import aesutil
import sys
from termcolor import cprint 
from pyfiglet import figlet_format
import rsautil1
import base64
import PIL.Image as PILImage
from simple_colors import *
import time
import tkinter.filedialog as fdialog
from gtts import gTTS

# Used to split string into parts.
def split_string(s_str,count=15):
    per_c=math.ceil(len(s_str)/count)
    c_cout=0
    out_str=''
    split_list=[]
    for s in s_str:
        out_str+=s
        c_cout+=1
        if c_cout == per_c:
            split_list.append(out_str)
            out_str=''
            c_cout=0
    if c_cout!=0:
        split_list.append(out_str)
    return split_list

# Used to count frames in Video
def countFrames():
    cap = cv2.VideoCapture(f_name)
    length = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    cprint(f"Total frame in video are : {length-1}",'blue')
    return length

# Extract the frames
def frame_extraction(video):
    if not os.path.exists("./tmp"):
        os.makedirs("tmp")
    temp_folder="./tmp"
    cprint("[INFO] tmp directory is created",'green')
    vidcap = cv2.VideoCapture(video)
    count = 0
    cprint("[INFO] Extracting frames from video \n Please be patient",'blue')
    while True:
        success, image = vidcap.read()
        if not success:
            break
        cv2.imwrite(os.path.join(temp_folder, "{:d}.png".format(count)), image)
        count += 1
    cprint("[INFO] All frames are extracted from video",'green')

#Encrypt and encode text into frames
def encode_string(input_string,root="./tmp/"):
    cprint("Select your encryption type \n 1) AES Encrypted {Symetric Encryption} \n 2) RSA Encrypted {Assysmetric Encryption}\n",'blue')
    Encryption_Style=int(input(""))
    if Encryption_Style == 1:
        res=input_string
        key123=int(input("Choose key type \n   \n 2.ASCII : "))
        key = input("Enter the key : ")
        if key123==1:
           input_string = aesutil.encrypt(key=key,source=res) 
        else:
            input_string = aesutil.encrypt(key=key,source=res,keyType='ascii')
        key_path = input("Enter the receiver publickey filename with path to encrypt key : ")
        key_rsa = rsautil1.encrypt(message=key,key_path=key_path)
        key_rsa = key_rsa.decode('utf-8')
        print(f"Asymetric encrypted key to be shared with receiver \n {key_rsa}")
        file_obj = open("./AES-ENC-Key/ReceiverKey.txt", "wb")
        key_rsa = key_rsa.encode()
        file_obj.write(key_rsa)
        file_obj.close()
        print(f"\n AES Encypted message: {input_string}")
        split_string_list=split_string(input_string)
        #print(split_string_list)
        split_string_length = len(split_string_list)
    
        FRAMES = list(map(int, input(f"Enter {split_string_length} FRAME NUMBERS seperated by space : ").split()))
    
        frame_choice = int(input("1) Do you want to store frame numbers in an image \n 2) No! Don't store : "))
        if frame_choice == 1:
            ENCODE_IMAGE = input("Enter image name with extension : ")
            res = str(FRAMES)
            if key123==1:
                FRAMES_ENCODED = aesutil.encrypt(key=key,source=res)
                secret = lsb.hide(ENCODE_IMAGE,str(FRAMES_ENCODED))
                secret.save("image-enc.png")
                cprint("[Info] Frames numbers are hidden inside the image with filename image-enc.png",'red') 
            else:
                FRAMES_ENCODED = aesutil.encrypt(key=key,source=res,keyType='ascii')
                secret = lsb.hide(ENCODE_IMAGE,str(FRAMES_ENCODED))
                secret.save("image-enc.png")
                cprint("[Info] Frames numbers are hidden inside the image with filename image-enc.png",'red')
        else :
            cprint("[Info] Frame numbers are not stored anywhere. Please remember them.",'red')
    else :
        res=input_string
        key_path = input("Enter the publickey filename with path : ")
        input_string = rsautil1.encrypt(message=res,key_path=key_path)
        input_string = input_string.decode('utf-8')
        input_string = str(input_string)
        print(f"Encypted message: \n {input_string}")
        split_string_list=split_string(input_string)
        #print(split_string_list)
        split_string_length = len(split_string_list)
        FRAMES = list(map(int, input(f"Enter {split_string_length} FRAME NUMBERS seperated by space : ").split()))
        frame_choice = int(input("1) Do you want to store frame numbers in an image \n2) No! Don't store : "))
        if frame_choice == 1:
            ENCODE_IMAGE = input("Enter image name with extension : ")
            res = str(FRAMES)
            FRAMES_ENCODED = rsautil1.encrypt(message=res,key_path=key_path)
            FRAMES_ENCODED = FRAMES_ENCODED.decode('utf-8')
            secret = lsb.hide(ENCODE_IMAGE,str(FRAMES_ENCODED))
            secret.save("image-enc.png")
            cprint("[Info] Frames numbers are hidden inside the image with filename image-enc.png",'red')
            #res = lsb.reveal("image-enc.png") #for debugging
            #res = res.decode('utf-8')
            #res = str(res)
            #print(f"Encrypted frame numbers : {res}") 
        else :
            cprint("[Info] Frame numbers are not stored anywhere. Please remember them.",'red')
    for i in range(0,len(FRAMES)):
        f_name="{}{}.png".format(root,FRAMES[i])
       #print(f_name)
        secret_enc=lsb.hide(f_name,split_string_list[i])
        secret_enc.save(f_name)
        cprint("[INFO] Frame {} holds {}".format(FRAMES[i],split_string_list[i]),'blue')

# delete temporary files
def clean_tmp(path="./tmp"):
    if os.path.exists(path):
        shutil.rmtree(path)
        print("[INFO] tmp files are cleaned up")
def main():
    ENCODE_CHOICE = int(input("Choose text or text from text document to hide inside image. \n Enter number either 1|2|3|4|5 : \n1.TEXT \n2.TEXT DOCUMENT \n3.Image Hide \n4.Audio Hide \n5.Video Hide \n6. Multiple format together \nEnter Your Choice : "))
    # print("Enter Your Choice : ")

    if ENCODE_CHOICE==1:
        TEXT_TO_ENCODE = input("Enter the text to encrypt and encode : ")
        countFrames()
        frame_extraction(f_name)
        encode_string(TEXT_TO_ENCODE)
    # Mix images into video and add audio.
        call(["ffmpeg", "-i",f_name, "-q:a", "0", "-map", "a", "tmp/audio.mp3", "-y"],stdout=open(os.devnull, "w"), stderr=STDOUT)  
        call(["ffmpeg", "-i", "tmp/%d.png" , "-vcodec", "png", "tmp/video.mov", "-y"],stdout=open(os.devnull, "w"), stderr=STDOUT)  
        call(["ffmpeg", "-i", "tmp/video.mov", "-i", "tmp/audio.mp3", "-codec", "copy", "video.mov", "-y"],stdout=open(os.devnull, "w"), stderr=STDOUT)

        cprint("Video is succesfully encoded with encrypted text.",'green')
        clean_tmp()
    if ENCODE_CHOICE==2:
        print("Please Select a Txt file as an Input")
        FILE_TO_ENCODE  =  filedialog.askopenfilename(initialdir = "/",title = "Select file",filetypes = (("Text files","*.txt"),("all files","*.*")))

        # FILE_TO_ENCODE = input("Select text from file:")
        TEXT_TO_ENCODE = []
        with open(FILE_TO_ENCODE) as f:
            for lines in f:
                TEXT_TO_ENCODE.append(lines)
        TEXT_TO_ENCODE = str(TEXT_TO_ENCODE)
        print(TEXT_TO_ENCODE)
        countFrames()
        frame_extraction(f_name)
        encode_string(TEXT_TO_ENCODE)
    # Mix images into video and add audio.
        call(["ffmpeg", "-i",f_name, "-q:a", "0", "-map", "a", "tmp/audio.mp3", "-y"],stdout=open(os.devnull, "w"), stderr=STDOUT)  
        call(["ffmpeg", "-i", "tmp/%d.png" , "-vcodec", "png", "tmp/video.mov", "-y"],stdout=open(os.devnull, "w"), stderr=STDOUT)  
        call(["ffmpeg", "-i", "tmp/video.mov", "-i", "tmp/audio.mp3", "-codec", "copy", "video.mov", "-y"],stdout=open(os.devnull, "w"), stderr=STDOUT)
        print(yellow('Video is succesfully encoded with encrypted text Document', ['bold']))
        # cprint("Video is succesfully encoded with encrypted text.",'yellow')
        clean_tmp()

    if ENCODE_CHOICE==3:
        # root=Tk()
        FILE_TO_ENCODE= input("\n Enter image name with extension : ")
        # FILE_TO_ENCODE  =  filedialog.askopenfilename(initialdir = "/",title = "Select file",filetypes = (("Image files","*.*"),("all files","*.*")))


        img=cv2.imread(FILE_TO_ENCODE)
        # img=cv2.resize(img,(1000,1000))
        li=[]

        # cv2.imshow("img",img)
        # root.destroy()
        # root.mainloop()
        # .deiconify()
        # print("Hello")
        # cv2.waitKey(0)
        # print("Hello2")
        # root.mainloop()
        for i in img:
            for j in i:
                for k in j:
                    li.append(k)

      
        s=" ".join(str(x) for x in li)
        print(s)
        countFrames()
        frame_extraction(f_name)
        encode_string(s)
        # Mix images into video and add audio.
        call(["ffmpeg", "-i",f_name, "-q:a", "0", "-map", "a", "tmp/audio.mp3", "-y"],stdout=open(os.devnull, "w"), stderr=STDOUT)  
        call(["ffmpeg", "-i", "tmp/%d.png" , "-vcodec", "png", "tmp/video.mov", "-y"],stdout=open(os.devnull, "w"), stderr=STDOUT)  
        call(["ffmpeg", "-i", "tmp/video.mov", "-i", "tmp/audio.mp3", "-codec", "copy", "video.mov", "-y"],stdout=open(os.devnull, "w"), stderr=STDOUT)
        print(yellow('Video is succesfully encoded with Image.', ['bold']))
        # cprint("Video is succesfully encoded with encrypted text.",'yellow')
        clean_tmp()

    if ENCODE_CHOICE==4:
        r=sr.Recognizer()
        # print("1")
        print(yellow('Audio Name Speech.wav is reading...', ['bold']))
        with sr.AudioFile('speech.wav') as source:

            audio_text = r.listen(source)
            # print("1")
            try:
                text = r.recognize_google(audio_text)
                # print('Converting audio transcripts into text ...')
                print(text)
            except:
                print('Sorry.. run again...')


        countFrames()
        frame_extraction(f_name)
        encode_string(text)
        # print("Hurreg")
    # Mix images into video and add audio.
        call(["ffmpeg", "-i",f_name, "-q:a", "0", "-map", "a", "tmp/audio.mp3", "-y"],stdout=open(os.devnull, "w"), stderr=STDOUT)  
        call(["ffmpeg", "-i", "tmp/%d.png" , "-vcodec", "png", "tmp/video.mov", "-y"],stdout=open(os.devnull, "w"), stderr=STDOUT)  
        call(["ffmpeg", "-i", "tmp/video.mov", "-i", "tmp/audio.mp3", "-codec", "copy", "video.mov", "-y"],stdout=open(os.devnull, "w"), stderr=STDOUT)

        cprint("Video is succesfully encoded with encrypted audio.",'green')
        clean_tmp()




    if ENCODE_CHOICE==5:
        print("Be Patient for processing")

        cap = cv2.VideoCapture("hid.mp4")
        length = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        li=[]
        count=0

        while(cap.isOpened()):

            ret, frame = cap.read()
            if ret == True:
                frame = cv2.resize(frame, (300, 300))
                # cv2.imshow('frame',frame)
                # count+=1
                # if(count%2==0):

                    # fp+=1
                # for i in frame:

                    # for j in i:
                        # for k in j:
                            # li.append(k)

                count+=1
                if(count%48==0):
                    # 4 lakh


                    # fp+=1
                    for i in frame:

                        for j in i:
                            for k in j:
                                li.append(k)
                            
                if cv2.waitKey(10) & 0xFF == ord('q'):
                    break
            else:
                break
        s=" ".join(str(x) for x in li)

        # r=sr.Recognizer()
        # # print("1")
        # print(yellow('Audio Name Speech.wav is reading...', ['bold']))
        # with sr.AudioFile('speech.wav') as source:

        #     audio_text = r.listen(source)
        #     # print("1")
        #     try:
        #         text = r.recognize_google(audio_text)
        #         # print('Converting audio transcripts into text ...')
        #         print(text)
        #     except:
        #         print('Sorry.. run again...')


        countFrames()
        frame_extraction(f_name)
        encode_string(s)
        # print("Hurreg")
    # Mix images into video and add audio.
        call(["ffmpeg", "-i",f_name, "-q:a", "0", "-map", "a", "tmp/audio.mp3", "-y"],stdout=open(os.devnull, "w"), stderr=STDOUT)  
        call(["ffmpeg", "-i", "tmp/%d.png" , "-vcodec", "png", "tmp/video.mov", "-y"],stdout=open(os.devnull, "w"), stderr=STDOUT)  
        call(["ffmpeg", "-i", "tmp/video.mov", "-i", "tmp/audio.mp3", "-codec", "copy", "video.mov", "-y"],stdout=open(os.devnull, "w"), stderr=STDOUT)

        cprint("Video is succesfully encoded with encrypted Video.",'green')
        clean_tmp()














        

            # File = askopenfile(parent=vishal, mode='r+', title = "ADD DATA",filetype=[("audio file",".wav"),("ALL FILES", ".*")])
            # img=cv2.imread(File.name)
            # img=cv2.resize(img,(500,500))
            # li=[]

            
            # for i in img:
            #     for j in i:
            #         for k in j:
            #             li.append(k)

        
            # text3=" ".join(str(x) for x in li)

            # a=input("this is halt")
            


            
            # r=sr.Recognizer()
            # # print("1")
            # print(yellow('Audio Name Speech.wav is reading...', ['bold']))
            # with sr.AudioFile('speech.wav') as source:

            #     audio_text = r.listen(source)
            #     # print("1")
            #     try:
            #         text = r.recognize_google(audio_text)
            #         # print('Converting audio transcripts into text ...')
            #         print(text)
                #     except:
                #         print('Sorry.. run again...')


        #     countFrames()
        #     frame_extraction(f_name)
        #     encode_string(s)
        #     # print("Hurreg")
        # # Mix images into video and add audio.
        #     call(["ffmpeg", "-i",f_name, "-q:a", "0", "-map", "a", "tmp/audio.mp3", "-y"],stdout=open(os.devnull, "w"), stderr=STDOUT)  
        #     call(["ffmpeg", "-i", "tmp/%d.png" , "-vcodec", "png", "tmp/video.mov", "-y"],stdout=open(os.devnull, "w"), stderr=STDOUT)  
        #     call(["ffmpeg", "-i", "tmp/video.mov", "-i", "tmp/audio.mp3", "-codec", "copy", "video.mov", "-y"],stdout=open(os.devnull, "w"), stderr=STDOUT)

        #     cprint("Video is succesfully encoded with encrypted Video.",'green')
        #     clean_tmp()



        
        # FILE_TO_ENCODE= input("\n Enter image name with extension : ")
        # FILE_TO_ENCODE  =  filedialog.askopenfilename(initialdir = "/",title = "Select file",filetypes = (("Image files","*.*"),("all files","*.*")))

        # # print("Succ")
        # # Language in which you want to convert
        # language = 'en'
        # myobj = gTTS(text=FILE_TO_ENCODE, lang=language, slow=False)
        # print("Succ1")
        # # img=cv2.imread(FILE_TO_ENCODE)
        # # Saving the converted audio in a mp3 file named
        # # welcome 
        # myobj.save("welcome1.mp3")
        # print("Succ2")
  
        #    Playing the converted file
        # os.system("welcome.mp3")
        # r = sr.Recognizer()
        # with sr.AudioFile('spech.wav') as source:


        #     audio_text = r.listen(source)
        # #    recoginize_() method will throw a request error if the API is unreachable, hence using exception handling
        #     try:


        # using google speech recognition
                # text = r.recognize_google(audio_text)
                # print('Converting audio transcripts into text ...')
                # print(text)
        




    

        
    
if __name__ == "__main__":
    os.system('cls' if os.name == 'nt' else 'clear')
    cprint(figlet_format('Group9', font='slant'),'yellow', attrs=['bold'])
    # time.sleep(3)
    print("\n")

    
    print(green('Guide: Prof. (Dr.) Premanand P. Ghadekar', ['bold']))
    # print("Guide: Prof. (Dr.) Premanand P. Ghadekar")
    # time.sleep(2)

    print("\n")
    print(blue('Group Members', ['bold']))
    # Prajwal Atram, Hitashri Patil, Nupur Shinde, Vishal Singh, Sameer Meshram
    print("\n")
    print("06 - Prajwal Atram")
    print("40 - Hitashri Patil")
    print("54 - Nupur Shinde")
    print("63 - Vishal Singh")
    print("76 - Sameer Meshram")
    
    print("\n\n")
    time.sleep(2)
    print(yellow('Video Steganography', ['bold']))
    print("\n\n")
    cprint(figlet_format('AES & RSA encrytion', font='digital'),'green', attrs=['bold'])
    f_name = sys.argv[1]
    #image_name = sys.argv[2]
    main()
