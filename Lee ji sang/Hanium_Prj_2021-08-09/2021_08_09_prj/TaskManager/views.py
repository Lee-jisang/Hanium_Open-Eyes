from django.http.response import StreamingHttpResponse
from TaskManager.sleep import Sleep_Detector
from TaskManager.sleep import Blink_Detector
from TaskManager.sleep import sleep_Blink_Detector
from TaskManager.models import *

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth.hashers import check_password
from django.core.paginator import Paginator
from django.core.serializers.json import DjangoJSONEncoder

from django.utils import timezone
import json

# sleep.py 에서 사용자 ID 값 참조를 위한 전역변수
ID = None
USERNAME = None


# 첫 페이지(index)
def index(request):
    user = None
    if request.session.get('id'):
        user = User.objects.get(id=request.session.get('id'))

    context = {
        'user': user
    }
    return render(request, "index.html", context=context)


# 회원 가입
def signup(request):
    global errorMsg     # 에러메시지
    # POST 요청 시 입력된 데이터(사용자 정보) 저장
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        confirm = request.POST['confirm']
        firstname = request.POST['firstname']
        lastname = request.POST['lastname']

        # 회원가입
        try:
            # 회원가입 실패 시
            if not (username and password and confirm and firstname and lastname and email):
                errorMsg = '빈칸이 존재합니다!'
            elif password != confirm:
                errorMsg = '비밀번호가 일치하지 않습니다!'
            # 회원가입 성공 시 회원정보 저장
            else:
                User.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    first_name=firstname,
                    last_name=lastname,
                    date_joined=timezone.now()
                ).save()
                return redirect('')         # 회원가입 성공했다는 메시지 출력 후 로그인 페이지로 이동(예정)
        except:
            errorMsg = '빈칸이 존재합니다!'
        return render(request, 'signup.html', {'error': errorMsg})
    # 회원가입 성공 후 이동
    return render(request, 'signup.html')


# 로그인
def login(request):
    global errorMsg         # 에러메시지
    # POST 요청시 입력된 데이터 저장
    if request.method == 'POST':                                        # 로그인 버튼 클릭
        username = request.POST['username']
        password = request.POST['password']
        try:
            if not (username and password):                             # 아이디/비밀번호 중 빈칸이 존재할 때
                errorMsg = '아이디/비밀번호를 입력하세요.'
            else:                                                       # 아이디/비밀번호 모두 입력됐을 때
                user = User.objects.get(username=username)                  # 등록된 아이디의 정보 가져오기
                if check_password(password, user.password):                 # 등록된 아이디의 비밀번호가 맞으면
                    request.session['id'] = user.id                         # 세션에 번호 추가
                    request.session['username'] = user.username             # 세션에 아이디 추가
                    request.session['email'] = user.email                   # 세션에 이메일 추가
                    request.session['first_name'] = user.first_name         # 세션에 이름 추가
                    request.session['last_name'] = user.last_name           # 세션에 성 추가
                    return redirect('index')
                else:                                                   # 등록된 아이디의 비밀번호가 틀리면
                    errorMsg = '비밀번호가 틀렸습니다.'
        except:                                                         # 등록된 아이디의 정보가 없을 때
            errorMsg = '가입하지 않은 아이디 입니다.'

        return render(request, 'login.html', {'error': errorMsg})   # 에러 메세지와 로그인 페이지(login.html) 리턴
    # GET 요청시
    return render(request, 'login.html')                            # 로그인 페이지(login.html) 리턴


# 로그아웃
def logout(request):
    # 사용자 정보 로드
    if request.session.get('id', None):
        del(request.session['id'])          # 사용자 번호 제거
        del(request.session['username'])    # 사용자 아이디 제거
    return redirect('/')            # 메인 페이지(index.html) 리턴


# 메인 페이지
def main(request):
    # 사용자 정보 로드
    global ID, USERNAME
    user = None
    # 로그인 되어있는 경우
    if request.session.get('id', None):
        user = AuthUser.objects.get(id=request.session.get('id', None))
        # DB 활용을 위한 전역변수 저장
        ID = user.id
        USERNAME = user.username
    # 로그인 하지 않은 사용자의 경우 로그인 페이지로 이동.
    else:
        return redirect('/login')

    # html로 세션 데이터 전송
    context = {
        'user': user
    }
    return render(request, "main.html", context=context)


