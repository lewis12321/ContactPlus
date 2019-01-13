FROM kennethreitz/pipenv

COPY .env server.py payment_flow.py Pipfile.lock /app/

COPY templates/ /app/templates/

RUN pipenv install --deploy --system --three

CMD bash -c "set -o allexport && source .env && set +o allexport && python3 server.py"