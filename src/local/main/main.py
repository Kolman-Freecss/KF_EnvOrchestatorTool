import build
import init_jenkins

def main():
    try:
        print('Starting Jenkins configuration...')
        init_jenkins.start()
        print('Building Jenkins... Done!')

        print('Building Jenkins Job...')
        build.start()
        print('Building Jenkins Job... Done!')
    except Exception as e:
        print("Error: ", e)

main()