# About 페이지
def about(request):
    # 사용자 정보 로드
    user = None
    if request.session.get('id', None):
        user = AuthUser.objects.get(id=request.session.get('id', None))

    context = {
        'user': user
    }
    return render(request, "about.html", context=context)


# 마이페이지 임시
def MyPage(request):
    # 사용자 정보 로드
    user = None
    if request.session.get('id', None):
        user = AuthUser.objects.get(id=request.session.get('id', None))
        d_data = DrowsinessData.objects.filter(id=user.id)
        d_data = list(d_data.values())
        b_data = BlinkData.objects.filter(id=user.id)

    context = {
        'user': user,
        'd_data': d_data,
        'b_data': json.dumps([data.to_json() for data in b_data])
    }
    return render(request, 'mypage.html', context=context)


# 통합 페이지
def Task_Manager(request):
    global ID, USERNAME
    ### 임시 코드 ###
    user = None
    new_Todo = None
    content = None
    if request.session.get('id', None):
        user = AuthUser.objects.get(id=request.session.get('id', None))
        new_Todo = DailyTodo.objects.filter(uid=user.id)
        ID = user.id
        USERNAME = user.username

    # POST 요청 시
    if request.method == 'POST':
        content = request.POST['content']
        # 일일 스케줄러에 할 일 추가
        DailyTodo.objects.create(
            uid=user,
            username=user.username,
            content=content
        ).save()

    context = {
        'user': user,
        'TodoList': new_Todo
    }
    return render(request, "TaskManager.html", context=context)


# 졸음 감지 페이지
def Drowsiness(request):
    global ID, USERNAME
    # 사용자 정보 로드
    user = None
    if request.session.get('id', None):
        user = AuthUser.objects.get(id=request.session.get('id', None))
        ID = user.id
        USERNAME = user.username

    context = {
        'user': user
    }
    return render(request, "Drowsiness.html", context=context)


# 눈 깜빡임 감지 페이지
def Blinking(request):
    global ID, USERNAME
    # 사용자 정보 로드
    user = None
    if request.session.get('id', None):
        user = AuthUser.objects.get(id=request.session.get('id', None))
        ID = user.id
        USERNAME = user.username

    context = {
        'user': user
    }
    return render(request, "Blinking.html", context=context)


###############################################################################################
# 게시판 선택 페이지
def Board(request):
    # 사용자 정보 로드
    user = None
    if request.session.get('id', None):
        user = AuthUser.objects.get(id=request.session.get('id', None))        # 사용자 정보 저장

    context = {
        'user': user
    }
    return render(request, "Board.html", context=context)


# Free Board 게시판
def freeboard(request):
    # 사용자정보 로드
    user = None
    if request.session.get('id'):                                 # 로그인 중이면
        user = User.objects.get(pk=request.session.get('id'))     # 사용자 정보 저장

    # 페이지정보 로드
    all_freeboard_posts = Freeboard.objects.all().order_by('-id')       # 모든 자유게시판 데이터를 id순으로 가져오기
    paginator = Paginator(all_freeboard_posts, 10)                      # 한 페이지에 10개씩 정렬
    page = int(request.GET.get('p', 1))                                 # p번 페이지 값, p값 없으면 1 반환
    posts = paginator.get_page(page)                                    # p번 페이지 가져오기

    # 자유 게시판 페이지(freeboard.html) 리턴
    return render(request, 'freeboard.html',
                  {'posts': posts, 'user': user})


# Free Board 게시글 쓰기
def freeboard_writing(request):
    # 사용자정보 로드
    user = None
    if request.session.get('id'):                                     # 로그인 중이면
        user = AuthUser.objects.get(pk=request.session.get('id'))       # 사용자 정보 저장
    # POST 요청시
    if request.method =='POST':
        # 새 게시글 객체 생성
        new_post = Freeboard.objects.create(
            title=request.POST['title'],
            contents=request.POST['contents'],
            uid=user,
            username=user.username
        )
        return redirect(f'/freeboard_post/{new_post.id}')               # 해당 게시글 페이지로 이동

    # GET 요청시 글쓰기 페이지(writing.html) 리턴
    return render(request, 'freeboard_writing.html', {'user' : user})


