import os

from ament_index_python.resources import get_resource


from python_qt_binding.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QScrollArea, QPushButton, QLineEdit, QCompleter
from python_qt_binding.QtCore import QTimer, Qt, QStringListModel
from python_qt_binding.QtGui import QIcon

from lifecycle_msgs.srv import GetState, ChangeState
from lifecycle_msgs.msg import State
from lifecycle_msgs.msg import Transition

from rclpy.validate_node_name import validate_node_name
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.validate_node_name import validate_node_name
from rclpy.validate_namespace import validate_namespace
from rclpy.exceptions import InvalidNodeNameException, InvalidNamespaceException



class LifeCycleControllerWidget(QWidget):

    _dict_nodes = {}
    _timer_revision = None

    reentrant_group = ReentrantCallbackGroup()

    _state_color = {
        State.PRIMARY_STATE_INACTIVE: "yellow",
        State.PRIMARY_STATE_ACTIVE: "green",
        State.PRIMARY_STATE_UNCONFIGURED: "purple",
        State.PRIMARY_STATE_FINALIZED: "grey",
        State.PRIMARY_STATE_UNKNOWN: "red"
                     }

    _transitions = { 
        State.PRIMARY_STATE_ACTIVE : Transition.TRANSITION_DEACTIVATE, # Deactivate()
        State.PRIMARY_STATE_UNCONFIGURED : Transition.TRANSITION_CONFIGURE, # Configure()
        State.PRIMARY_STATE_INACTIVE : Transition.TRANSITION_ACTIVATE # Activate()
    }

    def __init__(self, node):
        super(LifeCycleControllerWidget, self).__init__()
        self.setObjectName('LifeCycleControllerWidget')
        self._node = node
        self.setWindowTitle("Lifecycle controller")
        
        self._main_layout = QVBoxLayout(self)
        
        self._bar_with_buttons = QHBoxLayout(self)

        self._line = QLineEdit(self)
        self._line.returnPressed.connect(self.on_line_returnPressed)
        
        self._model = QStringListModel(self)
        self._node_completer = QCompleter(self)
        self._node_completer.setModel(self._model)
        self._line.setCompleter(self._node_completer)

        self._add_node_button = QPushButton(self)
        self._add_node_button.setIcon(QIcon.fromTheme('list-add'))
        self._add_node_button.clicked.connect(self.on_line_returnPressed)

        self._bar_with_buttons.addWidget(self._line)
        self._bar_with_buttons.addWidget(self._add_node_button)

        self._main_layout.addLayout(self._bar_with_buttons)

        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._main_layout.addWidget(self._scroll)

        _, package_path = get_resource('packages', 'rqt_lifecycle_controller')
        self._ui_file = os.path.join(package_path, 'share', 'rqt_lifecycle_controller', 'resource', 'known_nodes.txt')
        known_nodes = []
        with open(self._ui_file, 'r') as file:
            for linea in file:
                linea = linea.rstrip()
                known_nodes.append(linea)

        self.create_buttons(known_nodes)

        self._refresh_buttons_timer = QTimer(self)
        self._refresh_buttons_timer.timeout.connect(self.refresh_buttons)
        self._refresh_buttons_timer.start(1000)

    def create_buttons(self, known_nodes):
        
        self._buttons_container = QWidget()
        self._buttons_layout = QVBoxLayout(self._buttons_container)

        for name in known_nodes:
            self.add_node(name)

        self._scroll.setWidget(self._buttons_container)

    def refresh_buttons(self):
        node_list = []
        nodes_info = self._node.get_node_names_and_namespaces()
        for name, namespace in nodes_info:
            fqn = f"{namespace if namespace.endswith('/') else namespace + '/'}{name}"[1:]
            node_list.append(fqn)
            node_list.append("/" + fqn)
        self._model.setStringList(node_list)
        buttons = self._buttons_container.findChildren(QPushButton)
        futures = []

        if self._timer_revision is not None:
            self._timer_revision.cancel()
            self._node.destroy_timer(self._timer_revision)
            self._timer_revision = None

        for button in buttons:
            if button.text() == "": continue # Ignore all non node related buttons
            _, get, _ = self._dict_nodes[button.text()]
            if not get.service_is_ready():
                button.setStyleSheet(f"""background-color: {self._state_color[State.PRIMARY_STATE_UNKNOWN]};""")
                button.setProperty("State", State.PRIMARY_STATE_UNKNOWN) 
            else:
                request = GetState.Request()
                futures.append((get.call_async(request), button))
        self._timer_revision = self._node.create_timer(0.3, lambda: self.change_buttons_color(futures))

    def change_buttons_color(self, futures):
        self._timer_revision.cancel()
        for call_future, boton in futures:
            response = call_future.result()
            try:
                if not response:
                    boton.setStyleSheet(f"""background-color: {self._state_color[State.PRIMARY_STATE_UNKNOWN]};""")
                    boton.setProperty("State", State.PRIMARY_STATE_UNKNOWN)
                else:
                    boton.setStyleSheet(f"""background-color: {self._state_color[response.current_state.id]};""")
                    boton.setProperty("State", response.current_state.id)
            except: continue # The button was deleted

    def button_clicked(self, name, button):
        state = button.property("State")

        if state is None: return 
        if state in {State.PRIMARY_STATE_UNKNOWN, State.PRIMARY_STATE_FINALIZED}:
            return

        self._change_state(name, self._transitions[state])

    def elim_node_from_list(self, name, container):
        self._dict_nodes.pop(name)
        container.deleteLater()

    def cleanup_node(self, name) :
        #CleanUp()
        self._change_state(name, Transition.TRANSITION_CLEANUP)
        return

    def _change_state(self, node, transition):
        time_out = 1.0
        request = ChangeState.Request()
        request.transition.id = transition
        (_, _, change) = self._dict_nodes[node]
        change.call_async(request)
    
    def on_line_returnPressed(self):
        name = str(self._line.text())
        if name.strip() and name not in self._dict_nodes and ("/" + name) not in self._dict_nodes:
            self.add_node(name)
            
    def create_generic_button(self, name, function):
        button = QPushButton(name)

        button.setCursor(Qt.OpenHandCursor)

        button.clicked.connect(function)
        return button

    def create_button(self, name):
        button = self.create_generic_button(name, (lambda : self.button_clicked(name, button)))
        return button

    def create_eliminate_button(self, name, container):
        button =  self.create_generic_button("", (lambda: self.elim_node_from_list(name, container)))
        button.setIcon(QIcon.fromTheme('list-remove'))
        return button

    def create_cleanup_button(self, name):
        button = self.create_generic_button("", (lambda: self.cleanup_node(name)))
        button.setIcon(QIcon.fromTheme('edit-clear'))
        return button

    def create_client(self, name):
        get = self._node.create_client(GetState, name + '/get_state', callback_group=self.reentrant_group)
        change = self._node.create_client(ChangeState, name + '/change_state', callback_group=self.reentrant_group)
        self._dict_nodes[name] = (name, get, change)

    def create_button_layout(self, name):
        container = QWidget()
            
        row_layout = QHBoxLayout(container)
        
        cleanup_button = self.create_cleanup_button(name)
        button = self.create_button(name)
        eliminate_button = self.create_eliminate_button(name, container)
        
        row_layout.addWidget(cleanup_button)
        row_layout.addWidget(button)
        row_layout.addWidget(eliminate_button)
        return container
    
    def is_valid_node_name(self, name):
        parts = name.rsplit('/', 1)
        ns = parts[0] if parts[0] != '' else '/'
        name = parts[1]

        if not name:
            return False

        try:
            validate_namespace(ns)
            validate_node_name(name)
            return True
        except (InvalidNamespaceException, InvalidNodeNameException) as e:
            return False

    def add_node(self, name):
        if name[0] != '/' : name = "/" + name
        if not self.is_valid_node_name(name) : return 
        container = self.create_button_layout(name)
        self.create_client(name)
        self._buttons_layout.addWidget(container, alignment=Qt.AlignCenter)

    def destroy_clients(self):
        for x in self._dict_nodes:
            (_, get, change) = self._dict_nodes[x]
            self._node.destroy_client(get)
            self._node.destroy_client(change)
            self._dict_nodes.clear()