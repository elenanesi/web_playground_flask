# web_playground_flask
The web data playground website in a scalable version, deployed via Python (Flask)

Setup instructions:

- Install requirements.txt (pip install -r requirements.txt)
- Note: this websites simulates returning users by setting cookies. Disable the functions dedicated to this purpose if you don't want to use this feature.
To do so, comment out the `/user_saved` fetch in acceptAll() in analytics.js and the `returning_user_setup` hook in main.py.
  Saved client ids live in the GCS bucket set by the `BUCKET_NAME` env var (file `client_ids.json`).
- In static/analytics.js: 
	- substitute the value for GTM_ID with your own ID at line 2
	- substitute the value for GA_MEASUREMENT_ID with your own ID at line 4 (needed for returning users simulation)

How to launch/use:
- Call main.py to run from the folder you installed the code in. This command will start a server and log the IP address where the website is going to be available at. Normally you can also use http://localhost:8080/
- Visit the website (eg: at http://localhost:8080/)
- Have fun :)



Deploy (Cloud Run, scales to zero):

- The live site is deployed to Cloud Run from source (`Procfile` + `requirements.txt`).
- The project, region, service, bucket and exact deploy command live in `.local/deploy.md`, which is gitignored. Do not copy them into the repo.
- Required env vars: `SECRET_KEY` and `BUCKET_NAME`.
- `SECRET_KEY` must stay the same across deploys/instances, otherwise carts get lost.
- The Cloud Run service account needs `roles/storage.objectAdmin` on the bucket.
- Organization policies may block public (`allUsers`) invoker access; a policy exception may be needed before the service can be made public.
