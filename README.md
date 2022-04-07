# system-monitor-client
This is GUI client for flask_system_monitor
This is test client
### First login = registration

![Screenshot from 2022-04-07 10-04-37](https://user-images.githubusercontent.com/90110119/162139914-c838bdb8-ae54-4381-b345-eee99385ea51.png)

### In the settings there is a choice:
* Format data for transfer to server (Tb, Gb, Mg, Kb, B, default = Mb)
* Type data for transfer to server (cpu, memory, storage)
* Interval transfer data in seconds
* Type connect with server (http or Web Socket)

![Screenshot from 2022-04-07 10-05-41](https://user-images.githubusercontent.com/90110119/162140076-9686eb61-074d-4f4c-8589-42609b82b9d7.png)

### Client 
* Start = start data transfer with your settings
* Stop = stop thread
* Run time = time work data transfer (storage to server)
* Create log slice = create log file in client root derictory 
* Convert = converte unix time to utc or utc to unix time 

![Screenshot from 2022-04-07 10-14-33](https://user-images.githubusercontent.com/90110119/162141541-1428a06b-9ed2-4404-8fc6-d2c956371eb1.png)

### requirements
* python 3.9
* requirements.txt