# Free Board 게시글 보기
def freeboard_post(request, pk):
    # 사용자정보 로드
    user = None
    if request.session.get('id'):                                     # 로그인 중이면
        user = User.objects.get(pk=request.session.get('id'))     # 사용자 정보 저장

    # 게시글 정보 로드
    post = get_object_or_404(Freeboard, pk=pk)
    # 댓글 정보 로드
    comment = CommentFreeboard.objects.filter(pid=pk).order_by('created_date')

    # 해당 게시글 페이지(freeboard_post.html) 반환
    return render(request, 'freeboard_post.html',
                  {'post' : post, 'user' : user, 'comment': comment})


# Free Board 댓글작성
def freeboard_comment(request, pk):
    post = get_object_or_404(Freeboard, pk=pk)
    # 사용자정보 로드
    user = None
    if request.session.get('id'):  # 로그인 중이면
        user = AuthUser.objects.get(pk=request.session.get('id'))  # 사용자 이름 저장

    # POST 요청시
    if request.method == 'POST':
        new_comment = CommentFreeboard.objects.create(
            pid=Freeboard.objects.get(id=pk),
            uid=user.id,
            username=user.username,
            comments=request.POST['content'],
        )
        return redirect(f'/freeboard_post/{post.id}',{'post': post, 'user': user})  # 해당 게시글 페이지로 이동

    return render(request, f'/freeboard_post/{post.id}',{'post': post, 'user': user})


# Free Board 게시글 수정
def freeboard_edit(request, pk):
    # 사용자정보 로드
    user = None
    if request.session.get('id'):                                     # 로그인 중이면
        user = User.objects.get(pk=request.session.get('id'))     # 사용자 정보 저장

    # 게시글 정보 로드
    post = Freeboard.objects.get(pk=pk)

    # POST 요청시
    if request.method == "POST":
        post.title = request.POST['title']                              # 제목 수정 반영
        post.contents = request.POST['contents']                        # 내용 수정 반영
        post.save()                                                     # 수정된 내용 저장
        return redirect(f'/freeboard_post/{pk}')                        # 해당 게시글 페이지로 이동

    # GET 요청시 게시글 수정 페이지(postedit.html) 리턴
    return render(request, 'freeboard_edit.html', {'post':post, 'user' : user})

# Free Board 게시글 삭제
def freeboard_delete(request, pk):
    post = Freeboard.objects.get(id=pk)                                 # 해당 게시글 테이블 저장
    post.delete()                                                       # 해당 게시글 삭제
    return redirect(f'/freeboard')                                      # 자유 게시판 페이지로 이동


########################################################################################################################
# Q & A 게시판
def questionboard(request):
    # 사용자정보 로드
    user = None
    if request.session.get('id'):                                         # 로그인 중이면
        user = User.objects.get(pk=request.session.get('id'))         # 사용자 정보 저장

    # 페이지정보 로드
    all_questionboard_posts = Questionboard.objects.all().order_by('-id')   # 모든 자유게시판 데이터를 id순으로 가져오기
    paginator = Paginator(all_questionboard_posts, 10)                      # 한 페이지에 10개씩 정렬
    page = int(request.GET.get('p', 1))                                     # p번 페이지 값, p값 없으면 1 반환
    posts = paginator.get_page(page)                                        # p번 페이지 가져오기

    # 자유 게시판 페이지(freeboard.html) 리턴
    return render(request, 'questionboard.html',
                  {'posts': posts, 'user': user})


# Q & A 게시글 쓰기
def questionboard_writing(request):
    # 사용자정보 로드
    user = None
    if request.session.get('id'):                                         # 로그인 중이면
        user = AuthUser.objects.get(pk=request.session.get('id'))         # 사용자 정보 저장
    # POST 요청시
    if request.method =='POST':
        # 새 게시글 객체 생성
        new_post = Questionboard.objects.create(
            title=request.POST['title'],
            contents=request.POST['contents'],
            uid=user,
            username=user.username
        )
        return redirect(f'/questionboard_post/{new_post.id}')               # 해당 게시글 페이지로 이동

    # GET 요청시 글쓰기 페이지(writing.html) 리턴
    return render(request, 'questionboard_writing.html', {'user' : user})


