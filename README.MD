# rqt_lifecycle_controller
`rqt_lifecycle_controller` is a `rqt` plugin that provides a GUI for visualizing and controlling the state of managed nodes.

With this plugin, you can select any node that is registered on the ROS Graph  and add it to the current monitored nodes list. Each node on the list is shown on the GUI as a triplet of buttons: cleanup button, change state button (the one that has the node name) and the remove button.

The buttons do the following:

- Cleanup button: Sends the `cleanup()` transition (change state to `unconfigured`).
- Change State button: Sends a transition following this flow:
    -   `unconfigured` --> `inactive`
    -   `inactive` --> `active`
    -   `active` --> `inactive`
- Remove button: Removes node from the list and thus the triplet from the GUI.

It's important to notice that the `cleanup()` will succesfully transition the node only if the node is in the `inactive` state.


## Color scheme

The color of the buttons incate the state in which the correponding node is:

- `unconfigured`: `purple`
- `inactive`: `yellow`
- `active`: `green`
- `finalized`: `grey`
- `unkwon`: `red` 

The `unknown` state is assumed if the node's `/get_state` service is not ready. This will be always be true if the node isn't a managed node or if the node is not on the ROS Graph (in both cases, the node can be added to the list).
##### Note: this can be changed by changing the `_state_color` dictionary on the `lifecycle_controller_widget.py` file.

## Known nodes

It's possible to have a premade list of known nodes such that every time the plugin is opened, the list contains such known nodes.
This list is in the `resources` directory. To add a node to the list just add a new line with the name of the node.  
An example of this list might be:
### Example
lc_talker  
camera/camera  
/reach1

 ###### Note: the node can be written with and without the initial "/" character, just be sure that the name is the fully qualified name of the node.

## How to compile
```bash
cd <workspace-with-the-package>
colcon build --symlink-install --packages-select rqt_lifecycle_controller
source install/setup.bash
```
###### Note: If you don't compile with the "symlink-install" flag, the plugin will not detect the changes made to the known nodes list.

After compiling the first time you might need to run rqt with the `force-discover` flag because rqt will not know that the plugin is available.

https://github.com/user-attachments/assets/7ea3b933-148b-428b-918b-5f2b9e56070a
