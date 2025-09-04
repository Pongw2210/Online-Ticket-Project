from app import create_app

app = create_app()

if __name__ == "__main__":
    import pendulum

    now_vn = pendulum.now("Asia/Ho_Chi_Minh")
    print(now_vn.to_datetime_string())
    app.run(debug=True)

