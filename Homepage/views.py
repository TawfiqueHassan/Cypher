from django.shortcuts import render,HttpResponse,HttpResponseRedirect
from Homepage.models import UserProfile
from django.conf import settings
import face_recognition
import cv2
from cryptography.fernet import Fernet
from django.core.files.storage import FileSystemStorage
# Imaginary function to handle an uploaded file.

#Drive 
from allauth.socialaccount.models import SocialAccount, SocialApp
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from googleapiclient.http import MediaFileUpload
from allauth.socialaccount.models import SocialToken, SocialApp
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload
import io
import os
import docx2txt
stck=""
# Create your views here.
def index(request):
    return render(request, "index.html")

def FaceCheck(request):
    if request.method == 'GET':
            if(UserProfile.objects.filter(User_ID=request.user).exists()):
                User_Real_Face = face_recognition.load_image_file(f"media\{request.user.id}_{request.user}.jpg")
                User_Real_Face_encoding = face_recognition.face_encodings(User_Real_Face)[0]
                cam = cv2.VideoCapture(0)
                s, img = cam.read()
                if s:    # frame captured without any errors
                        cv2.imwrite("media/test.jpg",img)
                        Check_User_Face = face_recognition.load_image_file("media/test.jpg")
                        try:
                            face_recognition.face_encodings(Check_User_Face)[0]
                        except:
                            FaceCheck(request)
                        small_frame = cv2.resize(img, (0, 0), fx=0.25, fy=0.25)
                        # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
                        rgb_small_frame = small_frame[:, :, ::-1]
                        # Find all the faces and face encodings in the current frame of video
                        face_locations = face_recognition.face_locations(rgb_small_frame)
                        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations) 
                        try:                   
                            check=face_recognition.compare_faces(User_Real_Face_encoding, face_encodings)
                            if check[0]==True:
                                return HttpResponseRedirect('/homepage/drive/')
                            else:
                                return render(request, "unauthorized.html")   
                        except:
                             return render(request, "unauthorized.html") 
                else:
                    FaceCheck(request) 
            else:
                cam = cv2.VideoCapture(0)
                s, img = cam.read()              
                if s:    # frame captured without any errors 
                        cv2.imwrite(f"media\{request.user.id}_{request.user}.jpg",img)
                        User_Real_Face = face_recognition.load_image_file(f"media\{request.user.id}_{request.user}.jpg")
                        try:
                            User_Real_Face_encoding = face_recognition.face_encodings(User_Real_Face)[0]
                        except:
                            FaceCheck(request)  
                        obj = UserProfile()
                        obj.User_ID=request.user
                        key = Fernet.generate_key().decode()
                        obj.key=key
                        obj.Auth_Image= f"media\{request.user.id}_{request.user}.jpg"
                        obj.save()
                        return HttpResponseRedirect('/homepage/drive/')
                else:
                    return render(request, "unauthorized.html")   
                
                
def drive(request):
    app_google = SocialApp.objects.get(provider="google")
    account = SocialAccount.objects.get(user=request.user)
    user_tokens = account.socialtoken_set.first()
    
    creds = Credentials(
    token=user_tokens.token,
    refresh_token=user_tokens.token_secret,
    client_id=app_google.client_id,
    client_secret=app_google.secret,
    )
    try:
        service = build('drive', 'v3', credentials=creds)
        results = service.files().list(
            pageSize=10, fields="nextPageToken, files(id, name)").execute()
        items = results.get('files', [])
        flag=0
        if not items:
            print('No files found.')
        for i in items:
            if 'Cypher' in i.values():
                flag=1
        if (flag==0):
            file_metadata ={
                'name' : "Cypher",
                'mimeType' : "application/vnd.google-apps.folder",
            }
            service.files().create(body=file_metadata).execute()
            return HttpResponseRedirect('/homepage/drive/')    
    
        results = service.files().list(
            pageSize=10, fields="nextPageToken, files(id, name)").execute()
        items = results.get('files', [])
        if items:
            folder_id=""
            for item in items:
                if item['name']=="Cypher":
                    folder_id=item['id']
            page_token = None
            response = service.files().list(q=f"parents in '{folder_id}'",
                                                spaces='drive',
                                                fields='nextPageToken, files(id, name)',
                                                pageToken=page_token).execute()
            flist= response.get('files', [])
            if flist:
                folder_name=[]
                folder_ids=[]
                for item in flist:
                        folder_name.append(item['name'])
                        folder_ids.append(item['id'])
                        page_token = response.get('nextPageToken', None) 
                        
                mylist = zip(folder_name, folder_ids)
                context ={
                    "object_list": mylist,
                    }   
                return render(request, "check.html",context)       
    except HttpError as error:
        print(f'An error occurred: {error}')
        
    return render(request, "check.html")

