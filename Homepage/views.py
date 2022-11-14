from django.shortcuts import render,HttpResponse,HttpResponseRedirect
from Homepage.models import UserProfile
from django.conf import settings
import face_recognition
from django.core.files import File
import cv2
# Create your views here.
def index(request):
    return render(request, "index.html")

def FaceCheck(request):
    if request.method == 'GET':
            if(UserProfile.objects.filter(User_ID=request.user).exists()):
                test=cv2.imread(f"media\{request.user.id}_{request.user}.jpg")
                User_Real_Face = face_recognition.load_image_file(f"media\{request.user.id}_{request.user}.jpg")
                User_Real_Face_encoding = face_recognition.face_encodings(User_Real_Face)[0]
                cam = cv2.VideoCapture(0)
                s, img = cam.read()
                if s:    # frame captured without any errors
                        cv2.namedWindow("cam-test")
                        cv2.imshow("cam-test",img)
                        cv2.destroyWindow("cam-test")
                        cv2.imwrite("media/test.jpg",img)
                        Check_User_Face = face_recognition.load_image_file("media/test.jpg")
                        Check_User_Face_encoding = face_recognition.face_encodings(Check_User_Face)[0]
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
                                return HttpResponse("Unauthorized Access") 
                        except:
                            return HttpResponse("Unauthorized Access") 
  
                else:
                    return HttpResponse("Camera Issue") 
            else:
                cam = cv2.VideoCapture(0)
                s, img = cam.read()
                if s:    # frame captured without any errors
                        cv2.namedWindow("cam-test")
                        cv2.imshow("cam-test",img)
                        cv2.destroyWindow("cam-test")
                        cv2.imwrite(f"media\{request.user.id}_{request.user}.jpg",img)
                        obj = UserProfile()
                        obj.User_ID=request.user
                        obj.Auth_Image= f"media\{request.user.id}_{request.user}.jpg"
                        obj.save()
                        return render(request, "newuser.html")
                else:
                    return HttpResponse("Camera Issue")   
                
                
def drive(request):
    from allauth.socialaccount.models import SocialAccount, SocialApp
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    from google.oauth2.credentials import Credentials
    from allauth.socialaccount.models import SocialToken, SocialApp
    from googleapiclient.errors import HttpError
    
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

        if not items:
            print('No files found.')
            
        print('Files:')
        for item in items:
            print(u'{0} ({1})'.format(item['name'], item['id']))
        
    except HttpError as error:
        print(f'An error occurred: {error}')
    
    
    return render(request, "check.html")