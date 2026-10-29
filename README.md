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

User ID:
- If the first-party cookie `fc_user_id` is set (opaque ID like `FC000123`), every page pushes `{user_id: <value>}` to the dataLayer before GTM loads; if absent, nothing is pushed.
- Manual GTM step: in GTM-WZ4DNGJW, add a Data Layer Variable named `user_id` and map it to the `user_id` field in the Google tag's (GA4 config tag's) configuration settings — without this step, nothing reaches GA4.


