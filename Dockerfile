FROM kennethreitz/pipenv

COPY server.py account_handling.py payment_flow.py Pipfile.lock /app/

COPY templates/ /app/templates/

RUN pipenv install --deploy --system --three

CMD bash -c "gunicorn server:app"