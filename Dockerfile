FROM kennethreitz/pipenv

COPY server.py payment_flow.py Pipfile.lock /app/

COPY templates/ /app/templates/

RUN pipenv install --deploy --system --three

CMD bash -c "python3 server.py"