def upload(request):
    if request.method == 'POST':
        app_google = SocialApp.objects.get(provider="google")
        account = SocialAccount.objects.get(user=request.user)
        user_tokens = account.socialtoken_set.first()
        creds = Credentials(
        token=user_tokens.token,
        refresh_token=user_tokens.token_secret,
        client_id=app_google.client_id,
        client_secret=app_google.secret,
        )
        service = build('drive', 'v3', credentials=creds) 
        
        results = service.files().list(
            pageSize=10, fields="nextPageToken, files(id, name)").execute()
        items = results.get('files', [])
        folder_id=""
        for item in items:
            if item['name']=="Cypher":
                folder_id=item['id']
                
                
        fname=request.FILES['file']
        fs = FileSystemStorage()
        filename = fs.save(fname.name, fname)
        uploaded_file_path = fs.path(filename)
        tname= fname.name
        Object=UserProfile.objects.get(User_ID=request.user)
        ftool = Fernet(Object.key)
        
        data=''
        with open(uploaded_file_path,'rb') as reader:
            data=reader.read()
        print(data)
        
        encryptedData=ftool.encrypt(data)
        
        with open(uploaded_file_path,'wb') as writer:
            writer.write(encryptedData)
            writer.close()
    
        file_metadata={
            'name': tname,
            'parents' : [folder_id],
        }
        mime_Type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        media = MediaFileUpload(uploaded_file_path,mimetype=mime_Type)
        
        service.files().create(
            body=file_metadata,
            media_body=media,
        ).execute() 
    
        
        return HttpResponseRedirect('/homepage/drive/')    
    return render(request, "upload.html")


def openfile(request,id):
    if request.method == 'GET':
        app_google = SocialApp.objects.get(provider="google")
        account = SocialAccount.objects.get(user=request.user)
        user_tokens = account.socialtoken_set.first()
        creds = Credentials(
        token=user_tokens.token,
        refresh_token=user_tokens.token_secret,
        client_id=app_google.client_id,
        client_secret=app_google.secret,
        )
        service = build('drive', 'v3', credentials=creds) 
        file_id = id

        # pylint: disable=maybe-no-member
        request1 = service.files().get_media(fileId=file_id)
        dfile = io.BytesIO()
        downloader = MediaIoBaseDownload(dfile, request1)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            print(F'Download {int(status.progress() * 100)}.')
        fs = FileSystemStorage()
        filename = fs.save("test.docx", dfile)
        downloaded_file_path = fs.path(filename)
        Object=UserProfile.objects.get(User_ID=account.user_id)
        ftool = Fernet(Object.key)
        
        with open(downloaded_file_path,'rb') as reader1:
            data1=reader1.read()
        
        decryptedData=ftool.decrypt(data1)
        
        with open(downloaded_file_path,'wb') as writer1:
            writer1.write(decryptedData)
            
        my_text = docx2txt.process(downloaded_file_path)
        
        text=my_text.splitlines()
        context ={
            "object_list": text,
            }  
        
        if os.path.exists(downloaded_file_path):
            os.remove(downloaded_file_path)
        
        return render(request, "open.html", context) 
        
        
            
        