# Q & A 게시글 보기
def questionboard_post(request, pk):
    # 사용자정보 로드
    user = None
    if request.session.get('id'):                                         # 로그인 중이면
        user = User.objects.get(pk=request.session.get('id'))         # 사용자 정보 저장

    # 게시글 정보 로드
    post = get_object_or_404(Questionboard, pk=pk)

    # 댓글 정보 로드
    comment = CommentQuestionboard.objects.filter(pid=pk).order_by('created_date')

    # 해당 게시글 페이지(freeboard_post.html) 리턴
    return render(request, 'questionboard_post.html',
                  {'post' : post, 'user' : user, 'comment': comment})


# Q & A 댓글작성
def questionboard_comment(request, pk):
    post = get_object_or_404(Questionboard, pk=pk)
    # 사용자정보 로드
    username = None
    user = None
    if request.session.get('id'):  # 로그인 중이면
        user = AuthUser.objects.get(pk=request.session.get('id'))  # 사용자 이름 저장

    # POST 요청시
    if request.method == 'POST':
        new_comment = CommentQuestionboard.objects.create(
            pid=Questionboard.objects.get(id=pk),
            uid=user.id,
            username=user.username,
            comments=request.POST['content'],
        )
        return redirect(f'/questionboard_post/{post.id}',{'post' : post, 'username' : username})  # 해당 게시글 페이지로 이동

    return render(request, f'/questionboard_post/{post.id}',{'post' : post, 'username' : username})


# Q & A 게시글 수정
def questionboard_edit(request, pk):
    # 사용자정보 로드
    user = None
    if request.session.get('id'):                                         # 로그인 중이면
        user = User.objects.get(pk=request.session.get('id'))         # 사용자 정보 저장

    # 게시글 정보 로드
    post = Questionboard.objects.get(pk=pk)

    # POST 요청시
    if request.method=="POST":
        post.title = request.POST['title']                                  # 제목 수정 반영
        post.contents = request.POST['contents']                            # 내용 수정 반영
        post.save()                                                         # 수정된 내용 저장
        return redirect(f'/questionboard_post/{pk}')                        # 해당 게시글 페이지로 이동
    # GET 요청시 게시글 수정 페이지(postedit.html) 리턴
    return render(request, 'questionboard_edit.html', {'post':post, 'user' : user})

# Q & A 게시글 삭제
def questionboard_delete(request, pk):
    post = Questionboard.objects.get(id=pk)                                 # 해당 게시글 테이블 저장
    post.delete()                                                           # 해당 게시글 삭제
    return redirect(f'/questionboard')                                      # 자유 게시판 페이지로 이동
######################################################################################################


# 졸음 해소 스트레칭 동영상 페이지
def tip(request):
    # 사용자 정보 로드
    user = None
    if request.session.get('id'):
        user = AuthUser.objects.get(id=request.session.get('id'))           # 사용자 정보 저장

    context = {
        'user': user
    }
    return render(request, "tip.html", context=context)


# 카메라 연결
def gen(camera):
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')


def task_manager(request):
    return StreamingHttpResponse(gen(sleep_Blink_Detector()),
                                 content_type='multipart/x-mixed-replace; boundary=frame')


def sleep_detector(request):
    return StreamingHttpResponse(gen(Sleep_Detector()),
                                 content_type='multipart/x-mixed-replace; boundary=frame')


def blink_detector(request):
    return StreamingHttpResponse(gen(Blink_Detector()),
                                 content_type='multipart/x-mixed-replace; boundary=frame')


## test ##
# 마이페이지 임시
def Test(request):
    # 사용자 정보 로드
    user = None
    if request.session.get('id', None):
        user = AuthUser.objects.get(id=request.session.get('id', None))

        # 사용자의 졸음 감지 데이터
        # Python 객체를 JSON 포맷 데이터로 변환
        d_data = list(DrowsinessData.objects.filter(id=user.id).values())
        d_data_js = json.dumps(d_data, cls=DjangoJSONEncoder)

        # 사용자의 눈 깜빡임 감지 데이터
        # Python 객체를 JSON 포맷 데이터로 변환
        b_data = list(BlinkData.objects.filter(id=user.id).values())
        b_data_js = json.dumps(b_data, cls=DjangoJSONEncoder)

    context = {
        'user': user,
        'd_data_js': d_data_js,
        'b_data+js': b_data_js
    }
    return render(request, 'test.html', context=context)

def cam_test(request):
    return render(request, 'cam.html')