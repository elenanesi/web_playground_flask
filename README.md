# web_playground_flask
The web data playground website in a scalable version, deployed via Python (Flask)

Setup instructions:

- Install requirements.txt (pip install -r requirements.txt)
- Note: this websites simulates returning users by setting cookies. Disable the functions dedicated to this purpose if you don't want to use this feature.
To do so, you can comment in analytics.js lines 63 to 76 in the acceptAll() function and lines 240 to 244 in the main code.
- In static/analytics.js: 
	- substitute the value for GTM_ID with your own ID at line 2
	- substitute the value for GA_MEASUREMENT_ID with your own ID at line 4 (needed for returning users simulation)

How to launch/use:
- Call main.py to run from the folder you installed the code in. This command will start a server and log the IP address where the website is going to be available at. Normally you can also use http://localhost:8080/
- Visit the website (eg: at http://localhost:8080/)
- Have fun :)


