from setuptools import setup

package_name = 'rqt_lifecycle_controller'

setup(
    name=package_name,
    version='1.0',
    packages=[package_name],
    package_dir={'': 'src'},
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name + '/resource',
            ['resource/known_nodes.txt']),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name, ['plugin.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    keywords=['ROS'],
    license='BSD',
    entry_points={
        'console_scripts': [
            'rqt_lifecycle_controller = ' + package_name + '.main:main',
        ],
    },
)
