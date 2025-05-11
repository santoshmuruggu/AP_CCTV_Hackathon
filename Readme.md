
first: create a virtual env with python3.10
and run 
pip install --upgrade pip 
pip install -r requirments.txt


to use the video_processor.py: (this will extract the video and add to the database)
python video_processor.py path/to/your_video.mp4
eg: 
use case: 
python video_processor.py Anomaly/videos/GUNNY BAG STACKER IF YOU REQUIRED PLEASE CALL ME... 9949578818... TNQ.mp4

to use the streamlit app: (this will get the info from the database)
streamlit run streamlit_app.py
