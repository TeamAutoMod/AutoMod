import requests as rq



def main():
    r = rq.post("https://id.twitch.tv/oauth2/token", params={
        "client_id": "9fkkawhy8wm13hm9r8lrv1doetoq4r",
        "client_secret": "5kjrrz8dkqxu4y0zauz2uvynhu2zqe",
        "grant_type": "client_credentials"
    })
    print(r.json())


if __name__ == "__main__":
    main()