from setuptools import find_packages, setup

package_name = 'vicon_control'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='skn',
    maintainer_email='skn@todo.todo',
    description='TODO: Package description',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'vicon_bridge = vicon_control.vicon_bridge_node:main',
            'vicon_tracker = vicon_control.vicon_tracker_pp_node:main',
        ],
    },
)
