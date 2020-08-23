# Python Socket Programming
<p align="center">
<img src="./client_data/sample_image.png" alt="drawing" width="512"/>
</p>

A sample socket programming in python using low level networking interface *socket*. You will find follwing on top of vanilla implementation you find in any first tutorial link you get from googling:
* Allowing communication with trusted client only, check using first received message from client as key message
* Multithreading to handle multiple clients
* Use of pickel to serialize any type of data 
* Handling of variable length data by passing payload size along with payload
* Passing data identifier with payload as additional information to take specific action accordingly (eg. if data identifier is image then save payload as image)
* Using keyboard interrupt to close client and server cleanly

Note: While writing this program python 3.7.4 was used

Feel free to request more feature you would like, i wil try to add it when i get time

