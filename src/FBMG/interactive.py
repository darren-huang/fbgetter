import getpass

def get_client():
    #  the meat of the program:
    with open(passPath, "r") as f:
        email = f.readline().replace("\n", "")
        pWord = f.readline().replace("\n", "")
    input("email: ")

if __name__ == '__main__':

