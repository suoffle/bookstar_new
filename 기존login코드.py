
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewpoint" content="width=device-width, initial-scale=1">

    <!--bootstrap css-->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.1/dist/css/bootstrap.min.css" rel="stylesheet"
          integrity="sha384-F3w7mX95PdgyTmZZMECAngseQB83DfGTowi0iMjiWaeVhAn4FJkqJByhZMI3AhiU" crossorigin="anonymous">

    <!--jquery-->
    <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.4.1/jquery.min.js"></script>

    <title>BookStar Login</title>
</head>

<style>
    .floating_form{
        margin: 0px 30px;
    }

    .floating_label{
        margin-top:-4px;
        font-size:14px;
    }

    .floating_input{
        height: 50px; !important;
        padding-top:20px !important;
        font-size: 14px; !important;
    }
</style>

<body style="background-color: #8f8f8f;height: 100%">
<div style="font-size: 14px;text-align: center;width: 100%;min-height: 100vh;display: flex; flex-direction: row; align-items: center; justify-content: center">
    <div>
        <div class="mb-3" style="background-color: white; width: 350px; height: 380px; border: 1px solid rgba(0, 0, 0, 0.18);">
            <div style="display: flex;align-items: center;justify-content: center">
                <img style="height: 50px; object-fit: contain; margin: 30px 0"
                     src="https://cdn-icons-png.flaticon.com/512/864/864685.png">
            </div>
            <div class="form-floating mb-2 floating_form">
                <input type="email" class="floating_input form-control" id="floatingEmail"
                       placeholder="name@example.com">
                <label for="floatingEmail" class="floating_label">이메일 주소</label>
            </div>
            <div class="form-floating mb-3 floating_form">
                <input type="password" class="floating_input form-control" id="floatingPassword" placeholder="Password">
                <label for="floatingPassword" class="floating_label">비밀번호</label>
            </div>
            <div class="floating_form mb-3">
                <button id="button_login" type="button" class="btn btn-primary" style="width: 100%">로그인</button>
            </div>
        </div>
        <div style="background-color: white; width: 350px; height: 70px; border: 1px solid rgba(0, 0, 0, 0.18);">
            <div style="margin-top: 25px">
                계정이 없으신가요? <a href="{% url 'join' %}" style="font-weight: bold; color: cornflowerblue; text-decoration: none; cursor: pointer">가입하기</a>
            </div>
        </div>
    </div>
</div>

<script>
    $('#button_login').on('click', ()=>{
        let email = $('#floatingEmail').val();
        let password = $('#floatingPassword').val();

        $.ajax({
            url: "/user/login/",
            data: {
                email: email,
                password: password
            },
            method: "POST",
            dataType: "json",
            success: function (data){
                location.replace('{% url 'main' %}');
            },
            error:function (request, status, error){
                let data = JSON.parse(request.responseText);
                console.log(data.message);
                alert(data.message);
            }
        });
    });
</script>

<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.1/dist/js/bootstrap.bundle.min.js"
        integrity="sha384-/bQdsTh/da6pkI1MST/rWKFNjaCP5gBSY4sEBT38Q/9RBh9AH40zEOg7Hlq2THRZ"
        crossorigin="anonymous"></script>

</body>
</html>