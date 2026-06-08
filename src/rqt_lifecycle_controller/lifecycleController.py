from rqt_gui_py.plugin import Plugin

from .lifecycle_controller_widget import LifeCycleControllerWidget

class LifeCycleController(Plugin):

    def __init__(self, context):
        super(LifeCycleController, self).__init__(context)
        self.setObjectName('LifeCycleController')
        self._context = context
        self._node = context.node
        self._widget = LifeCycleControllerWidget(self._node)
        if context.serial_number() > 1:
            self._widget.setWindowTitle(
                self._widget.windowTitle() + (' (%d)' % context.serial_number()))
        context.add_widget(self._widget)

    def _update_title(self):
        if self._context.serial_number() > 1:
            self._widget.setWindowTitle(
                self._widget.windowTitle() + (' (%d)' % self._context.serial_number()))

    def trigger_configuration(self):
        self._update_title()

    def actualizar(self):
        self._widget.refresh_buttons()

    def shutdown_plugin(self):
        self._widget.destroy_clients()
        self._widget.close()
        self._widget.deleteLater()
        self._widget = None
        return super().shutdown_plugin()