# checkun

pip install pymongo
pip install json
pip install gunicorn
pip install boto3
pip install awscli
pip freeze > requirements.txt
echo python-2.7.10 > runtime.txt
echo web: gunicorn bot:app --log-file=- > Procfile