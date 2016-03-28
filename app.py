from ChatBulletServer import (
    create_app_and_socket,
    config,
)

app, socket = create_app_and_socket(config)


if __name__ == "__main__":
    socket.run(app, debug=True, host="0.0.0.0")
