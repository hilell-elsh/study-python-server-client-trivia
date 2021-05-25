import socket
import chatlib  # To use chatlib functions or consts, use chatlib.****
import sys

SERVER_IP = "127.0.0.1"  # Our server will run on same computer as client
SERVER_PORT = 5678


# HELPER SOCKET METHODS

def build_and_send_message(conn, code, data):
    """
    Builds a new message using chatlib, wanted code and message.
    Prints debug info, then sends it to the given socket.
    Parameters: conn (socket object), code (str), data (str)
    Returns: Nothing
    """
    full_msg = chatlib.build_message(code, data)
    conn.send(full_msg.encode())
    #  print("\n*massage sent*\ncommand:", code, "\ndata:", data, "\nsend:", full_msg)


def recv_message_and_parse(conn):
    """
    Receives a new message from given socket,
    then parses the message using chatlib.
    Parameters: conn (socket object)
    Returns: cmd (str) and data (str) of the received message.
    If error occurred, will return None, None
    """
    full_msg = conn.recv(10021).decode()
    cmd, data = chatlib.parse_message(full_msg)
    return cmd, data


def buile_send_recv_parse(conn, code, data=""):
    build_and_send_message(conn, code, data)
    return recv_message_and_parse(conn)


def connect():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((SERVER_IP, SERVER_PORT))
    return client_socket


def error_and_exit(error_msg):
    print("XXX Error found: XXX\n", error_msg)
    sys.exit()


def login(conn):
    username = input("Please enter username: \n")
    password = input("Please enter your password: \n")
    login_msg = username+chatlib.DATA_DELIMITER+password
    build_and_send_message(conn, chatlib.PROTOCOL_CLIENT["login_msg"], login_msg)
    answer = recv_message_and_parse(conn)
    while answer[0] != chatlib.PROTOCOL_SERVER["login_ok_msg"]:
        print("\nERROR! "+answer[1])
        username = input("Please enter username: \n")
        password = input("Please enter your password: \n")
        login_msg = username + chatlib.DATA_DELIMITER + password
        build_and_send_message(conn, chatlib.PROTOCOL_CLIENT["login_msg"], login_msg)
        answer = recv_message_and_parse(conn)
    print("logged-in")


def logout(conn):
    build_and_send_message(conn, chatlib.PROTOCOL_CLIENT["logout_msg"], "")
    print("goodbye")


def get_score(conn):
    ask = chatlib.PROTOCOL_CLIENT["score_msg"]
    cmd, data = buile_send_recv_parse(conn, ask, "")
    if cmd != chatlib.PROTOCOL_SERVER["score_msg"]:
        error_and_exit(data)
    else:
        print("Your score is:", data, "points.")


def get_highscore(conn):
    ask = chatlib.PROTOCOL_CLIENT["highscore_msg"]
    cmd, data = buile_send_recv_parse(conn, ask, "")
    if cmd != chatlib.PROTOCOL_SERVER["highscore_msg"]:
        error_and_exit(data)
    else:
        print("\nThe score of all players:\n" + data)


def play_question(conn):
    quest = buile_send_recv_parse(conn, chatlib.PROTOCOL_CLIENT["get_quest_msg"])
    if quest[0] == chatlib.PROTOCOL_SERVER["no_quest_msg"]:
        print("There is no available questions for you.")
        return None
    if quest[0] == chatlib.PROTOCOL_SERVER["error_msg"]:
        error_and_exit(quest[1])
    elif quest[0] == chatlib.PROTOCOL_SERVER["quest_msg"]:
        quest_data = quest[1].split(chatlib.DATA_DELIMITER)
        num = quest_data[0]
        question = quest_data[1]
        answers = [quest_data[2], quest_data[3], quest_data[4], quest_data[5]]
        print("\nQ: ", question)
        for i in range(1, 5):
            print("\t"+str(i)+":\t"+answers[i-1])
        ans_try = input("Choose an answer [1-4]: ")
        while ans_try not in ["1", "2", "3", "4"]:
            ans_try = input("Enter the number of your choice: ")
        score = buile_send_recv_parse(conn, chatlib.PROTOCOL_CLIENT["answer_msg"], num+chatlib.DATA_DELIMITER+ans_try)
        if score[0] == chatlib.PROTOCOL_SERVER["correct_answer_msg"]:
            print("Correct!")
        elif score[0] == chatlib.PROTOCOL_SERVER["wrong_answer_msg"]:
            print("Wrong... the correct answer is: #"+score[1])
        else:
            error_and_exit(score[1])


def get_logged_users(conn):
    logged_users = buile_send_recv_parse(conn, chatlib.PROTOCOL_CLIENT["logged_users_msg"])
    if logged_users[0] == chatlib.PROTOCOL_SERVER["logged_users_list"]:
        print("Logged_users:\n"+logged_users[1])
    else:
        error_and_exit(logged_users[1])


def main():
    sock = connect()
    login(sock)

    choice = input("""
        p       Play a trivia question
        s       Get my score
        h       Get highscore
        l       Get logged users
        q       Quit
        -Enter your choice: """)
    while choice != "q":
        if choice == "p":
            play_question(sock)
        elif choice == "s":
            get_score(sock)
        elif choice == "h":
            get_highscore(sock)
        elif choice == "l":
            get_logged_users(sock)
        else:
            print("Enter the letter of your choice: ")

        choice = input("""
        p       Play a trivia question
        s       Get my score
        h       Get highscore
        l       Get logged users
        q       Quit
        -Enter your choice: """)
    print("Bye!")

    logout(sock)
    sock.close()


if __name__ == '__main__':
    main()
