import sys

from rqt_gui.main import Main

def main():
    plugin = 'rqt_lifecycle_controller.lifecycleController.LifeCycleController'
    main = Main(filename=plugin)
    sys.exit(main.main(standalone=plugin))


if __name__ == '__main__':
    main()